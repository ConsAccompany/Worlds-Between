extends "rpg-2-star-ocean-the-second_protagonist-female_south-run-v07-godot-capture_m8-w10_20261018-082500-8770ac39.gd"

# TEST-ONLY real-Godot capture of the UNAPPROVED / NONRUNTIME female SOUTH RUN v09 (m8-w12, single direction): ONE
# authored pose / gait revision over the v07 control candidate.  This script EXTENDS the v07 capture tool (same folder,
# byte-identical, hash checked) which extends the v06 tool; v06 art / manifest and the v07 amendment are read-only.
#   * Control is v07's, unchanged and state for state: the gait driver class (Loco7: v06 stop event clock + re-press
#     rule + v07 rise lock) runs on the v06 manifest's gait (swing keys and views included) with the v07 amendment.
#   * Art: Comp9 extends v06's PartCompositor and changes only what is DRAWN for a state (v09 manifest art_amendment):
#     a swing boot in "toe" at lift >= 2 is drawn as a heel KICK (authored boot-<side>-kick under the knee); "hang", and
#     "reach" at lift >= 2, as the TUCKED leg (thigh + authored forward knee 1:1, foreshortened shaded shin, knee in front
#     of the boot, thigh lean over the cuff); the coat hem (rows >= 66) trails the torso shift by the cape lag; single
#     see-through texels enclosed on four sides below the neck are closed with outline ink.  Every
#     other state is drawn by v06's rules.
#   * --art=v07 runs the SAME harness with PartCompositor (the v07 candidate) so the comparison showreels see identical
#     input sequences AND identical gait states; only the pixels differ.
# Gates (exit 1): pins (v06 tool / manifest, v07 tool / amendment, every v09 PNG vs the v09 manifest, v8); flags false;
# neutral == v8; GDScript Comp9 == the v09 builder's 12 keyframes + shadows; steady gait == the v09 per-px table;
# exact-RGB / neck-shear / seam checks on every captured tick (inherited _drive); planted boot 0 px in world space;
# every stop ends on the v8 PNG with a 0-pixel switch, 30 fps <= 233.3 ms, 60 fps <= 200 ms, no boot raised > 100 ms;
# re-press alternation; 0 frames on which both boots rise.  No fluidity is claimed from any of these numbers.
# Run windowed from an isolated copy whose paths fit MAX_PATH (Godot does not use \\?\ paths):
#   Godot_v4.7.2-stable_win64_console.exe --path <copy>/game -s <copy>/tools/<this file> -- --motion-dir=<abs> --out-dir=<abs> [--art=v07]
#   (add --headless and -- --sim=1 for the window-free gait-driver sweep)

const V07_TOOL_FILE := "rpg-2-star-ocean-the-second_protagonist-female_south-run-v07-godot-capture_m8-w10_20261018-082500-8770ac39.gd"
const V07_TOOL_SHA256 := "1be872365334ffe57c91d33d2ad805fb2eb3b425fc98cb55ce9b1edfa8f37836"
const V09_DIR := "res://assets/characters/run-v09-unapproved/"
const V09_MANIFEST_GLOB := "_pose-gait-manifest_unapproved_20261018-133700-"
const STOP_V8_LIMIT_MS_60 := 200.0

var m9: Dictionary
var art := "v09"


# =====================================================================================================================
class Comp9 extends PartCompositor:
	var knee_fwd := {}        # side -> {y: [[x, Color], ...]}
	var shade := {}           # Color html -> Color (shin one ramp step darker)
	var hem_row := 66
	var seam_row0 := 41
	var cur := {}

	func setup9(art9: Dictionary) -> void:
		hem_row = int(art9["coat_hem_row"])
		seam_row0 = int(art9["seam_row0"])
		for k in art9["shin_shade_rgb"]:
			shade[Color(String(k)).to_html(false)] = Color(String(art9["shin_shade_rgb"][k]))
		for side in ["vl", "vr"]:
			var rows := {}
			for p in parts["knee-%s-fwd" % side]:
				var y: int = p[0].y
				if not rows.has(y):
					rows[y] = []
				rows[y].append([p[0].x, p[1]])
			knee_fwd[side] = rows

	func _ext(xs: Array) -> Array:
		var a := 1 << 30
		var b := -(1 << 30)
		for x in xs:
			a = mini(a, int(x))
			b = maxi(b, int(x))
		return [a, b]

	# v09 state -> pose: "kick" (heel up behind), "tuck" (knee forward, shin tucked) or "" (v06 leg)
	static func draw_kind(foot: Dictionary) -> String:
		var v := String(foot["view"])
		var l := int(foot["lift"])
		if v == "toe" and l >= 2:
			return "kick"
		if v == "hang" or (v == "reach" and l >= 2):
			return "tuck"
		return ""

	func leg(side: String, bob: int, foot: Dictionary) -> Dictionary:
		var kind := draw_kind(foot)
		if kind == "":
			return super(side, bob, foot)
		var dy: int = int(foot["o"]) - int(foot["lift"])
		var boot := {}
		var bt := 1 << 30
		for p in parts["boot-%s-%s" % [side, "kick" if kind == "kick" else String(foot["view"])]]:
			var q: Vector2i = p[0] + Vector2i(0, dy)
			boot[q] = p[1]
			bt = mini(bt, q.y)
		var k0: int = knee[side][0]
		var k1: int = knee[side][1]
		var nT := k0 - hip
		var nK := k1 - k0 + 1
		var n := bt - (hip + bob)
		var ns := maxi(0, n - nT - nK)
		var sh := IM.pick(range(k1 + 1, boot_top), ns)
		var src: Dictionary = leg_rows[side]
		var cx := []
		for q in boot:
			if q.y == bt:
				cx.append(q.x)
		var cuff := _ext(cx)
		var kx := []
		for e in knee_fwd[side][k1]:
			kx.append(int(e[0]))
		var kb := _ext(kx)
		var align := IM.rdiv(int(cuff[0]) + int(cuff[1]) - int(kb[0]) - int(kb[1]), 2)
		var kd: int = int(foot["kin"]) * int(inward[side]) + IM.rdiv(align * maxi(0, 4 - ns), 4)
		var out := {}
		for q in boot:
			out[q] = boot[q]
		var y := hip + bob
		for i in nT:
			var dx := IM.rdiv(kd * i * i, (nT - 1) * (nT - 1))
			for e in src.get(hip + i, []):
				out[Vector2i(int(e[0]) + dx, y)] = e[1]
			y += 1
		for sy in range(k0, k1 + 1):
			for e in knee_fwd[side].get(sy, []):
				out[Vector2i(int(e[0]) + kd, y)] = e[1]
			y += 1
		if ns > 0:
			var sx0 := []
			for e in src.get(boot_top - 1, []):
				sx0.append(int(e[0]))
			var se := _ext(sx0)
			var end := IM.rdiv(int(cuff[0]) + int(cuff[1]) - int(se[0]) - int(se[1]), 2)
			for i in sh.size():
				var dx := kd + IM.rdiv((end - kd) * (i + 1), sh.size() + 1)
				for e in src.get(sh[i], []):
					var c: Color = e[1]
					out[Vector2i(int(e[0]) + dx, y)] = shade.get(c.to_html(false), c)
				y += 1
		return {"texels": out, "boot": boot, "sole": int(ground[side]) + dy, "hip_to_sole": int(ground[side]) + dy - (hip + bob) + 1,
			"trouser_rows": bt - (hip + bob)}

	func _put(g: Dictionary, role: String, dx: int, b: int) -> void:
		if role != "coat-skirt" or cur.is_empty() or int(cur["csx"]) == int(cur["sx"]):
			super(g, role, dx, b)
			return
		var csx: int = int(cur["csx"])
		for p in parts[role]:
			var q: Vector2i = p[0]
			g[q + Vector2i(csx if q.y >= hem_row else dx, b)] = p[1]

	func compose(state: Dictionary) -> Dictionary:
		cur = state
		var r := super(state)
		cur = {}
		if r.has("error"):
			return r
		# v09 see-through seam fill (builder compose9): enclosed transparent texels at rows >= seam_row0 -> ink
		var img: Image = r["image"]
		var fill := []
		for y in range(seam_row0, H - 1):
			for x in range(1, W - 1):
				if img.get_pixel(x, y).a8 == 0 and img.get_pixel(x - 1, y).a8 != 0 and img.get_pixel(x + 1, y).a8 != 0 						and img.get_pixel(x, y - 1).a8 != 0 and img.get_pixel(x, y + 1).a8 != 0:
					fill.append(Vector2i(x, y))
		for q in fill:
			img.set_pixelv(q, IM.INK)
		r["v09_seam_filled"] = fill.size()
		return r


# =====================================================================================================================
func _fail(reason: String) -> void:
	push_error("RUN_V09_CAPTURE FAIL: " + reason)
	print("RUN_V09_CAPTURE FAIL: " + reason)
	Input.action_release("move_up")
	Input.action_release("move_down")
	quit(1)


func _out_name(scene_key: String, what: String, stamp: String, uid: String, ext: String) -> String:
	var n := "%s_%s_female-south-run-%s-%s-h48_unapproved_%s-%s.%s" % [SLUG, scene_key, art, what, stamp, uid, ext]
	if n.length() > 140:
		push_error("output name too long (%d): %s" % [n.length(), n])
	return n


func _find_v09_manifest() -> String:
	var d := DirAccess.open(V09_DIR)
	if d == null:
		return ""
	for f in d.get_files():
		if V09_MANIFEST_GLOB in f and f.ends_with(".json"):
			return f
	return ""


# ---------------------------------------------------------------------------------------------------------------------
# pins, manifest assembly, compositor + parity
func _prepare() -> String:
	var tdir := (get_script() as Script).resource_path.get_base_dir()
	if _sha_text_lf(tdir.path_join(V07_TOOL_FILE)) != V07_TOOL_SHA256:
		return "v07 capture tool (parent script) is not the pinned file"
	if _sha_text_lf(tdir.path_join(V06_TOOL_FILE)) != V06_TOOL_SHA256:
		return "v06 capture tool is not the pinned file"
	var mpath := ASSET_DIR + MANIFEST
	if _sha_text_lf(mpath) != V06_MANIFEST_SHA256:
		return "v06 manifest is not the pinned file"
	amend = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path(V07_DIR + V07_AMEND)))
	manifest = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path(mpath)))
	var m9name := _find_v09_manifest()
	if m9name == "":
		return "v09 manifest not found"
	m9 = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path(V09_DIR + m9name)))
	m9["_file"] = m9name
	m9["_sha256_text_lf_v1"] = _sha_text_lf(V09_DIR + m9name)
	for flag in V07_FLAGS:
		if bool(manifest[flag]) or bool(amend[flag]) or bool(m9[flag]):
			return "flag %s must stay false" % flag
	if String(m9["amends"]["v06_manifest_sha256_text_lf_v1"]) != V06_MANIFEST_SHA256:
		return "v09 manifest does not pin the v06 manifest"
	manifest["restart"]["v07_rise_lock"] = bool(amend["restart_amendment"]["rise_lock"])
	SDM = int(manifest["gait"]["stride_px"])
	shadow_alpha = float(manifest["display"]["shadow"]["opacity"])
	for e in manifest["parts"]:
		if FileAccess.get_sha256(ProjectSettings.globalize_path(ASSET_DIR + String(e["file"]))) != String(e["sha256"]):
			return "%s sha256 mismatch" % String(e["file"])
	for e in m9["parts_new"]:
		if FileAccess.get_sha256(ProjectSettings.globalize_path(V09_DIR + String(e["file"]))) != String(e["sha256"]):
			return "%s sha256 mismatch" % String(e["file"])
	for e in m9["keyframes"]:
		for k in [["file", "sha256"], ["shadow_file", "shadow_sha256"]]:
			if FileAccess.get_sha256(ProjectSettings.globalize_path(V09_DIR + String(e[k[0]]))) != String(e[k[1]]):
				return "%s sha256 mismatch" % String(e[k[0]])
	if FileAccess.get_sha256(ProjectSettings.globalize_path(V8_PATH)) != V8_SHA256:
		return "v8 sha256 mismatch"
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
	if art == "v09":
		if JSON.stringify(m9["gait"]["swing_keys"]) != JSON.stringify(manifest["gait"]["swing_keys"]):
			return "v09 manifest says the gait is v07's, but its swing keys differ from the v06 manifest"
		var c9 := Comp9.new()
		var err := c9.load_parts(manifest["parts"], ASSET_DIR, manifest["rig"])
		if err == "":
			err = c9.load_parts(m9["parts_new"], V09_DIR, manifest["rig"])
		if err != "":
			return err
		c9.setup9(m9["art_amendment"])
		comp = c9
	else:
		comp = PartCompositor.new()
		var err2 := comp.load_parts(manifest["parts"], ASSET_DIR, manifest["rig"])
		if err2 != "":
			return err2
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
		return "neutral composition != v8"
	v8_shadow_image = nc["shadow"]
	v8_shadow_tex = ImageTexture.create_from_image(v8_shadow_image)
	var kf: Array = m9["keyframes"] if art == "v09" else manifest["keyframes"]
	var kdir := V09_DIR if art == "v09" else ASSET_DIR
	for k in kf:
		var c := comp.compose(k["state"])
		if c.has("error") or (c["image"] as Image).get_data() != _load_rgba(kdir + String(k["file"])).get_data() \
				or (c["shadow"] as Image).get_data() != _load_rgba(kdir + String(k["shadow_file"])).get_data():
			return "GDScript compositor != builder keyframe %s (%s)" % [String(k["key"]), art]
	print("PARITY9 %s: neutral == v8, %d keyframes + shadows == builder PNGs" % [art, kf.size()])
	return ""


func _per_px() -> Array:
	return m9["metrics"]["nominal_per_px"] if art == "v09" else manifest["metrics"]["nominal_per_px"]


# =====================================================================================================================
# --sim=1: state-level sweep of the v09 gait (v07 driver) at 14 frame rates + jitter; also the v07 swing keys through the
# same code for comparison.  Gates: rise faults 0, alternation, raised <= 100 ms, 30 fps <= 233.3 ms, 60 fps <= 200 ms.
func _sim_stops(keys: Array) -> Dictionary:
	manifest["gait"]["swing_keys"] = keys
	var out := {}
	var ok := true
	for fps in SIM_FPS:
		var dt := 1.0 / float(fps)
		var per_tick := 280.0 / float(fps)
		var first := int(ceil((float(SDM) + 8.0) / per_tick))
		var count := int(ceil(float(SDM) / per_tick))
		var v8s := []
		var raised := 0.0
		var faults := 0
		var over := []
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
			v8s.append(float(sr["v8_ms"]))
			raised = maxf(raised, float(sr["raised_max_ms"]))
			if float(sr["raised_max_ms"]) > STOP_RAISED_LIMIT_MS + 1e-3:
				over.append({"release_frame": first + k, "raised_max_ms": sr["raised_max_ms"], "feet": _feet_rows(rec, first + k - 1, first + k + 9)})
		var mx: float = v8s.max()
		if faults > 0 or (fps >= 30 and raised > STOP_RAISED_LIMIT_MS + 1e-3) or (fps == 30 and mx > STOP_V8_LIMIT_MS_30FPS + 1e-3) \
				or (fps == 60 and mx > STOP_V8_LIMIT_MS_60 + 1e-3):
			ok = false
		out[str(fps)] = {"release_to_v8_ms": _sim_range(v8s), "raised_max_ms": raised, "rise_faults": faults, "per_stop_v8_ms": v8s,
			"stops_raised_over_limit": over}
		for o in over:
			print("SIM9 raised over limit at %d fps: %s" % [fps, str(o)])
	var rng := RandomNumberGenerator.new()
	rng.seed = 6061
	var jit := []
	for trial in 24:
		var plan := [{"input": false, "dt": 1.0 / 60.0}]
		var n := 30 + rng.randi_range(0, 40)
		for i in n:
			plan.append({"input": true, "dt": 1.0 / float([30, 45, 60, 144][rng.randi_range(0, 3)])})
		for i in 40:
			plan.append({"input": false, "dt": 1.0 / float([30, 45, 60, 144][rng.randi_range(0, 3)])})
		var rec := _sim_drive(plan)
		var sr := _sim_stop(rec, n + 1)
		if not sr.has("error"):
			jit.append(float(sr["v8_ms"]))
	out["jitter_seed_6061"] = _sim_range(jit)
	out["_ok"] = ok
	return out


func _sim9(out_abs: String, stamp: String, uid: String) -> void:
	var keys: Array = manifest["gait"]["swing_keys"]
	var s9 := _sim_stops(keys)
	var rep := _sim_repress_sweep(true)
	var t: Dictionary = rep["totals"]
	var same_table := JSON.stringify(m9["metrics"]["nominal_per_px"].map(func(r): return [r["bob"], r["sx"], r["csx"], r["hdy"], r["arms"],
		[r["feet"]["vl"]["o"], r["feet"]["vl"]["lift"], r["feet"]["vl"]["view"], r["feet"]["vl"]["kin"]],
		[r["feet"]["vr"]["o"], r["feet"]["vr"]["lift"], r["feet"]["vr"]["view"], r["feet"]["vr"]["kin"]]])) == 		JSON.stringify(manifest["metrics"]["nominal_per_px"].map(func(r): return [r["bob"], r["sx"], r["csx"], r["hdy"], r["arms"],
		[r["feet"]["vl"]["o"], r["feet"]["vl"]["lift"], r["feet"]["vl"]["view"], r["feet"]["vl"]["kin"]],
		[r["feet"]["vr"]["o"], r["feet"]["vr"]["lift"], r["feet"]["vr"]["view"], r["feet"]["vr"]["kin"]]]))
	var ok: bool = bool(s9["_ok"]) and int(t["alternation_failures"]) == 0 and int(t["rise_fault_frames"]) == 0 and same_table
	for fps in ["24", "30", "48", "60", "144"]:
		print("SIM9 %s fps release->v8 %s raised max %.1f" % [fps, str(s9[fps]["release_to_v8_ms"]), float(s9[fps]["raised_max_ms"])])
	print("SIM9 jitter %s" % str(s9["jitter_seed_6061"]))
	print("SIM9 re-press totals %s" % str(t))
	print("SIM9 v09 per-px gait table == v06/v07 per-px table: %s" % str(same_table))
	var report := {"purpose": "v09 state-level gait-driver sweep (v07 driver and gait; v09 changes only the drawing): stops from every frame of one stride at 14 frame rates + seeded jitter, re-press sweep (every release frame x gaps 1..30 at 14 frame rates + 600 mixed-frame-time cases); per-px state table identical to v07's",
		"art_approved": false, "human_reviewed": false, "runtime_integrated": false,
		"v09_manifest": m9["_file"], "v09_manifest_sha256_text_lf_v1": m9["_sha256_text_lf_v1"],
		"gait_state_identical_to_v07": same_table, "stops": s9, "repress": rep, "gates_ok": ok}
	if out_abs != "":
		var rname := "%s_gait-driver_female-south-run-v09-sim-timing-receipt_unapproved_%s-%s.json" % [SLUG, stamp, uid]
		var f := FileAccess.open(out_abs.path_join(rname), FileAccess.WRITE)
		f.store_string(JSON.stringify(report, " ") + "\n")
		f.close()
		print("SIM9 RECEIPT " + rname)
	print("SIM9 " + ("PASS" if ok else "FAIL"))
	quit(0 if ok else 1)


# =====================================================================================================================
# captured sweeps (bounded): walks, stops, re-presses, reversals, showreels
func _stop_case(spec: Array, scene_key: String, fps: int, n_walk: int, motion_dir: String) -> Dictionary:
	var dt: float = 1.0 / fps
	var su: Array = await _setup(spec)
	if su.is_empty():
		return {"error": "setup"}
	var plan := _plan_walk(n_walk, fps)
	for i in int(0.45 * fps):
		plan.append({"input": false, "dt": dt})
	var tag := "%s_stop-%dfps-%03d" % [scene_key, fps, n_walk]
	var crop := _crop_for(su, int(n_walk * 280.0 / fps) + 10) if motion_dir != "" else Rect2i()
	var ticks: Array = await _drive(su, plan, motion_dir, tag, crop)
	await _free(su[0])
	if ticks.is_empty():
		return {"error": "drive"}
	var summ := _summ(ticks)
	var rel: int = n_walk + 1
	var ws := _planted_stats(summ, 1, rel)
	var ss := _planted_stats(summ, rel, summ.size())
	if not _planted_ok(ws) or not _planted_ok(ss):
		return {"error": "%s planted boot moved" % tag}
	var rc := _release_checks(ticks, rel, dt)
	if rc.has("error"):
		return {"error": "%s: %s" % [tag, rc["error"]]}
	if int(rc["switch_to_v8_xor"]) != 0 or int(rc["settle"]["body_changes_per_tick_max_after_touchdown"]) > _change_limit(dt) \
			or not (rc["torso_or_arm_change_on_touchdown_tick"] as Array).is_empty():
		return {"error": "%s: stop checks %s" % [tag, str(rc)]}
	if (fps == 30 and float(rc["v8_after_ms"]) > STOP_V8_LIMIT_MS_30FPS + 1e-3) or (fps == 60 and float(rc["v8_after_ms"]) > STOP_V8_LIMIT_MS_60 + 1e-3):
		return {"error": "%s: release -> v8 %.1f ms over the limit" % [tag, float(rc["v8_after_ms"])]}
	for s in ["vl", "vr"]:
		if float(rc["raised_after_release"][s]["longest_raised_ms"]) > STOP_RAISED_LIMIT_MS:
			return {"error": "%s: boot %s raised too long" % [tag, s]}
	return {"tag": tag, "fps": fps, "released_at_phase_px": posmod(int(ticks[rel - 1]["phase"]), SDM), "v8_after_ms": rc["v8_after_ms"],
		"feet_down_ms_after_release": rc["settle"]["feet_down_ms_after_release"], "raised_after_release": rc["raised_after_release"],
		"stop_cell_xor_max": ss["cell_silhouette_xor_max_per_tick"], "rise_faults": _rise_faults(ticks),
		"states_release_to_v8": _state_rows(ticks, rel - 1, int(rc["v8_at"]))}


func _repress_case(spec: Array, scene_key: String, fps: int, n_walk: int, gap: int, limit: int) -> Dictionary:
	var dt := 1.0 / float(fps)
	var su: Array = await _setup(spec)
	if su.is_empty():
		return {"error": "setup"}
	var plan := _plan_walk(n_walk, fps)
	for i in gap:
		plan.append({"input": false, "dt": dt})
	for i in int(round(0.3 * fps)):
		plan.append({"input": true, "dt": dt})
	for i in maxi(2, int(round(4.0 * fps / 60.0))):
		plan.append({"input": false, "dt": dt})
	var tag := "%s_repress-%dfps-%03d-gap-%02d" % [scene_key, fps, n_walk, gap]
	var ticks: Array = await _drive(su, plan, "", tag, Rect2i())
	await _free(su[0])
	if ticks.is_empty():
		return {"error": "drive"}
	var summ := _summ(ticks)
	if not _planted_ok(_planted_stats(summ, 1, summ.size())):
		return {"error": "%s planted boot moved" % tag}
	var rel: int = n_walk + 1
	var rp: int = rel + gap
	var fx := _repress_facts(ticks, rp)
	if not bool(fx["alternation_ok"]):
		return {"error": "%s: alternation %s" % [tag, str(fx)]}
	var nti: int = int(fx["next_touchdown_index"])
	var handoff_max := 0
	var per_frame := []
	for i in range(rp, mini(summ.size(), rp + int(round(0.2 * fps)) + 1)):
		var xv := int(summ[i].get("cell_silhouette_xor", 0))
		per_frame.append(xv)
		if nti >= 0 and i <= nti:
			handoff_max = maxi(handoff_max, xv)
	var rec := fx.duplicate()
	rec.merge({"tag": tag, "fps": fps, "gap_ticks": gap, "released_at_phase_px": posmod(int(ticks[rel - 1]["phase"]), SDM),
		"rise_faults": _rise_faults(ticks), "rise_locks": _locks_in(ticks), "handoff_cell_xor_max": handoff_max,
		"steady_cell_xor_max_same_fps": limit, "cell_xor_per_frame_200ms": per_frame, "feet": _feet_rows(ticks, rp - 2, rp + 6)})
	return rec


const REEL_SEGS := [["idle", 18], ["down", 36], ["idle", 3], ["down", 12], ["up", 24], ["down", 24], ["idle", 30], ["down", 10], ["idle", 30]]


func _showreel(spec: Array, scene_key: String, fps: int, motion_dir: String) -> Dictionary:
	var su: Array = await _setup(spec)
	if su.is_empty():
		return {"error": "setup"}
	var dtr := 1.0 / float(fps)
	var reel := []
	var marks := []
	for sg in REEL_SEGS:
		var n_seg := maxi(1, int(round(float(sg[1]) * fps / 60.0)))
		marks.append([String(sg[0]), reel.size(), n_seg])
		for i in n_seg:
			reel.append({"input": String(sg[0]) != "idle", "dir": String(sg[0]) if String(sg[0]) != "idle" else "", "dt": dtr})
	var rtag := "%s_%s_showreel-%dfps" % [art, scene_key, fps]
	var rticks: Array = await _drive(su, reel, motion_dir, rtag, Rect2i(0, 0, 1280, 720))
	await _free(su[0])
	if rticks.is_empty():
		return {"error": "drive"}
	var rsumm := _summ(rticks)
	if not _planted_ok(_planted_stats(rsumm, 1, rsumm.size())):
		return {"error": "%s planted boot moved" % rtag}
	var releases := []
	for i in range(1, rticks.size()):
		if bool(rticks[i - 1]["input"]) and not bool(rticks[i]["input"]):
			var rc := _release_checks(rticks, i, dtr)
			var interrupted: bool = rc.has("error")
			if not interrupted and art == "v09":
				if int(rc["switch_to_v8_xor"]) != 0 or (fps == 30 and float(rc["v8_after_ms"]) > STOP_V8_LIMIT_MS_30FPS + 1e-3) \
						or (fps == 60 and float(rc["v8_after_ms"]) > STOP_V8_LIMIT_MS_60 + 1e-3):
					return {"error": "%s release at tick %d: %s" % [rtag, i, str(rc)]}
			releases.append({"release_tick": i, "released_at_phase_px": posmod(int(rticks[i - 1].get("phase", 0)), SDM),
				"interrupted_by_input_before_v8": interrupted, "v8_after_ms": -1.0 if interrupted else float(rc["v8_after_ms"]),
				"v8_at_tick": -1 if interrupted else int(rc["v8_at"])})
	var frames := []
	for tk in rticks:
		var row := {"tick": tk["tick"], "input": bool(tk["input"]), "dir": String(tk.get("dir", "")), "runtime_north": bool(tk.get("runtime_north", false)),
			"show_v8": bool(tk.get("show_v8", false))}
		if not bool(tk.get("runtime_north", false)):
			row["modes"] = tk["modes"]
			row["state"] = tk["state"]
			row["events"] = (tk["events"] as Array).map(func(e): return e.slice(0, 3))
		frames.append(row)
	var xs := []
	for e in rsumm:
		xs.append(int(e.get("cell_silhouette_xor", 0)))
	return {"tag": rtag, "fps": fps, "scene": scene_key, "segments": marks, "ticks": rticks.size(), "releases": releases,
		"rise_faults": _rise_faults(rticks), "rise_locks": _locks_in(rticks), "cell_xor_per_tick": xs, "frames": frames,
		"note": "full 1280x720 window frames, one per %d fps tick, normal speed; runtime_north ticks show the scene's own runtime hero (placeholder north walk), not pilot art" % fps}


func _run() -> void:
	var sim := _user_arg("sim") == "1"
	art = _user_arg("art") if _user_arg("art") != "" else "v09"
	if not (art in ["v07", "v09"]):
		_fail("--art must be v07 or v09")
		return
	var err := _prepare()
	if err != "":
		_fail(err)
		return
	var out_abs := _user_arg("out-dir") if _user_arg("out-dir") != "" else ProjectSettings.globalize_path(OUTPUT_DIR)
	var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var uid := "%08x" % (randi() & 0xffffffff)
	if sim:
		_sim9(out_abs, stamp, uid)
		return
	if DisplayServer.get_name() == "headless":
		_fail("windowed run required")
		return
	var motion_dir := _user_arg("motion-dir")
	if motion_dir == "" or DirAccess.make_dir_recursive_absolute(motion_dir) != OK:
		_fail("pass -- --motion-dir=<absolute scratch dir>")
		return
	var reels_only := _user_arg("reels-only") == "1"
	for sp in [AREA_SCRIPT, ANNEX_SCRIPT]:
		if float((load(sp) as GDScript).get_script_constant_map().get("MOVE_SPEED", -1.0)) != 140.0:
			_fail("%s MOVE_SPEED is not 140" % sp)
			return
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(1280, 720)
	SaveStore.root_path = "user://test-saves/m8-south-run-v09-capture"
	app = root.get_node("AppState")
	var report := {"project": "Worlds Between", "milestone": "M8", "art": art,
		"purpose": "TEST-ONLY real-Godot capture, female SOUTH RUN %s through the v09 harness (v07 control driver); %s" % [art,
			"v09 authored pose / gait revision" if art == "v09" else "v07 candidate (v06 art + v06 swing keys) for the same-input comparison"],
		"status": "UNAPPROVED / NONRUNTIME; not art acceptance; Codex / creator visual decision pending",
		"art_approved": false, "human_reviewed": false, "runtime_integrated": false,
		"renderer": "Godot %s windowed, viewport texture capture" % Engine.get_version_info()["string"],
		"canvas": [640, 360], "window": [1280, 720], "sprite_scale": 0.5,
		"capture_tool": "tools/" + (get_script() as Script).resource_path.get_file(),
		"v09_manifest": m9["_file"], "v09_manifest_sha256_text_lf_v1": m9["_sha256_text_lf_v1"], "scenes": {}}
	var all_faults := []
	var steady_checked := 0
	var per_px := _per_px()
	for scene_key in SCENES.keys():
		var spec: Array = SCENES[scene_key]
		var sr := {}
		var steady := {}
		if not reels_only:
			# ---------------------------------------------------------------- walks (start from v8 idle + steady)
			sr["walk"] = {}
			for mode in WALK_MODES.keys():
				var wm: Array = WALK_MODES[mode]
				var su: Array = await _setup(spec)
				if su.is_empty():
					return
				var ticks: Array = await _drive(su, _plan_walk(int(wm[0]), int(wm[1])), "", "%s_%s" % [scene_key, mode], Rect2i())
				await _free(su[0])
				if ticks.is_empty():
					return
				var summ := _summ(ticks)
				var stats := _planted_stats(summ, 1, summ.size())
				if not _planted_ok(stats):
					_fail("%s %s planted boot moved" % [scene_key, mode])
					return
				var sx_max := 0
				for i in ticks.size():
					var tk: Dictionary = ticks[i]
					if not bool(tk["input"]) or int(tk["dist"]) < SDM * 3 / 2:
						continue
					sx_max = maxi(sx_max, int(summ[i].get("cell_silhouette_xor", 0)))
					var row: Dictionary = per_px[posmod(int(tk["phase"]), per_px.size())]
					var stt: Dictionary = tk["state"]
					var ok: bool = int(row["bob"]) == int(stt["bob"]) and int(row["sx"]) == int(stt["sx"])
					for s in ["vl", "vr"]:
						for f in ["o", "lift", "kin"]:
							ok = ok and int(row["feet"][s][f]) == int(stt["feet"][s][f])
						ok = ok and String(row["feet"][s]["view"]) == String(stt["feet"][s]["view"])
					if not ok:
						_fail("%s %s tick %d: steady gait != %s per-px table" % [scene_key, mode, int(tk["tick"]), art])
						return
					steady_checked += 1
				var rf := _rise_faults(ticks)
				for x in rf:
					all_faults.append(["%s_%s" % [scene_key, mode], x[0], x[1]])
				steady[int(wm[1])] = sx_max
				sr["walk"][mode] = {"ticks": ticks.size(), "planted_pairs": stats["planted_tick_pairs"],
					"planted_row_disp_max": stats["planted_sole_row_world_disp_max_px"], "cell_xor_max_steady": sx_max,
					"floor_gap_rows_max": stats["floor_gap_rows_max"], "floor_gap_rows_mean": stats["floor_gap_rows_mean"],
					"rise_faults": rf, "start_feet": _feet_rows(ticks, 0, 8)}
				print("WALK9 %s %s %s steady cell-xor max %d floor gap max %d mean %.2f faults %d" % [art, scene_key, mode, sx_max,
					int(stats["floor_gap_rows_max"]), float(stats["floor_gap_rows_mean"]), rf.size()])
			# ---------------------------------------------------------------- stops (every frame of one stride at 30 fps; 60 fps every 2nd)
			sr["stops"] = {}
			for fs in ([[30, 1], [60, 2]] if scene_key == "city-bright" else [[30, 1]]):
				var fps: int = fs[0]
				var per_tick_px: float = 280.0 / fps
				var first := int(ceil((float(SDM) + 8.0) / per_tick_px))
				var count := int(ceil(float(SDM) / per_tick_px))
				for k in range(0, count, int(fs[1])):
					var r: Dictionary = await _stop_case(spec, scene_key, fps, first + k, "")
					if r.has("error"):
						_fail(String(r["error"]))
						return
					for x in r["rise_faults"]:
						all_faults.append([r["tag"], x[0], x[1]])
					sr["stops"][r["tag"]] = r
					print("STOP9 %s %s phase %d -> v8 %.1f ms (feet down %.1f) raised %.0f/%.0f" % [art, r["tag"], int(r["released_at_phase_px"]),
						float(r["v8_after_ms"]), float(r["feet_down_ms_after_release"]), float(r["raised_after_release"]["vl"]["longest_raised_ms"]),
						float(r["raised_after_release"]["vr"]["longest_raised_ms"])])
			# ---------------------------------------------------------------- re-press (30 fps every phase x gaps 1 / 3; 60 fps every 2nd x gap 1)
			sr["repress"] = {}
			for rs in [[30, 1, [1, 3]], [60, 2, [1]]]:
				var rfps: int = rs[0]
				var per_tick_px: float = 280.0 / float(rfps)
				var first := int(ceil((float(SDM) + 8.0) / per_tick_px))
				var count := int(ceil(float(SDM) / per_tick_px))
				var limit: int = int(steady.get(rfps, 0))
				for k in range(0, count, int(rs[1])):
					for gap in rs[2]:
						var r: Dictionary = await _repress_case(spec, scene_key, rfps, first + k, gap, limit)
						if r.has("error"):
							_fail(String(r["error"]))
							return
						for x in r["rise_faults"]:
							all_faults.append([r["tag"], x[0], x[1]])
						sr["repress"][r["tag"]] = r
				print("REPRESS9 %s %s %d fps: %d cases" % [art, scene_key, rfps, sr["repress"].size()])
			# ---------------------------------------------------------------- reversal (60 fps, every 6th phase; north = runtime placeholder)
			sr["reversal"] = {}
			var rev_first := int(ceil((float(SDM) + 8.0) / (280.0 / 60.0)))
			var rev_count := int(ceil(float(SDM) / (280.0 / 60.0)))
			for k in range(0, rev_count, 6):
				var n_walk: int = rev_first + k
				var su: Array = await _setup(spec)
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
				var ticks: Array = await _drive(su, plan, "", tag, Rect2i())
				await _free(su[0])
				if ticks.is_empty():
					return
				if not _planted_ok(_planted_stats(_summ(ticks), 1, ticks.size())):
					_fail("%s planted boot moved" % tag)
					return
				var rc := _release_checks(ticks, n_walk + 1 + 12 + 24, dt)
				if rc.has("error") or int(rc["switch_to_v8_xor"]) != 0:
					_fail("%s final stop %s" % [tag, str(rc)])
					return
				var rf := _rise_faults(ticks)
				for x in rf:
					all_faults.append([tag, x[0], x[1]])
				sr["reversal"][tag] = {"final_stop_v8_after_ms": rc["v8_after_ms"], "rise_faults": rf, "reentry_feet": _feet_rows(ticks, n_walk + 13, n_walk + 21)}
			print("REVERSAL9 %s %s %d cases" % [art, scene_key, sr["reversal"].size()])
		# ---------------------------------------------------------------- normal-speed showreel: bright 30 fps, dark 60 fps
		var reel_fps := 30 if scene_key == "city-bright" else 60
		var rr: Dictionary = await _showreel(spec, scene_key, reel_fps, motion_dir)
		if rr.has("error"):
			_fail(String(rr["error"]))
			return
		for x in rr["rise_faults"]:
			all_faults.append([rr["tag"], x[0], x[1]])
		sr["showreel"] = rr
		print("SHOWREEL9 %s ticks %d releases %s faults %d" % [rr["tag"], int(rr["ticks"]),
			str((rr["releases"] as Array).map(func(r): return [r["release_tick"], r["interrupted_by_input_before_v8"], r["v8_after_ms"]])), (rr["rise_faults"] as Array).size()])
		report["scenes"][scene_key] = sr
	report["steady_state_ticks_checked"] = steady_checked
	report["rise_faults_total"] = all_faults.size()
	report["rise_faults"] = all_faults
	report["reels_only"] = reels_only
	var rname := "%s_city-annex_female-south-run-%s-capture-receipt-h48_unapproved_%s-%s.json" % [SLUG, art, stamp, uid]
	var f := FileAccess.open(out_abs.path_join(rname), FileAccess.WRITE)
	f.store_string(JSON.stringify(report, " ") + "\n")
	f.close()
	print("RECEIPT " + rname)
	print("STAMP %s-%s" % [stamp, uid])
	if not all_faults.is_empty():
		print("RUN_V09_CAPTURE FAIL: %d rise-fault frames %s" % [all_faults.size(), str(all_faults.slice(0, 10))])
		quit(1)
		return
	print("RUN_V09_CAPTURE PASS (%s)" % art)
	quit(0)
