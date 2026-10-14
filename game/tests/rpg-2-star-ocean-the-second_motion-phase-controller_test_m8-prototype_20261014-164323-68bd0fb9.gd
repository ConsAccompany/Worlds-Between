extends SceneTree

# Headless test for the distance-driven motion-phase controller prototype.
# Run: Godot_v4.7.2-stable_win64_console.exe --headless --path game --script res://tests/<this file>

const Controller := preload("res://scripts/rpg-2-star-ocean-the-second_motion-phase-controller_m8-prototype_20261014-164323-a882463a.gd")

# Deliberately different shapes: today's 4-phase cycle, the proposed 8-frame pilot, and a 6-frame variant.
const SPECS := {
	"four_phase_runtime": {
		"walk_frame_count": 4, "cycle_length_px": 67.2, "contact_frames": [0, 2],
		"settle_hold_seconds": 0.12, "idle_frame_count": 1, "idle_hold_seconds": 0.3,
		"facing_hysteresis_ratio": 1.2,
	},
	"eight_frame_pilot": {
		"walk_frame_count": 8, "cycle_length_px": 40.0, "contact_frames": [0, 4],
		"settle_hold_seconds": 0.1, "idle_frame_count": 3, "idle_hold_seconds": 0.25,
		"facing_hysteresis_ratio": 1.2,
	},
	"six_frame_variant": {
		"walk_frame_count": 6, "cycle_length_px": 45.0, "contact_frames": [1, 4],
		"settle_hold_seconds": 0.2, "idle_frame_count": 2, "idle_hold_seconds": 0.25,
		"facing_hysteresis_ratio": 1.35,
	},
}

var failures: Array[String] = []
var checks := 0


func _initialize() -> void:
	_test_config_validation()
	_test_distance_drives_phase()
	_test_frame_rate_and_speed_independence()
	_test_blocked_movement_does_not_animate()
	_test_phase_survives_direction_change()
	_test_stop_settles_on_contact_frame()
	_test_settle_hold_is_frame_rate_independent()
	_test_zero_settle_hold_goes_straight_to_idle()
	_test_facing_hysteresis()
	_test_long_walk_has_no_drift()
	print("motion-phase-controller: %d checks, %d failures" % [checks, failures.size()])
	for failure in failures:
		printerr("FAIL: " + failure)
	print("RESULT: " + ("PASS" if failures.is_empty() else "FAIL"))
	quit(0 if failures.is_empty() else 1)


func _expect(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures.append(message)


func _make(spec_name: String, initial_facing: String = "south"):
	var controller = Controller.new()
	var ok: bool = controller.configure(SPECS[spec_name], initial_facing)
	_expect(ok, "%s configures (%s)" % [spec_name, controller.last_error])
	return controller


func _test_config_validation() -> void:
	for key in Controller.REQUIRED_KEYS:
		var spec: Dictionary = SPECS["eight_frame_pilot"].duplicate(true)
		spec.erase(key)
		var controller = Controller.new()
		_expect(not controller.configure(spec), "missing %s must fail, not default" % key)
		_expect(controller.last_error.contains(key), "error names missing %s" % key)
	var bad_cases := {
		"contact out of range": {"contact_frames": [0, 8]},
		"no contacts": {"contact_frames": []},
		"single frame": {"walk_frame_count": 1},
		"fractional frame count": {"walk_frame_count": 8.5},
		"zero cycle": {"cycle_length_px": 0.0},
		"ratio below one": {"facing_hysteresis_ratio": 0.9},
		"nan ratio": {"facing_hysteresis_ratio": NAN},
		"nan cycle": {"cycle_length_px": NAN},
		"infinite cycle": {"cycle_length_px": INF},
		"string cycle": {"cycle_length_px": "40"},
		"array cycle": {"cycle_length_px": [40.0]},
		"nan settle hold": {"settle_hold_seconds": NAN},
		"infinite settle hold": {"settle_hold_seconds": INF},
		"bool frame count": {"walk_frame_count": true},
		"contacts not an array": {"contact_frames": 3},
		"contacts as string": {"contact_frames": "04"},
	}
	for label in bad_cases:
		var spec: Dictionary = SPECS["eight_frame_pilot"].duplicate(true)
		spec.merge(bad_cases[label], true)
		var controller = Controller.new()
		_expect(not controller.configure(spec), "invalid config rejected: %s" % label)
		_expect(not controller.last_error.is_empty(), "rejection explains itself: %s" % label)
	# Each hold names its own key; zero settle is a valid "no hold", zero idle hold is not.
	var hold_cases := {
		"settle_hold_seconds": [-0.01, 0.0],
		"idle_hold_seconds": [0.0, 0.25],
	}
	for key in hold_cases:
		var spec: Dictionary = SPECS["eight_frame_pilot"].duplicate(true)
		spec[key] = hold_cases[key][0]
		var controller = Controller.new()
		_expect(not controller.configure(spec), "%s = %s rejected" % [key, str(spec[key])])
		_expect(controller.last_error.contains(key), "hold error names %s (%s)" % [key, controller.last_error])
		spec[key] = hold_cases[key][1]
		_expect(Controller.new().configure(spec), "%s = %s accepted" % [key, str(spec[key])])
	# A rejected reconfigure must leave the working configuration untouched.
	var live = _make("eight_frame_pilot")
	var broken: Dictionary = SPECS["six_frame_variant"].duplicate(true)
	broken["cycle_length_px"] = NAN
	_expect(not live.configure(broken) and live.walk_frame_count == 8 and live.cycle_length_px == 40.0, "failed reconfigure keeps the previous config")


func _test_distance_drives_phase() -> void:
	for spec_name in SPECS:
		var spec: Dictionary = SPECS[spec_name]
		var n: int = spec["walk_frame_count"]
		var cycle: float = spec["cycle_length_px"]
		var controller = _make(spec_name)
		var start: int = controller.contact_frames[0]
		var step := cycle / n
		var seen := {}
		var travelled := 0.0
		# Walk two full cycles in 1/7-frame increments; the frame must follow distance exactly.
		while travelled < cycle * 2.0 - 0.001:
			controller.tick(1.0 / 60.0, step / 7.0, Vector2.RIGHT)
			travelled += step / 7.0
			var expected := int(floor((start * step + travelled + 0.0001) / step)) % n
			if controller.display_frame() != expected:
				_expect(false, "%s frame at %.3f px: got %d want %d" % [spec_name, travelled, controller.display_frame(), expected])
				break
			seen[controller.display_frame()] = true
		_expect(seen.size() == n, "%s visits all %d declared frames (saw %d)" % [spec_name, n, seen.size()])
		_expect(controller.mode == Controller.MODE_WALK, "%s is in walk mode while moving" % spec_name)


# The C5 defect: clock-driven phase ties stride length to speed. Distance-driven phase must give
# the same frame at the same distance for any frame rate or speed.
func _test_frame_rate_and_speed_independence() -> void:
	var combos := [[30.0, 140.0], [60.0, 140.0], [144.0, 140.0], [60.0, 90.0], [37.0, 80.0]]
	var step := 40.0 / 8.0
	for combo in combos:
		var fps: float = combo[0]
		var speed: float = combo[1]
		var controller = _make("eight_frame_pilot")
		var travelled := 0.0
		var mismatches := 0
		var wraps := 0
		var previous: int = controller.display_frame()
		while travelled < 200.0:
			controller.tick(1.0 / fps, speed / fps, Vector2.DOWN)
			travelled += speed / fps
			var frame: int = controller.display_frame()
			if frame != int(floor((travelled + 0.0001) / step)) % 8:
				mismatches += 1
			if frame < previous:
				wraps += 1
			previous = frame
		print("fps %3.0f speed %3.0f: %d cycles over %.1f px -> 40.0 px/cycle (clock-driven 4 x 0.12 s would be %.1f px/cycle)" % [fps, speed, wraps, travelled, 0.48 * speed])
		_expect(mismatches == 0, "fps %.0f speed %.0f: %d ticks off the distance-derived frame" % [fps, speed, mismatches])
		_expect(wraps == int(floor(travelled / 40.0)), "fps %.0f speed %.0f: one cycle per 40 px (%d wraps over %.1f px)" % [fps, speed, wraps, travelled])


func _test_blocked_movement_does_not_animate() -> void:
	var controller = _make("eight_frame_pilot", "east")
	controller.tick(1.0 / 60.0, 12.0, Vector2.RIGHT)
	var before: int = controller.walk_frame()
	var distance_before: float = controller.cycle_distance
	for i in 30:
		controller.tick(1.0 / 60.0, 0.0, Vector2.RIGHT)
	_expect(controller.cycle_distance == distance_before and controller.mode != Controller.MODE_WALK, "pushing into a wall does not advance the cycle")
	_expect(controller.mode == Controller.MODE_IDLE, "blocked actor settles into idle after the hold")
	controller.tick(1.0 / 60.0, 1.0, Vector2.RIGHT)
	_expect(controller.display_frame() == controller.nearest_contact_frame(before), "unblocked walk resumes from the contact frame nearest %d" % before)


func _test_phase_survives_direction_change() -> void:
	var controller = _make("eight_frame_pilot", "east")
	controller.tick(1.0 / 60.0, 17.0, Vector2.RIGHT)
	var frame_before: int = controller.display_frame()
	var distance_before: float = controller.cycle_distance
	controller.tick(1.0 / 60.0, 1.0, Vector2.DOWN)
	_expect(controller.facing == "south", "hard turn to south switches facing")
	_expect(controller.mode == Controller.MODE_WALK, "turn does not drop to idle")
	_expect(is_equal_approx(controller.cycle_distance, distance_before + 1.0), "turn keeps accumulated distance")
	_expect(controller.display_frame() == frame_before, "1 px after turn stays on frame %d (got %d)" % [frame_before, controller.display_frame()])
	controller.tick(1.0 / 60.0, 5.0, Vector2.LEFT)
	_expect(controller.facing == "west", "reverse switches facing")
	_expect(controller.display_frame() == (frame_before + 1) % 8, "phase continues forward through turns")


func _test_stop_settles_on_contact_frame() -> void:
	for spec_name in SPECS:
		var spec: Dictionary = SPECS[spec_name]
		var n: int = spec["walk_frame_count"]
		var step: float = float(spec["cycle_length_px"]) / n
		for frame in n:
			var controller = _make(spec_name)
			var start: int = controller.contact_frames[0]
			controller.tick(0.016, posmod(frame - start, n) * step + step * 0.5, Vector2.UP)
			_expect(controller.walk_frame() == frame, "%s reached frame %d" % [spec_name, frame])
			controller.tick(0.016, 0.0, Vector2.ZERO)
			var contact: int = controller.display_frame()
			_expect(controller.mode == Controller.MODE_SETTLE, "%s stop enters settle" % spec_name)
			_expect(controller.contact_frames.has(contact), "%s stop from %d lands on a contact frame (%d)" % [spec_name, frame, contact])
			var gap := mini(posmod(contact - frame, n), posmod(frame - contact, n))
			for other in controller.contact_frames:
				_expect(gap <= mini(posmod(other - frame, n), posmod(frame - other, n)), "%s contact %d is nearest to %d" % [spec_name, contact, frame])
			var stable := true
			var hold_ticks := int(ceil(float(spec["settle_hold_seconds"]) / 0.016)) - 1
			for i in hold_ticks:
				controller.tick(0.016, 0.0, Vector2.ZERO)
				stable = stable and controller.display_frame() == contact and controller.mode == Controller.MODE_SETTLE
			_expect(stable, "%s contact frame %d is held for the settle duration" % [spec_name, contact])
			controller.tick(0.016, 0.0, Vector2.ZERO)
			controller.tick(0.016, 0.0, Vector2.ZERO)
			_expect(controller.mode == Controller.MODE_IDLE, "%s settles into idle" % spec_name)
			controller.tick(0.016, step * 0.5, Vector2.UP)
			_expect(controller.mode == Controller.MODE_WALK and controller.display_frame() == contact, "%s walk resumes from held contact %d (got %d)" % [spec_name, contact, controller.display_frame()])
	# Idle is time-driven over the declared idle frame count.
	var idle = _make("eight_frame_pilot")
	var idle_frames := []
	for i in 8:
		idle_frames.append(idle.display_frame())
		idle.tick(0.125, 0.0, Vector2.ZERO)
	_expect(idle_frames == [0, 0, 1, 1, 2, 2, 0, 0], "idle cycles 3 declared frames at 0.25 s holds: %s" % str(idle_frames))


# Settle-to-idle must happen on the first tick at or past the declared hold for any frame rate,
# and the overshoot carries into idle so the idle cycle tracks wall time, not tick boundaries.
func _test_settle_hold_is_frame_rate_independent() -> void:
	var rates := [24.0, 30.0, 37.0, 60.0, 144.0, 240.0]
	for spec_name in SPECS:
		var spec: Dictionary = SPECS[spec_name]
		var hold: float = spec["settle_hold_seconds"]
		var idle_hold: float = spec["idle_hold_seconds"]
		var idle_count: int = spec["idle_frame_count"]
		for fps in rates:
			var dt: float = 1.0 / fps
			var controller = _make(spec_name)
			controller.tick(dt, 12.0, Vector2.RIGHT)
			controller.tick(dt, 0.0, Vector2.ZERO)
			var elapsed := 0.0
			var idle_at := -1.0
			var idle_mismatch := ""
			var tick_count := 0
			while elapsed < hold + 1.0:
				controller.tick(dt, 0.0, Vector2.ZERO)
				tick_count += 1
				elapsed = tick_count * dt
				if idle_at < 0.0 and controller.mode == Controller.MODE_IDLE:
					idle_at = elapsed
				if idle_at >= 0.0 and idle_mismatch.is_empty():
					var position := (elapsed - hold) / idle_hold
					# Skip ticks that land within float noise of an idle frame boundary.
					if absf(position - roundf(position)) > 0.000001:
						var want := int(floor(position)) % idle_count
						if controller.display_frame() != want:
							idle_mismatch = "%.4f s into idle got %d want %d" % [elapsed - hold, controller.display_frame(), want]
			_expect(idle_at >= hold - 0.000001 and idle_at < hold + dt - 0.000001, "%s @%.0f fps leaves settle on the first tick at/after %.3f s (left at %.4f s)" % [spec_name, fps, hold, idle_at])
			_expect(idle_mismatch.is_empty(), "%s @%.0f fps idle tracks wall time: %s" % [spec_name, fps, idle_mismatch])
	# One long hitch (0.6 s) after stopping: 0.1 s settle, then 0.5 s of idle = frame 2 of 3.
	var hitch = _make("eight_frame_pilot")
	hitch.tick(1.0 / 60.0, 12.0, Vector2.RIGHT)
	hitch.tick(1.0 / 60.0, 0.0, Vector2.ZERO)
	hitch.tick(0.6, 0.0, Vector2.ZERO)
	_expect(hitch.mode == Controller.MODE_IDLE and hitch.display_frame() == 2, "hitch carries settle overshoot into idle (mode %s frame %d)" % [hitch.mode, hitch.display_frame()])


func _test_zero_settle_hold_goes_straight_to_idle() -> void:
	var spec: Dictionary = SPECS["eight_frame_pilot"].duplicate(true)
	spec["settle_hold_seconds"] = 0.0
	var controller = Controller.new()
	_expect(controller.configure(spec, "east"), "zero settle hold configures (%s)" % controller.last_error)
	controller.tick(1.0 / 60.0, 16.0, Vector2.RIGHT)
	var frame: int = controller.walk_frame()
	controller.tick(1.0 / 60.0, 0.0, Vector2.ZERO)
	_expect(controller.mode == Controller.MODE_IDLE, "zero hold never shows a settle tick (mode %s)" % controller.mode)
	_expect(controller.display_frame() == 0, "zero hold starts idle on idle frame 0 (got %d)" % controller.display_frame())
	controller.tick(1.0 / 60.0, 1.0, Vector2.RIGHT)
	_expect(controller.mode == Controller.MODE_WALK and controller.display_frame() == controller.nearest_contact_frame(frame), "zero hold still resumes walk from the contact nearest %d (got %d)" % [frame, controller.display_frame()])


func _test_facing_hysteresis() -> void:
	var controller = _make("eight_frame_pilot", "east")
	_expect(controller.update_facing(Vector2(1.0, 1.1)) == "east", "east kept at slightly-south diagonal")
	_expect(controller.update_facing(Vector2(1.0, 1.19)) == "east", "east kept below 1.2x")
	_expect(controller.update_facing(Vector2(1.0, 1.21)) == "south", "south wins above 1.2x")
	_expect(controller.update_facing(Vector2(1.15, 1.0)) == "south", "south kept at slightly-east diagonal")
	_expect(controller.update_facing(Vector2(-0.05, 1.0)) == "south", "south kept while still pressed")
	_expect(controller.update_facing(Vector2(-1.0, -0.2)) == "west", "releasing south switches at once")
	_expect(controller.update_facing(Vector2.ZERO) == "west", "no input keeps facing")
	_expect(_make("six_frame_variant", "east").update_facing(Vector2(1.0, 1.3)) == "east", "ratio is data: 1.35 keeps east at 1.3x")
	# Analog stick wobbling +-4 degrees around 45 degrees for 240 ticks.
	var hysteresis_flips := 0
	var naive_flips := 0
	var naive_facing := "east"
	controller.facing = "east"
	var previous: String = controller.facing
	for i in 240:
		var angle := deg_to_rad(45.0 + 4.0 * sin(i * 1.7))
		var input := Vector2(cos(angle), sin(angle))
		var next: String = controller.update_facing(input)
		if next != previous:
			hysteresis_flips += 1
		previous = next
		var naive := "south" if absf(input.y) >= absf(input.x) else "east"
		if naive != naive_facing:
			naive_flips += 1
		naive_facing = naive
	print("45-degree wobble flips: naive rule %d, hysteresis %d" % [naive_flips, hysteresis_flips])
	_expect(naive_flips > 20, "naive rule flickers on the wobble (sanity, %d)" % naive_flips)
	_expect(hysteresis_flips == 0, "hysteresis holds facing through the wobble (%d flips)" % hysteresis_flips)


func _test_long_walk_has_no_drift() -> void:
	var controller = _make("four_phase_runtime")
	for i in 100000:
		controller.tick(1.0 / 60.0, 140.0 / 60.0, Vector2.RIGHT)
	# 100000 * 7/3 px; cycle_distance must stay bounded and agree with the closed form.
	var total := 100000.0 * 140.0 / 60.0
	var expected_distance := fposmod(total, 67.2)
	_expect(controller.cycle_distance >= 0.0 and controller.cycle_distance < 67.2, "cycle distance stays wrapped")
	_expect(absf(controller.cycle_distance - expected_distance) < 0.05, "no drift after %.0f px (got %.4f want %.4f)" % [total, controller.cycle_distance, expected_distance])
