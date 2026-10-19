extends SceneTree

# TEST-ONLY full-output oracle for the fcx-v03 exact render optimization (UNAPPROVED, opt-in pilot only).
# FROZEN = the v02 model copies preserved in outputs/fcx-v03/frozen-v02 (compiled here from their source text);
# CURRENT = the optimized models in res://scripts/fexp. Both are driven by identical advance()/tick() sequences and
# every rendered pose is compared in full: EAST/WEST/NORTH render_pose() (full image, every role image, contacts /
# sole rows / leg info / leg images) and SOUTH Comp10.compose() (body image, shadow image, boots, soles, near, legs,
# seam / fill / island counts). The advance()/tick() snapshots themselves must also stay identical.
# Sequences per direction: dense (0.5 px per tick = one gait phase per tick, 300 ticks, then stop to rest) and
# 60 / 30 / mixed (1/60, 1/30, 1/144, 0.021, 1/48 s) at 140 px/s: start, run, stop, same-facing re-press during the
# stop, run, stop to rest; plus a short-tap re-press. Also times every render (frozen vs current, same process).
#   Godot --headless --path <checkout>/game -s <abs this file> -- --frozen=<abs dir> --report=<abs json>

const PACKAGE := "res://data/fexp/rpg-2-star-ocean-the-second_female-complete-explore_package_v01_20261019-184500-f2c0a7e1.json"
const SOUTH_RUNTIME := "res://data/fexp/rpg-2-star-ocean-the-second_female-complete-explore_south-runtime_v01_20261019-184900-f2c0a7e1.json"
const SPEED := 140.0
const RATES := {"60": [1.0 / 60.0], "30": [1.0 / 30.0], "mixed": [1.0 / 60.0, 1.0 / 30.0, 1.0 / 144.0, 0.021, 1.0 / 48.0]}

var report := {"tool": "female-complete-explore render oracle v03", "directions": {}}
var all_ok := true
var mismatches := []


func _initialize() -> void:
	var frozen_dir := ""
	var report_path := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--frozen="):
			frozen_dir = arg.substr(9)
		elif arg.begins_with("--report="):
			report_path = arg.substr(9)
	var package: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PACKAGE))
	for d in ["east", "west", "north"]:
		var cur_path := String(package["models"][d])
		var frozen := _compile(frozen_dir.path_join(cur_path.get_file()))
		var current := load(cur_path) as GDScript
		if frozen == null or current == null:
			_fail("load " + d)
			continue
		report["directions"][d] = _lateral(d, frozen, current)
	var south_path := String(package["south_model"])
	var fs := _compile(frozen_dir.path_join(south_path.get_file()))
	var cs := load(south_path) as GDScript
	if fs == null or cs == null:
		_fail("load south")
	else:
		report["directions"]["south"] = _south(fs, cs)
	# Self-test: the comparison must see a one-byte change in a nested role image.
	var probe := Image.create(4, 4, false, Image.FORMAT_RGBA8)
	var probe2 := probe.duplicate()
	probe2.set_pixel(3, 3, Color8(0, 0, 0, 1))
	report["self_test_detects_one_byte"] = not _same({"roles": {"x": probe}}, {"roles": {"x": probe2}}) and _same({"roles": {"x": probe}}, {"roles": {"x": probe.duplicate()}})
	if not report["self_test_detects_one_byte"]:
		_fail("self test")
	for d in ["east", "west", "north", "south"]:
		if not report["directions"].has(d) or int(report["directions"][d]["compared"]) < 200 or int(report["directions"][d]["mismatch"]) != 0:
			all_ok = false
	report["mismatch_samples"] = mismatches.slice(0, 20)
	report["pass"] = all_ok
	var f := FileAccess.open(report_path, FileAccess.WRITE)
	f.store_string(JSON.stringify(report, "\t"))
	f.close()
	for d in report["directions"]:
		var r: Dictionary = report["directions"][d]
		print("%s compared=%d unique=%d mismatch=%d frozen p50/p95/max=%.2f/%.2f/%.2f ms current p50/p95/max=%.2f/%.2f/%.2f ms startup frozen/current=%.1f/%.1f ms" % [
			d, r["compared"], r["unique_states"], r["mismatch"], r["frozen_ms"]["p50"], r["frozen_ms"]["p95"], r["frozen_ms"]["max"],
			r["current_ms"]["p50"], r["current_ms"]["p95"], r["current_ms"]["max"], r["startup_ms"]["frozen"], r["startup_ms"]["current"]])
	print("FCX_V03_ORACLE_PASS" if all_ok else "FCX_V03_ORACLE_FAIL")
	quit(0 if all_ok else 1)


func _compile(path: String) -> GDScript:
	if not FileAccess.file_exists(path):
		return null
	var s := GDScript.new()
	s.source_code = FileAccess.get_file_as_string(path)
	return s if s.reload() == OK else null


func _fail(what: String) -> void:
	all_ok = false
	mismatches.append(what)


# --- full deep comparison (Images by size, format and bytes) ---
func _same(a, b) -> bool:
	if a is Image:
		return b is Image and a.get_size() == b.get_size() and a.get_format() == b.get_format() and a.get_data() == b.get_data()
	if a is Dictionary:
		if not b is Dictionary or a.size() != b.size() or a.keys() != b.keys():
			return false
		for k in a:
			if not _same(a[k], b[k]):
				return false
		return true
	if a is Array:
		if not b is Array or a.size() != b.size():
			return false
		for i in a.size():
			if not _same(a[i], b[i]):
				return false
		return true
	return typeof(a) == typeof(b) and a == b


func _diff_px(a: Image, b: Image) -> int:
	var da := a.get_data()
	var db := b.get_data()
	var n := 0
	for i in range(0, mini(da.size(), db.size()), 4):
		if da[i] != db[i] or da[i + 1] != db[i + 1] or da[i + 2] != db[i + 2] or da[i + 3] != db[i + 3]:
			n += 1
	return n


func _stats(values: Array) -> Dictionary:
	if values.is_empty():
		return {"p50": 0.0, "p95": 0.0, "max": 0.0, "n": 0}
	var v := values.duplicate()
	v.sort()
	return {"p50": v[v.size() / 2], "p95": v[int(v.size() * 0.95)], "max": v[-1], "n": v.size()}


# Tick plans: [seconds moving or not, ...] as [[move, seconds], ...]
func _plans() -> Dictionary:
	var plans := {}
	for rate in RATES:
		plans[rate] = {"dts": RATES[rate], "speed": SPEED, "plan": [[false, 0.05], [true, 0.6], [false, 0.08], [true, 0.3], [false, 0.5],
			[true, 0.05], [false, 0.03], [true, 0.12], [false, 0.6]]}
	plans["dense"] = {"dts": [1.0 / 60.0], "speed": 30.0, "plan": [[false, 0.05], [true, 5.0], [false, 0.6]]}
	return plans


func _lateral(d: String, frozen: GDScript, current: GDScript) -> Dictionary:
	var out := {"compared": 0, "mismatch": 0, "snapshot_mismatch": 0, "unique_states": 0}
	var mem0 := OS.get_static_memory_usage()
	var obj0 := Performance.get_monitor(Performance.OBJECT_COUNT)
	var t0 := Time.get_ticks_usec()
	var fm = frozen.new()
	var t1 := Time.get_ticks_usec()
	var mem1 := OS.get_static_memory_usage()
	var obj1 := Performance.get_monitor(Performance.OBJECT_COUNT)
	var cm = current.new()
	var t2 := Time.get_ticks_usec()
	out["startup_ms"] = {"frozen": (t1 - t0) / 1000.0, "current": (t2 - t1) / 1000.0}
	out["construct_static_memory_bytes"] = {"frozen": mem1 - mem0, "current": OS.get_static_memory_usage() - mem1}
	out["construct_object_delta"] = {"frozen": obj1 - obj0, "current": Performance.get_monitor(Performance.OBJECT_COUNT) - obj1}
	var sign := -1.0 if d in ["west", "north"] else 1.0
	var intent := -1.0 if d == "west" else 1.0
	var tf := []
	var tc := []
	var seen := {}
	var per_plan := {}
	for name in _plans():
		var plan: Dictionary = _plans()[name]
		# Fresh models per plan, bootstrapped at rest like the driver does.
		fm = frozen.new()
		cm = current.new()
		var pos := 400.0
		fm.advance(0.0, pos, 0.0)
		cm.advance(0.0, pos, 0.0)
		var k := 0
		var n_plan := 0
		for seg in plan["plan"]:
			var t := 0.0
			while t < float(seg[1]) - 0.000001:
				var dt: float = plan["dts"][k % plan["dts"].size()]
				k += 1
				t += dt
				if seg[0]:
					pos += sign * float(plan["speed"]) * dt
				var sf: Dictionary = fm.advance(dt, pos, intent if seg[0] else 0.0)
				var sc: Dictionary = cm.advance(dt, pos, intent if seg[0] else 0.0)
				if var_to_str(sf) != var_to_str(sc):
					out["snapshot_mismatch"] += 1
					_fail("%s %s snapshot tick %d" % [d, name, k])
				var a := Time.get_ticks_usec()
				var rf: Dictionary = fm.render_pose(sf)
				var b := Time.get_ticks_usec()
				var rc: Dictionary = cm.render_pose(sf)
				var c := Time.get_ticks_usec()
				if String(sf["mode"]) != "idle":
					tf.append((b - a) / 1000.0)
					tc.append((c - b) / 1000.0)
				seen[var_to_str(sf)] = true
				out["compared"] += 1
				n_plan += 1
				if not _same(rf, rc):
					out["mismatch"] += 1
					_fail("%s %s tick %d mode %s full_px_diff %d" % [d, name, k, sf["mode"], _diff_px(rf["full"], rc["full"])])
		per_plan[name] = n_plan
	out["per_plan_ticks"] = per_plan
	out["unique_states"] = seen.size()
	out["frozen_ms"] = _stats(tf)
	out["current_ms"] = _stats(tc)
	return out


func _south(fs: GDScript, cs: GDScript) -> Dictionary:
	var out := {"compared": 0, "mismatch": 0, "snapshot_mismatch": 0, "unique_states": 0}
	var runtime: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SOUTH_RUNTIME))
	var comps := []
	var times := []
	for s in [fs, cs]:
		var mem0 := OS.get_static_memory_usage()
		var t0 := Time.get_ticks_usec()
		var comp = s.Comp10.new()
		for pair in runtime["part_lists"]:
			var err: String = comp.load_parts(pair[0], String(pair[1]), runtime["manifest"]["rig"])
			if err != "":
				_fail("south parts " + err)
		comp.setup9(runtime["art_amendment"])
		comp.setup10(runtime["leg_rule"], int(runtime["island_max_texels"]))
		var t1 := Time.get_ticks_usec()
		# First compose includes the current model's lazily built per-role tables.
		var neutral := {"bob": 0, "hdy": 0, "sx": 0, "csx": 0, "arms": {"R": "N", "L": "N"},
			"feet": {"vl": {"o": 0, "lift": 0, "view": "v8", "kin": 0}, "vr": {"o": 0, "lift": 0, "view": "v8", "kin": 0}}}
		comp.compose(neutral)
		var t2 := Time.get_ticks_usec()
		times.append({"setup_ms": (t1 - t0) / 1000.0, "first_compose_ms": (t2 - t1) / 1000.0, "static_memory_bytes": OS.get_static_memory_usage() - mem0})
		comps.append(comp)
	out["startup_ms"] = {"frozen": times[0]["setup_ms"] + times[0]["first_compose_ms"], "current": times[1]["setup_ms"] + times[1]["first_compose_ms"]}
	out["startup_detail"] = {"frozen": times[0], "current": times[1]}
	var neutral2 := {"bob": 0, "hdy": 0, "sx": 0, "csx": 0, "arms": {"R": "N", "L": "N"},
		"feet": {"vl": {"o": 0, "lift": 0, "view": "v8", "kin": 0}, "vr": {"o": 0, "lift": 0, "view": "v8", "kin": 0}}}
	out["rest_shadow_equal"] = _same(comps[0].compose(neutral2), comps[1].compose(neutral2))
	if not out["rest_shadow_equal"]:
		_fail("south neutral compose")
	var tf := []
	var tc := []
	var seen := {}
	var per_plan := {}
	for name in _plans():
		var plan: Dictionary = _plans()[name]
		var lf = fs.Loco10r1.new()
		var lc = cs.Loco10r1.new()
		lf.stagger = bool(runtime["stagger"])
		lc.stagger = bool(runtime["stagger"])
		var pos := 200.0
		lf.setup(runtime["manifest"], int(round(pos * 2.0)))
		lc.setup(runtime["manifest"], int(round(pos * 2.0)))
		var k := 0
		var n_plan := 0
		for seg in plan["plan"]:
			var t := 0.0
			while t < float(seg[1]) - 0.000001:
				var dt: float = plan["dts"][k % plan["dts"].size()]
				k += 1
				t += dt
				var moving: bool = seg[0]
				if moving:
					pos += float(plan["speed"]) * dt
				var rf: Dictionary = lf.tick(moving, dt, int(round(pos * 2.0)))
				var rc: Dictionary = lc.tick(moving, dt, int(round(pos * 2.0)))
				if var_to_str(rf) != var_to_str(rc):
					out["snapshot_mismatch"] += 1
					_fail("south %s tick snapshot %d" % [name, k])
				if bool(rf["show_v8"]):
					continue
				var st: Dictionary = rf["state"]
				var a := Time.get_ticks_usec()
				var cf: Dictionary = comps[0].compose(st)
				var b := Time.get_ticks_usec()
				var cc: Dictionary = comps[1].compose(st)
				var c := Time.get_ticks_usec()
				tf.append((b - a) / 1000.0)
				tc.append((c - b) / 1000.0)
				seen[var_to_str(st)] = true
				out["compared"] += 1
				n_plan += 1
				if out["compared"] % 5 == 1:
					out["fallback_compared"] = int(out.get("fallback_compared", 0)) + 1
					if not _same(cc, comps[1]._compose_v10(st)):
						out["mismatch"] += 1
						_fail("south %s tick %d fast != fallback" % [name, k])
				if cf.has("error") or not _same(cf, cc):
					out["mismatch"] += 1
					_fail("south %s tick %d body_px_diff %d shadow_px_diff %d" % [name, k,
						_diff_px(cf["image"], cc["image"]) if cf.has("image") and cc.has("image") else -1,
						_diff_px(cf["shadow"], cc["shadow"]) if cf.has("shadow") and cc.has("shadow") else -1])
		per_plan[name] = n_plan
	out["per_plan_ticks"] = per_plan
	out["unique_states"] = seen.size()
	out["frozen_ms"] = _stats(tf)
	out["current_ms"] = _stats(tc)
	return out
