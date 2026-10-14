extends RefCounted

# Self-contained prototype of the distance-driven walk controller proposed in
# docs/character-visuals/...exploration-walk-pipeline_feasibility-review_m8-v01 (C5, section 4).
# Not wired into any runtime scene. Frame counts, cycle length and contact frames are data,
# normally read from a variant manifest; a missing declaration is a failure, not a default.

const MODE_IDLE := "idle"
const MODE_WALK := "walk"
const MODE_SETTLE := "settle"
const REQUIRED_KEYS := [
	"walk_frame_count",
	"cycle_length_px",
	"contact_frames",
	"settle_hold_seconds",
	"idle_frame_count",
	"idle_hold_seconds",
	"facing_hysteresis_ratio",
]
# Same movement threshold the exploration scenes use to decide walk versus idle.
const MOVE_EPSILON_PX := 0.05
# Guards frame boundaries against accumulated float error (e.g. 50 ticks of 0.1 px).
const BOUNDARY_EPSILON_PX := 0.0001
# Same guard for summed tick deltas (e.g. 6 x 1/60 s falling just short of 0.1 s).
const HOLD_EPSILON_SECONDS := 0.000001

var last_error := ""
var walk_frame_count := 0
var cycle_length_px := 0.0
var contact_frames: Array[int] = []
var settle_hold_seconds := 0.0
var idle_frame_count := 0
var idle_hold_seconds := 0.0
var facing_hysteresis_ratio := 1.0

var facing := ""
var mode := MODE_IDLE
var cycle_distance := 0.0
var settle_frame := -1
var mode_time := 0.0


func configure(spec: Dictionary, initial_facing: String = "south") -> bool:
	last_error = ""
	for key in REQUIRED_KEYS:
		if not spec.has(key):
			return _fail("missing declaration: %s" % key)
	if not _is_whole(spec["walk_frame_count"]) or int(spec["walk_frame_count"]) < 2:
		return _fail("walk_frame_count must be an int >= 2")
	if not _is_whole(spec["idle_frame_count"]) or int(spec["idle_frame_count"]) < 1:
		return _fail("idle_frame_count must be an int >= 1")
	if not _is_number(spec["cycle_length_px"]) or float(spec["cycle_length_px"]) <= 0.0:
		return _fail("cycle_length_px must be a finite number > 0")
	# Zero settle is allowed and means "no hold": a stop goes straight to idle.
	if not _is_number(spec["settle_hold_seconds"]) or float(spec["settle_hold_seconds"]) < 0.0:
		return _fail("settle_hold_seconds must be a finite number >= 0")
	if not _is_number(spec["idle_hold_seconds"]) or float(spec["idle_hold_seconds"]) <= 0.0:
		return _fail("idle_hold_seconds must be a finite number > 0")
	if not _is_number(spec["facing_hysteresis_ratio"]) or float(spec["facing_hysteresis_ratio"]) < 1.0:
		return _fail("facing_hysteresis_ratio must be a finite number >= 1.0")
	if typeof(spec["contact_frames"]) != TYPE_ARRAY:
		return _fail("contact_frames must be an array of frame indices")
	var frames: Array[int] = []
	for value in spec["contact_frames"]:
		if not _is_whole(value) or int(value) < 0 or int(value) >= int(spec["walk_frame_count"]):
			return _fail("contact frame out of range: %s" % str(value))
		if not frames.has(int(value)):
			frames.append(int(value))
	if frames.is_empty():
		return _fail("contact_frames must declare at least one frame")
	if not ["south", "north", "east", "west"].has(initial_facing):
		return _fail("unknown facing: %s" % initial_facing)
	frames.sort()
	walk_frame_count = int(spec["walk_frame_count"])
	cycle_length_px = float(spec["cycle_length_px"])
	contact_frames = frames
	settle_hold_seconds = float(spec["settle_hold_seconds"])
	idle_frame_count = int(spec["idle_frame_count"])
	idle_hold_seconds = float(spec["idle_hold_seconds"])
	facing_hysteresis_ratio = float(spec["facing_hysteresis_ratio"])
	facing = initial_facing
	mode = MODE_IDLE
	mode_time = 0.0
	settle_frame = contact_frames[0]
	cycle_distance = _frame_start_distance(settle_frame)
	return true


# One gameplay tick. `travelled_px` is the distance the actor really moved this tick
# (after collision sliding), so pushing into a wall does not animate the legs.
func tick(delta: float, travelled_px: float, input_direction: Vector2) -> void:
	update_facing(input_direction)
	if travelled_px > MOVE_EPSILON_PX:
		if mode != MODE_WALK:
			# Resume from the held contact frame so walk-in matches the pose on screen.
			cycle_distance = _frame_start_distance(settle_frame)
			mode = MODE_WALK
			mode_time = 0.0
		cycle_distance = fposmod(cycle_distance + travelled_px, cycle_length_px)
		return
	if mode == MODE_WALK:
		# The stop tick shows the contact pose; the hold is timed from here on.
		settle_frame = nearest_contact_frame(walk_frame())
		mode = MODE_SETTLE if settle_hold_seconds > 0.0 else MODE_IDLE
		mode_time = 0.0
		return
	mode_time += delta
	if mode == MODE_SETTLE and mode_time >= settle_hold_seconds - HOLD_EPSILON_SECONDS:
		# Carry the overshoot so idle timing follows elapsed time, not tick boundaries.
		mode = MODE_IDLE
		mode_time = maxf(mode_time - settle_hold_seconds, 0.0)


func update_facing(input_direction: Vector2) -> String:
	if input_direction.length_squared() <= 0.0:
		return facing
	var dominant := _dominant_facing(input_direction)
	if dominant == facing:
		return facing
	var held := _component_along(facing, input_direction)
	if held > 0.0:
		# Current facing is still a pressed axis: switch only when the new axis clearly dominates.
		var challenger := _component_along(dominant, input_direction)
		if challenger < held * facing_hysteresis_ratio:
			return facing
	facing = dominant
	return facing


func walk_frame() -> int:
	var step := cycle_length_px / float(walk_frame_count)
	return int(floor((cycle_distance + BOUNDARY_EPSILON_PX) / step)) % walk_frame_count


# Frame to display for the current mode; pair with `mode` and `facing` to pick a texture.
func display_frame() -> int:
	match mode:
		MODE_WALK:
			return walk_frame()
		MODE_SETTLE:
			return settle_frame
	return int(floor(mode_time / idle_hold_seconds)) % idle_frame_count


func nearest_contact_frame(frame: int) -> int:
	var best := contact_frames[0]
	var best_gap := walk_frame_count
	for contact in contact_frames:
		var forward := posmod(contact - frame, walk_frame_count)
		var backward := posmod(frame - contact, walk_frame_count)
		# Ties resolve forward, so the stop keeps the direction of travel.
		var gap := mini(forward, backward)
		if gap < best_gap or (gap == best_gap and forward <= backward):
			best = contact
			best_gap = gap
	return best


func snapshot() -> Dictionary:
	return {"mode": mode, "facing": facing, "frame": display_frame(), "cycle_distance": cycle_distance}


func _frame_start_distance(frame: int) -> float:
	return cycle_length_px * float(frame) / float(walk_frame_count)


func _dominant_facing(direction: Vector2) -> String:
	if absf(direction.y) >= absf(direction.x):
		return "south" if direction.y > 0.0 else "north"
	return "east" if direction.x > 0.0 else "west"


func _component_along(direction_name: String, direction: Vector2) -> float:
	match direction_name:
		"south":
			return direction.y
		"north":
			return -direction.y
		"east":
			return direction.x
		"west":
			return -direction.x
	return 0.0


# JSON manifests parse every number as float, so whole floats are accepted as counts.
func _is_whole(value: Variant) -> bool:
	if typeof(value) == TYPE_INT:
		return true
	return typeof(value) == TYPE_FLOAT and float(value) == floor(float(value))


# Durations, lengths and ratios must be real numbers; NaN and INF pass every
# comparison check unnoticed, and strings or arrays would crash float().
func _is_number(value: Variant) -> bool:
	if typeof(value) == TYPE_INT:
		return true
	return typeof(value) == TYPE_FLOAT and is_finite(float(value))


func _fail(message: String) -> bool:
	last_error = message
	return false
