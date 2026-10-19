extends Node

# Opt-in female four-direction exploration pilot (UNAPPROVED; not art, motion or default adoption). Off by default:
# without `-- --female-complete-exploration-pilot` (or enabled_override = 1) attach() returns null before reading any
# file and the host keeps its existing sprite path. With the flag, attach() loads the self-contained package under
# res://data/fexp + res://assets/fexp + res://scripts/fexp once per session (EAST v03, WEST v01, NORTH v06 model
# copies, the extracted SOUTH v10r1 classes and the 12-phase idle-four loops) and fails the whole set on any error or
# hash mismatch, so no direction ever mixes with the legacy 32x48 frames.
#
# STRICT FALLBACK: the representative package/runtime JSON are raw-SHA pinned by the input guard and every runtime
# file is validated (paths, raw hashes, text-LF model hashes, PXO ZIP entries/layer bytes, PNG decode/size, SOUTH part
# hashes/alpha/counts and all nested field types) BEFORE a model constructor, SOUTH compositor or child/scale/flip
# mutation. Unknown, mutated or malformed packages are refused whole with a clear static refusal() status. This is
# not a general/custom package loader. Failures never leave a driver child or a changed target transform.
#
# The host calls step(delta, previous, actual, facing) once per frame AFTER its movement / collision / clamp and before
# it copies the hero texture (canopy silhouette). Presentation only: position, speed, collision, camera and y-sort stay
# the host's. face() / walk() / idle() are no-ops here, so nothing advances twice.
#   * The facing model sees only the facing axis of the ACTUAL displacement (a blocked or zero move is a stop).
#   * A new facing resets the incoming model to its exact rest at the current floor pin and bootstraps it from the
#     previous position; the same-facing re-press keeps the live model. No opposite-intent placeholder is ever used.
#     The instant handoff is not an authored turn and keeps no foot identity across 90 degrees.
#   * Idle (model at rest) plays the idle-four loop from phase 0, which equals each model's final rest exactly.
#   * Live poses come from the authoritative renderers. Cached ImageTextures are keyed by the complete render input
#     (every state field the renderer reads), bounded per direction; misses past the bound update one persistent
#     ImageTexture per cell size. Nothing is ever shown from a different state.
# PER-DRIVER STATE: the static cache shares only immutable inputs (validated scripts, idle textures, runtime contract);
# each attached driver owns its EAST/WEST/NORTH model objects, SOUTH Comp10 and Loco10r1, rest snapshots and caches.
# Two hosts can therefore reset/advance their own gait without touching each other.
# Pivot (40, 104) is the floor line, drawn FLOOR_DROP_TEXELS below the node like the sprite-set pilot; scale 0.5.

const Guard := preload("res://scripts/fexp/rpg-2-star-ocean-the-second_female-complete-explore_input-guard_v01_20261019-190507-a7d3e9b1.gd")
const FLAG := "--female-complete-exploration-pilot"
const ACTOR := "protagonist-female"
const PACKAGE := "res://data/fexp/rpg-2-star-ocean-the-second_female-complete-explore_package_v01_20261019-184500-f2c0a7e1.json"
const SOUTH_RUNTIME := "res://data/fexp/rpg-2-star-ocean-the-second_female-complete-explore_south-runtime_v01_20261019-184900-f2c0a7e1.json"
const DIRECTIONS := ["south", "west", "north", "east"]
const PIVOT := Vector2(40.0, 104.0)
const FLOOR_DROP_TEXELS := 2.0
const CACHE_LIMIT := 192
# Model state fields their render_pose() reads (checked against the copies by the package test).
const RENDER_KEYS := {"east": ["mode", "q", "feet", "body", "returnWeight"], "west": ["mode", "q", "feet", "body", "returnWeight"],
	"north": ["mode", "q", "feet", "body", "live"]}

static var enabled_override := -1
static var package_override := ""
static var runtime_override := ""
static var _assets := {}
static var last_refusal := {}
static var load_count := 0
static var construct_count := 0

var sprite: Sprite2D
var shadow: Sprite2D
var assets := {}
var runtime := {}
var facing := "south"
var bootstrapped := false
var model_mode := "idle"
var showing_idle := true
var idle_clock := 0.0
var last_key := ""
var last_texture: Texture2D
var last_state := {}
var cache := {}
var live_textures := {}
var oracle := false
var oracle_mismatch := 0
var stats := {"steps": 0, "step_us_total": 0, "step_us_max": 0, "renders": 0, "hits": 0, "live_updates": 0, "switches": 0}


static func enabled() -> bool:
	if enabled_override >= 0:
		return enabled_override == 1
	return OS.get_cmdline_user_args().has(FLAG)


static func refusal() -> Dictionary:
	return last_refusal.duplicate(true)


static func attach(target: Sprite2D, actor: String, initial_facing: String) -> Node:
	# Flag off is checked before any file read (load_count/Guard.io_reads must stay put).
	if not enabled() or actor != ACTOR:
		last_refusal = {}
		return null
	var loaded := load_assets()
	if not loaded["ok"]:
		last_refusal = {"stage": String(loaded.get("stage", "")), "error": String(loaded.get("error", ""))}
		return null
	# Construct and validate all per-driver mutable state before touching the target.
	var built := _build_runtime(loaded)
	if not built["ok"]:
		last_refusal = {"stage": String(built.get("stage", "")), "error": String(built.get("error", ""))}
		return null
	var driver = new()
	driver.name = "FemaleCompleteExplorationPilot"
	driver.sprite = target
	driver.assets = loaded
	driver.runtime = built["runtime"]
	driver.facing = initial_facing if DIRECTIONS.has(initial_facing) else "south"
	driver.shadow = Sprite2D.new()
	driver.shadow.name = "FemaleCompleteSouthShadow"
	driver.shadow.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	driver.shadow.show_behind_parent = true
	driver.shadow.modulate = Color(1, 1, 1, float(loaded["shadow_alpha"]))
	# Only now mutate the host node; everything above can still return null without side effects.
	target.scale = Vector2(0.5, 0.5)
	target.flip_h = false
	target.add_child(driver.shadow)
	target.add_child(driver)
	driver.set_process(false)
	driver._show_idle()
	last_refusal = {}
	return driver


static func clear_cache() -> void:
	_assets.clear()
	last_refusal = {}
	load_count = 0
	construct_count = 0


# Validated immutable bundle: scripts, idle textures, phase timing and the pinned runtime contract.
# Model/compositor/loco objects are never stored here.
static func load_assets(path := "") -> Dictionary:
	var package_path := path if path != "" else (package_override if package_override != "" else PACKAGE)
	var runtime_path := runtime_override if runtime_override != "" else SOUTH_RUNTIME
	var cache_key := package_path + "|" + runtime_path
	if _assets.has(cache_key):
		return _assets[cache_key]
	load_count += 1
	var result := {"ok": false, "error": "", "stage": ""}
	_assets[cache_key] = result
	var checked := Guard.load_pinned(package_path, runtime_path)
	if not checked["ok"]:
		result["stage"] = String(checked.get("stage", ""))
		result["error"] = String(checked.get("error", ""))
		return result
	var package: Dictionary = checked["package"]
	var south_runtime: Dictionary = checked["runtime"]
	var scripts := {}
	for d in ["east", "west", "north"]:
		var script := load(String(package["models"][d])) as GDScript
		if script == null:
			result["stage"] = "model_script"
			result["error"] = "model script " + d
			return result
		scripts[d] = script
	var south_script := load(String(package["south_model"])) as GDScript
	if south_script == null:
		result["stage"] = "south_script"
		result["error"] = "south model script"
		return result
	var idle := {}
	for d in DIRECTIONS:
		var frames := []
		var by_sha := {}
		for f in package["idle"]["directions"][d]:
			var sha := String(f["sha256"])
			if not by_sha.has(sha):
				var image := Image.load_from_file(ProjectSettings.globalize_path(String(f["file"])))
				if image == null or image.is_empty() or image.get_size() != Vector2i(80, 112):
					result["stage"] = "idle_frame"
					result["error"] = "idle frame " + String(f["file"])
					return result
				image.convert(Image.FORMAT_RGBA8)
				by_sha[sha] = {"image": image, "texture": ImageTexture.create_from_image(image)}
			frames.append(by_sha[sha])
		if frames.size() != 12:
			result["stage"] = "idle_count"
			result["error"] = "idle phase count " + d
			return result
		idle[d] = frames
	var seconds: Array = package["idle"]["phase_seconds"]
	result.merge({"ok": true, "scripts": scripts, "south_script": south_script, "idle": idle,
		"phase_seconds": seconds, "cycle": _sum(seconds), "south_runtime": south_runtime,
		"shadow_alpha": float(south_runtime["shadow_alpha"]),
		"package_path": package_path, "runtime_path": runtime_path}, true)
	return result


# Per-driver mutable runtime. Validation has already proved every input; constructors only run here.
static func _build_runtime(assets: Dictionary) -> Dictionary:
	var rt := {"models": {}, "rests": {}, "south_comp": null, "south_loco": null, "south_rest_shadow": null}
	for d in ["east", "west", "north"]:
		construct_count += 1
		var model = assets["scripts"][d].new()
		if model == null or model.original == null or model.original.is_empty():
			return {"ok": false, "stage": "model_construct", "error": "model source " + d}
		rt["models"][d] = model
		rt["rests"][d] = _capture_rest(model)
	construct_count += 1
	var comp = assets["south_script"].Comp10.new()
	if comp == null:
		return {"ok": false, "stage": "south_comp", "error": "SOUTH compositor"}
	for pair in assets["south_runtime"]["part_lists"]:
		var err: String = comp.load_parts(pair[0], String(pair[1]), assets["south_runtime"]["manifest"]["rig"])
		if err != "":
			return {"ok": false, "stage": "south_parts", "error": "SOUTH parts: " + err}
	comp.setup9(assets["south_runtime"]["art_amendment"])
	comp.setup10(assets["south_runtime"]["leg_rule"], int(assets["south_runtime"]["island_max_texels"]))
	var rest_shadow = _south_rest_shadow(comp)
	if not rest_shadow is Image:
		return {"ok": false, "stage": "south_rest", "error": "SOUTH rest shadow"}
	rt["south_comp"] = comp
	rt["south_rest_shadow"] = ImageTexture.create_from_image(rest_shadow)
	return {"ok": true, "runtime": rt}


# Exact rest = every script variable as constructed, except the immutable source layers.
static func _capture_rest(model) -> Dictionary:
	var rest := {}
	for p in model.get_property_list():
		if not (int(p["usage"]) & PROPERTY_USAGE_SCRIPT_VARIABLE):
			continue
		var value = model.get(p["name"])
		if value is Image or String(p["name"]) == "layers":
			continue
		rest[p["name"]] = value.duplicate(true) if (value is Array or value is Dictionary) else value
	return rest


static func _south_rest_shadow(comp):
	var neutral := {"bob": 0, "hdy": 0, "sx": 0, "csx": 0, "arms": {"R": "N", "L": "N"},
		"feet": {"vl": {"o": 0, "lift": 0, "view": "v8", "kin": 0}, "vr": {"o": 0, "lift": 0, "view": "v8", "kin": 0}}}
	var composed = comp.compose(neutral)
	if not composed is Dictionary or composed.has("error") or not composed.get("shadow") is Image:
		return null
	return composed["shadow"]


static func _sum(values: Array) -> float:
	var total := 0.0
	for v in values:
		total += float(v)
	return total


# Host-call compatibility with the sprite-set pilot; presentation advances only in step().
func face(_next_facing: String) -> void:
	pass


func walk() -> void:
	pass


func idle() -> void:
	pass


func step(delta: float, previous: Vector2, actual: Vector2, host_facing: String) -> void:
	var t0 := Time.get_ticks_usec()
	if not DIRECTIONS.has(host_facing):
		host_facing = facing
	if not bootstrapped or host_facing != facing:
		_switch(host_facing, previous)
	var at_rest := true
	if facing == "south":
		var r: Dictionary = runtime["south_loco"].tick(actual.y > previous.y + 0.000001, delta, int(round(actual.y * 2.0)))
		at_rest = bool(r["show_v8"])
		model_mode = "rest" if at_rest else "moving"
		if not at_rest:
			_show_south(r["state"])
	else:
		var model = runtime["models"][facing]
		var coordinate := actual.y if facing == "north" else actual.x
		var state: Dictionary = model.advance(delta, coordinate, -1.0 if facing == "west" else 1.0)
		model_mode = String(state["mode"])
		at_rest = model_mode == "idle"
		if not at_rest:
			_show_model(model, state)
	if at_rest:
		if not showing_idle:
			idle_clock = 0.0
		else:
			idle_clock = fposmod(idle_clock + delta, float(assets["cycle"]))
		_show_idle()
	var spent := Time.get_ticks_usec() - t0
	stats["steps"] += 1
	stats["step_us_total"] += spent
	stats["step_us_max"] = maxi(int(stats["step_us_max"]), spent)


func _switch(next_facing: String, pin: Vector2) -> void:
	facing = next_facing
	bootstrapped = true
	stats["switches"] += 1
	if facing == "south":
		var loco = assets["south_script"].Loco10r1.new()
		loco.stagger = bool(assets["south_runtime"]["stagger"])
		loco.setup(assets["south_runtime"]["manifest"], int(round(pin.y * 2.0)))
		runtime["south_loco"] = loco
	else:
		var model = runtime["models"][facing]
		var rest: Dictionary = runtime["rests"][facing]
		for name in rest:
			var value = rest[name]
			model.set(name, value.duplicate(true) if (value is Array or value is Dictionary) else value)
		# Bootstrap at the current floor pin with no intent: the rest model only records its world coordinate.
		model.advance(0.0, pin.y if facing == "north" else pin.x, 0.0)
	showing_idle = false
	idle_clock = 0.0
	_show_idle()


func idle_phase() -> int:
	var t := idle_clock
	var seconds: Array = assets["phase_seconds"]
	for i in seconds.size():
		t -= float(seconds[i])
		if t < -0.000001:
			return i
	return 0


func _show_idle() -> void:
	showing_idle = true
	var phase := idle_phase()
	last_key = "idle:%s:%d" % [facing, phase]
	_apply(assets["idle"][facing][phase]["texture"], null)
	if facing == "south":
		_apply_shadow(runtime["south_rest_shadow"])
	else:
		_apply_shadow(null)


func _show_model(model, state: Dictionary) -> void:
	showing_idle = false
	last_state = state.duplicate(true)
	var fields := {}
	for k in RENDER_KEYS[facing]:
		fields[k] = state[k]
	var key := facing + ":" + var_to_str(fields)
	last_key = key
	if cache.has(key):
		stats["hits"] += 1
		if oracle:
			var check: Image = model.render_pose(state)["full"]
			if check.get_data() != cache[key]["image"].get_data():
				oracle_mismatch += 1
		_apply(cache[key]["texture"], null)
		_apply_shadow(null)
		return
	stats["renders"] += 1
	var image: Image = model.render_pose(state)["full"]
	_apply(_store(key, image, null), null)
	_apply_shadow(null)


func _show_south(state: Dictionary) -> void:
	showing_idle = false
	last_state = state.duplicate(true)
	var key := "south:" + var_to_str(state)
	last_key = key
	if cache.has(key):
		stats["hits"] += 1
		if oracle:
			var check: Dictionary = runtime["south_comp"].compose(state)
			if check["image"].get_data() != cache[key]["image"].get_data():
				oracle_mismatch += 1
			if not cache[key].has("shadow_image") or check["shadow"].get_data() != cache[key]["shadow_image"].get_data():
				oracle_mismatch += 1
		_apply(cache[key]["texture"], null)
		_apply_shadow(cache[key]["shadow_texture"])
		return
	stats["renders"] += 1
	var c: Dictionary = runtime["south_comp"].compose(state)
	if c.has("error"):
		last_refusal = {"stage": "south_compose", "error": String(c["error"])}
		return
	_store(key, c["image"], c["shadow"])
	_apply(cache[key]["texture"] if cache.has(key) else live_textures[_size_key(c["image"], "")], null)
	_apply_shadow(cache[key]["shadow_texture"] if cache.has(key) else live_textures[_size_key(c["shadow"], "shadow")])


func _store(key: String, image: Image, shadow_image) -> Texture2D:
	var per_direction := 0
	for k in cache:
		if String(k).begins_with(facing + ":"):
			per_direction += 1
	if per_direction < CACHE_LIMIT:
		var entry := {"image": image, "texture": ImageTexture.create_from_image(image)}
		if shadow_image != null:
			entry["shadow_image"] = shadow_image
			entry["shadow_texture"] = ImageTexture.create_from_image(shadow_image)
		cache[key] = entry
		return entry["texture"]
	stats["live_updates"] += 1
	var tex := _live(image, "")
	if shadow_image != null:
		_live(shadow_image, "shadow")
	return tex


func _size_key(image: Image, role: String) -> String:
	return "%s%dx%d" % [role, image.get_width(), image.get_height()]


func _live(image: Image, role: String) -> ImageTexture:
	var k := _size_key(image, role)
	if not live_textures.has(k):
		live_textures[k] = ImageTexture.create_from_image(image)
	else:
		(live_textures[k] as ImageTexture).update(image)
	return live_textures[k]


func _apply(texture: Texture2D, _unused) -> void:
	last_texture = texture
	sprite.texture = texture
	sprite.offset = Vector2(texture.get_size()) * 0.5 - PIVOT + Vector2(0.0, FLOOR_DROP_TEXELS)


func _apply_shadow(texture: Texture2D) -> void:
	shadow.visible = texture != null
	if texture != null:
		shadow.texture = texture
		shadow.offset = Vector2(texture.get_size()) * 0.5 - PIVOT + Vector2(0.0, FLOOR_DROP_TEXELS)


func cache_bytes() -> int:
	var total := 0
	for k in cache:
		var image: Image = cache[k]["image"]
		total += image.get_width() * image.get_height() * 4 * (3 if cache[k].has("shadow_texture") else 2)
	return total


func report() -> Dictionary:
	var r := stats.duplicate()
	r["facing"] = facing
	r["model_mode"] = model_mode
	r["showing_idle"] = showing_idle
	r["idle_phase"] = idle_phase()
	r["cache_entries"] = cache.size()
	r["cache_bytes_estimate"] = cache_bytes()
	r["oracle_mismatch"] = oracle_mismatch
	r["key"] = last_key
	r["models"] = runtime.get("models", {})
	return r
