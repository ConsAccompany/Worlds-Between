extends "rpg-2-star-ocean-the-second_female-south-run-v09-godot-capture_m8-w12_20261018-133700-4d620536.gd"

# TEST-ONLY real-Godot capture of the UNAPPROVED / NONRUNTIME female SOUTH RUN v10 (m8-w13, single direction): ONE
# authored gait + push-off revision.  This script EXTENDS the v09 capture tool (same folder, hash checked), which extends
# the v07 and v06 tools; v06 / v07 / v09 art and manifests are read-only.
#   * Gait (v10 manifest gait / stop / restart replace the v06 ones in memory only): stride 128 px, stance 44 px per boot
#     (land +12, lift-off -32), 4.375 steps/s at MOVE_SPEED 140, 68.75 % of the cycle with a boot on the floor.
#   * Loco10 = Loco7 (v06 event-clock stop + re-press rule + v07 rise lock) with ONE driver change: the torso compression
#     bob has levels by px since touchdown (manifest gait.bob_levels, 0..2 rows) and moves at most one row per tick.
#   * Comp10 extends Comp9 (v09 forward knee, shaded shin, seam ink) with the v10 leg rule (long / medium / folded, the
#     boot drawn behind a folded or tucked leg, boot texels on the hips rows hidden), the v10 push-off boots and the coat
#     hem lagging the torso shift (csx) AND the bob (hdy).
# Gates (exit 1): pins (v06 / v07 / v09 tools, v06 manifest, every v06 / v09 / v10 PNG, v8); flags false; neutral == v8;
# GDScript Comp10 == the builder's 16 keyframes + shadows AND the sha256 of all 128 per-px nominal composites; steady
# gait == the v10 per-px table; exact-RGB / neck-shear checks on every captured tick (inherited); planted boot 0 px in
# world space; every stop ends on the v8 PNG with a 0-pixel switch, release -> v8 <= 250 ms at 30 / 60 fps (<= 300 ms
# mixed frame times, sim), no boot raised > 100 ms after a release; re-press alternation; 0 frames on which both boots
# rise.  No fluidity is claimed from any of these numbers.
# Run windowed from an isolated copy whose paths fit MAX_PATH:
#   Godot_v4.7.2-stable_win64_console.exe --path <copy>/game -s <copy>/tools/<this file> -- --motion-dir=<abs> --out-dir=<abs>
#   (add --headless and -- --sim=1 for the window-free gait-driver sweep)

const V09_TOOL_FILE := "rpg-2-star-ocean-the-second_female-south-run-v09-godot-capture_m8-w12_20261018-133700-4d620536.gd"
const V09_TOOL_SHA256 := "9839568e7e0c1e76c26053b95de940f0eaece6ba79d7c150edbf1fae48e24189"
const V10_DIR := "res://assets/characters/run-v10-unapproved/"
const V10_MANIFEST_GLOB := "_gait-pose-manifest_unapproved_20261018-143213-"
const V10_LIMIT_MS := 250.0           # Root: visual settle <= 250 ms at 30 / 60 fps
const V10_LIMIT_MIXED_MS := 300.0     # Root: <= 300 ms with mixed frame times

var m10: Dictionary
# v10 re-press / reversal sweeps: the 128 px stride + the 0.3 s re-press would carry the hero past the scenes' southern
# limit (city navigation y 160..305, annex clamp 78..305) from the v07 / v09 start rows, so these two sweeps release
# from half a stride + 8 px on (the gait is nominal from 52 px: the start re-plans vl, which lands at 52 px) and the city
# cases start at y 160 (the city navigation minimum).  Walks, stops and the showreels keep v07 / v09's starts and inputs.
const LATE_FIRST_PX := 72.0
const CITY_REPRESS_START_Y := 160.0


# =====================================================================================================================
class Comp10 extends Comp9:
	var n_fold := 8
	var hips_bottom := 66
	var tuck_views := ["kick", "hang"]
	var island_max := 12
	var leg_pos := {}          # every leg texel drawn by leg() during the current compose()

	func setup10(rule: Dictionary, island: int) -> void:
		n_fold = int(rule["n_fold_rows"])
		hips_bottom = int(rule["hips_bottom_row"])
		tuck_views = rule["tuck_views"]
		island_max = island

	# builder island_rule (after the v09 seam fill): a leg-only 8-connected fragment, not the largest component, of at
	# most island_max texels is not drawn
	func compose(state: Dictionary) -> Dictionary:
		leg_pos = {}
		var r := super(state)
		if r.has("error"):
			return r
		var img: Image = r["image"]
		var seen := {}
		var comps := []
		for y in H:
			for x in W:
				var s0 := Vector2i(x, y)
				if seen.has(s0) or img.get_pixelv(s0).a8 == 0:
					continue
				seen[s0] = true
				var st := [s0]
				var c := [s0]
				while not st.is_empty():
					var q: Vector2i = st.pop_back()
					for dy in [-1, 0, 1]:
						for dx in [-1, 0, 1]:
							var n2 := q + Vector2i(dx, dy)
							if n2.x < 0 or n2.y < 0 or n2.x >= W or n2.y >= H or seen.has(n2) or img.get_pixelv(n2).a8 == 0:
								continue
							seen[n2] = true
							c.append(n2)
							st.append(n2)
				comps.append(c)
		var big := 0
		for i in comps.size():
			if (comps[i] as Array).size() > (comps[big] as Array).size():
				big = i
		var dropped := 0
		for i in comps.size():
			var c: Array = comps[i]
			if i == big or c.size() > island_max:
				continue
			var all_leg := true
			for q in c:
				all_leg = all_leg and leg_pos.has(q)
			if all_leg:
				for q in c:
					img.set_pixelv(q, Color(0, 0, 0, 0))
				dropped += c.size()
		r["v10_leg_islands_dropped"] = dropped
		return r

	# builder leg_plan(): [thigh rows, knee rows, shin rows, mode]
	func _plan10(side: String, n: int) -> Array:
		var k0: int = knee[side][0]
		var k1: int = knee[side][1]
		var T := range(hip, k0)
		var K := range(k0, k1 + 1)
		var S := range(k1 + 1, boot_top)
		var full := T.size() + K.size() + S.size()
		if n >= full:
			var e := n - full
			var et := IM.rdiv(e * T.size(), T.size() + S.size())
			return [IM.pick(T, T.size() + et), K, IM.pick(S, S.size() + e - et), "long"]
		var mode := "medium" if n >= n_fold else "folded"
		var m := maxi(n, n_fold)
		var nk := maxi(knee_min, IM.rdiv(m * K.size(), full))
		var nt := maxi(1, IM.rdiv((m - nk) * T.size(), T.size() + S.size()))
		var ns := m - nk - nt
		if ns < 1:
			nt -= 1 - ns
			ns = 1
		return [IM.pick(T, nt), IM.pick(K, nk), IM.pick(S, ns), mode]

	func leg(side: String, bob: int, foot: Dictionary) -> Dictionary:
		var view := String(foot["view"])
		var dy: int = int(foot["o"]) - int(foot["lift"])
		var boot := {}
		var bt := 1 << 30
		for p in parts["boot-%s-%s" % [side, view]]:
			var q: Vector2i = p[0] + Vector2i(0, dy)
			boot[q] = p[1]
			bt = mini(bt, q.y)
		var n := bt - (hip + bob)
		var tuck := view in tuck_views
		var plan := _plan10(side, n)
		var th: Array = plan[0]
		var kn: Array = plan[1]
		var sh: Array = plan[2]
		var mode: String = plan[3]
		var k1: int = knee[side][1]
		var src: Dictionary = leg_rows[side]
		var ksrc: Dictionary = knee_fwd[side] if tuck else src
		var cx := []
		for q in boot:
			if q.y == bt:
				cx.append(q.x)
		var cuff := _ext(cx)
		var kd: int = int(foot["kin"]) * int(inward[side])
		if tuck and sh.size() < 4:
			var kx := []
			for e in ksrc[k1]:
				kx.append(int(e[0]))
			var kb := _ext(kx)
			kd += IM.rdiv(IM.rdiv(int(cuff[0]) + int(cuff[1]) - int(kb[0]) - int(kb[1]), 2) * (4 - sh.size()), 4)
		var out := {}
		var y := hip + bob
		for i in th.size():
			var dx := IM.rdiv(kd * i * i, (th.size() - 1) * (th.size() - 1)) if th.size() > 1 else 0
			for e in src.get(th[i], []):
				out[Vector2i(int(e[0]) + dx, y)] = e[1]
			y += 1
		for sy in kn:
			for e in ksrc.get(sy, []):
				out[Vector2i(int(e[0]) + kd, y)] = e[1]
			y += 1
		var end := kd
		if mode == "long" and sh.size() > boot_top - 1 - k1:
			var sx0 := []
			for e in src.get(boot_top - 1, []):
				sx0.append(int(e[0]))
			var se := _ext(sx0)
			end = IM.rdiv(int(cuff[0]) + int(cuff[1]) - int(se[0]) - int(se[1]), 2)
		elif mode == "medium" and not tuck:
			end = 0
		for i in sh.size():
			var dx := kd + IM.rdiv((end - kd) * (i + 1), sh.size() + 1)
			for e in src.get(sh[i], []):
				var c: Color = e[1]
				out[Vector2i(int(e[0]) + dx, y)] = shade.get(c.to_html(false), c) if tuck else c
			y += 1
		var full := {}
		if mode == "folded" or tuck:
			for q in boot:
				if q.y > hips_bottom + bob:
					full[q] = boot[q]
			for q in out:
				full[q] = out[q]
		else:
			for q in out:
				full[q] = out[q]
			for q in boot:
				if q.y > hips_bottom + bob:
					full[q] = boot[q]
		for q in full:
			leg_pos[q] = true
		return {"texels": full, "boot": boot, "sole": int(ground[side]) + dy, "hip_to_sole": int(ground[side]) + dy - (hip + bob) + 1,
			"trouser_rows": bt - (hip + bob), "mode": mode}

	# coat-skirt: rows < hem at (sx, bob); rows >= hem at (csx, bob + hdy); hdy = +1 repeats the hem's top row at (csx, bob)
	func _put(g: Dictionary, role: String, dx: int, b: int) -> void:
		if role != "coat-skirt" or cur.is_empty():
			for p in parts[role]:
				g[p[0] + Vector2i(dx, b)] = p[1]
			return
		var csx: int = int(cur["csx"])
		var h: int = int(cur["hdy"])
		for p in parts[role]:
			var q: Vector2i = p[0]
			if q.y >= hem_row:
				g[q + Vector2i(csx, b + h)] = p[1]
				if h > 0 and q.y == hem_row:
					g[q + Vector2i(csx, b)] = p[1]
			else:
				g[q + Vector2i(dx, b)] = p[1]


# =====================================================================================================================
# v10 gait driver: Loco7 with the multi-level torso compression bob (one row per tick).  tick() is v06 Loco.tick with
# only the bob lines changed, followed by v07's rise lock (Loco7.tick), because Loco7.tick calls Loco.tick directly.
class Loco10 extends Loco7:
	var bob_skips := 0         # ticks on which the wanted bob level was more than one row away (stepped by one)

	func _bob_level(q: int) -> int:
		var lv := 0
		for k in g["bob_levels"]:
			if q >= int(k[0]):
				lv = int(k[1])
		return lv

	func tick(moving: bool, dt: float, y: int) -> Dictionary:
		prev_clock = clock
		clock += dt * 1000.0
		multi_ok = dt * 1000.0 > gap_ms + 1e-6
		bob_evt = -1.0
		events = []
		if moving:
			if not was_moving:
				_restart(last_y)
			dist += y - last_y
			var views_before := [String(feet["vl"]["view"]), String(feet["vr"]["view"])]
			for s in ["vl", "vr"]:
				var f: Dictionary = feet[s]
				if f["mode"] == "contact":
					var o: int = int(f["wo"]) - y
					if o <= BK:
						_lift(s, dist - (BK - o))
					else:
						_contact_pose(f, o)
				if f["mode"] == "swing":
					if dist >= int(f["d1"]):
						var over: int = dist - int(f["d1"])
						var new_ref: int = int(f["d1"]) - (0 if s == "vl" else SD / 2)
						var dref := posmod(new_ref - ref, SD)
						if mini(dref, SD - dref) > 2:
							arms_synced = false
						ref = new_ref
						_land_contact(s, y, A - over)
					else:
						var u := IM.rdiv(1000 * (dist - int(f["d0"])), int(f["d1"]) - int(f["d0"]))
						_set_pose(f, IM.interp_keys(f["keys"], u))
			var want_bob := 0
			var want_sx := 0
			for s in ["vl", "vr"]:
				if feet[s]["mode"] == "contact":
					var q: int = A - int(feet[s]["o"])
					want_bob = maxi(want_bob, _bob_level(q))           # v10 (v06: 1 inside bob_stance_q)
					if q >= int(g["torso_shift_stance_q"][0]) and q < int(g["torso_shift_stance_q"][1]):
						want_sx = -int(inward[s])
			if was_moving:
				if absi(want_bob - bob) > 1:
					bob_skips += 1
				if want_bob != bob:
					bob += 1 if want_bob > bob else -1                 # v10: one row per tick
				_step_sx(want_sx)
			var target := {"R": _arm("R", dist - ref), "L": _arm("L", dist - ref)}
			if arms_synced:
				arms = target
			elif events.is_empty() and bob == prev_bob and views_before == [String(feet["vl"]["view"]), String(feet["vr"]["view"])]:
				for side in ["R", "L"]:
					if arms[side] != target[side]:
						var a := POSES_ORDER.find(arms[side])
						var b := POSES_ORDER.find(target[side])
						arms[side] = POSES_ORDER[a + (1 if b > a else -1)]
						break
			if not arms_synced:
				arms_synced = arms["R"] == target["R"] and arms["L"] == target["L"]
			done = false
		else:
			if was_moving:
				release_t = clock - dt * 1000.0
				stop_bob = bob
				last_arm_t = -1e9
				arms = arms.duplicate()
				for s in ["vl", "vr"]:
					var f: Dictionary = feet[s]
					if f["mode"] == "swing":
						f["saved_d1"] = f["d1"]
						_start_move(s, "land", release_t)
				events.append(["release"])
			if not done and started:
				_stop_step(y, dt)
		started = started or moving
		if bob != prev_bob:
			hdy_val = clampi(prev_bob - bob, -1, 1)
			bob_t = bob_evt if bob_evt >= 0.0 else clock
			prev_bob = bob
		var stopped := (not moving) and started
		var hair_lag := float(st["stop_hair_lag_ms"]) if stopped else float(st["hair_lag_ms"])
		var cape_lag := float(st["stop_cape_lag_ms"]) if stopped else float(st["hair_lag_ms"])
		var hdy := hdy_val if clock - bob_t < hair_lag - 1e-6 else 0
		hdy = clampi(hdy, hdy_shown - 1, hdy_shown + 1)
		hdy_shown = hdy
		if clock - sx_t >= cape_lag - 1e-6 and csx != sx:
			csx += 1 if sx > csx else -1
		was_moving = moving
		last_y = y
		var state := {"bob": bob, "hdy": hdy, "sx": sx, "csx": csx, "arms": arms.duplicate(), "feet": {}}
		for s in ["vl", "vr"]:
			var f: Dictionary = feet[s]
			if f["mode"] == "contact":
				_contact_pose(f, int(f["wo"]) - y)
			state["feet"][s] = {"o": int(f["o"]), "lift": int(f["lift"]), "view": String(f["view"]), "kin": int(f["kin"])}
		if not was_moving and not done and started:
			var at_spot := true
			for s in ["vl", "vr"]:
				at_spot = at_spot and feet[s]["mode"] == "contact" and int(feet[s]["wo"]) == y
			if at_spot and bob == 0 and hdy == 0 and sx == 0 and csx == 0 and arms["R"] == "N" and arms["L"] == "N":
				if neutral_seen:
					done = true
				neutral_seen = true
			else:
				neutral_seen = false
		var modes := {}
		for s in ["vl", "vr"]:
			modes[s] = String(feet[s]["mode"])
		var r := {"state": state, "show_v8": done, "modes": modes, "events": events.duplicate(), "phase": dist - ref, "dist": dist}
		# v07 rise lock (Loco7.tick)
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


# =====================================================================================================================
func _fail(reason: String) -> void:
	push_error("RUN_V10_CAPTURE FAIL: " + reason)
	print("RUN_V10_CAPTURE FAIL: " + reason)
	Input.action_release("move_up")
	Input.action_release("move_down")
	quit(1)


func _find_v10_manifest() -> String:
	var d := DirAccess.open(V10_DIR)
	if d == null:
		return ""
	for f in d.get_files():
		if V10_MANIFEST_GLOB in f and f.ends_with(".json"):
			return f
	return ""


func _composite_sha(c: Dictionary) -> String:
	var hc := HashingContext.new()
	hc.start(HashingContext.HASH_SHA256)
	hc.update((c["image"] as Image).get_data())
	hc.update((c["shadow"] as Image).get_data())
	return hc.finish().hex_encode()


func _prepare() -> String:
	art = "v10"
	var tdir := (get_script() as Script).resource_path.get_base_dir()
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
	var m10name := _find_v10_manifest()
	if m9name == "" or m10name == "":
		return "v09 / v10 manifest not found"
	m9 = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path(V09_DIR + m9name)))
	m10 = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path(V10_DIR + m10name)))
	m10["_file"] = m10name
	m10["_sha256_text_lf_v1"] = _sha_text_lf(V10_DIR + m10name)
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
	manifest["restart"]["v07_rise_lock"] = bool(amend["restart_amendment"]["rise_lock"]) and bool(m10["restart"]["v07_rise_lock"])
	SDM = int(manifest["gait"]["stride_px"])
	shadow_alpha = float(manifest["display"]["shadow"]["opacity"])
	for pair in [[manifest["parts"], ASSET_DIR], [m9["parts_new"], V09_DIR], [m10["parts_new"], V10_DIR]]:
		for e in pair[0]:
			if FileAccess.get_sha256(ProjectSettings.globalize_path(String(pair[1]) + String(e["file"]))) != String(e["sha256"]):
				return "%s sha256 mismatch" % String(e["file"])
	for e in m10["keyframes"]:
		for k in [["file", "sha256"], ["shadow_file", "shadow_sha256"]]:
			if FileAccess.get_sha256(ProjectSettings.globalize_path(V10_DIR + String(e[k[0]]))) != String(e[k[1]]):
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
		if c.has("error") or (c["image"] as Image).get_data() != _load_rgba(V10_DIR + String(k["file"])).get_data() \
				or (c["shadow"] as Image).get_data() != _load_rgba(V10_DIR + String(k["shadow_file"])).get_data():
			return "GDScript Comp10 != builder keyframe %s" % String(k["key"])
	var bad := []
	for row in m10["metrics"]["nominal_per_px"]:
		var c := comp.compose(row)
		if c.has("error") or _composite_sha(c) != String(row["composite_sha256"]):
			bad.append(int(row["phase_px"]))
	if not bad.is_empty():
		return "GDScript Comp10 != builder per-px composites at phases %s" % str(bad.slice(0, 12))
	print("PARITY10: neutral == v8, %d keyframes + shadows == builder PNGs, %d per-px composites == builder sha256" % [
		m10["keyframes"].size(), m10["metrics"]["nominal_per_px"].size()])
	return ""


# v10: the lagging coat hem (and the folded rear leg) are drawn in front of a planted rear boot, so a sole-edge texel
# can be covered on one tick and not the next.  A same-view pair counts as occlusion only (not slip) when every boot
# texel keeps its world position and RGB (the captured frame equals the composite exactly, checked on every tick) and
# the lowest visible row is unchanged; the visible-extent maximum is kept in the stats next to the gated value.
func _planted_stats(summ: Array, from_i: int, to_i: int) -> Dictionary:
	var st: Dictionary = super(summ, from_i, to_i)
	var x_max := 0
	var occl := 0
	for i in range(maxi(1, from_i), mini(summ.size(), to_i)):
		var e: Dictionary = summ[i]
		if bool(e.get("runtime_north", false)):
			continue
		for s in e.get("planted", {}):
			var p: Dictionary = e["planted"][s]
			if bool(p["view_changed"]):
				continue
			var xd := maxi(absi(int(p["sole_x0_d"])), absi(int(p["sole_x1_d"])))
			var lost: int = maxi(int(p["boot_texels_now"]), int(p["boot_texels_prev"])) - int(p["boot_texels_same_world_pos_and_rgb"])
			if xd != 0 and lost == 0 and int(p["sole_row_d"]) == 0:
				occl += 1
			else:
				x_max = maxi(x_max, xd)
	st["planted_sole_x_visible_extent_change_max_px_same_view"] = st["planted_sole_x_world_disp_max_px_same_view"]
	st["planted_sole_x_world_disp_max_px_same_view"] = x_max
	st["planted_pairs_visible_extent_changed_by_occlusion_only"] = occl
	return st


# diagnostic for a failed planted gate: the tick pairs whose planted boot changed on the capture
func _planted_bad(summ: Array) -> Array:
	var out := []
	for e in summ:
		for s in e.get("planted", {}):
			var p: Dictionary = e["planted"][s]
			var lost: int = maxi(int(p["boot_texels_now"]), int(p["boot_texels_prev"])) - int(p["boot_texels_same_world_pos_and_rgb"])
			if int(p["sole_row_d"]) != 0 or (not bool(p["view_changed"]) and (int(p["sole_x0_d"]) != 0 or int(p["sole_x1_d"]) != 0 or lost != 0)) 					or (bool(p["view_changed"]) and maxi(absi(int(p["sole_x0_d"])), absi(int(p["sole_x1_d"]))) > 2):
				out.append([int(e["tick"]), s, p, e["state"]["feet"][s], e["state"]["bob"], e["state"]["hdy"]])
	return out.slice(0, 6)


func _per_px() -> Array:
	return m10["metrics"]["nominal_per_px"]


# _drive / _sim_drive: v07's bodies with the v10 driver class (Loco10); nothing else differs
func _drive(su: Array, plan: Array, motion_dir: String, tag: String, crop: Rect2i, full_saves: Dictionary = {}) -> Array:
	var host: Node2D = su[0]
	var hero: Sprite2D = su[1]
	var ground_off: float = su[3]
	var bg: Image = su[4]
	var loco := Loco10.new()
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
			loco = Loco10.new()
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
	var loco := Loco10.new()
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


# =====================================================================================================================
# --sim=1: state-level sweep of the v10 gait (Loco10) at 14 frame rates + jitter.  Gates: rise faults 0, alternation,
# raised <= 100 ms at >= 30 fps, release -> v8 <= 250 ms at 30 and 60 fps, jitter <= 300 ms, steady state == the
# per-px table at 30 / 60 / 144 fps, measured cadence and floor contact.
func _sim_stops10() -> Dictionary:
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
		var slow := []
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
			if float(sr["v8_ms"]) > V10_LIMIT_MS + 1e-3 and fps >= 30:
				slow.append({"release_frame": first + k, "phase_px": sr["phase_px"], "v8_ms": sr["v8_ms"], "settle_log": sr["settle_log_ms_after_release"],
					"feet": _feet_rows(rec, first + k, first + k + 10), "states": _state_rows(rec, first + k, first + k + 10)})
		var mx: float = v8s.max()
		if faults > 0 or (fps >= 30 and raised > STOP_RAISED_LIMIT_MS + 1e-3) or ((fps == 30 or fps == 60) and mx > V10_LIMIT_MS + 1e-3):
			ok = false
		out[str(fps)] = {"release_to_v8_ms": _sim_range(v8s), "raised_max_ms": raised, "rise_faults": faults, "per_stop_v8_ms": v8s,
			"stops_raised_over_limit": over, "stops_over_v8_limit": slow}
	var rng := RandomNumberGenerator.new()
	rng.seed = 6061
	var jit := []
	var jit_raised := 0.0
	for trial in 24:
		var plan := [{"input": false, "dt": 1.0 / 60.0}]
		var n := 30 + rng.randi_range(0, 40)
		for i in n:
			plan.append({"input": true, "dt": 1.0 / float([30, 45, 60, 144][rng.randi_range(0, 3)])})
		for i in 40:
			plan.append({"input": false, "dt": 1.0 / float([30, 45, 60, 144][rng.randi_range(0, 3)])})
		var rec := _sim_drive(plan)
		var sr := _sim_stop(rec, n + 1)
		if sr.has("error"):
			ok = false
			continue
		jit.append(float(sr["v8_ms"]))
		jit_raised = maxf(jit_raised, float(sr["raised_max_ms"]))
	if jit.is_empty() or float(jit.max()) > V10_LIMIT_MIXED_MS + 1e-3:
		ok = false
	out["jitter_seed_6061"] = _sim_range(jit)
	out["jitter_raised_max_ms"] = jit_raised
	out["_ok"] = ok
	return out


func _sim_steady(fps: int) -> Dictionary:
	var dt := 1.0 / float(fps)
	var n := int(ceil(6.0 * float(SDM) / (280.0 / float(fps))))
	var plan := [{"input": false, "dt": dt}]
	for i in n:
		plan.append({"input": true, "dt": dt})
	var rec := _sim_drive(plan)
	var per_px := _per_px()
	var mism := 0
	var checked := 0
	var lands := []
	var contact_ms := 0.0
	var total_ms := 0.0
	var t := 0.0
	for i in range(1, rec.size()):
		t += float(rec[i]["dt"]) * 1000.0
		for ev in rec[i]["events"]:
			if String(ev[0]) == "land":
				lands.append(t)
		var r: Dictionary = rec[i]
		if int(r["dist"]) < SDM * 3 / 2:
			continue
		total_ms += float(r["dt"]) * 1000.0
		if String(r["modes"]["vl"]) == "contact" or String(r["modes"]["vr"]) == "contact":
			contact_ms += float(r["dt"]) * 1000.0
		var row: Dictionary = per_px[posmod(int(r["phase"]), per_px.size())]
		var st: Dictionary = r["state"]
		var ok: bool = int(row["bob"]) == int(st["bob"]) and int(row["sx"]) == int(st["sx"])
		for s in ["vl", "vr"]:
			for f in ["o", "lift", "kin"]:
				ok = ok and int(row["feet"][s][f]) == int(st["feet"][s][f])
			ok = ok and String(row["feet"][s]["view"]) == String(st["feet"][s]["view"])
		checked += 1
		mism += 0 if ok else 1
	var gaps := []
	for i in range(2, lands.size()):
		gaps.append(float(lands[i]) - float(lands[i - 1]))
	var mean := 0.0
	for gv in gaps:
		mean += float(gv)
	mean = mean / maxf(1.0, float(gaps.size()))
	return {"fps": fps, "ticks_checked": checked, "state_mismatches_vs_per_px": mism, "touchdowns": lands.size(),
		"touchdown_interval_ms": _sim_range(gaps), "touchdown_interval_mean_ms": mean,
		"measured_steps_per_s": 1000.0 / mean if mean > 0.0 else 0.0,
		"ticks_with_a_boot_in_contact_share": contact_ms / maxf(1.0, total_ms), "bob_level_skips": int(rec[-1]["bob_skips"])}


func _sim10(out_abs: String, stamp: String, uid: String) -> void:
	var s10 := _sim_stops10()
	var rep := _sim_repress_sweep(true)
	var t: Dictionary = rep["totals"]
	var steady := {}
	var steady_ok := true
	for fps in [30, 60, 144]:
		var sd := _sim_steady(fps)
		steady[str(fps)] = sd
		steady_ok = steady_ok and int(sd["state_mismatches_vs_per_px"]) == 0 and int(sd["ticks_checked"]) > 0 \
			and float(sd["measured_steps_per_s"]) >= 4.0 and float(sd["measured_steps_per_s"]) <= 4.5
		print("SIM10 steady %d fps: %s" % [fps, str(sd)])
	var ok: bool = bool(s10["_ok"]) and int(t["alternation_failures"]) == 0 and int(t["rise_fault_frames"]) == 0 and steady_ok
	for fps in ["24", "30", "48", "60", "144"]:
		print("SIM10 %s fps release->v8 %s raised max %.1f" % [fps, str(s10[fps]["release_to_v8_ms"]), float(s10[fps]["raised_max_ms"])])
	print("SIM10 jitter %s raised %.1f" % [str(s10["jitter_seed_6061"]), float(s10["jitter_raised_max_ms"])])
	print("SIM10 re-press totals %s" % str(t))
	var report := {"purpose": "v10 state-level gait-driver sweep (Loco10 = v07 driver + multi-level torso compression bob, v10 gait): steady state vs the per-px table and measured cadence at 30 / 60 / 144 fps; stops from every frame of one stride at 14 frame rates + seeded jitter; re-press sweep (every release frame x gaps 1..30 at 14 frame rates + 600 mixed-frame-time cases)",
		"art_approved": false, "human_reviewed": false, "runtime_integrated": false,
		"v10_manifest": m10["_file"], "v10_manifest_sha256_text_lf_v1": m10["_sha256_text_lf_v1"],
		"limits": {"release_to_v8_ms_30_60fps": V10_LIMIT_MS, "release_to_v8_ms_mixed": V10_LIMIT_MIXED_MS, "raised_ms_ge_30fps": STOP_RAISED_LIMIT_MS},
		"steady": steady, "stops": s10, "repress": rep, "gates_ok": ok}
	if out_abs != "":
		var rname := "%s_gait-driver_female-south-run-v10-sim-timing-receipt_unapproved_%s-%s.json" % [SLUG, stamp, uid]
		var f := FileAccess.open(out_abs.path_join(rname), FileAccess.WRITE)
		f.store_string(JSON.stringify(report, " ") + "\n")
		f.close()
		print("SIM10 RECEIPT " + rname)
	print("SIM10 " + ("PASS" if ok else "FAIL"))
	quit(0 if ok else 1)


# =====================================================================================================================
# captured cases: the v09 bodies with the v10 limits (250 ms at 30 and 60 fps)
func _stop_case(spec: Array, scene_key: String, fps: int, n_walk: int, motion_dir: String) -> Dictionary:
	var dt: float = 1.0 / fps
	var su: Array = await _setup(spec)
	if su.is_empty():
		return {"error": "setup"}
	var plan := _plan_walk(n_walk, fps)
	for i in int(0.45 * fps):
		plan.append({"input": false, "dt": dt})
	var tag := "%s_stop-%dfps-%03d" % [scene_key, fps, n_walk]
	var ticks: Array = await _drive(su, plan, "", tag, Rect2i())
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
	if float(rc["v8_after_ms"]) > V10_LIMIT_MS + 1e-3:
		return {"error": "%s: release -> v8 %.1f ms over the limit" % [tag, float(rc["v8_after_ms"])]}
	for s in ["vl", "vr"]:
		if float(rc["raised_after_release"][s]["longest_raised_ms"]) > STOP_RAISED_LIMIT_MS:
			return {"error": "%s: boot %s raised too long" % [tag, s]}
	return {"tag": tag, "fps": fps, "released_at_phase_px": posmod(int(ticks[rel - 1]["phase"]), SDM), "v8_after_ms": rc["v8_after_ms"],
		"feet_down_ms_after_release": rc["settle"]["feet_down_ms_after_release"], "raised_after_release": rc["raised_after_release"],
		"stop_cell_xor_max": ss["cell_silhouette_xor_max_per_tick"], "rise_faults": _rise_faults(ticks),
		"states_release_to_v8": _state_rows(ticks, rel - 1, int(rc["v8_at"]))}


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
			if not interrupted:
				if int(rc["switch_to_v8_xor"]) != 0 or float(rc["v8_after_ms"]) > V10_LIMIT_MS + 1e-3:
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
			row["phase"] = int(tk.get("phase", 0))
		frames.append(row)
	var xs := []
	for e in rsumm:
		xs.append(int(e.get("cell_silhouette_xor", 0)))
	return {"tag": rtag, "fps": fps, "scene": scene_key, "segments": marks, "ticks": rticks.size(), "releases": releases,
		"rise_faults": _rise_faults(rticks), "rise_locks": _locks_in(rticks), "cell_xor_per_tick": xs, "frames": frames,
		"note": "full 1280x720 window frames (the 640x360 logical canvas at 2x), one per %d fps tick, normal speed; runtime_north ticks show the scene's own runtime hero (placeholder north walk), not pilot art" % fps}


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
		_sim10(out_abs, stamp, uid)
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
	SaveStore.root_path = "user://test-saves/m8-south-run-v10-capture"
	app = root.get_node("AppState")
	var report := {"project": "Worlds Between", "milestone": "M8", "art": art,
		"purpose": "TEST-ONLY real-Godot capture, female SOUTH RUN v10 authored gait + push-off revision (Loco10 driver, Comp10 compositor)",
		"status": "UNAPPROVED / NONRUNTIME; not art acceptance; Root / creator visual decision pending",
		"art_approved": false, "human_reviewed": false, "runtime_integrated": false,
		"renderer": "Godot %s windowed, viewport texture capture" % Engine.get_version_info()["string"],
		"canvas_logical": [640, 360], "window_native": [1280, 720], "sprite_scale": 0.5,
		"limits": {"release_to_v8_ms": V10_LIMIT_MS, "raised_ms": STOP_RAISED_LIMIT_MS},
		"repress_reversal_sweep_note": "release window from %d px (half a stride + 8); city re-press / reversal cases start at y %d (navigation limit 305 would otherwise be crossed); walks, stops and showreels use the v07 / v09 starts" % [int(LATE_FIRST_PX), int(CITY_REPRESS_START_Y)],
		"capture_tool": "tools/" + (get_script() as Script).resource_path.get_file(),
		"v10_manifest": m10["_file"], "v10_manifest_sha256_text_lf_v1": m10["_sha256_text_lf_v1"], "scenes": {}}
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
				print("WALK10 %s %s steady cell-xor max %d head step max %d planted row max %d occlusion-only pairs %d faults %d" % [scene_key, mode, sx_max,
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
					print("STOP10 %s phase %d -> v8 %.1f ms (feet down %.1f) raised %.0f/%.0f" % [r["tag"], int(r["released_at_phase_px"]),
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
				print("REPRESS10 %s %d fps: %d cases" % [scene_key, rfps, sr["repress"].size()])
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
			print("REVERSAL10 %s %d cases" % [scene_key, sr["reversal"].size()])
		var reel_fps := 30 if scene_key == "city-bright" else 60
		var rr: Dictionary = await _showreel(spec, scene_key, reel_fps, motion_dir)
		if rr.has("error"):
			_fail(String(rr["error"]))
			return
		for x in rr["rise_faults"]:
			all_faults.append([rr["tag"], x[0], x[1]])
		sr["showreel"] = rr
		print("SHOWREEL10 %s ticks %d releases %s faults %d" % [rr["tag"], int(rr["ticks"]),
			str((rr["releases"] as Array).map(func(r): return [r["release_tick"], r["interrupted_by_input_before_v8"], r["v8_after_ms"]])), (rr["rise_faults"] as Array).size()])
		report["scenes"][scene_key] = sr
	report["steady_state_ticks_checked"] = steady_checked
	report["rise_faults_total"] = all_faults.size()
	report["rise_faults"] = all_faults
	report["reels_only"] = reels_only
	var rname := "%s_city-annex_female-south-run-v10-capture-receipt-h48_unapproved_%s-%s.json" % [SLUG, stamp, uid]
	var f := FileAccess.open(out_abs.path_join(rname), FileAccess.WRITE)
	f.store_string(JSON.stringify(report, " ") + "\n")
	f.close()
	print("RECEIPT " + rname)
	print("STAMP %s-%s" % [stamp, uid])
	if not all_faults.is_empty():
		print("RUN_V10_CAPTURE FAIL: %d rise-fault frames %s" % [all_faults.size(), str(all_faults.slice(0, 10))])
		quit(1)
		return
	print("RUN_V10_CAPTURE PASS")
	quit(0)
