extends "rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-godot-capture_m8-w09_20261017-211600-ff47ce98.gd"

# TEST-ONLY real-Godot capture of the UNAPPROVED / NONRUNTIME female SOUTH RUN motion pilot v07 (m8-w10, single direction).
# v07 is a versioned AMENDMENT, not a copy: this script EXTENDS the v06 capture tool (same folder, byte-identical, hash
# checked at start) and reads the v06 art / manifest read-only plus a small v07 amendment manifest
# (res://assets/characters/run-v07-unapproved/...restart-amendment-manifest...json).  ONE bounded control correction:
#   v06 QA defect 5 - at 30 fps a late-stance release then a re-press 1 frame later lifted BOTH boots on one frame.  The
#   restart re-plans the other boot into a fresh swing that rises to its peak at mid-swing, while the planted stance boot
#   passes its lift-off point within one 9.3 px step, so the re-planned boot was still rising when the stance boot left
#   the floor (a boot coming down to its v8 spot went back up).  v07 RISE LOCK (Loco7): while the other boot is off the
#   floor, a re-planned boot's drawn lift never increases (it reaches for the floor, as the leading boot does in the
#   steady run).  Offsets, views, touchdown distances, phase, alternation, planted boot and every stop rule are v06's.
# Overridden here: the gait driver class used by _drive / _sim_drive (Loco7), output names, _run (v07 sweep set) and the
# --sim=1 sweep.  Everything else (compositor, measurements, planted / release checks) is inherited unchanged.
# New gates (exit 1): no frame on which both boots rise (raised height up on both, or both leave contact) in any walk,
# stop, re-press, showreel, reversal or mixed-frame-time sequence; re-press at EVERY release phase of one stride at 30 /
# 60 fps (144 fps every 2nd) x several gaps; the stop sweeps (every phase, 30 / 60 / 144 fps) keep v06's limits.
# Review evidence only: not art acceptance, not runtime integration, not a production sprite.  Run windowed from the
# repository root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path of this file> -- --motion-dir=<abs scratch>
#   (add --headless and -- --sim=1 for the window-free gait-driver sweep)

const V06_TOOL_FILE := "rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-godot-capture_m8-w09_20261017-211600-ff47ce98.gd"
const V06_TOOL_SHA256 := "51f389a8b1a119dfc55f7b4848b3045d4c8fb50328de3204985c4393a884df7b"
const V06_MANIFEST_SHA256 := "f59b04fa672250c7525dda79d7cc3771830fa80a03fec339ff21fa19298e6b17"
const V07_DIR := "res://assets/characters/run-v07-unapproved/"
const V07_AMEND := "rpg-2-star-ocean-the-second_protagonist-female_south-run-v07-restart-amendment-manifest_unapproved-nonruntime_20261018-082500-a07441de.json"
const V07_FLAGS := ["art_approved", "human_reviewed", "runtime_integrated", "walk_animation_approved", "run_animation_approved",
	"stop_animation_approved", "counts_toward_art_acceptance"]
const STOP_V8_LIMIT_MS_60FPS := 200.0      # v06 60 fps release -> v8 150-200 ms: v07 must not be slower
const JITTER_DTS := [1.0 / 30.0, 1.0 / 45.0, 1.0 / 60.0, 1.0 / 144.0]
const DEFECT_CASE := "city-bright_repress-30fps-006-gap-01"    # v06 QA defect 5

var amend: Dictionary
var rise_lock_on := true          # --rise-lock=0 runs the v06 behaviour through the same harness (sim comparison only)


# =====================================================================================================================
# v07 gait driver: v06's Loco + the rise lock (manifest restart.v07_rise_lock, from the v07 amendment)
class Loco7 extends Loco:
	var rise_lock := false
	var drawn := {"vl": 0, "vr": 0}      # raised height drawn on the previous frame (0 = in contact)
	var locks := 0

	func setup(m: Dictionary, y: int) -> void:
		super(m, y)
		rise_lock = bool(m["restart"].get("v07_rise_lock", false))

	func tick(moving: bool, dt: float, y: int) -> Dictionary:
		var r: Dictionary = super(moving, dt, y)
		if rise_lock and moving:
			for s in ["vl", "vr"]:
				var o := "vr" if s == "vl" else "vl"
				var f: Dictionary = feet[s]
				if String(f["mode"]) == "swing" and bool(f.get("replanned", false)) and String(r["modes"][o]) != "contact" \
						and int(drawn[s]) > 0 and int(f["lift"]) > int(drawn[s]):
					r["events"].append(["rise-lock", s, int(f["lift"]), int(drawn[s])])
					f["lift"] = int(drawn[s])
					r["state"]["feet"][s]["lift"] = int(drawn[s])
					locks += 1
		for s in ["vl", "vr"]:
			drawn[s] = 0 if String(r["modes"][s]) == "contact" else int(r["state"]["feet"][s]["lift"])
		return r


func _fail(reason: String) -> void:
	push_error("RUN_V07_CAPTURE FAIL: " + reason)
	print("RUN_V07_CAPTURE FAIL: " + reason)
	Input.action_release("move_up")
	Input.action_release("move_down")
	quit(1)


func _out_name(scene_key: String, what: String, stamp: String, uid: String, ext: String) -> String:
	var n := "%s_%s_protagonist-female-south-run-v07-%s-h48_%s_%s-%s.%s" % [SLUG, scene_key, what, VARIANT, stamp, uid, ext]
	if n.length() > 150:
		push_error("output name too long (%d): %s" % [n.length(), n])
	return n


# raised height of a boot on a record: 0 in contact (or on the v8 PNG), else its drawn lift
func _hgt(rec: Dictionary, s: String) -> int:
	if bool(rec.get("show_v8", false)) or String(rec["modes"][s]) == "contact":
		return 0
	return int(rec["state"]["feet"][s]["lift"])


# v07 gate: frames on which BOTH boots rise (raised height up on both) or both leave contact.  Works on _drive ticks and
# on _sim_drive records; pairs touching a runtime_north tick are skipped (no pilot drawn there).
func _rise_faults(recs: Array) -> Array:
	var out := []
	for i in range(1, recs.size()):
		var a: Dictionary = recs[i - 1]
		var b: Dictionary = recs[i]
		if bool(a.get("runtime_north", false)) or bool(b.get("runtime_north", false)):
			continue
		var up := 0
		var off := 0
		for s in ["vl", "vr"]:
			if _hgt(b, s) > _hgt(a, s):
				up += 1
			if _hgt(a, s) == 0 and String(b["modes"][s]) != "contact" and not bool(b.get("show_v8", false)):
				off += 1
		if up == 2 or off == 2:
			out.append([i, "both-leave-floor" if off == 2 else "both-rise"])
	return out


func _locks_in(recs: Array) -> int:
	var n := 0
	for r in recs:
		for ev in r.get("events", []):
			if String(ev[0]) == "rise-lock":
				n += 1
	return n


# =====================================================================================================================
# _drive / _sim_drive: v06's bodies with the v07 driver class (Loco7); nothing else differs
func _drive(su: Array, plan: Array, motion_dir: String, tag: String, crop: Rect2i, full_saves: Dictionary = {}) -> Array:
	var host: Node2D = su[0]
	var hero: Sprite2D = su[1]
	var ground_off: float = su[3]
	var bg: Image = su[4]
	var loco := Loco7.new()
	loco.setup(manifest, _pin(hero, ground_off).y)
	var ticks := []
	var loco_reset := false
	for t in plan.size():
		var step: Dictionary = plan[t]
		var north: bool = String(step.get("dir", "")) == "up"
		var before := hero.position
		Input.action_release("move_up")
		if bool(step["input"]) and not north:
			Input.action_press("move_down")
		else:
			Input.action_release("move_down")
		if north:
			Input.action_press("move_up")
		host.call("_process", float(step["dt"]))
		hero.visible = false
		if north:
			if hero.position.x != before.x or hero.position.y >= before.y:
				_fail("%s tick %d: hero did not move straight north" % [tag, t])
				return []
			var hc: Array = await _draw_runtime(su)
			if motion_dir != "" and crop.size.x > 0:
				(hc[0] as Image).get_region(crop).save_png(motion_dir.path_join("%s_tick-%03d.png" % [tag, t]))
			if full_saves.has(t):
				(hc[0] as Image).save_png(String(full_saves[t]))
			ticks.append({"tick": t, "input": true, "dir": "up", "runtime_north": true, "dt": float(step["dt"]), "show_v8": false,
				"hero_logical": [hero.position.x, hero.position.y], "origin": hc[1],
				"modes": {"vl": "runtime-north", "vr": "runtime-north"}, "events": [["runtime-north"]]})
			loco_reset = true
			continue
		if loco_reset:
			loco = Loco7.new()
			loco.setup(manifest, _pin(hero, ground_off).y)
			loco_reset = false
		if bool(step["input"]):
			if hero.position.x != before.x or hero.position.y <= before.y:
				_fail("%s tick %d: hero did not move straight south" % [tag, t])
				return []
		elif hero.position != before:
			_fail("%s tick %d: hero moved without input" % [tag, t])
			return []
		var r := loco.tick(bool(step["input"]), float(step["dt"]), _pin(hero, ground_off).y)
		var img: Image
		var tex: Texture2D
		var shimg: Image
		var stex: Texture2D
		var info := {}
		if bool(r["show_v8"]):
			img = v8_image
			tex = v8_tex
			shimg = v8_shadow_image
			stex = v8_shadow_tex
		else:
			var c := comp.compose(r["state"])
			if c.has("error"):
				_fail("%s tick %d: %s" % [tag, t, c["error"]])
				return []
			img = c["image"]
			tex = ImageTexture.create_from_image(img)
			shimg = c["shadow"]
			stex = ImageTexture.create_from_image(shimg)
			info = c
		var dc: Array = await _draw_capture(su, tex, stex)
		var cap: Image = dc[0]
		var origin: Vector2i = dc[1]
		if motion_dir != "" and crop.size.x > 0:
			cap.get_region(crop).save_png(motion_dir.path_join("%s_tick-%03d.png" % [tag, t]))
		var fid := _fidelity(img, origin, cap)
		if fid["exact_rgb_matches"] != fid["opaque_texels"]:
			_fail("%s tick %d fidelity %s" % [tag, t, str(fid)])
			return []
		if full_saves.has(t):
			cap.save_png(String(full_saves[t]))
		var meas := _measure(cap, bg, origin, img, shimg)
		var neck := _neck(cap, origin)
		if int(neck["shear_dx"]) != 0 or int(neck["shear_dy"]) != 0 or float(neck["head_match"]) < 0.999 or float(neck["torso_match"]) < 0.999:
			_fail("%s tick %d: head / torso offsets differ on the capture %s" % [tag, t, str(neck)])
			return []
		if int(info.get("seams", 0)) != 0:
			_fail("%s tick %d: %d neck seam texels filled" % [tag, t, int(info["seams"])])
			return []
		var boots_w := {}
		for s in ["vl", "vr"]:
			if r["modes"][s] == "contact":
				var src: Dictionary = info["boots"][s] if not info.is_empty() else v8_boot[s]
				var world := {}
				var seen := {}
				var vis := 0
				var lowest := -1
				for q in src:
					var w: Vector2i = origin + q
					var bc: Color = src[q]
					world[w] = bc.to_html(false)
					var cc := cap.get_pixelv(w)
					if cc.r8 == bc.r8 and cc.g8 == bc.g8 and cc.b8 == bc.b8:
						vis += 1
						seen[w] = true
						lowest = maxi(lowest, w.y)
				var x0 := 1 << 30
				var x1 := -1
				for w in seen:
					if w.y == lowest:
						x0 = mini(x0, w.x)
						x1 = maxi(x1, w.x)
				boots_w[s] = {"world": world, "visible": vis, "lowest_row": lowest, "sole_x": [x0, x1],
					"view": String(r["state"]["feet"][s]["view"])}
		ticks.append({"tick": t, "input": bool(step["input"]), "dir": "down" if bool(step["input"]) else "", "dt": float(step["dt"]), "show_v8": bool(r["show_v8"]),
			"modes": r["modes"], "state": r["state"], "events": r["events"], "phase": r["phase"], "dist": r["dist"],
			"hero_logical": [hero.position.x, hero.position.y], "origin": origin, "meas": meas, "boots_w": boots_w,
			"cell_h": img.get_height(), "neck": neck, "legs": info.get("legs", {})})
	Input.action_release("move_down")
	last_settle_log = loco.settle_log.duplicate(true)
	return ticks


func _sim_drive(frames: Array) -> Array:
	var loco := Loco7.new()
	var y_log := 165.0
	loco.setup(manifest, int(round(2.0 * y_log)))
	var out := []
	for fr in frames:
		if bool(fr["input"]):
			y_log += 140.0 * float(fr["dt"])
		var r := loco.tick(bool(fr["input"]), float(fr["dt"]), int(round(2.0 * y_log)))
		out.append({"input": bool(fr["input"]), "dt": float(fr["dt"]), "show_v8": bool(r["show_v8"]), "modes": r["modes"],
			"state": r["state"], "events": r["events"], "phase": r["phase"], "clock": loco.clock})
	out[-1]["settle_log"] = loco.settle_log.duplicate(true)
	return out


# =====================================================================================================================
# helpers for the v07 sweeps
func _plan_frames(dts: Array, inputs: Array) -> Array:
	var plan := []
	for i in dts.size():
		plan.append({"input": bool(inputs[i]), "dt": float(dts[i])})
	return plan


func _sum_ms(recs: Array, i0: int, i1: int) -> float:
	var t := 0.0
	for i in range(i0, i1 + 1):
		t += float(recs[i]["dt"]) * 1000.0
	return t


# re-press analysis shared by the captured and the simulated sweeps (recs: _drive ticks or _sim_drive records)
func _repress_facts(recs: Array, rp: int) -> Dictionary:
	var last_land := ""
	for i in range(1, rp):
		for ev in recs[i]["events"]:
			if String(ev[0]) == "land":
				last_land = String(ev[1])
	var next_land := ""
	var next_land_i := -1
	var first_lift := ""
	var first_lift_i := -1
	for i in range(rp, recs.size()):
		for s in ["vl", "vr"]:
			if first_lift == "" and String(recs[i - 1]["modes"][s]) == "contact" and String(recs[i]["modes"][s]) != "contact":
				first_lift = s
				first_lift_i = i
		for ev in recs[i]["events"]:
			if next_land == "" and String(ev[0]) == "land":
				next_land = String(ev[1])
				next_land_i = i
	return {"last_touchdown_before_repress": last_land, "next_touchdown_after_repress": next_land,
		"alternation_ok": last_land == "" or next_land != last_land,
		"first_boot_to_lift_after_repress": first_lift,
		"first_lift_ms_after_repress": _sum_ms(recs, rp, first_lift_i) - float(recs[rp]["dt"]) * 1000.0 if first_lift_i >= 0 else -1.0,
		"next_touchdown_ms_after_repress": _sum_ms(recs, rp, next_land_i) - float(recs[rp]["dt"]) * 1000.0 if next_land_i >= 0 else -1.0,
		"next_touchdown_index": next_land_i,
		"modes_at_repress": recs[rp - 1]["modes"], "showing_v8_at_repress": bool(recs[rp - 1]["show_v8"])}


# boot heights / modes / views around a tick (compact receipt rows)
func _feet_rows(recs: Array, i0: int, i1: int) -> Array:
	var rows := []
	for i in range(maxi(0, i0), mini(recs.size(), i1)):
		var r: Dictionary = recs[i]
		if bool(r.get("runtime_north", false)):
			rows.append([i, "runtime-north"])
			continue
		var row := [i, bool(r["input"]), bool(r["show_v8"])]
		for s in ["vl", "vr"]:
			var f: Dictionary = r["state"]["feet"][s]
			row.append([String(r["modes"][s]), int(f["o"]), int(f["lift"]), String(f["view"])])
		var ev := []
		for e in r["events"]:
			if String(e[0]) in ["land", "lift", "restart", "rise-lock", "release"]:
				ev.append(e.slice(0, 4))
		row.append(ev)
		rows.append(row)
	return rows


func _state_rows(ticks: Array, i0: int, i1: int) -> Array:
	var rows := []
	for i in range(maxi(0, i0), mini(ticks.size(), i1 + 1)):
		rows.append({"tick": i, "show_v8": bool(ticks[i]["show_v8"]), "modes": ticks[i]["modes"], "state": ticks[i]["state"]})
	return rows


# =====================================================================================================================
# v07 --sim=1: v06's deterministic gait-driver sweep (stops per frame rate + jitter, unchanged) plus the v07 re-press
# sweep: a re-press after 1..30 idle frames from EVERY frame of one stride at 14 frame rates, and mixed-frame-time
# re-presses (fixed seeds; dt drawn from {30, 45, 60, 144} fps and uniformly in [1/144, 1/30] s).  The same sweep runs
# with the rise lock off (--rise-lock=0 semantics, in-process) so the receipt carries the v06 counts next to v07's.
const SIM_GAPS := [1, 2, 3, 4, 5, 6, 8, 10, 15, 30]


func _sim_repress_sweep(lock: bool) -> Dictionary:
	manifest["restart"]["v07_rise_lock"] = lock
	var rows := {}
	var tot := {"cases": 0, "alternation_failures": 0, "rise_fault_frames": 0, "cases_with_rise_faults": 0, "locks": 0}
	var worst := []
	for fps in SIM_FPS:
		var dt := 1.0 / float(fps)
		var per_tick := 280.0 / float(fps)
		var first := int(ceil((float(SDM) + 8.0) / per_tick))
		var count := int(ceil(float(SDM) / per_tick))
		var r := {"cases": 0, "alternation_failures": 0, "rise_fault_frames": 0, "cases_with_rise_faults": 0, "locks": 0,
			"next_touchdown_ms": [], "first_lift_ms": []}
		for k in count:
			for gap in SIM_GAPS:
				var plan := [{"input": false, "dt": dt}]
				for i in first + k:
					plan.append({"input": true, "dt": dt})
				for i in gap:
					plan.append({"input": false, "dt": dt})
				for i in int(0.3 * fps):
					plan.append({"input": true, "dt": dt})
				var rec := _sim_drive(plan)
				var rp: int = first + k + 1 + gap
				var fx := _repress_facts(rec, rp)
				var rf := _rise_faults(rec)
				r["cases"] += 1
				r["alternation_failures"] += 0 if bool(fx["alternation_ok"]) else 1
				r["rise_fault_frames"] += rf.size()
				r["cases_with_rise_faults"] += 1 if not rf.is_empty() else 0
				r["locks"] += _locks_in(rec)
				(r["next_touchdown_ms"] as Array).append(float(fx["next_touchdown_ms_after_repress"]))
				(r["first_lift_ms"] as Array).append(float(fx["first_lift_ms_after_repress"]))
				if not rf.is_empty() and worst.size() < 12:
					worst.append({"fps": fps, "release_frame": first + k, "gap": gap, "faults": rf, "feet": _feet_rows(rec, rp - 2, rp + 4)})
		r["next_touchdown_ms"] = _sim_range(r["next_touchdown_ms"])
		r["first_lift_ms"] = _sim_range(r["first_lift_ms"])
		rows[str(fps)] = r
		for key in ["cases", "alternation_failures", "rise_fault_frames", "cases_with_rise_faults", "locks"]:
			tot[key] += int(r[key])
	# mixed frame times
	var jit := {"cases": 0, "alternation_failures": 0, "rise_fault_frames": 0, "cases_with_rise_faults": 0, "locks": 0,
		"raised_max_ms_after_release": 0.0}
	for mode in ["choice", "uniform"]:
		var rng := RandomNumberGenerator.new()
		rng.seed = 7071 if mode == "choice" else 7072
		for trial in 300:
			var dts := [1.0 / 60.0]
			var ins := [false]
			var n := 24 + rng.randi_range(0, 60)
			var gap := rng.randi_range(1, 10)
			for i in n + gap + 40:
				dts.append(JITTER_DTS[rng.randi_range(0, 3)] if mode == "choice" else rng.randf_range(1.0 / 144.0, 1.0 / 30.0))
				ins.append(i < n or i >= n + gap)
			var rec := _sim_drive(_plan_frames(dts, ins))
			var rp := n + 1 + gap
			var fx := _repress_facts(rec, rp)
			var rf := _rise_faults(rec)
			jit["cases"] += 1
			jit["alternation_failures"] += 0 if bool(fx["alternation_ok"]) else 1
			jit["rise_fault_frames"] += rf.size()
			jit["cases_with_rise_faults"] += 1 if not rf.is_empty() else 0
			jit["locks"] += _locks_in(rec)
	for key in ["cases", "alternation_failures", "rise_fault_frames", "cases_with_rise_faults", "locks"]:
		tot[key] += int(jit[key])
	manifest["restart"]["v07_rise_lock"] = rise_lock_on
	return {"rise_lock": lock, "totals": tot, "per_fps": rows, "jitter": jit, "examples_with_faults": worst}


func _sim7(out_abs: String, stamp: String, uid: String) -> void:
	var report := {"purpose": "v07 deterministic gait-driver sweep (state level, no pixels, no scene): v06's stop sweep per frame rate and jitter (unchanged rules), plus re-press from every frame of one stride x gaps 1..30 at 14 frame rates and 600 mixed-frame-time re-presses, with the v07 rise lock on and (comparison) off",
		"art_approved": false, "human_reviewed": false, "runtime_integrated": false, "fps": {}, "jitter": {}}
	var ok := true
	manifest["restart"]["v07_rise_lock"] = rise_lock_on
	for fps in SIM_FPS:
		var dt := 1.0 / float(fps)
		var per_tick := 280.0 / float(fps)
		var first := int(ceil((float(SDM) + 8.0) / per_tick))
		var count := int(ceil(float(SDM) / per_tick))
		var stops := []
		var faults := 0
		for k in count:
			var plan := [{"input": false, "dt": dt}]
			for i in first + k:
				plan.append({"input": true, "dt": dt})
			for i in int(0.6 * fps):
				plan.append({"input": false, "dt": dt})
			var rec := _sim_drive(plan)
			faults += _rise_faults(rec).size()
			var sr := _sim_stop(rec, first + k + 1)
			if sr.has("error"):
				ok = false
				continue
			stops.append(sr)
		var v8s := stops.map(func(e): return e["v8_ms"])
		var raised := stops.map(func(e): return e["raised_max_ms"])
		report["fps"][str(fps)] = {"stops": stops.size(), "release_to_v8_ms": _sim_range(v8s),
			"feet_down_ms": _sim_range(stops.map(func(e): return e["feet_down_ms"])),
			"post_contact_to_v8_ms": _sim_range(stops.map(func(e): return e["post_contact_ms"])),
			"raised_max_ms": raised.max(), "rise_fault_frames_in_walk_and_stop": faults, "per_stop_v8_ms": v8s}
		if faults > 0 or (fps >= 30 and float(raised.max()) > STOP_RAISED_LIMIT_MS + 1e-3):
			ok = false
		print("SIM7 %3d fps: %2d stops release->v8 %s ms raised max %.0f rise faults %d" % [fps, stops.size(),
			str(_sim_range(v8s).map(func(v): return snappedf(v, 0.1))), raised.max(), faults])
	# v06's jitter stop run (same seed 6061 and plan): the stop rules are unchanged, so these times must equal v06's
	var rng := RandomNumberGenerator.new()
	rng.seed = 6061
	var jit := []
	var jfaults := 0
	for trial in 24:
		var plan := [{"input": false, "dt": 1.0 / 60.0}]
		var n := 30 + rng.randi_range(0, 40)
		for i in n:
			plan.append({"input": true, "dt": 1.0 / float([30, 45, 60, 144][rng.randi_range(0, 3)])})
		for i in 40:
			plan.append({"input": false, "dt": 1.0 / float([30, 45, 60, 144][rng.randi_range(0, 3)])})
		var rec := _sim_drive(plan)
		jfaults += _rise_faults(rec).size()
		var sr := _sim_stop(rec, n + 1)
		if sr.has("error"):
			ok = false
			continue
		jit.append(sr)
	report["jitter"] = {"seed": 6061, "frame_rates_mixed": [30, 45, 60, 144], "stops": jit.size(),
		"release_to_v8_ms": _sim_range(jit.map(func(e): return e["v8_ms"])),
		"feet_down_ms": _sim_range(jit.map(func(e): return e["feet_down_ms"])),
		"raised_max_ms": jit.map(func(e): return e["raised_max_ms"]).max(), "rise_fault_frames": jfaults,
		"per_stop_v8_ms": jit.map(func(e): return e["v8_ms"]), "per_stop_feet_down_ms": jit.map(func(e): return e["feet_down_ms"])}
	ok = ok and jfaults == 0
	print("SIM7 jitter stops: %s ms raised max %.0f" % [str(report["jitter"]["release_to_v8_ms"]), report["jitter"]["raised_max_ms"]])
	var on := _sim_repress_sweep(true)
	var off := _sim_repress_sweep(false)
	report["repress_v07_rise_lock_on"] = on
	report["repress_v06_behaviour_rise_lock_off"] = off
	var t: Dictionary = on["totals"]
	ok = ok and int(t["alternation_failures"]) == 0 and int(t["rise_fault_frames"]) == 0
	print("SIM7 re-press (lock on):  %s" % str(t))
	print("SIM7 re-press (lock off): %s" % str(off["totals"]))
	report["gates_ok"] = ok
	var rname := "%s_gait-driver_protagonist-female-south-run-v07-sim-timing-receipt_%s_%s-%s.json" % [SLUG, VARIANT, stamp, uid]
	if out_abs != "":
		var f := FileAccess.open(out_abs.path_join(rname), FileAccess.WRITE)
		f.store_string(JSON.stringify(report, " ") + "\n")
		f.close()
		print("SIM7 RECEIPT " + rname)
	print("SIM7 " + ("PASS" if ok else "FAIL"))
	quit(0 if ok else 1)


# =====================================================================================================================
func _run() -> void:
	var sim := _user_arg("sim") == "1"
	rise_lock_on = _user_arg("rise-lock") != "0"
	if DisplayServer.get_name() == "headless" and not sim:
		_fail("windowed run required")
		return
	var motion_dir := _user_arg("motion-dir")
	if not sim and (motion_dir == "" or DirAccess.make_dir_recursive_absolute(motion_dir) != OK):
		_fail("pass -- --motion-dir=<absolute scratch dir>")
		return
	var only := _user_arg("only")
	var quick := _user_arg("quick") == "1"
	# ---------------------------------------------------------------- v07 amendment: parent tool + v06 manifest pinned
	var parent_path := (get_script() as Script).resource_path.get_base_dir().path_join(V06_TOOL_FILE)
	if _sha_text_lf(parent_path) != V06_TOOL_SHA256:
		_fail("v06 capture tool (the parent script) is not the pinned file")
		return
	var mpath := ASSET_DIR + MANIFEST
	var mdigest := _sha_text_lf(mpath)
	if mdigest != V06_MANIFEST_SHA256:
		_fail("v06 manifest is not the pinned file")
		return
	var apath := V07_DIR + V07_AMEND
	var adigest := _sha_text_lf(apath)
	amend = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path(apath)))
	manifest = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path(mpath)))
	for flag in V07_FLAGS:
		if bool(manifest[flag]) or bool(amend[flag]):
			_fail("manifest / amendment flag %s must stay false" % flag)
			return
	if String(amend["amends"]["manifest_sha256_text_lf_v1"]) != V06_MANIFEST_SHA256 or String(amend["amends"]["capture_tool_sha256_text_lf_v1"]) != V06_TOOL_SHA256:
		_fail("amendment does not pin the v06 manifest / tool")
		return
	manifest["restart"]["v07_rise_lock"] = bool(amend["restart_amendment"]["rise_lock"]) and rise_lock_on
	var disp: Dictionary = manifest["display"]
	if float(disp["scale"]) != 0.5 or int(disp["logical_height_px"]) != 48 or bool(disp["flip_h"]):
		_fail("display block is not 48 px / 0.5 / no flip")
		return
	shadow_alpha = float(disp["shadow"]["opacity"])
	SDM = int(manifest["gait"]["stride_px"])
	if sim:
		var sim_out := _user_arg("out-dir") if _user_arg("out-dir") != "" else ProjectSettings.globalize_path(OUTPUT_DIR)
		var sim_stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
		_sim7(sim_out, sim_stamp, "%08x" % (randi() & 0xffffffff))
		return
	var sources := {"manifest": {"path": mpath, "sha256_text_lf_v1": mdigest}, "amendment": {"path": apath, "sha256_text_lf_v1": adigest},
		"parent_capture_tool": {"path": "tools/" + V06_TOOL_FILE, "sha256_text_lf_v1": V06_TOOL_SHA256}}
	for e in manifest["parts"] + manifest["keyframes"]:
		if FileAccess.get_sha256(ProjectSettings.globalize_path(ASSET_DIR + String(e["file"]))) != String(e["sha256"]):
			_fail("%s sha256 mismatch" % String(e["file"]))
			return
	for e in manifest["keyframes"]:
		if FileAccess.get_sha256(ProjectSettings.globalize_path(ASSET_DIR + String(e["shadow_file"]))) != String(e["shadow_sha256"]):
			_fail("%s sha256 mismatch" % String(e["shadow_file"]))
			return
	if FileAccess.get_sha256(ProjectSettings.globalize_path(V8_PATH)) != V8_SHA256:
		_fail("v8 sha256 mismatch")
		return
	sources["v8"] = V8_SHA256
	sources["parts_count"] = (manifest["parts"] as Array).size()
	sources["keyframes_count"] = (manifest["keyframes"] as Array).size()
	v8_image = _load_rgba(V8_PATH)
	v8_tex = ImageTexture.create_from_image(v8_image)
	for y in range(8, 41):
		for x in 80:
			var c := v8_image.get_pixel(x, y)
			if c.a8 == 0:
				continue
			if y <= 28 and x >= 25:
				neck_head.append([Vector2i(x, y), c])
			elif y >= 36 and x >= 28 and x <= 44:
				neck_torso.append([Vector2i(x, y), c])
	comp = PartCompositor.new()
	var err := comp.load_parts(manifest["parts"], ASSET_DIR, manifest["rig"])
	if err != "":
		_fail(err)
		return
	for q in comp.parts["boot-vl-v8"]:
		v8_boot.get_or_add("vl", {})[q[0]] = q[1]
	for q in comp.parts["boot-vr-v8"]:
		v8_boot.get_or_add("vr", {})[q[0]] = q[1]
	var neutral := {"bob": 0, "hdy": 0, "sx": 0, "csx": 0, "arms": {"R": "N", "L": "N"},
		"feet": {"vl": {"o": 0, "lift": 0, "view": "v8", "kin": 0}, "vr": {"o": 0, "lift": 0, "view": "v8", "kin": 0}}}
	var nc := comp.compose(neutral)
	var v8_pad := Image.create_empty(80, 120, false, Image.FORMAT_RGBA8)
	v8_pad.blit_rect(v8_image, Rect2i(0, 0, 80, 112), Vector2i.ZERO)
	if (nc["image"] as Image).get_data() != v8_pad.get_data():
		_fail("GDScript neutral composition != v8")
		return
	v8_shadow_image = nc["shadow"]
	v8_shadow_tex = ImageTexture.create_from_image(v8_shadow_image)
	for k in manifest["keyframes"]:
		var c := comp.compose(k["state"])
		if c.has("error") or (c["image"] as Image).get_data() != _load_rgba(ASSET_DIR + String(k["file"])).get_data() \
				or (c["shadow"] as Image).get_data() != _load_rgba(ASSET_DIR + String(k["shadow_file"])).get_data():
			_fail("GDScript compositor != builder keyframe " + String(k["key"]))
			return
	var parity := {"neutral_equals_v8": true, "keyframes_and_shadows_equal_builder_pngs": (manifest["keyframes"] as Array).size()}
	print("PARITY neutral == v8, %d keyframes + shadows == builder PNGs" % parity["keyframes_and_shadows_equal_builder_pngs"])
	var per_px: Array = manifest["metrics"]["nominal_per_px"]
	var move_speeds := {}
	for sp in [AREA_SCRIPT, ANNEX_SCRIPT]:
		var ms: float = float((load(sp) as GDScript).get_script_constant_map().get("MOVE_SPEED", -1.0))
		if ms != 140.0:
			_fail("%s MOVE_SPEED %s" % [sp, str(ms)])
			return
		move_speeds[sp] = ms
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(1280, 720)
	var out_abs := _user_arg("out-dir") if _user_arg("out-dir") != "" else ProjectSettings.globalize_path(OUTPUT_DIR)
	var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var uid := "%08x" % (randi() & 0xffffffff)
	SaveStore.root_path = "user://test-saves/m8-south-run-v07-capture"
	app = root.get_node("AppState")
	var outputs := {}
	var report_scenes := {}
	var steady_checked := 0
	var all_faults := []          # [tag, frame, kind]
	var handoff_over := []        # [tag, handoff cell xor max, steady max]
	var total_locks := 0
	for scene_key in SCENES.keys():
		if only != "" and scene_key != only:
			continue
		var spec: Array = SCENES[scene_key]
		var sr := {"kind": spec[0], "destination": spec[1], "annex_room": spec[2], "note": spec[4], "walk": {}, "stops": {}, "repress": {},
			"repress_jitter": {}, "stop_jitter": {}}
		var su: Array
		# ---------------------------------------------------------------- runs at 30 / 60 / 144 fps (start from v8 idle + steady)
		var steady_xor := {}
		for mode in WALK_MODES.keys():
			var wm: Array = WALK_MODES[mode]
			su = await _setup(spec)
			if su.is_empty():
				return
			var start_y: float = su[1].position.y
			var ticks := await _drive(su, _plan_walk(int(wm[0]), int(wm[1])), "", "%s_%s" % [scene_key, mode], Rect2i())
			if ticks.is_empty():
				return
			var summ := _summ(ticks)
			var stats := _planted_stats(summ, 1, summ.size())
			if not _planted_ok(stats):
				_fail("%s %s planted boot moved in world space %s" % [scene_key, mode, str(stats)])
				return
			var sx_max := 0
			for i in ticks.size():
				var tk: Dictionary = ticks[i]
				if not bool(tk["input"]) or int(tk["dist"]) < int(manifest["gait"]["stride_px"]) * 3 / 2:
					continue
				sx_max = maxi(sx_max, int(summ[i].get("cell_silhouette_xor", 0)))
				var row: Dictionary = per_px[posmod(int(tk["phase"]), per_px.size())]
				var stt: Dictionary = tk["state"]
				var ok: bool = int(row["bob"]) == int(stt["bob"]) and int(row["sx"]) == int(stt["sx"]) \
					and row["arms"]["R"] == stt["arms"]["R"] and row["arms"]["L"] == stt["arms"]["L"]
				for s in ["vl", "vr"]:
					for f in ["o", "lift", "kin"]:
						ok = ok and int(row["feet"][s][f]) == int(stt["feet"][s][f])
					ok = ok and String(row["feet"][s]["view"]) == String(stt["feet"][s]["view"])
				if not ok:
					_fail("%s %s tick %d: steady gait %s != manifest per-px %s" % [scene_key, mode, int(tk["tick"]), str(stt), str(row)])
					return
				steady_checked += 1
			var rf := _rise_faults(ticks)
			for x in rf:
				all_faults.append(["%s_%s" % [scene_key, mode], x[0], x[1]])
			total_locks += _locks_in(ticks)
			var fps_w := int(wm[1])
			steady_xor[fps_w] = sx_max
			var start_xor := 0
			for i in range(1, mini(summ.size(), 1 + int(round(0.3 * fps_w)))):
				start_xor = maxi(start_xor, int(summ[i].get("cell_silhouette_xor", 0)))
			sr["walk"][mode] = {"ticks": ticks.size(), "logical_px_per_s_measured": (su[1].position.y - start_y) / (float(int(wm[0])) / float(wm[1])),
				"planted": {"pairs": stats["planted_tick_pairs"], "row_disp_max": stats["planted_sole_row_world_disp_max_px"],
					"texels_changed_same_view": stats["planted_boot_texels_changed_same_view"]},
				"cell_xor_max_whole_walk": stats["cell_silhouette_xor_max_per_tick"], "cell_xor_max_steady": sx_max,
				"cell_xor_max_first_300ms_start": start_xor, "floor_gap_rows_max": stats["floor_gap_rows_max"],
				"floor_gap_rows_mean": stats["floor_gap_rows_mean"], "rise_faults": rf, "rise_locks": _locks_in(ticks),
				"start_feet": _feet_rows(ticks, 0, 8)}
			print("RUN7 %s %s steady cell-xor max %d, start (300 ms) cell-xor max %d, rise faults %d, locks %d" % [scene_key, mode, sx_max, start_xor, rf.size(), _locks_in(ticks)])
			await _free(su[0])
		sr["steady_cell_xor_max_by_fps"] = steady_xor
		# ---------------------------------------------------------------- stops from every frame of one stride (v06 rules unchanged)
		var fps_list := [60, 30] if scene_key != "city-bright" else [60, 30, 144]
		if quick:
			fps_list = [30]
		for fps in fps_list:
			var dt: float = 1.0 / fps
			var per_tick_px: float = 280.0 / fps
			var first := int(ceil((float(SDM) + 8.0) / per_tick_px))
			var count := int(ceil(float(SDM) / per_tick_px))
			for k in range(0, count, 1 if not quick else 4):
				var n_walk: int = first + k
				su = await _setup(spec)
				if su.is_empty():
					return
				var plan := _plan_walk(n_walk, fps)
				for i in int(0.45 * fps):
					plan.append({"input": false, "dt": dt})
				var tag := "%s_stop-%dfps-%03d" % [scene_key, fps, n_walk]
				var save_motion: bool = fps == 30
				var crop := _crop_for(su, int(n_walk * per_tick_px) + 10) if save_motion else Rect2i()
				var ticks := await _drive(su, plan, motion_dir if save_motion else "", tag, crop)
				if ticks.is_empty():
					return
				var summ := _summ(ticks)
				var rel: int = n_walk + 1
				var ws := _planted_stats(summ, 1, rel)
				var ss := _planted_stats(summ, rel, summ.size())
				if not _planted_ok(ws) or not _planted_ok(ss):
					_fail("%s planted boot moved %s %s" % [tag, str(ws), str(ss)])
					return
				var rc := _release_checks(ticks, rel, dt)
				if rc.has("error"):
					_fail("%s: %s" % [tag, rc["error"]])
					return
				if int(rc["switch_to_v8_xor"]) != 0 or int(rc["settle"]["body_changes_per_tick_max_after_touchdown"]) > _change_limit(dt) \
						or not (rc["torso_or_arm_change_on_touchdown_tick"] as Array).is_empty():
					_fail("%s: stop checks %s" % [tag, str(rc)])
					return
				if (fps == 30 and float(rc["v8_after_ms"]) > STOP_V8_LIMIT_MS_30FPS + 1e-3) or (fps == 60 and float(rc["v8_after_ms"]) > STOP_V8_LIMIT_MS_60FPS + 1e-3):
					_fail("%s: release -> v8 %.1f ms over the limit" % [tag, float(rc["v8_after_ms"])])
					return
				for s in ["vl", "vr"]:
					if float(rc["raised_after_release"][s]["longest_raised_ms"]) > STOP_RAISED_LIMIT_MS:
						_fail("%s: boot %s raised %.0f ms after the release" % [tag, s, float(rc["raised_after_release"][s]["longest_raised_ms"])])
						return
				var rf := _rise_faults(ticks)
				for x in rf:
					all_faults.append([tag, x[0], x[1]])
				var v8_at: int = rc["v8_at"]
				sr["stops"][tag] = {"fps": fps, "release_tick": rel, "released_at_phase_px": posmod(int(ticks[rel - 1]["phase"]), SDM),
					"v8_after_ms": rc["v8_after_ms"], "release_to_at_rest_ms": rc["release_to_at_rest_ms"],
					"feet_down_ms_after_release": rc["settle"]["feet_down_ms_after_release"], "post_contact_to_v8_ms": rc["settle"]["post_contact_to_v8_ms"],
					"raised_after_release": rc["raised_after_release"], "body_changes_per_tick_max_after_touchdown": rc["settle"]["body_changes_per_tick_max_after_touchdown"],
					"stop_cell_xor_max": ss["cell_silhouette_xor_max_per_tick"], "rise_faults": rf,
					"states_release_to_v8": _state_rows(ticks, rel - 1, v8_at), "crop": [crop.position.x, crop.position.y, crop.size.x, crop.size.y]}
				print("STOP7 %s phase %d -> v8 %.1f ms (feet down %.1f) raised %.0f/%.0f faults %d" % [tag, sr["stops"][tag]["released_at_phase_px"],
					float(rc["v8_after_ms"]), float(rc["settle"]["feet_down_ms_after_release"]), float(rc["raised_after_release"]["vl"]["longest_raised_ms"]),
					float(rc["raised_after_release"]["vr"]["longest_raised_ms"]), rf.size()])
				await _free(su[0])
		# ---------------------------------------------------------------- re-press at every release phase of one stride x gaps
		# [fps, phase step, gaps, save frames, extra release frames inside the FIRST stride (v06's 30 fps defect case is
		# release frame 6; these also cover re-presses while the start step is still settling)]
		var rep_sets := []
		if scene_key == "city-bright":
			rep_sets = [[30, 1, [1, 2, 3, 4, 5, 7, 10, 15], true, [5, 6, 7, 8, 9]], [60, 1, [1, 2, 3, 5, 8, 14, 30], true, [8, 12, 16]],
				[144, 2, [1, 3, 7, 12, 19, 34], false, [20, 29, 38]]]
		else:
			rep_sets = [[30, 1, [1, 2, 4, 15], true, [6, 8]], [60, 2, [1, 3, 8], false, [12, 16]]]
		if quick:
			rep_sets = [[30, 1, [1, 4], true, [6]]]
		for rset in rep_sets:
			var rfps: int = rset[0]
			var dt := 1.0 / float(rfps)
			var per_tick_px: float = 280.0 / float(rfps)
			var first := int(ceil((float(SDM) + 8.0) / per_tick_px))
			var count := int(ceil(float(SDM) / per_tick_px))
			var limit: int = int(steady_xor.get(rfps, 0))
			var frames_rel: Array = (rset[4] as Array).duplicate()
			for k in range(0, count, int(rset[1])):
				frames_rel.append(first + k)
			for n_walk in frames_rel:
				for gap in rset[2]:
					su = await _setup(spec)
					if su.is_empty():
						return
					var plan := _plan_walk(n_walk, rfps)
					for i in gap:
						plan.append({"input": false, "dt": dt})
					for i in int(round(0.3 * rfps)):
						plan.append({"input": true, "dt": dt})
					for i in maxi(2, int(round(4.0 * rfps / 60.0))):
						plan.append({"input": false, "dt": dt})
					var tag := "%s_repress-%dfps-%03d-gap-%02d" % [scene_key, rfps, n_walk, gap]
					var crop := _crop_for(su, int((n_walk + int(round(0.3 * rfps))) * per_tick_px) + 10) if bool(rset[3]) else Rect2i()
					var full := {}
					var rel: int = n_walk + 1
					var rp: int = rel + gap
					if tag == DEFECT_CASE:
						for pk in [[rp - 1, "before-repress"], [rp, "repress-frame"]]:
							var nm := _out_name(scene_key, "diag-repress30-r%03d-g%02d-%s" % [n_walk, gap, pk[1]], stamp, uid, "png")
							full[int(pk[0])] = out_abs.path_join(nm)
							outputs[nm] = {"kind": "diagnostic-still", "scene": scene_key, "tick": int(pk[0]), "case": tag}
					var ticks := await _drive(su, plan, motion_dir if bool(rset[3]) else "", tag, crop, full)
					if ticks.is_empty():
						return
					var summ := _summ(ticks)
					var all_st := _planted_stats(summ, 1, summ.size())
					if not _planted_ok(all_st):
						_fail("%s planted boot moved %s" % [tag, str(all_st)])
						return
					var fx := _repress_facts(ticks, rp)
					if not bool(fx["alternation_ok"]):
						_fail("%s: re-press broke alternation %s" % [tag, str(fx)])
						return
					var rf := _rise_faults(ticks)
					for x in rf:
						all_faults.append([tag, x[0], x[1]])
					var rr := _planted_stats(summ, rp, mini(summ.size(), rp + int(round(0.2 * rfps))))
					var xs := []
					for i in range(rp, mini(summ.size(), rp + 3)):
						xs.append(int(summ[i].get("cell_silhouette_xor", 0)))
					# v07: per-frame pose change from the re-press through 200 ms; the HANDOFF window is the re-press frame up to
					# and including the next touchdown (gate: <= the steady run's per-frame maximum at this frame rate)
					var per_frame := []
					var handoff_max := 0
					var nti: int = int(fx["next_touchdown_index"])
					for i in range(rp, mini(summ.size(), rp + int(round(0.2 * rfps)) + 1)):
						var xv := int(summ[i].get("cell_silhouette_xor", 0))
						var kinds := []
						for ev in ticks[i]["events"]:
							kinds.append(String(ev[0]))
						per_frame.append([i - rp, xv, kinds, ticks[i]["state"]["arms"], summ[i]["sole_window_y"], summ[i]["pin_window_y"]])
						if nti >= 0 and i <= nti:
							handoff_max = maxi(handoff_max, xv)
					if handoff_max > limit:
						handoff_over.append([tag, handoff_max, limit])
					var locks := _locks_in(ticks)
					total_locks += locks
					var rec := fx.duplicate()
					rec.merge({"fps": rfps, "release_tick": rel, "repress_tick": rp, "gap_ticks": gap,
						"released_at_phase_px": posmod(int(ticks[rel - 1]["phase"]), SDM),
						"repress_200ms_cell_xor_max": int(rr["cell_silhouette_xor_max_per_tick"]), "cell_xor_repress_frame_and_next_2": xs,
						"steady_run_cell_xor_max_same_fps": limit, "within_steady_run_xor": int(rr["cell_silhouette_xor_max_per_tick"]) <= limit,
						"handoff_cell_xor_max": handoff_max, "handoff_within_steady_run_xor": handoff_max <= limit, "cell_xor_per_frame_200ms": per_frame,
						"floor_gap_rows_max_200ms": rr["floor_gap_rows_max"], "rise_faults": rf, "rise_locks": locks,
						"planted_pairs": all_st["planted_tick_pairs"], "feet": _feet_rows(ticks, rp - 2, rp + 6),
						"crop": [crop.position.x, crop.position.y, crop.size.x, crop.size.y]})
					sr["repress"][tag] = rec
					print("REPRESS7 %s phase %d: last down %s next down %s at %.1f ms, handoff cell-xor max %d, 200ms max %d (steady %d) frame xor %s faults %d locks %d" % [tag,
						rec["released_at_phase_px"], fx["last_touchdown_before_repress"], fx["next_touchdown_after_repress"],
						float(fx["next_touchdown_ms_after_repress"]), handoff_max, rec["repress_200ms_cell_xor_max"], limit, str(xs), rf.size(), locks])
					await _free(su[0])
		# ---------------------------------------------------------------- mixed frame times (city-bright): re-presses + stops
		if scene_key == "city-bright" and not quick:
			var rng := RandomNumberGenerator.new()
			rng.seed = 7073
			for trial in 24:
				# frame times: even trials draw from {30, 45, 60, 144} fps, odd trials uniformly in [1/144, 1/30] s.  Time budget
				# (keeps the hero inside the 720 px window): run 0.35..0.65 s, release for 1..8 frames, re-press for 0.3 s, then
				# release; the last 8 trials have no re-press (a full stop to v8 on mixed frame times)
				var stop_case := trial >= 16
				var dts := [1.0 / 60.0]
				var ins := [false]
				var walk_ms := rng.randf_range(350.0, 650.0)
				var gap := rng.randi_range(1, 8)
				var n := 0
				var t_ms := 0.0
				while t_ms < walk_ms:
					var d: float = JITTER_DTS[rng.randi_range(0, 3)] if trial % 2 == 0 else rng.randf_range(1.0 / 144.0, 1.0 / 30.0)
					dts.append(d)
					ins.append(true)
					t_ms += d * 1000.0
					n += 1
				var tail_ms := 0.0
				var k_tail := 0
				while (stop_case and k_tail < 60) or (not stop_case and (k_tail < gap or tail_ms < 300.0 or k_tail < gap + 4)):
					var d: float = JITTER_DTS[rng.randi_range(0, 3)] if trial % 2 == 0 else rng.randf_range(1.0 / 144.0, 1.0 / 30.0)
					var moving_now: bool = (not stop_case) and k_tail >= gap
					dts.append(d)
					ins.append(moving_now)
					if moving_now:
						tail_ms += d * 1000.0
					k_tail += 1
				for i in 4:
					dts.append(JITTER_DTS[rng.randi_range(0, 3)])
					ins.append(false)
				su = await _setup(spec)
				if su.is_empty():
					return
				var tag := "%s_jitter-%s-%02d" % [scene_key, "stop" if stop_case else "repress", trial]
				var crop := _crop_for(su, int((t_ms + tail_ms) * 0.28) + 20)
				var ticks := await _drive(su, _plan_frames(dts, ins), motion_dir, tag, crop)
				if ticks.is_empty():
					return
				var summ := _summ(ticks)
				var all_st := _planted_stats(summ, 1, summ.size())
				if not _planted_ok(all_st):
					_fail("%s planted boot moved %s" % [tag, str(all_st)])
					return
				var rf := _rise_faults(ticks)
				for x in rf:
					all_faults.append([tag, x[0], x[1]])
				var rel := n + 1
				if stop_case:
					var v8_at := -1
					for i in range(rel, ticks.size()):
						if bool(ticks[i]["show_v8"]):
							v8_at = i
							break
					if v8_at < 0 or _xor(ticks[v8_at]["meas"]["mask"], ticks[v8_at - 1]["meas"]["mask"]) != 0:
						_fail("%s: no clean return to v8" % tag)
						return
					var raised := 0.0
					for s in ["vl", "vr"]:
						var run := 0.0
						for i in range(rel, v8_at):
							run = run + float(ticks[i]["dt"]) * 1000.0 if String(ticks[i]["modes"][s]) != "contact" else 0.0
							raised = maxf(raised, run)
					sr["stop_jitter"][tag] = {"frames": dts.size(), "release_tick": rel, "v8_after_ms": _sum_ms(ticks, rel, v8_at),
						"raised_max_ms": raised, "rise_faults": rf, "dts_ms_release_to_v8": ticks.slice(rel, v8_at + 1).map(func(e): return snappedf(float(e["dt"]) * 1000.0, 0.01))}
					print("JITTER7 %s stop -> v8 %.1f ms raised max %.1f faults %d" % [tag, _sum_ms(ticks, rel, v8_at), raised, rf.size()])
				else:
					var rp := rel + gap
					var fx := _repress_facts(ticks, rp)
					if not bool(fx["alternation_ok"]):
						_fail("%s: re-press broke alternation %s" % [tag, str(fx)])
						return
					var rec := fx.duplicate()
					rec.merge({"frames": dts.size(), "release_tick": rel, "repress_tick": rp, "gap_ticks": gap, "rise_faults": rf,
						"rise_locks": _locks_in(ticks), "feet": _feet_rows(ticks, rp - 2, rp + 6),
						"dts_ms_around_repress": ticks.slice(maxi(0, rp - 3), mini(ticks.size(), rp + 6)).map(func(e): return snappedf(float(e["dt"]) * 1000.0, 0.01))})
					sr["repress_jitter"][tag] = rec
					print("JITTER7 %s re-press: next down %s at %.1f ms faults %d locks %d" % [tag, fx["next_touchdown_after_repress"],
						float(fx["next_touchdown_ms_after_repress"]), rf.size(), rec["rise_locks"]])
				total_locks += _locks_in(ticks)
				await _free(su[0])
		# ---------------------------------------------------------------- NORMAL-SPEED SHOWREELS at 60 and 30 fps (v06's segments)
		for reel_fps in ([] if quick else [60, 30]):
			su = await _setup(spec)
			if su.is_empty():
				return
			var dtr := 1.0 / float(reel_fps)
			var reel := []
			var segs := [["idle", 18], ["down", 36], ["idle", 3], ["down", 12], ["up", 24], ["down", 24], ["idle", 30], ["down", 10], ["idle", 30]]
			var seg_marks := []
			for sg in segs:
				var n_seg := maxi(1, int(round(float(sg[1]) * reel_fps / 60.0)))
				seg_marks.append([String(sg[0]), reel.size(), n_seg])
				for i in n_seg:
					reel.append({"input": String(sg[0]) != "idle", "dir": String(sg[0]) if String(sg[0]) != "idle" else "", "dt": dtr})
			var rtag := "%s_showreel-%dfps" % [scene_key, reel_fps]
			var rticks := await _drive(su, reel, motion_dir, rtag, Rect2i(0, 0, 1280, 720))
			if rticks.is_empty():
				return
			var rsumm := _summ(rticks)
			var rstats := _planted_stats(rsumm, 1, rsumm.size())
			if not _planted_ok(rstats):
				_fail("%s planted boot moved %s" % [rtag, str(rstats)])
				return
			var releases := []
			for i in range(1, rticks.size()):
				if bool(rticks[i - 1]["input"]) and not bool(rticks[i]["input"]):
					var rc := _release_checks(rticks, i, dtr)
					var interrupted: bool = rc.has("error")
					if not interrupted:
						if int(rc["switch_to_v8_xor"]) != 0 or int(rc["settle"]["body_changes_per_tick_max_after_touchdown"]) > _change_limit(dtr) \
								or not (rc["torso_or_arm_change_on_touchdown_tick"] as Array).is_empty() \
								or (reel_fps == 30 and float(rc["v8_after_ms"]) > STOP_V8_LIMIT_MS_30FPS + 1e-3) \
								or (reel_fps == 60 and float(rc["v8_after_ms"]) > STOP_V8_LIMIT_MS_60FPS + 1e-3):
							_fail("%s release at tick %d: %s" % [rtag, i, str(rc)])
							return
						for s in ["vl", "vr"]:
							if float(rc["raised_after_release"][s]["longest_raised_ms"]) > STOP_RAISED_LIMIT_MS:
								_fail("%s release at tick %d: boot %s raised too long" % [rtag, i, s])
								return
					releases.append({"release_tick": i, "released_at_phase_px": posmod(int(rticks[i - 1].get("phase", 0)), SDM),
						"interrupted_by_input_before_v8": interrupted, "v8_after_ms": -1.0 if interrupted else float(rc["v8_after_ms"]),
						"raised_after_release": {} if interrupted else rc["raised_after_release"]})
			var rf := _rise_faults(rticks)
			for x in rf:
				all_faults.append([rtag, x[0], x[1]])
			total_locks += _locks_in(rticks)
			var rframes := []
			for tk in rticks:
				rframes.append({"tick": tk["tick"], "dir": String(tk.get("dir", "")), "runtime_north": bool(tk.get("runtime_north", false)),
					"show_v8": bool(tk["show_v8"]), "pin_window": [int(round(float(tk["hero_logical"][0]) * 2.0)), int(tk["origin"].y) + PIN.y]})
			sr["showreel_%dfps" % reel_fps] = {"fps": reel_fps, "segments": seg_marks, "frames_dir_tag": rtag, "ticks": rticks.size(),
				"releases": releases, "rise_faults": rf, "rise_locks": _locks_in(rticks), "frames": rframes,
				"floor_gap_rows_max": rstats["floor_gap_rows_max"], "floor_gap_rows_mean": rstats["floor_gap_rows_mean"],
				"cell_xor_max": rstats["cell_silhouette_xor_max_per_tick"], "planted_pairs": rstats["planted_tick_pairs"],
				"note": "full 1280x720 window frames, one per %d fps tick (normal speed); runtime_north ticks show the scene's own runtime hero sprite (placeholder north walk), not the pilot" % reel_fps}
			print("SHOWREEL7 %s ticks %d releases %s faults %d locks %d" % [rtag, rticks.size(),
				str(releases.map(func(r): return [r["release_tick"], r["interrupted_by_input_before_v8"], r["v8_after_ms"]])), rf.size(), _locks_in(rticks)])
			await _free(su[0])
		# ---------------------------------------------------------------- reversal sweep at 60 fps (re-entry uses the start rule)
		var rev_first := int(ceil((float(SDM) + 8.0) / (280.0 / 60.0)))
		var rev_count := int(ceil(float(SDM) / (280.0 / 60.0)))
		sr["reversal"] = {}
		for k in range(0, rev_count, (3 if scene_key == "city-bright" else 6) if not quick else 99):
			var n_walk: int = rev_first + k
			su = await _setup(spec)
			if su.is_empty():
				return
			var dt := 1.0 / 60.0
			var plan := _plan_walk(n_walk, 60)
			for i in 12:
				plan.append({"input": true, "dir": "up", "dt": dt})
			for i in 24:
				plan.append({"input": true, "dir": "down", "dt": dt})
			for i in 30:
				plan.append({"input": false, "dt": dt})
			var tag := "%s_reversal-%03d" % [scene_key, n_walk]
			var ticks := await _drive(su, plan, "", tag, Rect2i())
			if ticks.is_empty():
				return
			var summ := _summ(ticks)
			if not _planted_ok(_planted_stats(summ, 1, summ.size())):
				_fail("%s planted boot moved" % tag)
				return
			var rel: int = n_walk + 1 + 12 + 24
			var rc := _release_checks(ticks, rel, dt)
			if rc.has("error") or int(rc["switch_to_v8_xor"]) != 0 or int(rc["settle"]["body_changes_per_tick_max_after_touchdown"]) > _change_limit(dt) \
					or not (rc["torso_or_arm_change_on_touchdown_tick"] as Array).is_empty():
				_fail("%s final stop %s" % [tag, str(rc)])
				return
			var rf := _rise_faults(ticks)
			for x in rf:
				all_faults.append([tag, x[0], x[1]])
			total_locks += _locks_in(ticks)
			sr["reversal"][tag] = {"final_stop_v8_after_ms": rc["v8_after_ms"], "rise_faults": rf, "rise_locks": _locks_in(ticks),
				"reentry_feet": _feet_rows(ticks, n_walk + 13, n_walk + 21)}
			print("REVERSAL7 %s final stop v8 %.0f ms faults %d" % [tag, float(rc["v8_after_ms"]), rf.size()])
			await _free(su[0])
		report_scenes[scene_key] = sr
	for nm in outputs:
		outputs[nm]["sha256_bytes"] = FileAccess.get_sha256(out_abs.path_join(nm))
	var report := {
		"project": "Worlds Between", "milestone": "M8",
		"purpose": "TEST-ONLY real-Godot captures of the UNAPPROVED / NONRUNTIME female SOUTH RUN motion pilot v07: v06 art, gait and stop with ONE control correction (re-press rise lock: a re-planned boot never rises while the other boot is off the floor), moved by the scenes' own _process at MOVE_SPEED 140; runs at 30 / 60 / 144 fps; stops from every frame of one stride (30 / 60 fps both scenes, 144 fps city-bright); re-press from every release phase (144 fps every 2nd) x several gaps; mixed-frame-time re-presses and stops; normal-speed showreels at 60 and 30 fps; reversal sweep",
		"status": "UNAPPROVED / NONRUNTIME; not art acceptance; Codex / creator visual decision pending",
		"art_approved": false, "human_reviewed": false, "runtime_integrated": false, "quick_debug_run": quick or only != "",
		"approved_scope_unchanged": "selout v8 SOUTH IDLE static frame and the 48 logical px display scale only",
		"capture_tool": "tools/" + (get_script() as Script).resource_path.get_file(), "rise_lock": bool(manifest["restart"]["v07_rise_lock"]),
		"renderer": "Godot %s windowed, viewport texture capture" % Engine.get_version_info()["string"],
		"canvas": [640, 360], "window": [1280, 720], "sprite_scale": 0.5, "filter": "nearest (CanvasItem.TEXTURE_FILTER_NEAREST)",
		"move_speed_logical_px_s": move_speeds, "sources": sources, "parity": parity, "steady_state_ticks_checked": steady_checked,
		"rise_faults_total": all_faults.size(), "rise_faults": all_faults, "rise_locks_total": total_locks,
		"handoff_over_steady_xor": handoff_over,
		"gates_passed": ["v06 parent tool + v06 manifest + v07 amendment pinned (sha256-text-lf-v1); part / keyframe / shadow PNG + v8 hash locks; flags false",
			"MOVE_SPEED 140; 1280x720; compositor == v8 (neutral) and == all builder keyframes and shadows; steady-state gait == manifest per-px table",
			"exact-RGB fidelity, neck shear 0, no seam fill on every captured tick (inherited _drive checks)",
			"planted boot: 0 px world displacement (row always; x / texels while the view holds) in every walk, stop, re-press, mixed-frame-time, showreel and reversal sequence",
			"every stop (30 / 60 / 144 fps sweeps, showreels, reversal finals, mixed-frame-time stops): 0-pixel switch to v8; v06 settle limits; 30 fps <= 233.3 ms and 60 fps <= 200 ms release -> v8; no boot raised > 100 ms (fixed-rate sweeps)",
			"every re-press (fixed-rate and mixed-frame-time): the next touchdown is the other boot"],
		"gate_rise_faults": "exit 1 if rise_faults_total > 0 (a frame on which both boots rise or both leave the floor)",
		"gate_handoff_xor": "exit 1 if any fixed-rate re-press has a frame between the re-press and the next touchdown whose pose change (cell silhouette XOR) exceeds the steady run's per-frame maximum at that frame rate in that scene",
		"outputs": outputs, "scenes": report_scenes,
	}
	var rname := "%s_city-annex_protagonist-female-south-run-v07-capture-receipt-h48_%s_%s-%s.json" % [SLUG, VARIANT, stamp, uid]
	var f := FileAccess.open(out_abs.path_join(rname), FileAccess.WRITE)
	f.store_string(JSON.stringify(report, " ") + "\n")
	f.close()
	print("RECEIPT " + rname)
	print("STAMP %s-%s" % [stamp, uid])
	if not all_faults.is_empty() or not handoff_over.is_empty():
		print("RUN_V07_CAPTURE FAIL: %d rise-fault frames %s; handoff over steady %s" % [all_faults.size(), str(all_faults.slice(0, 20)), str(handoff_over.slice(0, 20))])
		quit(1)
		return
	print("RUN_V07_CAPTURE PASS")
	quit(0)
