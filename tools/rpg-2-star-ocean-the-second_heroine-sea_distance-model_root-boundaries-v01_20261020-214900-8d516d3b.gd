extends SceneTree

var Model
var count := 0
var bad := []

func ck(ok: bool, label: String) -> void:
	count += 1
	if not ok:
		bad.append(label)
		print("DISTANCE_BOUNDARY_FAIL ", label)

func fresh():
	var m = Model.new()
	m.reset("east")
	return m

func stable_fields(s: Dictionary) -> Array:
	return [s.get("action"), s.get("phase"), s.get("frame"), s.get("facing")]

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	Model = load(OS.get_cmdline_user_args()[0])
	ck(Model != null, "load model")
	if Model == null:
		quit(1)
		return
	var paths := [[1.0/30, 1.0/30, 1.0/30], [1.0/60,1.0/60,1.0/60,1.0/60,1.0/60,1.0/60], [0.01,0.04,0.013,0.037]]
	for plan in paths:
		var m = fresh()
		var p := Vector2.ZERO
		var s: Dictionary
		for dt in plan:
			var q := p + Vector2(float(dt) * 120.0,0)
			s = m.step(float(dt),p,q,"east")
			p = q
		ck(is_equal_approx(float(s.get("phase",-1)),0.25), "equal path distance regardless of dt " + str(plan))
		ck(int(s.get("frame",-1)) == 3, "phase quarter frame3")
	for index in 12:
		var m = fresh()
		# Place at each distinct phase via real displacement, not by modifying model internals.
		var d := (float(index) + 0.25) * 4.0
		var s: Dictionary = m.step(1.0/30,Vector2.ZERO,Vector2(d,0),"east")
		ck(int(s.get("frame",-1)) == index, "entry frame " + str(index))
		s = m.step(0.04,Vector2(d,0),Vector2(d,0),"east")
		ck(s.get("action") != "walk", "blocked actual motion stops walk " + str(index))
		var phase := float(s.get("phase",-1))
		s = m.step(1.0/60,Vector2(d,0),Vector2(d+0.1,0),"east")
		ck(is_equal_approx(float(s.get("phase",-2)),fposmod(phase + 0.1/48.0,1.0)), "repress preserves settled phase " + str(index))
		for n in 5:
			s = m.step(0.03,Vector2(d,0),Vector2(d,0),"east")
		ck(s.get("action") == "idle" and int(s.get("frame",-1)) == 0, "settled at <=150ms " + str(index))
		var rest := stable_fields(s)
		s = m.step(20.0,Vector2(d,0),Vector2(d,0),"east")
		ck(stable_fields(s) == rest, "idle no timer drift " + str(index))
	var independent = fresh()
	var bounded = fresh()
	bounded.step(0.1,Vector2.ZERO,Vector2(10,0),"east")
	var partial: Dictionary = bounded.step(0.04,Vector2(10,0),Vector2(10,0),"east")
	ck(is_equal_approx(float(partial.get("settle_elapsed",-1)),0.04), "first stopped tick consumes its elapsed time")
	var completed: Dictionary = bounded.step(0.08,Vector2(10,0),Vector2(10,0),"east")
	ck(completed.get("action") == "idle", "inclusive120ms from first observed stop, no extra skipped tick")
	ck(is_equal_approx(float(completed.get("diagnostics",{}).get("cosmetic_phase_advance",-1)),0.5 - 10.0/48.0), "completion diagnostic preserves original settle start before clearing state")
	var other = fresh()
	var first: Dictionary = independent.step(0.1,Vector2.ZERO,Vector2(12,0),"east")
	other.step(0.1,Vector2.ZERO,Vector2(22,0),"west")
	var after: Dictionary = independent.step(0.1,Vector2(12,0),Vector2(13,0),"east")
	ck(is_equal_approx(float(after.get("phase",-1)),13.0/48.0), "two models do not share phase")
	var snapshot := stable_fields(after)
	for invalid in [-1.0,NAN,INF]:
		var rejected: Dictionary = independent.step(invalid,Vector2(13,0),Vector2(14,0),"east")
		ck(stable_fields(rejected) == snapshot, "invalid delta does not mutate " + str(invalid))
	var malformed: Dictionary = independent.step(0.1,Vector2(NAN,0),Vector2(14,0),"east")
	ck(stable_fields(malformed) == snapshot, "NaN position does not mutate")
	malformed = independent.step(0.1,Vector2(13,0),Vector2(14,0),"upward")
	ck(stable_fields(malformed) == snapshot, "unknown facing does not mutate")
	var last: Dictionary = independent.step(0.1,Vector2.ZERO,Vector2(1000,0),"east")
	ck(last.get("action") != "walk", "teleport is not locomotion")
	if bad.is_empty():
		print("DISTANCE_BOUNDARY_ROOT_PASS checks=",count)
		quit(0)
	else:
		print("DISTANCE_BOUNDARY_ROOT_FAIL ",JSON.stringify(bad))
		quit(1)
