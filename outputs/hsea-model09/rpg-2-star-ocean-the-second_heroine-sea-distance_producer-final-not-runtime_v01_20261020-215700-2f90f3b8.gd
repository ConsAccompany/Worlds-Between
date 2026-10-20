extends RefCounted

# HSEA09 — bounded PURE locomotion phase model for an OPT-IN Sea-style heroine driver.
#
# Not a loader, host, scene, sprite, animation or collision change. It reads no input intent and
# never touches a Node/Sprite/collision shape. The host calls step() ONCE per frame AFTER applying
# its own movement/collision/clamp, passing the position before and after that movement. Engine
# position, speed, collision and camera remain the host's; this file only maps ACTUAL Euclidean
# displacement to a 12-frame walk phase and a bounded cosmetic stop settle.
#
# Contract summary:
#   * phase is normalized 0 <= phase < 1; frame = floor(phase * 12), 0..11 (never 12).
#   * Walk phase advances by distance / cycle_distance_logical (default 48), never by wallclock.
#     Horizontal, vertical and diagonal displacement use the same Euclidean length.
#   * displacement <= MOVE_EPSILON_LOGICAL (including a fully blocked collision) is a stop: it adds
#     no walk phase. No input vector is read or inferred.
#   * A same-facing re-press during settle resumes from the CURRENT displayed phase (settle is not
#     reset, no second phase rise). A facing change (reversal or 90 degrees) resets the incoming
#     phase to contact 0 once; no foot/body identity is preserved across the turn.
#   * A stop advances the phase COSMETICALLY to the first contact strictly ahead (0.5 or 1.0 -> 0)
#     over settle_duration (default .12 s, never more than .12 s), then returns exact idle frame 0.
#     The settle is visual only. This model never claims true world foot lock: the host moved the
#     actor and collision may have shortened the actual displacement.
#   * settle_entry_frame is retained for a supplemental two-pose bridge the root may choose.
#   * Idle owns no advancing clock: repeated idle steps return frame 0 / phase 0 with elapsed 0.
#   * Invalid/non-finite delta or positions and unknown facings return a safe refusal with NO state
#     mutation. Displacement > 64 logical per step is a teleport: it resets safely to idle contact 0
#     instead of advancing a giant phase. Valid huge deltas clamp the settle to its duration in one
#     step (no loop). Configuration is validated (finite positive cycle, finite positive settle
#     duration <= .12 default .12); a rejected configuration leaves the previous one intact.
#   * All state is per instance. There is no static mutable gait state.
#
# Deterministic numeric checks live in tests/hsea09/. They are a synthetic fixture, NOT gameplay
# evidence, motion review or creator approval.

const DIRECTIONS := ["south", "north", "east", "west"]
const WALK_FRAMES := 12
const DEFAULT_CYCLE_DISTANCE_LOGICAL := 48.0
const DEFAULT_SETTLE_DURATION := 0.12
const MAX_SETTLE_DURATION := 0.12
const MOVE_EPSILON_LOGICAL := 0.0001
const TELEPORT_DISTANCE_LOGICAL := 64.0
const FRAME_BOUNDARY_EPSILON := 0.000000001
const CONTACT_BOUNDARY_EPSILON := 0.000000001
const SETTLE_TIME_EPSILON := 0.000000001

# Public state (read-only by convention; mutate through reset/configure/step).
var facing := "south"
var phase := 0.0
var action := "idle"
var settle_entry_frame := -1
var settle_elapsed := 0.0
var settle_progress := 0.0
var cycle_distance_logical := DEFAULT_CYCLE_DISTANCE_LOGICAL
var settle_duration := DEFAULT_SETTLE_DURATION

var last_config_error := ""
var last_diagnostics: Dictionary = {}

var _settle_active := false
var _settle_start_unwrapped := 0.0
var _settle_target_unwrapped := 0.0
var _settle_target_frame := -1
var _settle_entry := -1
var _facing_changed := false


func _init(cycle_distance_arg: float = DEFAULT_CYCLE_DISTANCE_LOGICAL, settle_duration_arg: float = DEFAULT_SETTLE_DURATION) -> void:
	if not configure(cycle_distance_arg, settle_duration_arg):
		cycle_distance_logical = DEFAULT_CYCLE_DISTANCE_LOGICAL
		settle_duration = DEFAULT_SETTLE_DURATION
	reset("south")


# Scalar form: configure(cycle_distance, settle_duration). Dictionary form (one argument) accepts
# cycle_distance_logical/cycle_distance/cycle_length_px and settle_duration/settle_hold_seconds.
# Missing dictionary keys keep the current values. Rejection never changes the live configuration.
func configure(cycle_distance_arg: Variant, settle_duration_arg: Variant = null) -> bool:
	var cycle_raw: Variant = cycle_distance_arg
	var duration_raw: Variant = settle_duration_arg
	if typeof(cycle_distance_arg) == TYPE_DICTIONARY:
		if settle_duration_arg != null:
			return _config_fail("dictionary config takes exactly one argument")
		var spec: Dictionary = cycle_distance_arg
		cycle_raw = _spec_value(spec, ["cycle_distance_logical", "cycle_distance", "cycle_length_px"], cycle_distance_logical)
		duration_raw = _spec_value(spec, ["settle_duration", "settle_hold_seconds"], settle_duration)
	elif settle_duration_arg == null:
		duration_raw = settle_duration
	if not _is_finite_number(cycle_raw):
		return _config_fail("cycle distance must be a finite number > 0")
	if not _is_finite_number(duration_raw):
		return _config_fail("settle duration must be a finite number > 0")
	var next_cycle := float(cycle_raw)
	var next_duration := float(duration_raw)
	if next_cycle <= 0.0:
		return _config_fail("cycle distance must be a finite number > 0")
	if next_duration <= 0.0:
		return _config_fail("settle duration must be a finite number > 0")
	if next_duration > MAX_SETTLE_DURATION:
		return _config_fail("settle duration must be <= %.3f s" % MAX_SETTLE_DURATION)
	cycle_distance_logical = next_cycle
	settle_duration = next_duration
	last_config_error = ""
	return true


func set_cycle_distance(value: float) -> bool:
	return configure(value, settle_duration)


func set_settle_duration(value: float) -> bool:
	return configure(cycle_distance_logical, value)


# Clears all gait/settle state to the exact idle contact pose. An unknown facing is a refusal and
# leaves the instance untouched.
func reset(initial_facing: String = "south") -> Dictionary:
	if not DIRECTIONS.has(initial_facing):
		return _refusal("unknown facing: %s" % initial_facing)
	facing = initial_facing
	phase = 0.0
	action = "idle"
	_facing_changed = false
	_clear_settle()
	return _pack("idle", 0, 0.0, -1, 0.0, 0.0, 0.0, 0.0, {})


func snapshot() -> Dictionary:
	return {
		"action": action,
		"frame": _frame_for_phase(phase),
		"phase": _wrap_phase(phase),
		"facing": facing,
		"settle_entry_frame": settle_entry_frame,
		"settle_elapsed": settle_elapsed,
		"settle_progress": settle_progress,
		"cycle_distance_logical": cycle_distance_logical,
		"settle_duration": settle_duration,
	}


# Host-call compatibility: presentation state moves only in step(). These are deliberately no-ops,
# so repeated walk()/idle()/face() calls cannot advance or reset the phase.
func face(_next_facing: String) -> void:
	pass


func walk() -> void:
	pass


func idle() -> void:
	pass


# One gameplay step, called once AFTER movement. Returns a Dictionary because the contract asks for
# action/frame/phase/facing/settle fields plus diagnostics. `previous` is pre-movement, `actual` is
# post-movement/post-collision. Invalid input returns ok=false and mutates nothing.
func step(delta: float, previous: Vector2, actual: Vector2, host_facing: String) -> Dictionary:
	var error := _validate_step(delta, previous, actual, host_facing)
	if not error.is_empty():
		return _refusal(error)

	_facing_changed = host_facing != facing
	if _facing_changed:
		facing = host_facing
		phase = 0.0
		_clear_settle()
		action = "idle"

	var displacement := actual - previous
	var distance := displacement.length()
	if not is_finite(distance) or distance > TELEPORT_DISTANCE_LOGICAL:
		return _teleport_to_idle(distance)

	if distance > MOVE_EPSILON_LOGICAL:
		return _advance_walk(distance)
	return _advance_rest(delta)


func _validate_step(delta: float, previous: Vector2, actual: Vector2, host_facing: String) -> String:
	if not is_finite(delta):
		return "non-finite delta"
	if delta < 0.0:
		return "negative delta: %s" % str(delta)
	if not _finite_vector(previous):
		return "non-finite previous position"
	if not _finite_vector(actual):
		return "non-finite actual position"
	if not DIRECTIONS.has(host_facing):
		return "unknown facing: %s" % host_facing
	return ""


func _advance_walk(distance: float) -> Dictionary:
	var was_settling := _settle_active
	var cancelled_entry := _settle_entry
	var phase_before := phase
	var advance := distance / cycle_distance_logical
	if not is_finite(advance):
		return _teleport_to_idle(distance)
	advance = fposmod(advance, 1.0)
	phase = _wrap_phase(phase + advance)
	if was_settling:
		_clear_settle()
	action = "walk"
	return _pack("walk", _frame_for_phase(phase), phase, -1, 0.0, 0.0, distance, advance, {
		"phase_before": phase_before,
		"settle_cancelled": was_settling,
		"repress_during_settle": was_settling,
		"repress_entry_frame": cancelled_entry,
	})


func _advance_rest(delta: float) -> Dictionary:
	if _settle_active:
		return _advance_settle(delta)
	if action == "walk":
		_settle_active = true
		_settle_entry = _frame_for_phase(phase)
		settle_entry_frame = _settle_entry
		settle_elapsed = 0.0
		settle_progress = 0.0
		_settle_start_unwrapped = phase
		_settle_target_unwrapped = _next_contact_unwrapped(phase)
		_settle_target_frame = _frame_for_phase(fposmod(_settle_target_unwrapped, 1.0))
		action = "settle"
		# The movement tick that discovers the stop shows the entry pose. A long frame that already
		# spans the whole settle may complete it immediately; short frames start the visual settle on
		# the next call, so the entry pose is not skipped.
		if delta >= settle_duration:
			return _advance_settle(delta)
		settle_elapsed = 0.0
		settle_progress = 0.0
		return _pack("settle", _frame_for_phase(phase), phase, _settle_entry, 0.0, 0.0, 0.0, 0.0, {
			"settle_target_phase": _wrap_phase(_settle_target_unwrapped),
			"settle_target_frame": _settle_target_frame,
			"cosmetic_phase_advance": 0.0,
		})
	action = "idle"
	phase = 0.0
	_clear_settle()
	return _pack("idle", 0, 0.0, -1, 0.0, 0.0, 0.0, 0.0, {"idle_timer_advanced": false})


func _advance_settle(delta: float) -> Dictionary:
	var entry := _settle_entry
	var target := _settle_target_unwrapped
	var target_frame := _settle_target_frame
	var remaining := settle_duration - settle_elapsed
	if remaining <= 0.0 or remaining <= SETTLE_TIME_EPSILON or delta >= remaining:
		# Exact bound: one valid huge delta completes here; there is no loop and no overshoot timer.
		action = "idle"
		phase = 0.0
		_clear_settle()
		return _pack("idle", 0, 0.0, entry, settle_duration, 1.0, 0.0, 0.0, {
			"settle_completed": true,
			"settle_target_phase": _wrap_phase(target),
			"settle_target_frame": target_frame,
			"cosmetic_phase_advance": target - _settle_start_unwrapped,
		})
	settle_elapsed += delta
	if settle_elapsed > settle_duration:
		settle_elapsed = settle_duration
	settle_progress = clampf(settle_elapsed / settle_duration, 0.0, 1.0)
	phase = _wrap_phase(_settle_start_unwrapped + (target - _settle_start_unwrapped) * settle_progress)
	action = "settle"
	return _pack("settle", _frame_for_phase(phase), phase, entry, settle_elapsed, settle_progress, 0.0, 0.0, {
		"settle_target_phase": _wrap_phase(target),
		"settle_target_frame": target_frame,
		"cosmetic_phase_advance": (target - _settle_start_unwrapped) * settle_progress,
	})


func _teleport_to_idle(distance: float) -> Dictionary:
	action = "idle"
	phase = 0.0
	_clear_settle()
	return _pack("idle", 0, 0.0, -1, 0.0, 0.0, distance, 0.0, {
		"teleport": true,
		"distance_finite": is_finite(distance),
	})


# First contact strictly ahead in the direction of travel: 0.5 when phase < 0.5, else 1.0 (wrapped
# to 0 by the caller). This is the "NEXT" contact, not the nearest contact behind the actor.
func _next_contact_unwrapped(value: float) -> float:
	var current := _wrap_phase(value)
	if current >= 0.5 - CONTACT_BOUNDARY_EPSILON:
		return 1.0
	return 0.5


func _frame_for_phase(value: float) -> int:
	var wrapped := _wrap_phase(value)
	var index := int(floor(wrapped * float(WALK_FRAMES) + FRAME_BOUNDARY_EPSILON))
	if index < 0:
		return 0
	if index >= WALK_FRAMES:
		return 0
	return index


func _wrap_phase(value: float) -> float:
	if not is_finite(value):
		return 0.0
	var wrapped := fposmod(value, 1.0)
	if wrapped <= 0.0:
		return 0.0
	if wrapped >= 1.0:
		return 0.0
	return wrapped


func _clear_settle() -> void:
	_settle_active = false
	_settle_start_unwrapped = 0.0
	_settle_target_unwrapped = 0.0
	_settle_target_frame = -1
	_settle_entry = -1
	settle_entry_frame = -1
	settle_elapsed = 0.0
	settle_progress = 0.0


func _pack(action_name: String, frame_value: int, phase_value: float, entry_frame: int, elapsed: float, progress: float, distance: float, advance: float, extra: Dictionary = {}) -> Dictionary:
	var safe_phase := _wrap_phase(phase_value)
	var safe_frame := frame_value
	if safe_frame < 0 or safe_frame >= WALK_FRAMES:
		safe_frame = 0
	var diag := {
		"actual_distance": _safe_number(distance),
		"phase_advance": _safe_number(advance),
		"cosmetic_phase_advance": _safe_number(float(extra.get("cosmetic_phase_advance", 0.0))),
		"phase_before": _safe_number(float(extra.get("phase_before", safe_phase))),
		"cycle_distance_logical": cycle_distance_logical,
		"settle_duration": settle_duration,
		"settle_active": _settle_active,
		"settle_completed": bool(extra.get("settle_completed", false)),
		"settle_cancelled": bool(extra.get("settle_cancelled", false)),
		"repress_during_settle": bool(extra.get("repress_during_settle", false)),
		"repress_entry_frame": int(extra.get("repress_entry_frame", -1)),
		"facing_changed": _facing_changed,
		"teleport": bool(extra.get("teleport", false)),
		"distance_finite": bool(extra.get("distance_finite", is_finite(distance))),
		"refused": false,
		"error": "",
		"visual_only": action_name == "settle",
		"world_footlock_claim": false,
		"input_intent_read": false,
		"engine_state_changed": false,
		"idle_timer_advanced": bool(extra.get("idle_timer_advanced", false)),
		"settle_target_phase": _safe_number(float(extra.get("settle_target_phase", -1.0))),
		"settle_target_frame": int(extra.get("settle_target_frame", -1)),
	}
	last_diagnostics = diag.duplicate(true)
	return {
		"ok": true,
		"action": action_name,
		"frame": safe_frame,
		"phase": safe_phase,
		"facing": facing,
		"settle_entry_frame": entry_frame,
		"settle_elapsed": _safe_number(elapsed),
		"settle_progress": clampf(_safe_number(progress), 0.0, 1.0),
		"diagnostics": diag,
	}


# Refusal builds its result without touching any live field or last_diagnostics. The action/frame/
# phase/facing describe the unchanged current pose so a caller can keep rendering it safely.
func _refusal(error: String) -> Dictionary:
	return {
		"ok": false,
		"action": action,
		"frame": _frame_for_phase(phase),
		"phase": _wrap_phase(phase),
		"facing": facing,
		"settle_entry_frame": settle_entry_frame,
		"settle_elapsed": _safe_number(settle_elapsed),
		"settle_progress": clampf(_safe_number(settle_progress), 0.0, 1.0),
		"diagnostics": {
			"actual_distance": 0.0,
			"phase_advance": 0.0,
			"cosmetic_phase_advance": 0.0,
			"phase_before": _wrap_phase(phase),
			"cycle_distance_logical": cycle_distance_logical,
			"settle_duration": settle_duration,
			"settle_active": _settle_active,
			"settle_completed": false,
			"settle_cancelled": false,
			"repress_during_settle": false,
			"repress_entry_frame": -1,
			"facing_changed": false,
			"teleport": false,
			"distance_finite": true,
			"refused": true,
			"error": error,
			"visual_only": action == "settle",
			"world_footlock_claim": false,
			"input_intent_read": false,
			"engine_state_changed": false,
			"idle_timer_advanced": false,
			"settle_target_phase": -1.0,
			"settle_target_frame": -1,
		},
	}


func _config_fail(message: String) -> bool:
	last_config_error = message
	return false


func _spec_value(spec: Dictionary, keys: Array, fallback: Variant) -> Variant:
	for key in keys:
		if spec.has(key):
			return spec[key]
	return fallback


func _is_finite_number(value: Variant) -> bool:
	if typeof(value) == TYPE_INT:
		return true
	if typeof(value) == TYPE_FLOAT:
		return is_finite(float(value))
	return false


func _finite_vector(value: Vector2) -> bool:
	return is_finite(value.x) and is_finite(value.y)


func _safe_number(value: float) -> float:
	if is_finite(value):
		return value
	return 0.0
