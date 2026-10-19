extends SceneTree

# TEST-ONLY check of the opt-in female complete-exploration driver through its real attach()/step() API on a Sprite2D
# (host movement simulated: 140 px/s, the hosts' dominant-axis facing rule). Checks default-off (no file read), whole-set
# load, exact rest == idle phase 00 for all four directions at 30 / 60 / mixed frame times, turns (fresh incoming model
# at rest, never the opposite-intent placeholder), same-facing re-press keeps the model, blocked movement stops,
# diagonals, every cache hit against a fresh render (RGBA oracle), pivot offsets and per-step cost / cache memory.
#   Godot --headless --path <checkout>/game -s <abs this file> -- --report=<abs json>

const Pilot := preload("res://scripts/exploration_sprite_set_pilot.gd")
const Driver := preload("res://scripts/fexp/rpg-2-star-ocean-the-second_female-complete-explore_driver_pilot-v01_20261019-184900-f2c0a7e1.gd")
const SPEED := 140.0
const VEC := {"east": Vector2(1, 0), "west": Vector2(-1, 0), "north": Vector2(0, -1), "south": Vector2(0, 1)}

var checks := {}
var root_node: Node2D


func _initialize() -> void:
	var report_path := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--report="):
			report_path = arg.substr(9)
	var report := {"tool": "female-complete-explore driver check v01"}
	# Default off: neither pilot attaches and the package is never read.
	var off_sprite := Sprite2D.new()
	var off := Pilot.attach(off_sprite, "protagonist-female", "south")
	_check("default_off_null", off == null and Driver.load_count == 0 and off_sprite.get_child_count() == 0,
		{"load_count": Driver.load_count})
	off_sprite.free()
	Driver.enabled_override = 1
	var mem0 := OS.get_static_memory_usage()
	var t0 := Time.get_ticks_usec()
	var assets := Driver.load_assets()
	report["attach_load_ms"] = (Time.get_ticks_usec() - t0) / 1000.0
	report["static_memory_after_load_bytes"] = OS.get_static_memory_usage() - mem0
	_check("package_loads_whole_set", bool(assets["ok"]), {"error": assets.get("error", "")})
	if not bool(assets["ok"]):
		_finish(report, report_path)
		return
	root_node = Node2D.new()
	get_root().add_child(root_node)
	# Non-female actor stays on the existing path.
	var other := Sprite2D.new()
	root_node.add_child(other)
	_check("other_actor_not_attached", Driver.attach(other, "protagonist-male", "south") == null, {})
	var rates := {"60": [1.0 / 60.0], "30": [1.0 / 30.0], "mixed": [1.0 / 60.0, 1.0 / 30.0, 1.0 / 144.0, 0.021, 1.0 / 48.0]}
	var rest_results := {}
	var costs := {}
	for rate in rates:
		for d in ["south", "west", "north", "east"]:
			var r := _run_stop(d, rates[rate])
			rest_results["%s-%s" % [d, rate]] = r
			costs["%s-%s" % [d, rate]] = r["cost"]
	var all_rest := true
	for k in rest_results:
		all_rest = all_rest and bool(rest_results[k]["pass"])
	_check("run_stop_rest_exact_all_dirs_rates", all_rest, rest_results)
	_check("turns", _turns(), {})
	_check("same_facing_repress_keeps_model", _repress(), {})
	_check("blocked_move_stops", _blocked(), {})
	_check("diagonals_dominant_axis", _diagonal(), {})
	report["costs"] = costs
	var fail := []
	for k in checks:
		if not bool(checks[k]["pass"]):
			fail.append(k)
	report["checks"] = checks
	report["fail"] = fail
	_finish(report, report_path)


func _new_driver(facing: String) -> Array:
	var s := Sprite2D.new()
	s.position = Vector2(320, 200)
	root_node.add_child(s)
	var d = Pilot.attach(s, "protagonist-female", facing)
	d.oracle = true
	return [s, d]


func _move(s: Sprite2D, d, facing: String, v: Vector2, dt: float, blocked := false) -> void:
	var from := s.position
	if not blocked:
		s.position += v.normalized() * SPEED * dt
	d.step(dt, from, s.position, facing)


func _visible_image(s: Sprite2D) -> Image:
	var image := s.texture.get_image()
	image.convert(Image.FORMAT_RGBA8)
	return image


func _run_stop(direction: String, dts: Array) -> Dictionary:
	var pair := _new_driver(direction)
	var s: Sprite2D = pair[0]
	var d = pair[1]
	var assets: Dictionary = Driver.load_assets()
	var rest: Image = assets["idle"][direction][0]["image"]
	var i := 0
	var trace := []
	var steps_us := []
	d.step(dts[0], s.position, s.position, direction)
	for t in 60:
		var dt: float = dts[i % dts.size()]
		i += 1
		var a := Time.get_ticks_usec()
		_move(s, d, direction, VEC[direction], dt)
		steps_us.append(Time.get_ticks_usec() - a)
	var moving_ok: bool = String(d.model_mode) != "idle" and String(d.model_mode) != "rest" and not d.showing_idle
	var stop_ticks := 0
	var first_idle_exact := false
	var stop_us := []
	while stop_ticks < 120:
		var dt: float = dts[i % dts.size()]
		i += 1
		var a := Time.get_ticks_usec()
		d.step(dt, s.position, s.position, direction)
		stop_us.append(Time.get_ticks_usec() - a)
		stop_ticks += 1
		trace.append([d.model_mode, d.showing_idle])
		if d.showing_idle:
			first_idle_exact = _visible_image(s).get_data() == rest.get_data() and d.idle_phase() == 0
			break
	var pivot_ok := s.offset == Vector2(s.texture.get_size()) * 0.5 - Vector2(40, 104) + Vector2(0, 2) and s.scale == Vector2(0.5, 0.5)
	var shadow_ok: bool = (d.shadow.visible == (direction == "south"))
	var r := {"moving_ok": moving_ok, "stop_ticks": stop_ticks, "first_idle_exact": first_idle_exact, "pivot_ok": pivot_ok,
		"shadow_ok": shadow_ok, "oracle_mismatch": d.oracle_mismatch, "final_mode_flag": d.model_mode,
		"cost": {"run_us_mean": _mean(steps_us), "run_us_max": steps_us.max(), "stop_us_mean": _mean(stop_us),
			"renders": d.stats["renders"], "hits": d.stats["hits"], "cache_entries": d.cache.size(), "cache_bytes": d.cache_bytes()}}
	r["pass"] = moving_ok and first_idle_exact and pivot_ok and shadow_ok and d.oracle_mismatch == 0 and stop_ticks < 120
	s.queue_free()
	return r


func _turns() -> bool:
	var ok := true
	for pair_dirs in [["east", "north"], ["north", "west"], ["west", "south"], ["south", "east"], ["east", "west"], ["north", "south"]]:
		var pair := _new_driver(pair_dirs[0])
		var s: Sprite2D = pair[0]
		var d = pair[1]
		for t in 30:
			_move(s, d, pair_dirs[0], VEC[pair_dirs[0]], 1.0 / 60.0)
		var switches: int = d.stats["switches"]
		_move(s, d, pair_dirs[1], VEC[pair_dirs[1]], 1.0 / 60.0)
		ok = ok and d.facing == pair_dirs[1] and d.stats["switches"] == switches + 1 and String(d.model_mode) != "reverse-placeholder"
		for t in 20:
			_move(s, d, pair_dirs[1], VEC[pair_dirs[1]], 1.0 / 60.0)
			ok = ok and String(d.model_mode) != "reverse-placeholder"
		ok = ok and not d.showing_idle and d.oracle_mismatch == 0
		s.queue_free()
	return ok


func _repress() -> bool:
	var pair := _new_driver("east")
	var s: Sprite2D = pair[0]
	var d = pair[1]
	for t in 40:
		_move(s, d, "east", VEC["east"], 1.0 / 60.0)
	for t in 3:
		d.step(1.0 / 60.0, s.position, s.position, "east")
	var mid: String = d.model_mode
	var switches: int = d.stats["switches"]
	for t in 10:
		_move(s, d, "east", VEC["east"], 1.0 / 60.0)
	var ok: bool = mid == "stop" and d.stats["switches"] == switches and String(d.model_mode) == "run"
	s.queue_free()
	return ok


func _blocked() -> bool:
	var ok := true
	for direction in ["south", "west", "north", "east"]:
		var pair := _new_driver(direction)
		var s: Sprite2D = pair[0]
		var d = pair[1]
		for t in 30:
			_move(s, d, direction, VEC[direction], 1.0 / 60.0)
		var n := 0
		while n < 120 and not d.showing_idle:
			_move(s, d, direction, VEC[direction], 1.0 / 60.0, true)
			n += 1
		ok = ok and d.showing_idle
		s.queue_free()
	return ok


func _diagonal() -> bool:
	var ok := true
	for v in [Vector2(1, -0.6), Vector2(-1, 0.6), Vector2(0.6, -1), Vector2(-0.6, 1), Vector2(1, 1)]:
		var facing := "east" if v.x > 0.0 else "west"
		if absf(v.y) >= absf(v.x):
			facing = "south" if v.y > 0.0 else "north"
		var pair := _new_driver(facing)
		var s: Sprite2D = pair[0]
		var d = pair[1]
		for t in 40:
			_move(s, d, facing, v, 1.0 / 60.0)
		ok = ok and d.facing == facing and not d.showing_idle and d.oracle_mismatch == 0
		s.queue_free()
	return ok


func _check(name: String, value: bool, detail) -> void:
	checks[name] = {"pass": value, "detail": detail}


func _mean(values: Array) -> float:
	var total := 0.0
	for v in values:
		total += float(v)
	return total / maxf(values.size(), 1.0)


func _finish(report: Dictionary, path: String) -> void:
	var text := JSON.stringify(report, "  ")
	print(text)
	if path != "":
		var f := FileAccess.open(path, FileAccess.WRITE)
		f.store_string(text)
		f.close()
	var ok: bool = report.get("fail", ["x"]).is_empty()
	Driver.clear_cache()
	if root_node != null:
		root_node.queue_free()
	print("FCX_DRIVER_CHECK_PASS" if ok else "FCX_DRIVER_CHECK_FAIL")
	quit(0 if ok else 1)
