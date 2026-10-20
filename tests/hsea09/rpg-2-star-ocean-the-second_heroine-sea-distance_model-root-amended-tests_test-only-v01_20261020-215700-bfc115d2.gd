extends SceneTree

# HSEA09 deterministic HEADLESS numeric tests for the PURE locomotion phase model.
#
# This is a SYNTHETIC fixture. It does not run the game, a scene, a collision body, an input map,
# a renderer or the opt-in driver, and it is NOT gameplay, motion-review or creator-approval
# evidence. It only checks the model's contract at 30/60/mixed simulated dt.
#
# Run under the bounded checked runner; a parser/runtime ERROR/SCRIPT_ERROR fails even on exit 0.
#   HSEA09_TESTS_OK is the expected success marker.

const Model := preload("res://scripts/rpg-2-star-ocean-the-second_hsea09_locomotion-phase_model_v01_20261020-174416-39e12f18.gd")
const DIRECTIONS := ["south", "north", "east", "west"]
const HSEA09_EPS := 0.00001

var checks := 0
var failures: Array[String] = []


func _initialize() -> void:
	call_deferred("_run")


func _ck(condition: bool, message: String, detail: Variant = null) -> void:
	checks += 1
	if condition:
		print("HSEA09_CHECK PASS ", message)
	else:
		var suffix := "" if detail == null else " :: " + str(detail)
		failures.append(message + suffix)
		print("HSEA09_CHECK FAIL ", message, suffix)


func _near(a: float, b: float, epsilon: float = HSEA09_EPS) -> bool:
	return absf(a - b) <= epsilon


func _new(cycle: float = 48.0, settle: float = 0.12):
	var instance = Model.new(cycle, settle)
	return instance


func _walk(m, distance: float, facing: String = "south", delta: float = 0.0, origin: Vector2 = Vector2(137.0, -211.0)) -> Dictionary:
	var actual := origin + Vector2(distance, 0.0)
	return m.step(delta, origin, actual, facing)


func _walk_vec(m, displacement: Vector2, facing: String, delta: float = 0.0, origin: Vector2 = Vector2(-53.0, 89.0)) -> Dictionary:
	return m.step(delta, origin, origin + displacement, facing)


func _sane(r: Dictionary) -> bool:
	if typeof(r) != TYPE_DICTIONARY:
		return false
	if not r.has("action") or not r.has("frame") or not r.has("phase") or not r.has("facing"):
		return false
	if not r.has("settle_entry_frame") or not r.has("settle_elapsed") or not r.has("settle_progress") or not r.has("diagnostics"):
		return false
	if not ["walk", "settle", "idle"].has(String(r["action"])):
		return false
	var frame := int(r["frame"])
	if frame < 0 or frame >= 12:
		return false
	var p := float(r["phase"])
	if not is_finite(p) or p < 0.0 or p >= 1.0:
		return false
	if not DIRECTIONS.has(String(r["facing"])):
		return false
	if not is_finite(float(r["settle_elapsed"])) or float(r["settle_elapsed"]) < 0.0:
		return false
	if not is_finite(float(r["settle_progress"])) or float(r["settle_progress"]) < 0.0 or float(r["settle_progress"]) > 1.0:
		return false
	var d: Dictionary = r["diagnostics"]
	if typeof(d) != TYPE_DICTIONARY:
		return false
	for key in ["actual_distance", "phase_advance", "cosmetic_phase_advance", "phase_before", "cycle_distance_logical", "settle_duration", "settle_target_phase"]:
		if not d.has(key) or not is_finite(float(d[key])):
			return false
	if bool(d.get("world_footlock_claim", true)):
		return false
	return true


func _state_key(m) -> String:
	return "%s|%s|%.12f|%d|%.12f|%.12f|%.12f|%.12f" % [
		String(m.action), String(m.facing), float(m.phase), int(m.settle_entry_frame),
		float(m.settle_elapsed), float(m.settle_progress), float(m.cycle_distance_logical), float(m.settle_duration)]


func _run() -> void:
	_test_defaults_and_config()
	_test_distance_and_frame_rate()
	_test_slow_fast_diagonal()
	_test_blocked_movement()
	_test_stop_every_entry()
	_test_exact_boundaries()
	_test_repress_during_settle()
	_test_facing_change_reset()
	_test_teleport()
	_test_huge_delta()
	_test_invalid_inputs()
	_test_idle_no_drift()
	_test_instances_independent()
	_finish()


func _finish() -> void:
	print("HSEA09_CHECKS total=%d failures=%d" % [checks, failures.size()])
	if failures.is_empty():
		print("HSEA09_TESTS_OK")
		quit(0)
	else:
		for failure in failures:
			print("HSEA09_FAILURE ", failure)
		print("HSEA09_TESTS_FAIL")
		quit(1)


func _test_defaults_and_config() -> void:
	var m = _new()
	_ck(_sane(m.reset()), "default reset result is sane")
	_ck(m.cycle_distance_logical == 48.0, "default cycle distance is 48 logical")
	_ck(m.settle_duration == 0.12, "default settle duration is .12 s")
	_ck(m.action == "idle" and m.phase == 0.0 and m.facing == "south", "default state is south idle contact 0")
	_ck(int(m.snapshot()["frame"]) == 0, "default frame is 0")

	var live = _new()
	_ck(live.configure(32.0, 0.08), "valid scalar config accepted")
	_ck(live.cycle_distance_logical == 32.0 and live.settle_duration == 0.08, "valid scalar config applied")
	var bad_cycles := [0.0, -1.0, NAN, INF, -INF, "48", true, [48.0]]
	for bad in bad_cycles:
		_ck(not live.configure(bad, 0.08), "invalid cycle rejected: %s" % str(bad))
		_ck(live.cycle_distance_logical == 32.0 and live.settle_duration == 0.08, "invalid cycle keeps config: %s" % str(bad))
		_ck(not live.last_config_error.is_empty(), "invalid cycle explains itself: %s" % str(bad))
	var bad_durations := [0.0, -0.001, NAN, INF, -INF, 0.1200001, 0.5, ".12", false]
	for bad in bad_durations:
		_ck(not live.configure(32.0, bad), "invalid settle duration rejected: %s" % str(bad))
		_ck(live.cycle_distance_logical == 32.0 and live.settle_duration == 0.08, "invalid duration keeps config: %s" % str(bad))
	_ck(live.configure(32.0, 0.12), "settle duration exactly .12 accepted")
	_ck(live.configure(32.0, 0.12 - 1e-12), "settle duration just below .12 accepted")
	_ck(live.configure({"cycle_distance_logical": 24.0, "settle_duration": 0.06}), "dictionary config accepted")
	_ck(live.cycle_distance_logical == 24.0 and live.settle_duration == 0.06, "dictionary config applied")
	_ck(not live.configure({"cycle_distance_logical": NAN}), "dictionary NaN cycle rejected")
	_ck(live.cycle_distance_logical == 24.0, "rejected dictionary keeps config")
	_ck(not live.configure(null), "null config argument rejected")
	_ck(live.cycle_distance_logical == 24.0 and live.settle_duration == 0.06, "failed no-arg config keeps config")

	var bad_init = Model.new(NAN, 0.12)
	_ck(bad_init.cycle_distance_logical == 48.0 and bad_init.settle_duration == 0.12, "invalid constructor falls back to defaults")
	var bad_init2 = Model.new(48.0, 0.5)
	_ck(bad_init2.cycle_distance_logical == 48.0 and bad_init2.settle_duration == 0.12, "oversize constructor duration falls back")

	# Reconfigure must change only the cycle, not the live phase or facing.
	live.reset("north")
	var walked = _walk(live, 6.0, "north")
	_ck(live.phase > 0.0, "configured cycle moves phase")
	_ck(live.configure(32.0, 0.06), "reconfigure while live accepted")
	var after = live.step(0.0, Vector2.ZERO, Vector2.ZERO, "north")
	_ck(_near(after["phase"], walked["phase"]), "reconfigure preserves current phase")
	_ck(after["facing"] == "north", "reconfigure preserves facing")


func _test_distance_and_frame_rate() -> void:
	# Same 24-logical path at 30/60/mixed dt, with different partitions.
	var runs := [
		{"dt": 1.0 / 30.0, "step": 0.5, "count": 48},
		{"dt": 1.0 / 60.0, "step": 0.25, "count": 96},
		{"dt": 1.0 / 30.0, "step": 1.0, "count": 24},
	]
	var phases := []
	for run in runs:
		var m = _new()
		var pos := Vector2(10.0, 20.0)
		var total := 0.0
		var last := {}
		for i in int(run["count"]):
			var nxt := pos + Vector2(float(run["step"]), 0.0)
			last = m.step(float(run["dt"]), pos, nxt, "south")
			pos = nxt
			total += float(run["step"])
		_ck(_near(total, 24.0), "30/60 fixture path totals 24 logical (got %.12f)" % total)
		_ck(_sane(last) and String(last["action"]) == "walk", "30/60 fixture remains walking")
		_ck(_near(float(last["phase"]), 0.5), "same path distance reaches phase .5 at %s fps" % str(1.0 / float(run["dt"])), last["phase"])
		_ck(int(last["frame"]) == 6, "phase .5 is frame 6 at %s fps" % str(1.0 / float(run["dt"])), last["frame"])
		phases.append(float(last["phase"]))
	for i in range(1, phases.size()):
		_ck(_near(phases[0], phases[i]), "same path distance phase equal across partitions")
		_ck(int(floor(phases[0] * 12.0 + 1e-9)) == int(floor(phases[i] * 12.0 + 1e-9)), "same path frame equal across partitions")

	# Mixed dt with the same distances must not change phase.
	var mixed = _new()
	var mixed_pos := Vector2.ZERO
	var mixed_last := {}
	var mixed_total := 0.0
	for i in 48:
		var nxt := mixed_pos + Vector2(0.5, 0.0)
		var dt: float = float([1.0 / 30.0, 1.0 / 60.0, 1.0 / 120.0, 1.0 / 45.0][i % 4])
		mixed_last = mixed.step(dt, mixed_pos, nxt, "south")
		mixed_pos = nxt
		mixed_total += 0.5
	_ck(_near(mixed_total, 24.0), "mixed dt path totals 24 logical")
	_ck(_near(float(mixed_last["phase"]), 0.5), "mixed dt same path reaches phase .5", mixed_last["phase"])
	_ck(int(mixed_last["frame"]) == 6, "mixed dt same path reaches frame 6", mixed_last["frame"])

	# One full cycle returns to exact contact 0, not phase 1.0 / frame 12.
	var full = _new()
	var full_r = _walk(full, 48.0)
	_ck(String(full_r["action"]) == "walk", "full-cycle step is still walking")
	_ck(float(full_r["phase"]) == 0.0, "full cycle phase is exactly 0, not 1", full_r["phase"])
	_ck(int(full_r["frame"]) == 0, "full cycle frame is 0, not 12", full_r["frame"])

	# A trapezoid of varying speeds over the same measured distance has the same phase.
	var slow = _new()
	var slow_pos := Vector2.ZERO
	var slow_r := {}
	for i in 24:
		var nxt := slow_pos + Vector2(0.5, 0.0)
		slow_r = slow.step(1.0 / 30.0, slow_pos, nxt, "south")
		slow_pos = nxt
	var fast = _new()
	var fast_r = _walk(fast, 12.0)
	_ck(_near(float(slow_r["phase"]), float(fast_r["phase"])), "slow and fast paths of 12 logical have equal phase")
	_ck(int(slow_r["frame"]) == int(fast_r["frame"]), "slow and fast paths have equal frame")


func _test_slow_fast_diagonal() -> void:
	var straight = _new()
	var straight_r = _walk(straight, 5.0)
	var diagonal = _new()
	var diagonal_r = _walk_vec(diagonal, Vector2(3.0, 4.0), "south")
	_ck(_near(float(diagonal_r["phase"]), 5.0 / 48.0), "diagonal (3,4) uses Euclidean length 5", diagonal_r["phase"])
	_ck(_near(float(diagonal_r["phase"]), float(straight_r["phase"])), "diagonal and straight 5 share phase")
	_ck(absf(float(diagonal_r["phase"]) - 7.0 / 48.0) > 0.03, "diagonal did not use Manhattan length 7")
	var neg_diagonal = _new()
	var neg_r = _walk_vec(neg_diagonal, Vector2(-3.0, -4.0), "south")
	_ck(_near(float(neg_r["phase"]), 5.0 / 48.0), "negative diagonal uses Euclidean length")

	var one = _new()
	var one_r = _walk(one, 12.0)
	var many = _new()
	var many_pos := Vector2(100.0, 100.0)
	var many_r := {}
	for i in 24:
		var nxt := many_pos + Vector2(0.5, 0.0)
		many_r = many.step(1.0 / 60.0, many_pos, nxt, "east")
		many_pos = nxt
	_ck(_near(float(one_r["phase"]), 0.25), "fast 12-logical step is phase .25", one_r["phase"])
	_ck(_near(float(many_r["phase"]), 0.25), "slow 24 x .5 logical is phase .25", many_r["phase"])
	_ck(_near(float(one_r["phase"]), float(many_r["phase"])), "slow and fast normalized actual distance match")

	# Position origin is irrelevant; displacement alone drives phase.
	var a = _new()
	var b = _new()
	var ra = a.step(1.0 / 60.0, Vector2(0.0, 0.0), Vector2(3.0, 4.0), "south")
	var rb = b.step(1.0 / 60.0, Vector2(-9999.0, 1234.0), Vector2(-9996.0, 1238.0), "south")
	_ck(_near(float(ra["phase"]), float(rb["phase"])), "position origin does not affect phase")
	_ck(_near(float(ra["phase"]), 5.0 / 48.0), "offset path uses actual displacement length")


func _test_blocked_movement() -> void:
	var idle = _new()
	var idle_r = idle.step(1.0 / 60.0, Vector2(4.0, 4.0), Vector2(4.0, 4.0), "south")
	_ck(String(idle_r["action"]) == "idle", "zero actual displacement from idle is idle")
	_ck(float(idle_r["phase"]) == 0.0, "zero actual displacement does not advance phase")
	_ck(float(idle_r["diagnostics"]["actual_distance"]) == 0.0, "zero actual distance is reported")
	_ck(float(idle_r["diagnostics"]["phase_advance"]) == 0.0, "zero actual distance has zero phase advance")

	var m = _new()
	var walked = _walk(m, 12.0)
	var before := float(walked["phase"])
	var stopped = m.step(1.0 / 60.0, Vector2(2.0, 2.0), Vector2(2.0, 2.0), "south")
	_ck(String(stopped["action"]) == "settle", "zero actual displacement after walk enters settle")
	_ck(_near(float(stopped["phase"]), before + (0.5-before) * ((1.0/60.0)/0.12)), "first stop tick advances only cosmetic settle within120ms bound", [before, stopped["phase"]])
	_ck(float(stopped["diagnostics"]["actual_distance"]) == 0.0, "stop tick actual distance is zero")
	_ck(float(stopped["diagnostics"]["phase_advance"]) == 0.0, "stop tick walk phase advance is zero")
	_ck(bool(stopped["diagnostics"]["visual_only"]), "settle is marked visual only")

	# Tiny collision jitter inside epsilon is not movement and must not add walk phase.
	var jitter = _new()
	_walk(jitter, 12.0)
	var jitter_before := float(jitter.phase)
	for i in 10:
		var pos := Vector2(5.0, 5.0)
		var r = jitter.step(1.0 / 60.0, pos, pos + Vector2(0.00001, 0.0), "south")
		_ck(float(r["diagnostics"]["phase_advance"]) == 0.0, "sub-epsilon jitter adds no walk phase (%d)" % i)
	_ck(_near(float(jitter.phase), jitter_before) or jitter.action == "settle" or jitter.action == "idle", "jitter never turns into walk")
	_ck(String(jitter.action) != "walk", "blocked actor does not claim walking")


func _test_stop_every_entry() -> void:
	for i in 24:
		var entry := float(i) / 24.0
		var m = _new()
		var distance := 48.0 if i == 0 else entry * 48.0
		var walk_r = _walk(m, distance)
		_ck(String(walk_r["action"]) == "walk", "entry %.4f is walking before stop" % entry)
		_ck(_near(float(walk_r["phase"]), entry), "entry %.4f reached exactly" % entry, walk_r["phase"])
		var entry_frame := int(walk_r["frame"])
		var stop_r = m.step(0.0, Vector2(7.0, 7.0), Vector2(7.0, 7.0), "south")
		_ck(_sane(stop_r), "entry %.4f stop result sane" % entry)
		_ck(String(stop_r["action"]) == "settle", "entry %.4f stop enters settle" % entry)
		_ck(_near(float(stop_r["phase"]), entry), "entry %.4f stop starts at entry phase" % entry)
		_ck(int(stop_r["settle_entry_frame"]) == entry_frame, "entry %.4f retains entry frame" % entry)
		_ck(int(stop_r["frame"]) == entry_frame, "entry %.4f stop frame is entry frame" % entry)
		_ck(float(stop_r["settle_progress"]) == 0.0, "entry %.4f settle progress starts 0" % entry)
		var expected_target := 0.5 if entry < 0.5 - 0.000000001 else 0.0
		_ck(_near(float(stop_r["diagnostics"]["settle_target_phase"]), expected_target), "entry %.4f targets the next contact" % entry, stop_r["diagnostics"].get("settle_target_phase"))
		var expected_target_frame := 6 if expected_target == 0.5 else 0
		_ck(int(stop_r["diagnostics"]["settle_target_frame"]) == expected_target_frame, "entry %.4f target frame is %d" % [entry, expected_target_frame])

		var total := 0.0
		var r: Dictionary = stop_r
		var guard := 0
		while String(r["action"]) == "settle" and guard < 40:
			r = m.step(0.01, Vector2(7.0, 7.0), Vector2(7.0, 7.0), "south")
			total += 0.01
			guard += 1
			_ck(_sane(r), "entry %.4f settle frame sane" % entry)
			_ck(float(r["phase"]) < 1.0, "entry %.4f settle phase stays normalized" % entry)
			_ck(float(r["settle_elapsed"]) <= 0.12 + HSEA09_EPS, "entry %.4f settle elapsed bounded" % entry)
			if String(r["action"]) == "settle":
				_ck(bool(r["diagnostics"]["visual_only"]), "entry %.4f cosmetic settle marked visual only" % entry)
				_ck(float(r["diagnostics"]["actual_distance"]) == 0.0, "entry %.4f settle invents no actual distance" % entry)
		_ck(guard < 40, "entry %.4f settle terminates" % entry)
		_ck(String(r["action"]) == "idle", "entry %.4f settles to idle" % entry)
		_ck(int(r["frame"]) == 0 and float(r["phase"]) == 0.0, "entry %.4f final idle is exact frame 0/phase 0" % entry)
		_ck(int(r["settle_entry_frame"]) == entry_frame, "entry %.4f completion retains entry frame" % entry)
		_ck(_near(float(r["settle_elapsed"]), 0.12), "entry %.4f settle elapsed completes at .12" % entry, r["settle_elapsed"])
		_ck(float(r["settle_progress"]) == 1.0, "entry %.4f settle progress completes at 1" % entry)
		_ck(total <= 0.12 + 0.01 + HSEA09_EPS, "entry %.4f settle wall total <= 120 ms + one host tick" % entry, total)
		_ck(float(m.settle_elapsed) == 0.0 and int(m.settle_entry_frame) == -1, "entry %.4f idle state owns no settle clock" % entry)


func _test_exact_boundaries() -> void:
	var m = _new()
	var boundary_ok := true
	var detail := ""
	for i in 12:
		var p := float(i) / 12.0
		var inst = _new()
		var distance := 48.0 if i == 0 else p * 48.0
		var r = _walk(inst, distance)
		var want_frame := i
		if int(r["frame"]) != want_frame:
			boundary_ok = false
			detail += "phase %.6f got %d want %d; " % [p, int(r["frame"]), want_frame]
	_ck(boundary_ok, "exact 1/12 phase boundaries map to frames 0..11", detail)

	var below = _new()
	var below_r = _walk(below, 47.999)
	_ck(int(below_r["frame"]) == 11, "just below a full cycle is frame 11", below_r["frame"])
	var above = _new()
	var above_r = _walk(above, 48.001)
	_ck(int(above_r["frame"]) == 0, "just above a full cycle wraps to frame 0", above_r["frame"])
	_ck(float(above_r["phase"]) < 1.0, "wrapped phase stays below 1")

	var mid = _new()
	var mid_r = _walk(mid, 24.0)
	_ck(float(mid_r["phase"]) == 0.5 and int(mid_r["frame"]) == 6, "exact half cycle is phase .5/frame 6", [mid_r["phase"], mid_r["frame"]])
	var three_q = _new()
	var three_q_r = _walk(three_q, 36.0)
	_ck(_near(float(three_q_r["phase"]), 0.75) and int(three_q_r["frame"]) == 9, "three-quarter cycle is phase .75/frame 9", [three_q_r["phase"], three_q_r["frame"]])

	var samples = _new()
	var sample_ok := true
	for i in 1200:
		var p := float(i) / 1200.0
		var inst = _new()
		var distance := 48.0 if i == 0 else p * 48.0
		var r = _walk(inst, distance)
		var frame := int(r["frame"])
		if frame < 0 or frame > 11:
			sample_ok = false
		var want := int(floor(p * 12.0 + 1e-9))
		if want >= 12:
			want = 0
		if frame != want:
			sample_ok = false
	_ck(sample_ok, "1200 phase samples never produce frame 12")

	# Repeated small steps must not accumulate a frame-12 or phase >= 1.
	var long = _new()
	var pos := Vector2.ZERO
	var long_ok := true
	for i in 5000:
		var nxt := pos + Vector2(0.5, 0.0)
		var r = long.step(1.0 / 60.0, pos, nxt, "south")
		pos = nxt
		if float(r["phase"]) < 0.0 or float(r["phase"]) >= 1.0 or int(r["frame"]) >= 12:
			long_ok = false
	_ck(long_ok, "5000 small steps keep phase normalized and frame < 12")
	var expected := fposmod(2500.0 / 48.0, 1.0)
	_ck(_near(float(long.phase), expected, 0.00001), "long walk phase tracks closed form", [long.phase, expected])


func _test_repress_during_settle() -> void:
	var m = _new()
	var walked = _walk(m, 14.4)
	_ck(_near(float(walked["phase"]), 0.3), "repress fixture reaches phase .3")
	var stopped = m.step(0.05, Vector2.ZERO, Vector2.ZERO, "south")
	_ck(String(stopped["action"]) == "settle", "repress fixture is settling")
	_ck(_near(float(stopped["phase"]), 0.3 + 0.2 * (0.05 / 0.12)), "first stopped tick consumes its elapsed time within120ms bound")
	var mid = m.step(0.05, Vector2.ZERO, Vector2.ZERO, "south")
	_ck(String(mid["action"]) == "settle", "repress fixture advances into settle")
	var settle_phase := float(mid["phase"])
	_ck(settle_phase > 0.3 and settle_phase < 0.5, "settle phase is between entry and target")
	var entry_frame := int(stopped["settle_entry_frame"])
	var resumed = m.step(0.0, Vector2.ZERO, Vector2(2.4, 0.0), "south")
	_ck(String(resumed["action"]) == "walk", "same-facing re-press during settle resumes walking")
	_ck(bool(resumed["diagnostics"]["repress_during_settle"]), "repress is diagnosed")
	_ck(bool(resumed["diagnostics"]["settle_cancelled"]), "repress cancels settle")
	_ck(int(resumed["diagnostics"]["repress_entry_frame"]) == entry_frame, "repress keeps settle entry frame for bridge choice")
	_ck(_near(float(resumed["phase"]), settle_phase + 0.05), "repress continues from current settle pose, not reset", [settle_phase, resumed["phase"]])
	_ck(float(resumed["phase"]) > settle_phase, "repress phase does not fall back")
	_ck(not _near(float(resumed["phase"]), 0.05), "repress did not reset to contact 0")
	_ck(int(resumed["settle_entry_frame"]) == -1, "active settle fields clear on repress")

	# Repress near the end of settle, including a target-0.5-to-0 path, must not double-rise.
	var n = _new()
	_walk(n, 33.6)
	n.step(0.0, Vector2.ZERO, Vector2.ZERO, "south")
	var stop_n = n.step(0.108, Vector2.ZERO, Vector2.ZERO, "south")
	_ck(String(stop_n["action"]) == "settle", "late repress fixture settling")
	var late_phase := float(stop_n["phase"])
	var late_resume = n.step(0.0, Vector2.ZERO, Vector2(1.2, 0.0), "south")
	_ck(_near(float(late_resume["phase"]), late_phase + 0.025), "late repress adds exactly one actual phase advance", [late_phase, late_resume["phase"]])

	# Repress after idle starts a new walk from contact 0 (no stale settle phase).
	var idle = _new()
	_walk(idle, 12.0)
	idle.step(1.0, Vector2.ZERO, Vector2.ZERO, "south")
	_ck(String(idle.action) == "idle", "long stop completed to idle")
	var fresh = idle.step(0.0, Vector2.ZERO, Vector2(2.4, 0.0), "south")
	_ck(_near(float(fresh["phase"]), 0.05), "walk after idle starts from contact 0", fresh["phase"])


func _test_facing_change_reset() -> void:
	var east = _new()
	_walk(east, 12.0, "east")
	_ck(_near(float(east.phase), 0.25), "facing fixture reaches .25 east")
	var south = east.step(0.0, Vector2.ZERO, Vector2.ZERO, "south")
	_ck(String(south["facing"]) == "south", "90-degree change switches facing")
	_ck(float(south["phase"]) == 0.0, "90-degree change resets incoming phase to contact 0")
	_ck(String(south["action"]) == "idle", "90-degree change with no movement is idle")
	_ck(int(south["frame"]) == 0, "90-degree change frame is contact 0")

	var east2 = _new()
	_walk(east2, 12.0, "east")
	var west = east2.step(0.0, Vector2.ZERO, Vector2(4.8, 0.0), "west")
	_ck(String(west["facing"]) == "west", "reversal switches facing")
	_ck(_near(float(west["phase"]), 0.1), "reversal resets then adds only this step's distance", west["phase"])
	_ck(not _near(float(west["phase"]), 0.35), "reversal does not carry incoming phase")

	var same = _new()
	_walk(same, 9.6)
	var same2 = same.step(0.0, Vector2.ZERO, Vector2(4.8, 0.0), "south")
	_ck(_near(float(same2["phase"]), 0.3), "same-facing step keeps accumulated phase", same2["phase"])

	var settle_turn = _new()
	_walk(settle_turn, 14.4)
	settle_turn.step(0.05, Vector2.ZERO, Vector2.ZERO, "south")
	var turned = settle_turn.step(0.0, Vector2.ZERO, Vector2.ZERO, "north")
	_ck(String(turned["action"]) == "idle" and float(turned["phase"]) == 0.0, "turn during settle cancels to contact 0")
	_ck(String(turned["facing"]) == "north", "turn during settle adopts new facing")
	_ck(int(turned["settle_entry_frame"]) == -1, "turn during settle clears entry frame")

	# Repeated same-facing calls are not a turn and must not reset.
	var repeat = _new()
	_walk(repeat, 4.8)
	for i in 5:
		repeat.step(0.0, Vector2.ZERO, Vector2.ZERO, "south")
	_ck(String(repeat.facing) == "south", "same-facing calls keep facing")


func _test_teleport() -> void:
	var m = _new()
	_walk(m, 12.0)
	var tele = m.step(1.0 / 60.0, Vector2.ZERO, Vector2(65.0, 0.0), "south")
	_ck(_sane(tele), "teleport result sane")
	_ck(String(tele["action"]) == "idle" and float(tele["phase"]) == 0.0 and int(tele["frame"]) == 0, "distance > 64 resets safely to idle contact 0")
	_ck(bool(tele["diagnostics"]["teleport"]), "teleport diagnosed")
	_ck(float(tele["diagnostics"]["phase_advance"]) == 0.0, "teleport does not advance a giant phase")

	var exact = _new()
	var exact_r = exact.step(0.0, Vector2.ZERO, Vector2(64.0, 0.0), "south")
	_ck(not bool(exact_r["diagnostics"]["teleport"]), "exactly 64 logical is not a teleport")
	_ck(String(exact_r["action"]) == "walk" and _near(float(exact_r["phase"]), fposmod(64.0 / 48.0, 1.0)), "exactly 64 advances a bounded phase", exact_r["phase"])

	var negative = _new()
	var neg_r = negative.step(0.0, Vector2.ZERO, Vector2(-65.0, 0.0), "south")
	_ck(String(neg_r["action"]) == "idle" and bool(neg_r["diagnostics"]["teleport"]), "negative teleport resets safely")

	var diagonal = _new()
	var diag_r = diagonal.step(0.0, Vector2.ZERO, Vector2(1000.0, 1000.0), "south")
	_ck(String(diag_r["action"]) == "idle" and bool(diag_r["diagnostics"]["teleport"]), "huge diagonal teleport resets safely")

	var during = _new()
	_walk(during, 14.4)
	during.step(0.05, Vector2.ZERO, Vector2.ZERO, "south")
	var during_r = during.step(0.05, Vector2.ZERO, Vector2(1000.0, 0.0), "south")
	_ck(String(during_r["action"]) == "idle" and float(during_r["phase"]) == 0.0, "teleport during settle clears to idle")
	_ck(String(during.action) == "idle" and int(during.settle_entry_frame) == -1, "teleport clears live settle fields")

	var turn_tele = _new()
	var tt = turn_tele.step(0.0, Vector2.ZERO, Vector2(1000.0, 0.0), "east")
	_ck(String(tt["facing"]) == "east" and String(tt["action"]) == "idle", "teleport respects the new facing while resetting")


func _test_huge_delta() -> void:
	var m = _new()
	_walk(m, 17.76)
	var huge = m.step(5.0, Vector2.ZERO, Vector2.ZERO, "south")
	_ck(_sane(huge), "huge delta result sane")
	_ck(String(huge["action"]) == "idle", "huge delta settles to idle in one call")
	_ck(float(huge["phase"]) == 0.0 and int(huge["frame"]) == 0, "huge delta final pose is exact idle frame 0")
	_ck(_near(float(huge["settle_elapsed"]), 0.12), "huge delta settle elapsed clamped to .12", huge["settle_elapsed"])
	_ck(float(huge["settle_progress"]) == 1.0, "huge delta settle progress clamped to 1")
	_ck(float(m.settle_elapsed) == 0.0, "huge delta leaves no drifting timer")

	var enormous = _new()
	_walk(enormous, 9.6)
	var enormous_r = enormous.step(1000000.0, Vector2.ZERO, Vector2.ZERO, "south")
	_ck(String(enormous_r["action"]) == "idle" and float(enormous_r["settle_elapsed"]) <= 0.12, "enormous delta cannot loop or overrun")

	var exact = _new()
	_walk(exact, 9.6)
	var exact_r = exact.step(0.12, Vector2.ZERO, Vector2.ZERO, "south")
	_ck(String(exact_r["action"]) == "idle" and _near(float(exact_r["settle_elapsed"]), 0.12), "delta exactly .12 completes at the bound", exact_r["settle_elapsed"])

	var under = _new()
	_walk(under, 9.6)
	under.step(0.0, Vector2.ZERO, Vector2.ZERO, "south")
	var under_r = under.step(0.12 - 1e-9, Vector2.ZERO, Vector2.ZERO, "south")
	_ck(String(under_r["action"]) == "settle", "delta just under .12 still settles")
	_ck(float(under_r["settle_elapsed"]) < 0.12, "under-bound settle elapsed is below .12", under_r["settle_elapsed"])
	var finish = under.step(0.00000001, Vector2.ZERO, Vector2.ZERO, "south")
	_ck(String(finish["action"]) == "idle" and _near(float(finish["settle_elapsed"]), 0.12), "tiny remainder completes at exactly .12")

	var over = _new()
	_walk(over, 9.6)
	var over_r = over.step(0.1200000001, Vector2.ZERO, Vector2.ZERO, "south")
	_ck(String(over_r["action"]) == "idle", "delta just over .12 completes")

	var custom = _new(48.0, 0.05)
	_walk(custom, 9.6)
	var custom_r = custom.step(10.0, Vector2.ZERO, Vector2.ZERO, "south")
	_ck(String(custom_r["action"]) == "idle" and _near(float(custom_r["settle_elapsed"]), 0.05), "custom settle bound used for huge delta", custom_r["settle_elapsed"])


func _test_invalid_inputs() -> void:
	var m = _new()
	_walk(m, 9.6)
	var before := _state_key(m)
	var cases := [
		{"label": "NaN delta", "delta": NAN, "previous": Vector2.ZERO, "actual": Vector2(1.0, 0.0), "facing": "south"},
		{"label": "+Infinity delta", "delta": INF, "previous": Vector2.ZERO, "actual": Vector2(1.0, 0.0), "facing": "south"},
		{"label": "-Infinity delta", "delta": -INF, "previous": Vector2.ZERO, "actual": Vector2(1.0, 0.0), "facing": "south"},
		{"label": "negative delta", "delta": -0.001, "previous": Vector2.ZERO, "actual": Vector2(1.0, 0.0), "facing": "south"},
		{"label": "NaN previous x", "delta": 0.016, "previous": Vector2(NAN, 0.0), "actual": Vector2(1.0, 0.0), "facing": "south"},
		{"label": "Infinity previous y", "delta": 0.016, "previous": Vector2(0.0, INF), "actual": Vector2(1.0, 0.0), "facing": "south"},
		{"label": "NaN actual x", "delta": 0.016, "previous": Vector2.ZERO, "actual": Vector2(NAN, 0.0), "facing": "south"},
		{"label": "Infinity actual y", "delta": 0.016, "previous": Vector2.ZERO, "actual": Vector2(0.0, -INF), "facing": "south"},
		{"label": "unknown facing", "delta": 0.016, "previous": Vector2.ZERO, "actual": Vector2(1.0, 0.0), "facing": "up"},
		{"label": "empty facing", "delta": 0.016, "previous": Vector2.ZERO, "actual": Vector2(1.0, 0.0), "facing": ""},
		{"label": "capitalized facing", "delta": 0.016, "previous": Vector2.ZERO, "actual": Vector2(1.0, 0.0), "facing": "South"},
		{"label": "trailing-space facing", "delta": 0.016, "previous": Vector2.ZERO, "actual": Vector2(1.0, 0.0), "facing": "south "},
	]
	for c in cases:
		var r = m.step(float(c["delta"]), c["previous"], c["actual"], String(c["facing"]))
		_ck(not bool(r["ok"]), "invalid %s refuses" % String(c["label"]))
		_ck(bool(r["diagnostics"]["refused"]), "invalid %s is marked refused" % String(c["label"]))
		_ck(not String(r["diagnostics"]["error"]).is_empty(), "invalid %s explains itself" % String(c["label"]))
		_ck(_sane(r), "invalid %s returns a safe pose" % String(c["label"]))
		_ck(_state_key(m) == before, "invalid %s does not mutate state" % String(c["label"]))

	var still = m.step(0.0, Vector2.ZERO, Vector2(0.5, 0.0), "south")
	_ck(String(still["action"]) == "walk", "model remains usable after refusals")
	_ck(_near(float(still["phase"]), 9.6 / 48.0 + 0.5 / 48.0), "valid step after refusals advances normally", still["phase"])

	var reset_before := _state_key(m)
	var bad_reset = m.reset("sideways")
	_ck(not bool(bad_reset["ok"]) and bool(bad_reset["diagnostics"]["refused"]), "unknown reset facing refuses")
	_ck(_state_key(m) == reset_before, "unknown reset facing does not mutate state")

	# NaN velocity/speed-style vectors are just non-finite positions, not a teleport.
	var nan_move = m.step(0.016, Vector2(-INF, 0.0), Vector2(INF, 0.0), "south")
	_ck(not bool(nan_move["ok"]) and _state_key(m) == reset_before, "non-finite movement refuses without teleport mutation")


func _test_idle_no_drift() -> void:
	var m = _new()
	var ok := true
	for i in 1000:
		var r = m.step(0.016, Vector2(3.0, 3.0), Vector2(3.0, 3.0), "south")
		if String(r["action"]) != "idle" or int(r["frame"]) != 0 or float(r["phase"]) != 0.0:
			ok = false
		if float(r["settle_elapsed"]) != 0.0 or float(r["settle_progress"]) != 0.0:
			ok = false
	_ck(ok, "1000 idle steps never drift timer, frame or phase")

	var settled = _new()
	_walk(settled, 14.4)
	settled.step(1.0, Vector2.ZERO, Vector2.ZERO, "south")
	_ck(String(settled.action) == "idle", "settled fixture is idle")
	var ok2 := true
	for i in 1000:
		var r = settled.step(0.5, Vector2(1.0, 1.0), Vector2(1.0, 1.0), "south")
		if String(r["action"]) != "idle" or int(r["frame"]) != 0 or float(r["phase"]) != 0.0:
			ok2 = false
		if float(r["settle_elapsed"]) != 0.0 or float(r["settle_progress"]) != 0.0:
			ok2 = false
	_ck(ok2, "post-settle idle never restarts or drifts the settle timer")

	var noop = _new()
	_walk(noop, 9.6)
	var before_noop := _state_key(noop)
	for i in 25:
		noop.walk()
		noop.idle()
		noop.face("west")
	_ck(_state_key(noop) == before_noop, "repeated walk/idle/face callbacks do not advance state")


func _test_instances_independent() -> void:
	var a = _new(48.0, 0.12)
	var b = _new(24.0, 0.06)
	_walk(a, 14.4)
	_walk(b, 16.8)
	_ck(_near(float(a.phase), 0.3), "instance A reaches its phase")
	_ck(_near(float(b.phase), 0.7), "instance B reaches its phase")
	var b_phase := float(b.phase)
	a.step(0.05, Vector2.ZERO, Vector2.ZERO, "south")
	_ck(_near(float(b.phase), b_phase) and String(b.action) == "walk", "A settling does not move B")
	a.reset()
	_ck(_near(float(b.phase), b_phase), "A reset does not move B")
	var a_walk = _walk(a, 4.8)
	var b_before := _state_key(b)
	var b_step = b.step(0.0, Vector2.ZERO, Vector2(1.2, 0.0), "south")
	_ck(_near(float(b_step["phase"]), 0.7 + 0.05), "B still advances on its own cycle", b_step["phase"])
	_ck(_near(float(a_walk["phase"]), 0.1), "A advances on its own cycle", a_walk["phase"])
	_ck(_state_key(a) != b_before, "instances keep separate state keys")

	a.configure(32.0, 0.08)
	_ck(_near(float(a.cycle_distance_logical), 32.0), "A config changes independently")
	_ck(_near(float(b.cycle_distance_logical), 24.0), "A config does not change B")
	var a_phase_before := float(a.phase)
	var a_configured = _walk(a, 8.0)
	_ck(_near(float(a_configured["phase"]), a_phase_before + 0.25), "A advances on its new cycle")
	_ck(_near(float(b.phase), 0.7 + 0.05), "B phase stays independent after A reconfigure")
