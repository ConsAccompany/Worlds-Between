extends "rpg-2-star-ocean-the-second_female-south-run-v10-godot-capture_m8-w13_20261018-143213-ed496e32.gd"

# TEST-ONLY real-Godot capture of the UNAPPROVED / NONRUNTIME female SOUTH RUN v10r1 (m8-w14, single direction): ONE
# bounded amendment of v10.  This script EXTENDS the v10 capture tool (same folder, hash checked); v10's art, manifest,
# tools and evidence are read-only and preserved.
#   * Gait: the v10r1 manifest (same 128 px stride / 44 px stance / 4.375 steps/s / 68.75 % contact; land +8, lift-off
#     -36; re-authored swing keys) replaces v06's gait / stop / restart in memory.  Compositor: v10's Comp10, unchanged.
#   * Loco10r1 = Loco10 with ONE stop change (manifest stop.v10r1_landing_rule): after a release, landing boots move on
#     their own event clock - a landing boot's mid-key view change is no longer held back by the other boot's change;
#     only touchdowns are staggered (never two on one frame; the later boot keeps its last in-air key and lands on the
#     next frame).  v06's no-pose-skip, the shuffle and the body settle are unchanged.  stagger=false runs v10's rule
#     through the same code (sim comparison only).
#   * Planted gate: a planted boot whose every texel keeps its world position and RGB (the capture equals the composite
#     exactly on every tick) is not slipping, even when the coat / folded leg / hips cover part or all of it (the rear
#     boot at -36 sits behind the hips); such pairs are counted (occlusion-only, fully hidden) in the receipt.
# Gates (exit 1): pins (v06 / v07 / v09 / v10 tools, v06 / v10 manifests, every PNG, v8); flags false; neutral == v8;
# Comp10 == the r1 builder's 16 keyframes + shadows and all 128 per-px composites; steady gait == the r1 per-px table;
# planted boot 0 px; every stop ends on the v8 PNG with a 0-pixel switch; release -> v8 <= 250 ms at 30 / 60 fps and
# <= 300 ms with mixed frame times; EVERY boot down <= 100 ms after release at every constant rate >= 30 fps AND in every
# mixed-frame-time stop (the 24 existing seed-6061 cases plus 600 more); re-press alternation; 0 both-rise frames.
# 24 fps is recorded, not gated.  No fluidity is claimed from any of these numbers.
#   Godot_v4.7.2-stable_win64_console.exe --path <copy>/game -s <copy>/tools/<this file> -- --motion-dir=<abs> --out-dir=<abs>
#   (add --headless and -- --sim=1 for the window-free gait-driver sweep)

const V10_TOOL_FILE := "rpg-2-star-ocean-the-second_female-south-run-v10-godot-capture_m8-w13_20261018-143213-ed496e32.gd"
const V10_TOOL_SHA256 := "52ff5ffdf35c8572ef5e971ac59138dda8f65911ce63558972103b9bf1c68101"
const R1_DIR := "res://assets/characters/run-v10r1-unapproved/"
const R1_MANIFEST_GLOB := "_gait-pose-manifest_unapproved_20261018-142136-"
const RAISED_GATE_MS := 100.0

var stagger_on := true


# =====================================================================================================================
class Loco10r1 extends Loco10:
	var stagger := true

	func _stop_step(y: int, dt: float) -> void:
		var landed_now := false
		var moving_feet := 0
		var prop := {}
		for s in ["vl", "vr"]:
			var f: Dictionary = feet[s]
			if f["mode"] == "land" or f["mode"] == "shuffle":
				var u := _move_u(f)
				prop[s] = {"land": true} if u >= 1000 else {"land": false, "pose": IM.interp_keys(f["keys"], u), "u": u}
		if not stagger:
			# v06 / v10 rule (comparison runs only): at most one boot changes its view per tick, the other holds
			var changers0 := []
			for s in prop:
				var nv0 := "v8" if bool(prop[s]["land"]) else String(prop[s]["pose"]["view"])
				if nv0 != String(feet[s]["view"]):
					changers0.append(s)
			if changers0.size() == 2:
				var hold: String = changers0[1]
				if bool(prop[changers0[1]]["land"]) and not bool(prop[changers0[0]]["land"]):
					hold = changers0[0]
				prop.erase(hold)
				feet[hold]["t0"] = float(feet[hold]["t0"]) + minf(dt * 1000.0, hold_ms)
				events.append(["hold-one-tick", hold])
		else:
			# v10r1 landing rule: landing boots keep their own clock (a mid-key view change is not held back by the other
			# boot); only TOUCHDOWNS are staggered - the boot whose touchdown is due first (tie: earlier move start, then
			# vl) lands, the other keeps its last in-air key (u 999) and touches down on the next frame
			var landers := []
			for s in prop:
				if bool(prop[s]["land"]):
					landers.append(s)
			if landers.size() == 2:
				var a: String = landers[0]
				var b: String = landers[1]
				var da := float(feet[a]["t0"]) + float(feet[a]["dur"])
				var db := float(feet[b]["t0"]) + float(feet[b]["dur"])
				var keep := a
				if db < da - 1e-6 or (absf(db - da) <= 1e-6 and float(feet[b]["t0"]) < float(feet[a]["t0"]) - 1e-6):
					keep = b
				var later := b if keep == a else a
				prop[later] = {"land": false, "pose": IM.interp_keys(feet[later]["keys"], 999), "u": 999}
				events.append(["touchdown-staggered", later])
		var changers := []
		for s in prop:
			var nv := "v8" if bool(prop[s]["land"]) else String(prop[s]["pose"]["view"])
			if nv != String(feet[s]["view"]):
				changers.append(s)
		var boot_changed := not changers.is_empty()
		for s in ["vl", "vr"]:
			var f: Dictionary = feet[s]
			if f["mode"] == "land" or f["mode"] == "shuffle":
				if not prop.has(s):
					moving_feet += 1
				elif bool(prop[s]["land"]):
					_land_contact(s, y, 0)
					landed_now = true
				else:
					_set_pose(f, prop[s]["pose"])
					f["seg"] = maxi(int(f["seg"]), 1 if int(prop[s]["u"]) >= 500 else 0)
					moving_feet += 1
		if moving_feet == 0 and not landed_now:
			var cand := ""
			for s in ["vl", "vr"]:
				if feet[s]["mode"] == "contact" and int(feet[s]["wo"]) != y:
					if cand == "" or int(feet[s]["wo"]) - y < int(feet[cand]["wo"]) - y:
						cand = s
			if cand != "":
				feet[cand]["o"] = int(feet[cand]["wo"]) - y
				# the shuffle starts at the previous frame (the frame that showed the touchdown), as in v05
				_start_move(cand, "shuffle", prev_clock)
				var f: Dictionary = feet[cand]
				var u := _move_u(f)
				_set_pose(f, IM.interp_keys(f["keys"], u))
				f["seg"] = 1 if u >= 500 else 0
				moving_feet = 1
				boot_changed = true
		# v06 settle on the EVENT CLOCK.  The frame that shows the last touchdown is the settle origin: the dip lands with it
		# (the weight arrives with the boot) and nothing else changes on that frame, so the boot visibly lands first.  Then
		# v05's order, each change at an event time: the hair catches up the dip at its bob time + stop_hair_lag_ms; each
		# torso step, then each arm step, then the dip release at least settle_gap_ms after the previous change (arm steps
		# also arm_step_ms apart, the dip release also settle_ms after the origin); the hair follows the dip release by
		# stop_hair_lag_ms.  A frame applies every change whose event time has passed (at most one when the frame is not
		# longer than settle_gap_ms).  While a boot is still moving: the body keeps its release height, the torso leans
		# over the boot that carries the weight, and the arms step only on ticks where no boot changes its view and the
		# torso does not move (v05).
		var all_spot := moving_feet == 0
		var planted := ""
		for s in ["vl", "vr"]:
			all_spot = all_spot and feet[s]["mode"] == "contact" and int(feet[s]["wo"]) == y
			if feet[s]["mode"] == "contact":
				planted = s if planted == "" else "both"
		if all_spot:
			if settle_t < 0.0:
				settle_t = clock
				ev_t = clock
				if bob != 1:
					bob = 1
					bob_evt = clock
					hair_due = clock + float(st["stop_hair_lag_ms"])
				settle_log.append([clock, "origin", clock])
			else:
				_settle_events()
		else:
			bob = stop_bob
			var sx0 := sx
			if planted == "vl" or planted == "vr":
				_step_sx(-int(inward[planted]))
			# v05: an arm step only on a frame where no boot changes and the torso does not move.  v06: a frame longer than
			# settle_gap_ms (30 fps) spans two 60 fps frames, so it may carry an arm step next to ONE boot or torso change
			var others := (1 if boot_changed else 0) + (1 if sx != sx0 else 0)
			if (others == 0 or (multi_ok and others == 1)) and _arm_step_due():
				_arm_step()



func _prepare() -> String:
	art = "v10r1"
	var tdir := (get_script() as Script).resource_path.get_base_dir()
	if _sha_text_lf(tdir.path_join(V10_TOOL_FILE)) != V10_TOOL_SHA256:
		return "v10 capture tool (parent script) is not the pinned file"
	if _sha_text_lf(tdir.path_join(V09_TOOL_FILE)) != V09_TOOL_SHA256:
		return "v09 capture tool (parent script) is not the pinned file"
	if _sha_text_lf(tdir.path_join(V07_TOOL_FILE)) != V07_TOOL_SHA256:
		return "v07 capture tool is not the pinned file"
	if _sha_text_lf(tdir.path_join(V06_TOOL_FILE)) != V06_TOOL_SHA256:
		return "v06 capture tool is not the pinned file"
	var mpath := ASSET_DIR + MANIFEST
	if _sha_text_lf(mpath) != V06_MANIFEST_SHA256:
		return "v06 manifest is not the pinned file"
	amend = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path(V07_DIR + V07_AMEND)))
	manifest = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path(mpath)))
	var m9name := _find_v09_manifest()
	var m10name := _find_r1_manifest()
	var v10name := _find_v10_manifest()
	if m9name == "" or m10name == "" or v10name == "":
		return "v09 / v10 / v10r1 manifest not found"
	m9 = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path(V09_DIR + m9name)))
	m10 = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path(R1_DIR + m10name)))
	m10["_file"] = m10name
	m10["_sha256_text_lf_v1"] = _sha_text_lf(R1_DIR + m10name)
	if String(m10["parent"]["v10_manifest_sha256_text_lf_v1"]) != _sha_text_lf(V10_DIR + v10name):
		return "v10r1 manifest does not pin the current v10 manifest (parent)"
	# the inherited v09 receipt fields read m9["_file"]; they name the v10 manifest here
	m9["_file"] = m10name
	m9["_sha256_text_lf_v1"] = m10["_sha256_text_lf_v1"]
	for flag in V07_FLAGS:
		if bool(manifest[flag]) or bool(amend[flag]) or bool(m9[flag]) or bool(m10[flag]):
			return "flag %s must stay false" % flag
	if String(m10["based_on"]["v09_manifest_sha256_text_lf_v1"]) != _sha_text_lf(V09_DIR + m9name):
		return "v10 manifest does not pin the current v09 manifest"
	# v10 control: the v10 gait / stop / restart replace v06's in memory (the v06 manifest file is read-only)
	manifest["gait"] = m10["gait"]
	manifest["stop"] = m10["stop"]
	manifest["restart"] = m10["restart"]
	stagger_on = m10["stop"].has("v10r1_landing_rule")
	manifest["restart"]["v07_rise_lock"] = bool(amend["restart_amendment"]["rise_lock"]) and bool(m10["restart"]["v07_rise_lock"])
	SDM = int(manifest["gait"]["stride_px"])
	shadow_alpha = float(manifest["display"]["shadow"]["opacity"])
	for pair in [[manifest["parts"], ASSET_DIR], [m9["parts_new"], V09_DIR], [m10["parts_new"], V10_DIR]]:
		for e in pair[0]:
			if FileAccess.get_sha256(ProjectSettings.globalize_path(String(pair[1]) + String(e["file"]))) != String(e["sha256"]):
				return "%s sha256 mismatch" % String(e["file"])
	for e in m10["keyframes"]:
		for k in [["file", "sha256"], ["shadow_file", "shadow_sha256"]]:
			if FileAccess.get_sha256(ProjectSettings.globalize_path(R1_DIR + String(e[k[0]]))) != String(e[k[1]]):
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
	var c10 := Comp10.new()
	var err := c10.load_parts(manifest["parts"], ASSET_DIR, manifest["rig"])
	if err == "":
		err = c10.load_parts(m9["parts_new"], V09_DIR, manifest["rig"])
	if err == "":
		err = c10.load_parts(m10["parts_new"], V10_DIR, manifest["rig"])
	if err != "":
		return err
	c10.setup9(m9["art_amendment"])
	c10.setup10(m10["leg_rule"], int(m10["island_max_texels"]))
	comp = c10
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
	for k in m10["keyframes"]:
		var c := comp.compose(k["state"])
		if c.has("error") or (c["image"] as Image).get_data() != _load_rgba(R1_DIR + String(k["file"])).get_data() \
				or (c["shadow"] as Image).get_data() != _load_rgba(R1_DIR + String(k["shadow_file"])).get_data():
			return "GDScript Comp10 != v10r1 builder keyframe %s" % String(k["key"])
	var bad := []
	for row in m10["metrics"]["nominal_per_px"]:
		var c := comp.compose(row)
		if c.has("error") or _composite_sha(c) != String(row["composite_sha256"]):
			bad.append(int(row["phase_px"]))
	if not bad.is_empty():
		return "GDScript Comp10 != builder per-px composites at phases %s" % str(bad.slice(0, 12))
	print("PARITY10R1: neutral == v8, %d keyframes + shadows == builder PNGs, %d per-px composites == builder sha256" % [
		m10["keyframes"].size(), m10["metrics"]["nominal_per_px"].size()])
	return ""


func _drive(su: Array, plan: Array, motion_dir: String, tag: String, crop: Rect2i, full_saves: Dictionary = {}) -> Array:
	var host: Node2D = su[0]
	var hero: Sprite2D = su[1]
	var ground_off: float = su[3]
	var bg: Image = su[4]
	var loco := _new_loco()
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
			loco = _new_loco()
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


func _find_r1_manifest() -> String:
	var d := DirAccess.open(R1_DIR)
	if d == null:
		return ""
	for f in d.get_files():
		if R1_MANIFEST_GLOB in f and f.ends_with(".json"):
			return f
	return ""


func _new_loco() -> Loco10r1:
	var l := Loco10r1.new()
	l.stagger = stagger_on
	return l


func _sim_drive(frames: Array) -> Array:
	var loco := _new_loco()
	var y_log := 165.0
	loco.setup(manifest, int(round(2.0 * y_log)))
	var out := []
	for fr in frames:
		if bool(fr["input"]):
			y_log += 140.0 * float(fr["dt"])
		var r := loco.tick(bool(fr["input"]), float(fr["dt"]), int(round(2.0 * y_log)))
		out.append({"input": bool(fr["input"]), "dt": float(fr["dt"]), "show_v8": bool(r["show_v8"]), "modes": r["modes"],
			"state": r["state"], "events": r["events"], "phase": r["phase"], "dist": r["dist"], "clock": loco.clock, "bob_skips": loco.bob_skips})
	out[-1]["settle_log"] = loco.settle_log.duplicate(true)
	return out


# v10r1 planted gate: same-view pairs with every boot texel unchanged in world position + RGB are occlusion, not slip
func _planted_stats(summ: Array, from_i: int, to_i: int) -> Dictionary:
	var st: Dictionary = super(summ, from_i, to_i)
	var row_max := 0
	var x_max := 0
	var occl := 0
	var hidden := 0
	for i in range(maxi(1, from_i), mini(summ.size(), to_i)):
		var e: Dictionary = summ[i]
		if bool(e.get("runtime_north", false)):
			continue
		for s in e.get("planted", {}):
			var p: Dictionary = e["planted"][s]
			var lost: int = maxi(int(p["boot_texels_now"]), int(p["boot_texels_prev"])) - int(p["boot_texels_same_world_pos_and_rgb"])
			var xd := maxi(absi(int(p["sole_x0_d"])), absi(int(p["sole_x1_d"])))
			if not bool(p["view_changed"]) and lost == 0:
				if xd != 0 or int(p["sole_row_d"]) != 0:
					occl += 1
				if int(p["boot_texels_visible_now"]) == 0:
					hidden += 1
				continue
			row_max = maxi(row_max, absi(int(p["sole_row_d"])))
			if not bool(p["view_changed"]):
				x_max = maxi(x_max, xd)
	st["planted_sole_row_visible_change_max_px"] = st["planted_sole_row_world_disp_max_px"]
	st["planted_sole_row_world_disp_max_px"] = row_max
	st["planted_sole_x_world_disp_max_px_same_view"] = x_max
	st["planted_pairs_visible_extent_changed_by_occlusion_only"] = occl
	st["planted_pairs_boot_fully_hidden"] = hidden
	return st


# =====================================================================================================================
# --sim=1: the r1 gait through Loco10r1 (and, for comparison only, the same gait through v10's landing rule)
func _mixed_plan(rng: RandomNumberGenerator, mode: String, n_extra: int) -> Array:
	var plan := [{"input": false, "dt": 1.0 / 60.0}]
	var n := 30 + rng.randi_range(0, n_extra)
	for i in n:
		plan.append({"input": true, "dt": (1.0 / float([30, 45, 60, 144][rng.randi_range(0, 3)])) if mode == "choice" else rng.randf_range(1.0 / 144.0, 1.0 / 30.0)})
	for i in 40:
		plan.append({"input": false, "dt": (1.0 / float([30, 45, 60, 144][rng.randi_range(0, 3)])) if mode == "choice" else rng.randf_range(1.0 / 144.0, 1.0 / 30.0)})
	return [plan, n]


func _mixed_set(seed_v: int, mode: String, trials: int, n_extra: int) -> Dictionary:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_v
	var v8s := []
	var raised := []
	var downs := []
	var worst := []
	var errors := 0
	var faults := 0
	for trial in trials:
		var pn: Array = _mixed_plan(rng, mode, n_extra)
		var rec := _sim_drive(pn[0])
		faults += _rise_faults(rec).size()
		var sr := _sim_stop(rec, int(pn[1]) + 1)
		if sr.has("error"):
			errors += 1
			continue
		v8s.append(float(sr["v8_ms"]))
		raised.append(float(sr["raised_max_ms"]))
		downs.append(float(sr["feet_down_ms"]))
		if float(sr["raised_max_ms"]) > RAISED_GATE_MS + 1e-3 and worst.size() < 6:
			worst.append({"trial": trial, "raised_max_ms": sr["raised_max_ms"], "v8_ms": sr["v8_ms"],
				"feet": _feet_rows(rec, int(pn[1]), int(pn[1]) + 8),
				"dts_ms": rec.slice(int(pn[1]), int(pn[1]) + 8).map(func(r): return snappedf(float(r["dt"]) * 1000.0, 0.1))})
	var over := raised.filter(func(v): return float(v) > RAISED_GATE_MS + 1e-3).size()
	return {"seed": seed_v, "mode": mode, "trials": trials, "errors": errors, "rise_faults": faults,
		"release_to_v8_ms": _sim_range(v8s), "raised_max_ms": raised.max() if not raised.is_empty() else -1.0,
		"stops_raised_over_100ms": over, "all_feet_down_ms": _sim_range(downs), "examples_over": worst}


func _sim_stops_r1() -> Dictionary:
	var out := {}
	var ok := true
	for fps in SIM_FPS:
		var dt := 1.0 / float(fps)
		var per_tick := 280.0 / float(fps)
		var first := int(ceil((float(SDM) + 8.0) / per_tick))
		var count := int(ceil(float(SDM) / per_tick))
		var v8s := []
		var downs := []
		var raised := 0.0
		var faults := 0
		var errors := 0
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
				errors += 1
				continue
			v8s.append(float(sr["v8_ms"]))
			downs.append(float(sr["feet_down_ms"]))
			raised = maxf(raised, float(sr["raised_max_ms"]))
		var gated: bool = int(fps) >= 30
		var row_ok := errors == 0 and faults == 0
		if gated:
			row_ok = row_ok and raised <= RAISED_GATE_MS + 1e-3
		if fps == 30 or fps == 60:
			row_ok = row_ok and float(v8s.max()) <= V10_LIMIT_MS + 1e-3
		ok = ok and (row_ok or not gated)
		out[str(fps)] = {"gated": gated, "release_to_v8_ms": _sim_range(v8s), "raised_max_ms": raised, "all_feet_down_ms": _sim_range(downs),
			"rise_faults": faults, "errors": errors, "per_stop_v8_ms": v8s, "gates_ok": row_ok}
	var existing := _mixed_set(6061, "choice", 24, 40)
	var more_c := _mixed_set(8081, "choice", 300, 60)
	var more_u := _mixed_set(8082, "uniform", 300, 60)
	for m in [existing, more_c, more_u]:
		m["gates_ok"] = int(m["errors"]) == 0 and int(m["rise_faults"]) == 0 and int(m["stops_raised_over_100ms"]) == 0 \
			and float(m["release_to_v8_ms"][1]) <= V10_LIMIT_MIXED_MS + 1e-3
		ok = ok and bool(m["gates_ok"])
	out["mixed_existing_seed_6061"] = existing
	out["mixed_extra_seed_8081_choice"] = more_c
	out["mixed_extra_seed_8082_uniform"] = more_u
	out["_ok"] = ok
	return out


func _sim_r1(out_abs: String, stamp: String, uid: String) -> void:
	var s1 := _sim_stops_r1()
	# comparison only: the same r1 gait through v10's landing rule (one view change per frame, the other boot held)
	stagger_on = false
	var cmp := {"mixed_existing_seed_6061": _mixed_set(6061, "choice", 24, 40), "mixed_extra_seed_8081_choice": _mixed_set(8081, "choice", 300, 60),
		"mixed_extra_seed_8082_uniform": _mixed_set(8082, "uniform", 300, 60)}
	stagger_on = true
	var rep := _sim_repress_sweep(true)
	var t: Dictionary = rep["totals"]
	var steady := {}
	var steady_ok := true
	for fps in [30, 60, 144]:
		var sd := _sim_steady(fps)
		steady[str(fps)] = sd
		steady_ok = steady_ok and int(sd["state_mismatches_vs_per_px"]) == 0 and int(sd["ticks_checked"]) > 0 \
			and float(sd["measured_steps_per_s"]) >= 4.0 and float(sd["measured_steps_per_s"]) <= 4.5
	var ok: bool = bool(s1["_ok"]) and int(t["alternation_failures"]) == 0 and int(t["rise_fault_frames"]) == 0 and steady_ok
	for fps in ["24", "30", "48", "60", "144"]:
		print("SIMR1 %s fps release->v8 %s raised max %.1f all feet down %s" % [fps, str(s1[fps]["release_to_v8_ms"]), float(s1[fps]["raised_max_ms"]),
			str(s1[fps]["all_feet_down_ms"])])
	for k in ["mixed_existing_seed_6061", "mixed_extra_seed_8081_choice", "mixed_extra_seed_8082_uniform"]:
		print("SIMR1 %s: v8 %s raised max %.1f over-100 %d | v10 rule: raised max %.1f over-100 %d" % [k, str(s1[k]["release_to_v8_ms"]),
			float(s1[k]["raised_max_ms"]), int(s1[k]["stops_raised_over_100ms"]), float(cmp[k]["raised_max_ms"]), int(cmp[k]["stops_raised_over_100ms"])])
	print("SIMR1 steady %s" % str(steady.values().map(func(d): return [d["fps"], d["measured_steps_per_s"], d["state_mismatches_vs_per_px"]])))
	print("SIMR1 re-press totals %s" % str(t))
	var report := {"purpose": "v10r1 state-level gait-driver sweep (Loco10r1: v10 driver + staggered-touchdown landing rule; r1 gait): steady state vs the per-px table and measured cadence; stops from every frame of one stride at 14 frame rates; mixed-frame-time stops (the 24 existing seed-6061 cases + 600 more), each gated per stop; the same mixed sets through v10's landing rule for comparison; re-press sweep",
		"art_approved": false, "human_reviewed": false, "runtime_integrated": false,
		"v10r1_manifest": m10["_file"], "v10r1_manifest_sha256_text_lf_v1": m10["_sha256_text_lf_v1"],
		"limits": {"release_to_v8_ms_30_60fps": V10_LIMIT_MS, "release_to_v8_ms_mixed": V10_LIMIT_MIXED_MS,
			"every_boot_down_after_release_ms": RAISED_GATE_MS, "gated_rates": "every constant rate >= 30 fps and every mixed-frame-time stop; 24 fps recorded only"},
		"steady": steady, "stops": s1, "comparison_v10_landing_rule_same_gait": cmp, "repress": rep, "gates_ok": ok}
	if out_abs != "":
		var rname := "%s_gait-driver_female-south-run-v10r1-sim-timing-receipt_unapproved_%s-%s.json" % [SLUG, stamp, uid]
		var f := FileAccess.open(out_abs.path_join(rname), FileAccess.WRITE)
		f.store_string(JSON.stringify(report, " ") + "\n")
		f.close()
		print("SIMR1 RECEIPT " + rname)
	print("SIMR1 " + ("PASS" if ok else "FAIL"))
	quit(0 if ok else 1)


func _run() -> void:
	var sim := _user_arg("sim") == "1"
	var err := _prepare()
	if err != "":
		_fail(err)
		return
	var out_abs := _user_arg("out-dir") if _user_arg("out-dir") != "" else ProjectSettings.globalize_path(OUTPUT_DIR)
	var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var uid := "%08x" % (randi() & 0xffffffff)
	if sim:
		_sim_r1(out_abs, stamp, uid)
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
	SaveStore.root_path = "user://test-saves/m8-south-run-v10r1-capture"
	app = root.get_node("AppState")
	var report := {"project": "Worlds Between", "milestone": "M8", "art": art,
		"purpose": "TEST-ONLY real-Godot capture, female SOUTH RUN v10r1 bounded amendment of v10 (reach +8 / -36, re-authored swing, staggered-touchdown landing rule; Loco10r1 driver, Comp10 compositor)",
		"status": "UNAPPROVED / NONRUNTIME; not art acceptance; Root / creator visual decision pending",
		"art_approved": false, "human_reviewed": false, "runtime_integrated": false,
		"renderer": "Godot %s windowed, viewport texture capture" % Engine.get_version_info()["string"],
		"canvas_logical": [640, 360], "window_native": [1280, 720], "sprite_scale": 0.5,
		"limits": {"release_to_v8_ms": V10_LIMIT_MS, "raised_ms": STOP_RAISED_LIMIT_MS},
		"repress_reversal_sweep_note": "release window from %d px (half a stride + 8); city re-press / reversal cases start at y %d (navigation limit 305 would otherwise be crossed); walks, stops and showreels use the v07 / v09 starts" % [int(LATE_FIRST_PX), int(CITY_REPRESS_START_Y)],
		"capture_tool": "tools/" + (get_script() as Script).resource_path.get_file(),
		"v10r1_manifest": m10["_file"], "v10r1_manifest_sha256_text_lf_v1": m10["_sha256_text_lf_v1"],
		"parent_v10_manifest_sha256_text_lf_v1": m10["parent"]["v10_manifest_sha256_text_lf_v1"], "scenes": {}}
	var all_faults := []
	var steady_checked := 0
	var per_px := _per_px()
	for scene_key in SCENES.keys():
		var spec: Array = SCENES[scene_key]
		var sr := {}
		var steady := {}
		if not reels_only:
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
					_fail("%s %s planted boot moved %s" % [scene_key, mode, str(_planted_bad(summ))])
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
						_fail("%s %s tick %d: steady gait != v10 per-px table" % [scene_key, mode, int(tk["tick"])])
						return
					steady_checked += 1
				var rf := _rise_faults(ticks)
				for x in rf:
					all_faults.append(["%s_%s" % [scene_key, mode], x[0], x[1]])
				steady[int(wm[1])] = sx_max
				sr["walk"][mode] = {"ticks": ticks.size(), "planted_pairs": stats["planted_tick_pairs"],
					"planted_row_disp_max": stats["planted_sole_row_world_disp_max_px"],
					"planted_x_disp_max_same_view": stats["planted_sole_x_world_disp_max_px_same_view"],
					"planted_boot_texels_changed_same_view": stats["planted_boot_texels_changed_same_view"],
					"planted_pairs_visible_extent_changed_by_occlusion_only": stats["planted_pairs_visible_extent_changed_by_occlusion_only"],
					"planted_sole_x_visible_extent_change_max_px_same_view": stats["planted_sole_x_visible_extent_change_max_px_same_view"],
					"cell_xor_max_steady": sx_max, "head_step_max_px": stats["head_step_max_px"],
					"floor_gap_rows_max": stats["floor_gap_rows_max"], "floor_gap_rows_mean": stats["floor_gap_rows_mean"],
					"rise_faults": rf, "start_feet": _feet_rows(ticks, 0, 8)}
				print("WALK10R1 %s %s steady cell-xor max %d head step max %d planted row max %d occlusion-only pairs %d faults %d" % [scene_key, mode, sx_max,
					int(stats["head_step_max_px"]), int(stats["planted_sole_row_world_disp_max_px"]),
					int(stats["planted_pairs_visible_extent_changed_by_occlusion_only"]), rf.size()])
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
					print("STOP10R1 %s phase %d -> v8 %.1f ms (feet down %.1f) raised %.0f/%.0f" % [r["tag"], int(r["released_at_phase_px"]),
						float(r["v8_after_ms"]), float(r["feet_down_ms_after_release"]), float(r["raised_after_release"]["vl"]["longest_raised_ms"]),
						float(r["raised_after_release"]["vr"]["longest_raised_ms"])])
			sr["repress"] = {}
			var spec_r: Array = spec.duplicate()
			if scene_key == "city-bright":
				spec_r[3] = Vector2(spec[3].x, CITY_REPRESS_START_Y)
			for rs in [[30, 1, [1, 3]], [60, 2, [1]]]:
				var rfps: int = rs[0]
				var per_tick_px: float = 280.0 / float(rfps)
				var first := int(ceil(LATE_FIRST_PX / per_tick_px))
				var count := int(ceil(float(SDM) / per_tick_px))
				var limit: int = int(steady.get(rfps, 0))
				for k in range(0, count, int(rs[1])):
					for gap in rs[2]:
						var r: Dictionary = await _repress_case(spec_r, scene_key, rfps, first + k, gap, limit)
						if r.has("error"):
							_fail(String(r["error"]))
							return
						for x in r["rise_faults"]:
							all_faults.append([r["tag"], x[0], x[1]])
						sr["repress"][r["tag"]] = r
				print("REPRESS10R1 %s %d fps: %d cases" % [scene_key, rfps, sr["repress"].size()])
			sr["reversal"] = {}
			var rev_first := int(ceil(LATE_FIRST_PX / (280.0 / 60.0)))
			var rev_count := int(ceil(float(SDM) / (280.0 / 60.0)))
			for k in range(0, rev_count, 6):
				var n_walk: int = rev_first + k
				var su: Array = await _setup(spec_r)
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
			print("REVERSAL10R1 %s %d cases" % [scene_key, sr["reversal"].size()])
		var reel_fps := 30 if scene_key == "city-bright" else 60
		var rr: Dictionary = await _showreel(spec, scene_key, reel_fps, motion_dir)
		if rr.has("error"):
			_fail(String(rr["error"]))
			return
		for x in rr["rise_faults"]:
			all_faults.append([rr["tag"], x[0], x[1]])
		sr["showreel"] = rr
		print("SHOWREEL10R1 %s ticks %d releases %s faults %d" % [rr["tag"], int(rr["ticks"]),
			str((rr["releases"] as Array).map(func(r): return [r["release_tick"], r["interrupted_by_input_before_v8"], r["v8_after_ms"]])), (rr["rise_faults"] as Array).size()])
		report["scenes"][scene_key] = sr
	report["steady_state_ticks_checked"] = steady_checked
	report["rise_faults_total"] = all_faults.size()
	report["rise_faults"] = all_faults
	report["reels_only"] = reels_only
	var rname := "%s_city-annex_female-south-run-v10r1-capture-receipt-h48_unapproved_%s-%s.json" % [SLUG, stamp, uid]
	var f := FileAccess.open(out_abs.path_join(rname), FileAccess.WRITE)
	f.store_string(JSON.stringify(report, " ") + "\n")
	f.close()
	print("RECEIPT " + rname)
	print("STAMP %s-%s" % [stamp, uid])
	if not all_faults.is_empty():
		print("RUN_V10R1_CAPTURE FAIL: %d rise-fault frames %s" % [all_faults.size(), str(all_faults.slice(0, 10))])
		quit(1)
		return
	print("RUN_V10R1_CAPTURE PASS")
	quit(0)
