extends SceneTree

# TEST-ONLY real-Godot 1280x720 capture of the UNAPPROVED / NONRUNTIME female south compact locomotion pilot v02 (m8-w05).
# Review evidence only: not art acceptance, not runtime integration.  The creator approved only the selout v8 SOUTH IDLE
# static frame and the 48 logical px display scale; motion is not approved.  Lives in tools/ (outside res://), so no game/
# file is added or edited, and no runtime script is changed.  Run windowed from the repository root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path of this file> -- --motion-dir=<abs scratch>
#
# What it does.  The hidden runtime hero is moved by each scene's OWN _process(delta) with "move_down" held (MOVE_SPEED 140,
# asserted), exactly as v01.  A TEST-ONLY compositor (class PartCompositor, a line-for-line port of compose() in the v02 builder)
# stacks the v02 part PNGs every tick; a TEST-ONLY gait driver (class Loco) decides the foot states from the manifest's gait
# keys, stop rule and re-press rule:
#   * body parts at the logical position (no root lock, no body hop);
#   * a boot in contact keeps the window row fixed when it landed (o = world row - body row), so it does not slide;
#   * phase is distance-driven (travelled window px), so 30 / 60 / 144 fps share one gait;
#   * release: airborne boots fly to their v8 spots, then off-spot planted boots shuffle; then the v8 PNG itself;
#   * re-press: the boot that landed LAST stays planted; the other one is re-planned from where it is.
# Gates (exit 1): manifest sha256-text-lf-v1 + every PNG + v8 sha256-bytes; flags false; MOVE_SPEED 140; 1280x720; GDScript
# compositor == builder keyframe PNGs (all 12) and == v8 at the neutral state; steady-state gait == the manifest's per-px
# table; exact-RGB fidelity of the drawn image on every captured tick; straight-south movement; hero stationary without input;
# and, MEASURED ON CAPTURED PIXELS: a boot in contact on two consecutive ticks keeps its lowest window row, its sole-row
# x-extent and every visible boot texel (world space).
# Reported: per-tick planted-boot world displacement, airborne boot steps, silhouette XOR per tick (walk vs stop vs re-press),
# stop durations, re-press order, crown steps, frame extents.
const ASSET_DIR := "res://assets/characters/locomotion-pilots-compact-v02/"
const MANIFEST := "rpg-2-star-ocean-the-second_protagonist-female_south-locomotion-compact-v02-manifest_m8-w05_20261016-200500-a5615443.json"
const V8_PATH := "res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png"
const V8_SHA256 := "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"
const PIN := Vector2i(40, 104)
const LEG_SPLIT_X := 38
const AREA_SCENE := "res://scenes/scifi_exploration_area.tscn"
const AREA_SCRIPT := "res://scripts/scifi_exploration_area.gd"
const ANNEX_SCENE := "res://scenes/survey_annex.tscn"
const ANNEX_SCRIPT := "res://scripts/survey_annex.gd"
const SCENES := {
	"city-bright": ["area", "scifi.city", 0, Vector2(340, 165), "science city, default first-visit layout (bright)"],
	"outskirts-bright": ["area", "scifi.outskirts", 0, Vector2(250, 150), "sunlit outskirts warm beige paving (bright)"],
	"annex-dark": ["annex", "scifi.city", 2, Vector2(240, 150), "city survey annex room 2, darkest annex floor"],
}
const WALK_MODES := {"walk-60fps": [50, 60], "walk-30fps": [25, 30], "walk-144fps": [120, 144]}   # 0.83 s, 117 logical px (v01's room)
const OUTPUT_DIR := "res://../outputs"
const SLUG := "rpg-2-star-ocean-the-second"
const VARIANT := "m8-w05"
const STILL_STOP_CASES := {30: "from-stance-vl", 36: "from-flight"}   # 60 fps release ticks saved as full 1280x720 stills

var app: Node
var manifest: Dictionary
var comp: PartCompositor
var v8_image: Image
var v8_tex: Texture2D


# =====================================================================================================================
# integer helpers shared with the Python builder (floor division and floor(n / d + 1/2)); an inner class so the other
# inner classes can reach them
class IM:
	const INK := Color8(0x0a, 0x0a, 0x0e)

	static func fdiv(a: int, b: int) -> int:
		var q := a / b
		if (a % b != 0) and ((a < 0) != (b < 0)):
			q -= 1
		return q


	static func rdiv(n: int, d: int) -> int:
		return fdiv(2 * n + d, 2 * d)


	static func pick(src: Array, n: int) -> Array:
		var out := []
		var k := src.size()
		for i in n:
			out.append(src[mini(k - 1, (i * k) / n)])
		return out


	static func interp_keys(keys: Array, u: int) -> Dictionary:
		for i in keys.size() - 1:
			var k0: Array = keys[i]
			var k1: Array = keys[i + 1]
			var u0 := int(k0[0])
			var u1 := int(k1[0])
			if (u0 <= u and u < u1) or (i == keys.size() - 2 and u >= u1):
				var t := mini(u, u1) - u0
				return {"o": int(k0[1]) + rdiv((int(k1[1]) - int(k0[1])) * t, u1 - u0),
					"lift": int(k0[2]) + rdiv((int(k1[2]) - int(k0[2])) * t, u1 - u0), "view": String(k0[3]), "kin": int(k0[4])}
		push_error("u outside key table")
		return {}




# =====================================================================================================================
# TEST-ONLY part compositor: line-for-line port of compose() / compose_leg() / pinhole_fill() in the v02 builder.
class PartCompositor:
	var W := 80
	var H := 120
	var parts := {}            # role -> Array of [Vector2i, Color]
	var leg_rows := {}         # side -> {y: Array of [x, Color]}
	var ground := {}
	var knee := {}
	var inward := {}
	var hip := 61
	var boot_top := 85
	var knee_min := 5
	var hdy_tag := {-1: "m1", 0: "0", 1: "p1"}

	func load_parts(entries: Array, dir: String, rig: Dictionary) -> String:
		for e in entries:
			var img := Image.load_from_file(ProjectSettings.globalize_path(dir + String(e["file"])))
			if img == null:
				return "cannot load " + String(e["file"])
			img.convert(Image.FORMAT_RGBA8)
			if img.get_size() != Vector2i(W, H):
				return "part size " + String(e["role"])
			var px := []
			for y in H:
				for x in W:
					var c := img.get_pixel(x, y)
					if c.a8 == 255:
						px.append([Vector2i(x, y), c])
					elif c.a8 != 0:
						return "non-binary alpha in " + String(e["role"])
			parts[String(e["role"])] = px
		for side in ["vl", "vr"]:
			ground[side] = int(rig["ground_rows"][side])
			knee[side] = [int(rig["knee_band_rows"][side][0]), int(rig["knee_band_rows"][side][1])]
			inward[side] = int(rig["inward_dx"][side])
			var rows := {}
			for p in parts["leg-src-" + side]:
				var y: int = p[0].y
				if not rows.has(y):
					rows[y] = []
				rows[y].append([p[0].x, p[1]])
			leg_rows[side] = rows
		hip = int(rig["hip_row"])
		boot_top = int(rig["boot_top_row"])
		return ""

	func _plan(side: String, bob: int, bt: int) -> Array:
		var k0: int = knee[side][0]
		var k1: int = knee[side][1]
		var T := range(hip, k0)
		var K := range(k0, k1 + 1)
		var S := range(k1 + 1, boot_top)
		var n := bt - (hip + bob)
		if n < K.size() + 2:
			if n - 2 < knee_min:
				return []
			return [[T[0]], IM.pick(K, n - 2), [S[S.size() - 1]]]
		var rest := n - K.size()
		var nt := maxi(1, mini(rest - 1, IM.rdiv(rest * T.size(), T.size() + S.size())))
		return [IM.pick(T, nt), K, IM.pick(S, rest - nt)]

	func leg(side: String, bob: int, foot: Dictionary) -> Dictionary:
		var dy: int = int(foot["o"]) - int(foot["lift"])
		var boot := {}
		var bt := 1 << 30
		for p in parts["boot-%s-%s" % [side, String(foot["view"])]]:
			var q: Vector2i = p[0] + Vector2i(0, dy)
			boot[q] = p[1]
			bt = mini(bt, q.y)
		var plan := _plan(side, bob, bt)
		if plan.is_empty():
			return {"error": "no room for leg %s %s" % [side, str(foot)]}
		var th: Array = plan[0]
		var kn: Array = plan[1]
		var sh: Array = plan[2]
		var kdx: int = int(foot["kin"]) * int(inward[side])
		var src: Dictionary = leg_rows[side]
		var out := {}
		var y := hip + bob
		for i in th.size():
			var dx := IM.rdiv(kdx * i * i, (th.size() - 1) * (th.size() - 1)) if th.size() > 1 else 0
			for e in src.get(th[i], []):
				out[Vector2i(int(e[0]) + dx, y)] = e[1]
			y += 1
		for sy in kn:
			for e in src.get(sy, []):
				out[Vector2i(int(e[0]) + kdx, y)] = e[1]
			y += 1
		for i in sh.size():
			var dx := kdx + IM.rdiv(-kdx * (i + 1), sh.size() + 1)
			for e in src.get(sh[i], []):
				out[Vector2i(int(e[0]) + dx, y)] = e[1]
			y += 1
		for q in boot:
			out[q] = boot[q]
		return {"texels": out, "boot": boot, "sole": int(ground[side]) + dy}

	static func in_contact(foot: Dictionary) -> bool:
		return int(foot["lift"]) == 0 and String(foot["view"]) == "v8"

	func near_leg(feet: Dictionary) -> String:
		var cl := in_contact(feet["vl"])
		var cr := in_contact(feet["vr"])
		if cl != cr:
			return "vl" if not cl else "vr"
		return "vl" if int(feet["vl"]["o"]) > int(feet["vr"]["o"]) else "vr"

	func _put(g: Dictionary, role: String, b: int) -> void:
		for p in parts[role]:
			g[p[0] + Vector2i(0, b)] = p[1]

	# -> {"image": Image, "boots": {side: {Vector2i: Color}}, "soles": {...}, "near": String} or {"error": ...}
	func compose(state: Dictionary) -> Dictionary:
		var b: int = int(state["bob"])
		var h: int = int(state["hdy"])
		var legs := {}
		var boots := {}
		var soles := {}
		for side in ["vl", "vr"]:
			var l := leg(side, b, state["feet"][side])
			if l.has("error"):
				return l
			legs[side] = l["texels"]
			boots[side] = l["boot"]
			soles[side] = l["sole"]
		var near := near_leg(state["feet"])
		var far := "vl" if near == "vr" else "vr"
		var R := String(state["arms"]["R"])
		var L := String(state["arms"]["L"])
		var g := {}
		_put(g, "cape-hdy-" + String(hdy_tag[h]), b)
		_put(g, "arm-vl-%s-back" % R, b)
		_put(g, "arm-vr-%s-back" % L, b)
		var legmask := {}
		for p in parts["hips"]:
			legmask[p[0] + Vector2i(0, b)] = true
		_put(g, "hips", b)
		for q in legs[far]:
			g[q] = legs[far][q]
			legmask[q] = true
		for q in legs[near]:
			g[q] = legs[near][q]
			legmask[q] = true
		_put(g, "coat-skirt", b)
		_put(g, "upper-body", b)
		_put(g, "arm-vl-%s-seam" % R, b)
		_put(g, "arm-vr-%s-seam" % L, b)
		_put(g, "hair-hdy-" + String(hdy_tag[h]), b)
		_put(g, "arm-vl-%s-front" % R, b)
		_put(g, "arm-vr-%s-front" % L, b)
		var holes := []
		for y in range(hip + b, H):
			for x in range(1, W - 1):
				var q := Vector2i(x, y)
				if g.has(q):
					continue
				var a1 := Vector2i(x - 1, y)
				var a2 := Vector2i(x + 1, y)
				var a3 := Vector2i(x, y - 1)
				if g.has(a1) and g.has(a2) and g.has(a3) and (legmask.has(a1) or legmask.has(a2) or legmask.has(a3)):
					holes.append(q)
		for q in holes:
			g[q] = IM.INK
		var img := Image.create_empty(W, H, false, Image.FORMAT_RGBA8)
		for q in g:
			if q.x < 0 or q.y < 0 or q.x >= W or q.y >= H:
				return {"error": "texel outside the cell " + str(q)}
			img.set_pixelv(q, g[q])
		return {"image": img, "boots": boots, "soles": soles, "near": near}


# =====================================================================================================================
# TEST-ONLY gait driver (event-driven per foot; the manifest's gait keys, stop rule and re-press rule).
class Loco:
	var g: Dictionary          # manifest["gait"]
	var st: Dictionary         # manifest["stop"]
	var rs: Dictionary         # manifest["restart"]
	var SD := 96
	var E := 20
	var A := 8
	var BK := -12
	var clock := 0.0           # ms
	var dist := 0              # travelled window px while moving
	var last_y := 0
	var was_moving := false
	var started := false
	var ref := 0               # arm phase reference: phase = dist - ref (vl lands at phase 0, vr at SD / 2)
	var feet := {}             # side -> {mode, o, lift, view, kin, wo, d0, d1, keys, t0, dur, land_t, saved_d1}
	var bob := 0
	var prev_bob := 0
	var bob_t := -1e9
	var hdy_val := 0
	var hdy_shown := 0
	var arms := {"R": "N", "L": "N"}
	var release_t := 0.0
	var stop_bob := 0
	var last_arm_t := -1e9
	var arms_synced := true
	var settle_t := -1.0
	var done := true
	var neutral_seen := false
	var events := []

	func setup(m: Dictionary, y: int) -> void:
		g = m["gait"]
		st = m["stop"]
		rs = m["restart"]
		SD = int(g["stride_px"])
		E = int(g["stance_px"])
		A = int(g["land_offset"])
		BK = int(g["liftoff_offset"])
		last_y = y
		for s in ["vl", "vr"]:
			feet[s] = {"mode": "contact", "o": 0, "lift": 0, "view": "v8", "kin": 0, "wo": y, "land_t": -1.0, "saved_d1": -1}

	func _arm(side: String, phase: int) -> String:
		var f := posmod(phase - int(g["arm_peak_px"][side]), SD)
		if 6 * f <= SD or 6 * f >= 5 * SD:
			return "F1"
		if SD <= 3 * f and 3 * f <= 2 * SD:
			return "B1"
		return "N"

	static func land_keys(o0: int, l0: int, v0: String, k0: int) -> Array:
		return [[0, o0, l0, v0, k0], [600, IM.rdiv(o0, 3), maxi(IM.rdiv(l0, 3), mini(4, IM.rdiv(absi(o0), 3))), "reach", 0],
			[1000, 0, 0, "strike", 0]]

	static func shuffle_keys(o0: int) -> Array:
		return [[0, o0, 0, "heelup", 0], [450, IM.rdiv(o0, 2), mini(4, 1 + absi(o0) / 3), "hang", 1], [1000, 0, 0, "strike", 0]]

	func replan_keys(o0: int, l0: int, v0: String, k0: int, hs: int) -> Array:
		return [[0, o0, l0, "heelup" if v0 == "v8" else v0, k0], [500, IM.rdiv(o0 + A, 2), maxi(l0, hs), "hang", 1],
			[800, A - 1, IM.rdiv(hs, 2), "reach", 0], [1000, A, 0, "strike", 0]]

	func _set_pose(f: Dictionary, p: Dictionary) -> void:
		f["o"] = p["o"]
		f["lift"] = p["lift"]
		f["view"] = p["view"]
		f["kin"] = p["kin"]

	func _land_contact(s: String, y: int, o: int) -> void:
		var f: Dictionary = feet[s]
		f["mode"] = "contact"
		f["wo"] = y + o
		f["o"] = o
		f["lift"] = 0
		f["view"] = "v8"
		f["kin"] = 1 if A - o < int(g["stance_knee_bend_px"]) else 0
		f["land_t"] = clock
		events.append(["land", s, o])

	func _restart(y: int) -> void:
		var contacts := []
		for s in ["vl", "vr"]:
			if feet[s]["mode"] == "contact":
				contacts.append(s)
		var stance := ""
		if contacts.size() == 2:
			# the boot that landed LAST stays planted; never landed (fresh idle) -> vr stays, vl (v8's back foot) lifts
			stance = "vl" if float(feet["vl"]["land_t"]) > float(feet["vr"]["land_t"]) else "vr"
		elif contacts.size() == 1:
			stance = contacts[0]
		if stance != "":
			var other := "vl" if stance == "vr" else "vr"
			var o_s: int = int(feet[stance]["wo"]) - y
			var q_s := clampi(A - o_s, 0, E)
			ref = dist - q_s - (0 if stance == "vl" else SD / 2)
			var rem := SD / 2 - q_s
			_replan(other, rem)
			events.append(["restart", "stance", stance, "lifts", other, "q_s", q_s, "remaining_px", rem])
		else:
			for s in ["vl", "vr"]:
				var rem := maxi(int(feet[s]["saved_d1"]) - dist, 12)
				_replan(s, rem)
			events.append(["restart", "no-contact", "resume frozen phase"])
		settle_t = -1.0
		done = false
		neutral_seen = false
		arms_synced = false

	func _replan(s: String, rem: int) -> void:
		var f: Dictionary = feet[s]
		var hs := clampi(IM.rdiv(8 * rem, SD - E), int(rs["replan_lift_min"]), int(rs["replan_lift_max"]))
		f["keys"] = replan_keys(int(f["o"]), int(f["lift"]), String(f["view"]), int(f["kin"]), hs)
		f["mode"] = "swing"
		f["d0"] = dist
		f["d1"] = dist + rem
		f["replanned"] = true

	func _lift(s: String, d0: int) -> void:
		var f: Dictionary = feet[s]
		f["mode"] = "swing"
		f["keys"] = g["swing_keys"]
		f["d0"] = d0
		f["d1"] = d0 + SD - E
		f["replanned"] = false
		events.append(["lift", s])

	# moving: hero window pin row y (already moved this tick by the scene's own _process)
	func tick(moving: bool, dt: float, y: int) -> Dictionary:
		clock += dt * 1000.0
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
					if o <= BK:          # same boundary as the builder: stance is o in (liftoff_offset, land_offset]
						_lift(s, dist - (BK - o))
					else:
						f["o"] = o
						f["kin"] = 1 if A - o < int(g["stance_knee_bend_px"]) else 0
				if f["mode"] == "swing":
					if dist >= int(f["d1"]):
						var over: int = dist - int(f["d1"])
						var new_ref: int = int(f["d1"]) - (0 if s == "vl" else SD / 2)
						var dref := posmod(new_ref - ref, SD)
						if mini(dref, SD - dref) > 2:
							arms_synced = false        # a re-planned landing moved the phase: ease the arms again
						ref = new_ref
						_land_contact(s, y, A - over)
					else:
						var u := IM.rdiv(1000 * (dist - int(f["d0"])), int(f["d1"]) - int(f["d0"]))
						_set_pose(f, IM.interp_keys(f["keys"], u))
			var any_c := false
			for s in ["vl", "vr"]:
				any_c = any_c or feet[s]["mode"] == "contact"
			if was_moving:          # on the re-press tick the bob holds (one change fewer in that tick)
				bob = int(g["bob_in_stance"]) if any_c else 0
			var target := {"R": _arm("R", dist - ref), "L": _arm("L", dist - ref)}
			if arms_synced:
				arms = target
			elif events.is_empty() and bob == prev_bob and views_before == [String(feet["vl"]["view"]), String(feet["vr"]["view"])]:
				# after a re-press: one arm, one pose step per tick, until both match the gait; never on a tick where a
				# boot lifts, lands or changes its view, or the bob changes
				for side in ["R", "L"]:
					if arms[side] != target[side]:
						var order := ["B1", "N", "F1"]
						var a := order.find(arms[side])
						var b := order.find(target[side])
						arms[side] = order[a + (1 if b > a else -1)]
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
			bob_t = clock
			prev_bob = bob
		var hdy := hdy_val if clock - bob_t < float(st["hair_lag_ms"]) - 1e-6 else 0
		hdy = clampi(hdy, hdy_shown - 1, hdy_shown + 1)      # the hair / cape lag moves at most one row per tick
		hdy_shown = hdy
		was_moving = moving
		last_y = y
		var state := {"bob": bob, "hdy": hdy, "arms": arms.duplicate(), "feet": {}}
		for s in ["vl", "vr"]:
			var f: Dictionary = feet[s]
			if f["mode"] == "contact":
				f["o"] = int(f["wo"]) - y
			state["feet"][s] = {"o": int(f["o"]), "lift": int(f["lift"]), "view": String(f["view"]), "kin": int(f["kin"])}
		if not was_moving and not done and started:
			var at_spot := true
			for s in ["vl", "vr"]:
				at_spot = at_spot and feet[s]["mode"] == "contact" and int(feet[s]["wo"]) == y
			if at_spot and bob == 0 and hdy == 0 and arms["R"] == "N" and arms["L"] == "N":
				# the composite of this tick already equals v8 (neutral state); the v8 PNG itself is shown from the next tick
				if neutral_seen:
					done = true
				neutral_seen = true
			else:
				neutral_seen = false
		var modes := {}
		for s in ["vl", "vr"]:
			modes[s] = String(feet[s]["mode"])
		return {"state": state, "show_v8": done, "modes": modes, "events": events.duplicate(), "phase": dist - ref, "dist": dist}

	func _start_move(s: String, kind: String, t0: float) -> void:
		var f: Dictionary = feet[s]
		var o: int = int(f["o"])
		var l: int = int(f["lift"])
		var dur := 0.0
		if kind == "land":
			f["keys"] = land_keys(o, l, String(f["view"]), int(f["kin"]))
			dur = clampf(float(st["land_ms_base"]) + float(st["land_ms_per_px"]) * absi(o) + float(st["land_ms_per_lift"]) * l,
				float(st["land_ms_base"]), float(st["land_ms_max"]))
		else:
			f["keys"] = shuffle_keys(o)
			dur = clampf(float(st["shuffle_ms_base"]) + float(st["shuffle_ms_per_px"]) * absi(o), float(st["shuffle_ms_base"]), float(st["shuffle_ms_max"]))
		f["mode"] = kind
		f["t0"] = t0
		f["dur"] = dur
		events.append([kind + "-move-start", s, o, l, dur])

	func _stop_step(y: int, dt: float) -> void:
		var landed_now := false
		var moving_feet := 0
		var prop := {}
		for s in ["vl", "vr"]:
			var f: Dictionary = feet[s]
			if f["mode"] == "land" or f["mode"] == "shuffle":
				var u := clampi(int(floor(1000.0 * (clock - float(f["t0"])) / float(f["dur"]) + 1e-6)), 0, 1000)
				prop[s] = {"land": true} if u >= 1000 else {"land": false, "pose": IM.interp_keys(f["keys"], u)}
		# at most one boot changes its view (or touches down) per tick; the other holds one tick
		var changers := []
		for s in prop:
			var nv := "v8" if bool(prop[s]["land"]) else String(prop[s]["pose"]["view"])
			if nv != String(feet[s]["view"]):
				changers.append(s)
		if changers.size() == 2:
			var hold: String = changers[1]
			if bool(prop[changers[1]]["land"]) and not bool(prop[changers[0]]["land"]):
				hold = changers[0]
			prop.erase(hold)
			feet[hold]["t0"] = float(feet[hold]["t0"]) + dt * 1000.0
			events.append(["hold-one-tick", hold])
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
					moving_feet += 1
		if moving_feet == 0 and not landed_now:
			var cand := ""
			for s in ["vl", "vr"]:
				if feet[s]["mode"] == "contact" and int(feet[s]["wo"]) != y:
					if cand == "" or int(feet[s]["wo"]) - y < int(feet[cand]["wo"]) - y:
						cand = s
			if cand != "":
				feet[cand]["o"] = int(feet[cand]["wo"]) - y
				_start_move(cand, "shuffle", clock - dt * 1000.0)
				var f: Dictionary = feet[cand]
				var u := clampi(int(floor(1000.0 * (clock - float(f["t0"])) / float(f["dur"]) + 1e-6)), 0, 1000)
				_set_pose(f, IM.interp_keys(f["keys"], u))
				moving_feet = 1
				boot_changed = true
		# arms: one arm per arm_step_ms (R first), only on a tick where no boot changes its view
		if not boot_changed and clock - last_arm_t >= float(st["arm_step_ms"]) - 1e-6:
			if arms["R"] != "N":
				arms["R"] = "N"
				last_arm_t = clock
			elif arms["L"] != "N":
				arms["L"] = "N"
				last_arm_t = clock
		var any_c := false
		var all_spot := moving_feet == 0
		for s in ["vl", "vr"]:
			any_c = any_c or feet[s]["mode"] == "contact"
			all_spot = all_spot and feet[s]["mode"] == "contact" and int(feet[s]["wo"]) == y
		if all_spot:
			if settle_t < 0.0:
				settle_t = clock
			bob = 0 if clock - settle_t >= float(st["settle_ms"]) - 1e-6 else stop_bob
		else:
			bob = stop_bob


# =====================================================================================================================
func _initialize() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("LOCO_V02_CAPTURE FAIL: " + reason)
	print("LOCO_V02_CAPTURE FAIL: " + reason)
	Input.action_release("move_down")
	quit(1)


func _user_arg(name: String) -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return ""


func _load_rgba(path: String) -> Image:
	var image := Image.load_from_file(ProjectSettings.globalize_path(path))
	if image == null:
		return null
	image.convert(Image.FORMAT_RGBA8)
	return image


func _sha_text_lf(path: String) -> String:
	var text := FileAccess.get_file_as_string(ProjectSettings.globalize_path(path)).replace("\r\n", "\n")
	var hasher := HashingContext.new()
	hasher.start(HashingContext.HASH_SHA256)
	hasher.update(text.to_utf8_buffer())
	return hasher.finish().hex_encode()


func _capture() -> Image:
	await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_viewport().get_texture().get_image()
	image.convert(Image.FORMAT_RGB8)
	return image


func _fidelity(img: Image, origin: Vector2i, cap: Image) -> Dictionary:
	var total := 0
	var exact := 0
	for y in img.get_height():
		for x in img.get_width():
			var t := img.get_pixel(x, y)
			if t.a8 == 0:
				continue
			total += 1
			var s := cap.get_pixel(origin.x + x, origin.y + y)
			if s.r8 == t.r8 and s.g8 == t.g8 and s.b8 == t.b8:
				exact += 1
	return {"opaque_texels": total, "exact_rgb_matches": exact}


# Sprite mask = window pixels that differ from the sprite-free background.  Per leg band (cell x < 38 = vl): lowest
# window row and the x extent of that row.
func _measure(cap: Image, bg: Image, origin: Vector2i, cell_h: int) -> Dictionary:
	var head := -1
	var low := {"vl": -1, "vr": -1}
	var mask := {}
	var cmask := {}      # the same pixels in cell coordinates (body frame)
	for y in cell_h:
		for x in 80:
			var px := origin + Vector2i(x, y)
			if px.x < 0 or px.y < 0 or px.x >= cap.get_width() or px.y >= cap.get_height():
				continue
			var a := cap.get_pixel(px.x, px.y)
			var b := bg.get_pixel(px.x, px.y)
			if a.r8 == b.r8 and a.g8 == b.g8 and a.b8 == b.b8:
				continue
			mask[px] = true
			cmask[Vector2i(x, y)] = true
			if head < 0 and x >= 10 and x < 70:
				head = px.y
			var side := "vl" if x < LEG_SPLIT_X else "vr"
			low[side] = maxi(low[side], px.y)
	var ext := {}
	for side in ["vl", "vr"]:
		var x0 := 1 << 30
		var x1 := -1
		for px in mask:
			if px.y == low[side] and ((px.x - origin.x < LEG_SPLIT_X) == (side == "vl")):
				x0 = mini(x0, px.x)
				x1 = maxi(x1, px.x)
		ext[side] = [x0, x1]
	return {"head_top_window_y": head, "sole_window_y": low, "sole_x_extent": ext, "mask": mask, "cell_mask": cmask}


func _xor(a: Dictionary, b: Dictionary) -> int:
	var n := 0
	for k in a:
		if not b.has(k):
			n += 1
	for k in b:
		if not a.has(k):
			n += 1
	return n


func _instantiate(spec: Array) -> Node2D:
	app.begin_new_run()
	app.hero_appearance = "female"
	if not app.select_destination(String(spec[1])):
		_fail("destination rejected: " + String(spec[1]))
		return null
	if spec[0] == "annex":
		app.current_annex_room = int(spec[2])
		app.resume_annex_pending = false
	var host: Node2D = (load(AREA_SCENE if spec[0] == "area" else ANNEX_SCENE) as PackedScene).instantiate()
	root.add_child(host)
	current_scene = host
	await process_frame
	await process_frame
	host.set_process(false)
	if String(host.get("destination_id")) != String(spec[1]):
		_fail("scene fell back to " + String(host.get("destination_id")))
		return null
	return host


func _setup(spec: Array) -> Array:
	var host: Node2D = await _instantiate(spec)
	if host == null:
		return []
	var hero: Sprite2D = host.get("hero")
	hero.position = spec[3]
	var ph := hero.texture.get_image()
	ph.convert(Image.FORMAT_RGBA8)
	var ph_bottom := 0
	for y in ph.get_height():
		for x in ph.get_width():
			if ph.get_pixel(x, y).a8 >= 128:
				ph_bottom = y + 1
	var ground_off := floorf(hero.offset.y - ph.get_height() * 0.5 + ph_bottom)
	hero.visible = false
	var pilot := Sprite2D.new()
	pilot.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	pilot.centered = false
	pilot.offset = -Vector2(PIN)
	pilot.scale = Vector2(0.5, 0.5)
	pilot.visible = false
	host.add_child(pilot)
	var bg := await _capture()
	if bg.get_size() != Vector2i(1280, 720):
		_fail("capture size " + str(bg.get_size()))
		return []
	pilot.visible = true
	return [host, hero, pilot, ground_off, bg]


func _pin(hero: Sprite2D, ground_off: float) -> Vector2i:
	return Vector2i(int(round(hero.position.x * 2.0)), int(round((hero.position.y + ground_off) * 2.0)))


func _draw_capture(pilot: Sprite2D, tex: Texture2D, hero: Sprite2D, ground_off: float) -> Array:
	hero.visible = false
	var p := _pin(hero, ground_off)
	pilot.texture = tex
	pilot.position = Vector2(p.x * 0.5, p.y * 0.5)
	pilot.z_index = int(hero.position.y)
	var cap := await _capture()
	return [cap, p - PIN]


func _free(host: Node) -> void:
	host.queue_free()
	await process_frame
	await process_frame


func _out_name(scene_key: String, what: String, stamp: String, uid: String, ext: String) -> String:
	return "%s_%s_protagonist-female-south-locomotion-compact-v02-%s-h48_%s_%s-%s.%s" % [SLUG, scene_key, what, VARIANT, stamp, uid, ext]


# Drives one sequence.  plan: Array of {"input": bool, "dt": float}.  Returns per-tick records.
func _drive(su: Array, plan: Array, motion_dir: String, tag: String, crop: Rect2i, full_saves: Dictionary = {}) -> Array:
	var host: Node2D = su[0]
	var hero: Sprite2D = su[1]
	var pilot: Sprite2D = su[2]
	var ground_off: float = su[3]
	var bg: Image = su[4]
	var loco := Loco.new()
	loco.setup(manifest, _pin(hero, ground_off).y)
	var ticks := []
	for t in plan.size():
		var step: Dictionary = plan[t]
		var before := hero.position
		if bool(step["input"]):
			Input.action_press("move_down")
		else:
			Input.action_release("move_down")
		host.call("_process", float(step["dt"]))
		hero.visible = false
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
		var info := {}
		if bool(r["show_v8"]):
			img = v8_image
			tex = v8_tex
		else:
			var c := comp.compose(r["state"])
			if c.has("error"):
				_fail("%s tick %d: %s" % [tag, t, c["error"]])
				return []
			img = c["image"]
			tex = ImageTexture.create_from_image(img)
			info = c
		var dc: Array = await _draw_capture(pilot, tex, hero, ground_off)
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
		var meas := _measure(cap, bg, origin, img.get_height())
		# planted boots: window texels of the boot (expected) and which of them are visible with the boot's colour
		# planted boots: expected world texels (window pos -> rgb) and how many of them are visible with that colour
		var boots_w := {}
		for s in ["vl", "vr"]:
			if r["modes"][s] == "contact":
				var src: Dictionary = info["boots"][s] if not info.is_empty() else v8_boot[s]
				var world := {}
				var vis := 0
				for q in src:
					var w: Vector2i = origin + q
					var bc: Color = src[q]
					world[w] = bc.to_html(false)
					var cc := cap.get_pixelv(w)
					if cc.r8 == bc.r8 and cc.g8 == bc.g8 and cc.b8 == bc.b8:
						vis += 1
				boots_w[s] = {"world": world, "visible": vis}
		ticks.append({"tick": t, "input": bool(step["input"]), "dt": float(step["dt"]), "show_v8": bool(r["show_v8"]),
			"modes": r["modes"], "state": r["state"], "events": r["events"], "phase": r["phase"], "dist": r["dist"],
			"hero_logical": [hero.position.x, hero.position.y], "origin": origin, "meas": meas, "boots_w": boots_w,
			"cell_h": img.get_height()})
	Input.action_release("move_down")
	return ticks


var v8_boot := {}     # side -> {Vector2i cell: Color}


# Per-tick summary: planted-boot world displacement (pixels), airborne steps, silhouette XOR, crown step.
func _summ(ticks: Array) -> Array:
	var out := []
	var prev: Dictionary = {}
	for tk in ticks:
		var m: Dictionary = tk["meas"]
		var e := {"tick": tk["tick"], "input": tk["input"], "show_v8": tk["show_v8"], "modes": tk["modes"], "state": tk["state"],
			"events": tk["events"], "phase": tk["phase"], "hero_logical": tk["hero_logical"], "pin_window_y": tk["origin"].y + PIN.y,
			"head_top_window_y": m["head_top_window_y"], "sole_window_y": m["sole_window_y"], "sole_x_extent": m["sole_x_extent"],
			"lowest_cell_row": maxi(m["sole_window_y"]["vl"], m["sole_window_y"]["vr"]) - tk["origin"].y}
		if not prev.is_empty():
			e["head_step"] = m["head_top_window_y"] - prev["meas"]["head_top_window_y"]
			e["silhouette_xor"] = _xor(m["mask"], prev["meas"]["mask"])                 # window frame (includes body travel)
			e["cell_silhouette_xor"] = _xor(m["cell_mask"], prev["meas"]["cell_mask"])   # body frame (pose change only)
			var pl := {}
			for s in ["vl", "vr"]:
				if tk["modes"][s] == "contact" and prev["modes"][s] == "contact" and tk["boots_w"].has(s) and prev["boots_w"].has(s):
					var a: Dictionary = prev["boots_w"][s]["world"]
					var b: Dictionary = tk["boots_w"][s]["world"]
					var same := 0
					for k in b:
						if a.has(k) and a[k] == b[k]:
							same += 1
					pl[s] = {"sole_row_d": int(m["sole_window_y"][s]) - int(prev["meas"]["sole_window_y"][s]),
						"sole_x0_d": int(m["sole_x_extent"][s][0]) - int(prev["meas"]["sole_x_extent"][s][0]),
						"sole_x1_d": int(m["sole_x_extent"][s][1]) - int(prev["meas"]["sole_x_extent"][s][1]),
						"boot_texels_prev": a.size(), "boot_texels_now": b.size(), "boot_texels_same_world_pos_and_rgb": same,
						"boot_texels_visible_now": tk["boots_w"][s]["visible"]}
			e["planted"] = pl
			var air := {}
			for s in ["vl", "vr"]:
				if not (tk["modes"][s] == "contact" and prev["modes"][s] == "contact"):
					air[s] = int(m["sole_window_y"][s]) - int(prev["meas"]["sole_window_y"][s])
			e["unplanted_sole_row_step"] = air
		out.append(e)
		prev = tk
	return out


func _planted_stats(summ: Array, from_i: int, to_i: int) -> Dictionary:
	var n := 0
	var row_max := 0
	var x_max := 0
	var tex_lost := 0
	var tex_total := 0
	var vis_total := 0
	var air_max := 0
	var xor_max := 0
	var cxor_max := 0
	var head_max := 0
	var per_contact := {}
	for i in range(maxi(1, from_i), mini(summ.size(), to_i)):
		var e: Dictionary = summ[i]
		xor_max = maxi(xor_max, int(e.get("silhouette_xor", 0)))
		cxor_max = maxi(cxor_max, int(e.get("cell_silhouette_xor", 0)))
		head_max = maxi(head_max, absi(int(e.get("head_step", 0))))
		for s in e.get("planted", {}):
			var p: Dictionary = e["planted"][s]
			n += 1
			row_max = maxi(row_max, absi(int(p["sole_row_d"])))
			x_max = maxi(x_max, maxi(absi(int(p["sole_x0_d"])), absi(int(p["sole_x1_d"]))))
			tex_total += int(p["boot_texels_now"])
			tex_lost += maxi(int(p["boot_texels_now"]), int(p["boot_texels_prev"])) - int(p["boot_texels_same_world_pos_and_rgb"])
			vis_total += int(p["boot_texels_visible_now"])
		for s in e.get("unplanted_sole_row_step", {}):
			air_max = maxi(air_max, absi(int(e["unplanted_sole_row_step"][s])))
	return {"planted_tick_pairs": n, "planted_sole_row_world_disp_max_px": row_max, "planted_sole_x_world_disp_max_px": x_max,
		"planted_boot_texels_compared": tex_total, "planted_boot_texels_changed": tex_lost,
		"planted_boot_texels_visible_on_screen": vis_total,
		"unplanted_sole_row_step_max_px": air_max, "silhouette_xor_max_per_tick": xor_max, "cell_silhouette_xor_max_per_tick": cxor_max, "head_step_max_px": head_max}


func _plan_walk(n: int, fps: int) -> Array:
	var plan := [{"input": false, "dt": 1.0 / fps}]
	for i in n:
		plan.append({"input": true, "dt": 1.0 / fps})
	return plan


func _crop_for(su: Array, travel_px: int) -> Rect2i:
	var p := _pin(su[1], su[3])
	return Rect2i(p.x - 80, p.y - 140, 160, 140 + travel_px + 40)


func _run() -> void:
	if DisplayServer.get_name() == "headless":
		_fail("windowed run required")
		return
	var motion_dir := _user_arg("motion-dir")
	if motion_dir == "" or DirAccess.make_dir_recursive_absolute(motion_dir) != OK:
		_fail("pass -- --motion-dir=<absolute scratch dir>")
		return
	var only := _user_arg("only")     # optional: a single scene key (debug)
	var mpath := ASSET_DIR + MANIFEST
	var mdigest := _sha_text_lf(mpath)
	manifest = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path(mpath)))
	for flag in ["art_approved", "human_reviewed", "runtime_integrated", "walk_animation_approved", "stop_animation_approved",
			"counts_toward_art_acceptance"]:
		if bool(manifest[flag]):
			_fail("manifest flag %s must stay false" % flag)
			return
	var disp: Dictionary = manifest["display"]
	if float(disp["scale"]) != 0.5 or int(disp["logical_height_px"]) != 48 or bool(disp["flip_h"]):
		_fail("display block is not 48 px / 0.5 / no flip")
		return
	var sources := {"manifest": {"path": mpath, "sha256_text_lf_v1": mdigest}, "parts": {}, "keyframes": {}}
	for e in manifest["parts"] + manifest["keyframes"]:
		var dg := FileAccess.get_sha256(ProjectSettings.globalize_path(ASSET_DIR + String(e["file"])))
		if dg != String(e["sha256"]):
			_fail("%s sha256 mismatch" % String(e["file"]))
			return
	if FileAccess.get_sha256(ProjectSettings.globalize_path(V8_PATH)) != V8_SHA256:
		_fail("v8 sha256 mismatch")
		return
	sources["v8"] = V8_SHA256
	sources["parts_count"] = (manifest["parts"] as Array).size()
	sources["keyframes_count"] = (manifest["keyframes"] as Array).size()
	v8_image = _load_rgba(V8_PATH)
	v8_tex = ImageTexture.create_from_image(v8_image)
	comp = PartCompositor.new()
	var err := comp.load_parts(manifest["parts"], ASSET_DIR, manifest["rig"])
	if err != "":
		_fail(err)
		return
	for q in comp.parts["boot-vl-v8"]:
		v8_boot.get_or_add("vl", {})[q[0]] = q[1]
	for q in comp.parts["boot-vr-v8"]:
		v8_boot.get_or_add("vr", {})[q[0]] = q[1]
	# ---------------------------------------------------------------- compositor parity gates
	var parity := {}
	var neutral := {"bob": 0, "hdy": 0, "arms": {"R": "N", "L": "N"},
		"feet": {"vl": {"o": 0, "lift": 0, "view": "v8", "kin": 0}, "vr": {"o": 0, "lift": 0, "view": "v8", "kin": 0}}}
	var nimg: Image = comp.compose(neutral)["image"]
	var v8_pad := Image.create_empty(80, 120, false, Image.FORMAT_RGBA8)
	v8_pad.blit_rect(v8_image, Rect2i(0, 0, 80, 112), Vector2i.ZERO)
	if nimg.get_data() != v8_pad.get_data():
		_fail("GDScript neutral composition != v8")
		return
	parity["neutral_equals_v8"] = true
	for k in manifest["keyframes"]:
		var ref_img := _load_rgba(ASSET_DIR + String(k["file"]))
		var c := comp.compose(k["state"])
		if c.has("error") or (c["image"] as Image).get_data() != ref_img.get_data():
			_fail("GDScript compositor != builder keyframe " + String(k["key"]))
			return
	parity["keyframes_equal_builder_pngs"] = (manifest["keyframes"] as Array).size()
	print("PARITY neutral == v8, %d keyframes == builder PNGs" % parity["keyframes_equal_builder_pngs"])
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
	var out_abs := _user_arg("out-dir") if _user_arg("out-dir") != "" else ProjectSettings.globalize_path(OUTPUT_DIR)   # --out-dir: scratch debug runs
	var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var uid := "%08x" % (randi() & 0xffffffff)
	SaveStore.root_path = "user://test-saves/m8-south-locomotion-compact-v02-capture"
	app = root.get_node("AppState")
	var outputs := {}
	var report_scenes := {}
	var steady_checked := 0
	for scene_key in SCENES.keys():
		if only != "" and scene_key != only:
			continue
		var spec: Array = SCENES[scene_key]
		var sr := {"kind": spec[0], "destination": spec[1], "annex_room": spec[2], "note": spec[4], "walk": {}, "stops": {}, "repress": {}}
		# ---------------------------------------------------------------- stills at one pin: v8 + the 12 keyframes
		var su: Array = await _setup(spec)
		if su.is_empty():
			return
		var stills := []
		var items := [["v8-idle-reference", v8_image, v8_tex]]
		for k in manifest["keyframes"]:
			var im := _load_rgba(ASSET_DIR + String(k["file"]))
			items.append(["keyframe-phase-%02dpx" % int(k["phase_px"]), im, ImageTexture.create_from_image(im)])
		for it in items:
			var dc: Array = await _draw_capture(su[2], it[2], su[1], su[3])
			var cap: Image = dc[0]
			var fid := _fidelity(it[1], dc[1], cap)
			if fid["exact_rgb_matches"] != fid["opaque_texels"]:
				_fail("%s still %s fidelity %s" % [scene_key, it[0], str(fid)])
				return
			var save: bool = scene_key == "city-bright" or String(it[0]) in ["v8-idle-reference", "keyframe-phase-00px", "keyframe-phase-24px", "keyframe-phase-48px", "keyframe-phase-72px"]
			var name := _out_name(scene_key, "still-" + String(it[0]), stamp, uid, "png")
			if save:
				cap.save_png(out_abs.path_join(name))
				outputs[name] = {"kind": "still", "scene": scene_key}
			stills.append({"frame": it[0], "fidelity": fid, "capture": name if save else null})
		sr["stills"] = stills
		await _free(su[0])
		# ---------------------------------------------------------------- walks at 30 / 60 / 144 fps
		for mode in WALK_MODES.keys():
			var wm: Array = WALK_MODES[mode]
			su = await _setup(spec)
			if su.is_empty():
				return
			var start_y: float = su[1].position.y
			var crop := _crop_for(su, 240) if mode == "walk-60fps" else Rect2i()
			var ticks := await _drive(su, _plan_walk(int(wm[0]), int(wm[1])), motion_dir, "%s_%s" % [scene_key, mode], crop)
			if ticks.is_empty():
				return
			var summ := _summ(ticks)
			var stats := _planted_stats(summ, 1, summ.size())
			if stats["planted_sole_row_world_disp_max_px"] != 0 or stats["planted_sole_x_world_disp_max_px"] != 0 or stats["planted_boot_texels_changed"] != 0:
				_fail("%s %s planted boot moved in world space %s" % [scene_key, mode, str(stats)])
				return
			# steady state (after the first full stride) must equal the manifest's per-px table
			for tk in ticks:
				if not bool(tk["input"]) or int(tk["dist"]) < int(manifest["gait"]["stride_px"]) + 48:
					continue
				var row: Dictionary = per_px[posmod(int(tk["phase"]), per_px.size())]
				var stt: Dictionary = tk["state"]
				var ok: bool = int(row["bob"]) == int(stt["bob"]) and row["arms"]["R"] == stt["arms"]["R"] and row["arms"]["L"] == stt["arms"]["L"]
				for s in ["vl", "vr"]:
					for f in ["o", "lift", "kin"]:
						ok = ok and int(row["feet"][s][f]) == int(stt["feet"][s][f])
					ok = ok and String(row["feet"][s]["view"]) == String(stt["feet"][s]["view"])
				if not ok:
					_fail("%s %s tick %d: steady gait %s != manifest per-px %s" % [scene_key, mode, int(tk["tick"]), str(stt), str(row)])
					return
				steady_checked += 1
			stats["logical_px_per_s_measured"] = (su[1].position.y - start_y) / (float(int(wm[0])) / float(wm[1]))
			stats["crop"] = [crop.position.x, crop.position.y, crop.size.x, crop.size.y]
			stats["ticks"] = summ
			var contacts := []     # world rows per contact run (pixels)
			for s in ["vl", "vr"]:
				var run := []
				for e in summ:
					if e["modes"][s] == "contact" and bool(e["input"]):
						run.append(int(e["sole_window_y"][s]))
					elif not run.is_empty():
						contacts.append({"side": s, "ticks": run.size(), "world_row_min": run.min(), "world_row_max": run.max()})
						run = []
			stats["contact_runs"] = contacts
			sr["walk"][mode] = stats
			print("WALK %s %s ticks %d speed %.3f planted pairs %d row-disp %d x-disp %d texels-changed %d cell-xor-max %d" % [scene_key, mode,
				ticks.size(), stats["logical_px_per_s_measured"], stats["planted_tick_pairs"], stats["planted_sole_row_world_disp_max_px"],
				stats["planted_sole_x_world_disp_max_px"], stats["planted_boot_texels_changed"], stats["cell_silhouette_xor_max_per_tick"]])
			await _free(su[0])
		# ---------------------------------------------------------------- immediate stops from every tick of one stride
		var fps_list := [60] if scene_key != "city-bright" else [60, 30, 144]
		for fps in fps_list:
			var dt: float = 1.0 / fps
			var per_tick_px: float = 280.0 / fps
			var first := int(ceil((96.0 + 8.0) / per_tick_px))         # release inside the 2nd stride
			var count := int(ceil(96.0 / per_tick_px))
			var step := 1 if fps != 144 else 3
			for k in range(0, count, step):
				var n_walk: int = first + k
				su = await _setup(spec)
				if su.is_empty():
					return
				var plan := _plan_walk(n_walk, fps)
				for i in int(0.45 * fps):
					plan.append({"input": false, "dt": dt})
				var tag := "%s_stop-%dfps-%03d" % [scene_key, fps, n_walk]
				var save_motion: bool = fps == 60
				var crop := _crop_for(su, int(n_walk * per_tick_px) + 10) if save_motion else Rect2i()
				var full := {}
				if fps == 60 and n_walk in STILL_STOP_CASES:
					var rel0: int = n_walk + 1
					for pk in [[rel0 - 1, "1-last-move-tick"], [rel0 + 2, "2-stop-plus-2-ticks"], [rel0 + 5, "3-stop-plus-5-ticks"], [plan.size() - 1, "4-v8-idle"]]:
						var nm := _out_name(scene_key, "stop-%s-%s" % [String(STILL_STOP_CASES[n_walk]), pk[1]], stamp, uid, "png")
						full[int(pk[0])] = out_abs.path_join(nm)
						outputs[nm] = {"kind": "stop-still", "scene": scene_key, "tick": int(pk[0])}
				var ticks := await _drive(su, plan, motion_dir if save_motion else "", tag, crop, full)
				if ticks.is_empty():
					return
				var summ := _summ(ticks)
				var rel: int = n_walk + 1
				var ws := _planted_stats(summ, 1, rel)
				var ss := _planted_stats(summ, rel, summ.size())
				if ss["planted_sole_row_world_disp_max_px"] != 0 or ss["planted_sole_x_world_disp_max_px"] != 0 or ss["planted_boot_texels_changed"] != 0 \
						or ws["planted_sole_row_world_disp_max_px"] != 0 or ws["planted_boot_texels_changed"] != 0:
					_fail("%s planted boot moved %s %s" % [tag, str(ws), str(ss)])
					return
				var v8_at := -1
				for i in range(rel, ticks.size()):
					if bool(ticks[i]["show_v8"]):
						v8_at = i
						break
				if v8_at < 0:
					_fail("%s: never returned to v8" % tag)
					return
				# composite on the tick before v8 must already equal v8 (no pop at the switch)
				var pop := _xor(ticks[v8_at]["meas"]["mask"], ticks[v8_at - 1]["meas"]["mask"])
				var last: Dictionary = ticks[rel - 1]
				var rec := {"fps": fps, "release_tick": rel, "released_at_phase_px": posmod(int(last["phase"]), 96),
					"modes_at_release": last["modes"], "state_at_release": last["state"],
					"v8_after_ms": 1000.0 * (v8_at - rel + 1) * dt, "switch_to_v8_xor": pop,
					"walk": ws, "stop": ss, "events": [], "crop": [crop.position.x, crop.position.y, crop.size.x, crop.size.y]}
				for i in range(rel, v8_at + 1):
					for ev in ticks[i]["events"]:
						rec["events"].append([i - rel] + ev)
				rec["ticks"] = summ.slice(maxi(0, rel - 8), mini(summ.size(), v8_at + 3))
				sr["stops"][tag] = rec
				print("STOP %s phase %d modes %s -> v8 after %.0f ms, stop cell-xor-max %d walk cell-xor-max %d, switch xor %d, air-step max %d" % [tag,
					rec["released_at_phase_px"], str(last["modes"]), rec["v8_after_ms"], ss["cell_silhouette_xor_max_per_tick"],
					ws["cell_silhouette_xor_max_per_tick"], pop, ss["unplanted_sole_row_step_max_px"]])
				if pop != 0:
					_fail("%s: switch to v8 changed %d pixels" % [tag, pop])
					return
				await _free(su[0])
		# ---------------------------------------------------------------- re-press: release at 6 phases x re-press after k ticks
		var rel_walk := [12, 16, 20, 24, 28, 32] if scene_key == "city-bright" else [16, 24, 32]
		var gaps := [1, 2, 3, 5, 8, 14, 30] if scene_key == "city-bright" else [1, 3, 8, 30]
		for n_walk in rel_walk:
			for gap in gaps:
				su = await _setup(spec)
				if su.is_empty():
					return
				var dt := 1.0 / 60.0
				var plan := _plan_walk(n_walk, 60)
				for i in gap:
					plan.append({"input": false, "dt": dt})
				for i in 18:
					plan.append({"input": true, "dt": dt})
				for i in 4:
					plan.append({"input": false, "dt": dt})
				var tag := "%s_repress-%03d-gap-%02d" % [scene_key, n_walk, gap]
				var save_motion: bool = gap in ([1, 3, 8, 30] if scene_key == "city-bright" else [1, 8])
				var crop := _crop_for(su, int((n_walk + 18) * 280.0 / 60.0) + 10) if save_motion else Rect2i()
				var ticks := await _drive(su, plan, motion_dir if save_motion else "", tag, crop)
				if ticks.is_empty():
					return
				var summ := _summ(ticks)
				var rel: int = n_walk + 1
				var rp: int = rel + gap
				var all_st := _planted_stats(summ, 1, summ.size())
				if all_st["planted_sole_row_world_disp_max_px"] != 0 or all_st["planted_boot_texels_changed"] != 0:
					_fail("%s planted boot moved %s" % [tag, str(all_st)])
					return
				# which boot touched down last before the re-press, and which one lifts first after it
				var last_land := ""
				var last_land_tick := -1
				for i in range(1, rp):
					for ev in ticks[i]["events"]:
						if String(ev[0]) == "land":
							last_land = String(ev[1])
							last_land_tick = i
				var first_lift := ""
				var first_lift_ms := -1.0
				var next_land := ""
				var next_land_ms := -1.0
				var last_land_planted_ms := -1.0
				for i in range(rp, ticks.size()):
					for s in ["vl", "vr"]:
						if first_lift == "" and ticks[i - 1]["modes"][s] == "contact" and ticks[i]["modes"][s] != "contact":
							first_lift = s
							first_lift_ms = 1000.0 * (i - rp) * dt
					for ev in ticks[i]["events"]:
						if next_land == "" and String(ev[0]) == "land":
							next_land = String(ev[1])
							next_land_ms = 1000.0 * (i - rp) * dt
					if last_land != "" and last_land_planted_ms < 0.0 and ticks[i]["modes"][last_land] != "contact":
						last_land_planted_ms = 1000.0 * (i - rp) * dt
				var planted_at_rp: bool = last_land != "" and ticks[rp - 1]["modes"][last_land] == "contact"
				var alternation_ok: bool = last_land == "" or next_land != last_land
				# how long the last-landed boot stood (touchdown -> lift-off, across the stop): a boot that lands in the stop
				# and is lifted again on the re-press would show a stand of only the gap
				var stood_ms := -1.0
				if last_land != "":
					for i in range(last_land_tick + 1, ticks.size()):
						if ticks[i]["modes"][last_land] != "contact":
							stood_ms = 1000.0 * (i - last_land_tick) * dt
							break
				var rr := _planted_stats(summ, rp, mini(summ.size(), rp + 12))
				var rec := {"release_tick": rel, "repress_tick": rp, "gap_ticks": gap, "released_at_phase_px": posmod(int(ticks[rel - 1]["phase"]), 96),
					"modes_at_repress": ticks[rp - 1]["modes"], "showing_v8_at_repress": bool(ticks[rp - 1]["show_v8"]),
					"last_touchdown_before_repress": last_land, "first_boot_to_lift_after_repress": first_lift,
					"first_lift_ms_after_repress": first_lift_ms, "next_touchdown_after_repress": next_land,
					"next_touchdown_ms_after_repress": next_land_ms, "last_landed_boot_planted_at_repress": planted_at_rp,
					"last_landed_boot_stays_planted_ms_after_repress": last_land_planted_ms,
					"alternation_ok_next_touchdown_is_the_other_boot": alternation_ok, "last_landed_boot_stood_ms_touchdown_to_liftoff": stood_ms,
					"repress_200ms": rr, "events": [], "crop": [crop.position.x, crop.position.y, crop.size.x, crop.size.y]}
				for i in range(rel, mini(ticks.size(), rp + 14)):
					for ev in ticks[i]["events"]:
						rec["events"].append([i - rel] + ev)
				rec["ticks"] = summ.slice(maxi(0, rel - 6), mini(summ.size(), rp + 24))
				sr["repress"][tag] = rec
				if not alternation_ok:
					_fail("%s: re-press broke alternation (last down %s, next down %s)" % [tag, last_land, next_land])
					return
				print("REPRESS %s phase %d gap %d: last down %s (stood %.0f ms, %.0f ms after re-press), next down %s at %.0f ms, cell-xor-max %d air-step %d" % [tag,
					rec["released_at_phase_px"], gap, last_land, stood_ms, last_land_planted_ms, next_land, next_land_ms,
					rr["cell_silhouette_xor_max_per_tick"], rr["unplanted_sole_row_step_max_px"]])
				await _free(su[0])
		report_scenes[scene_key] = sr
	for nm in outputs:
		outputs[nm]["sha256_bytes"] = FileAccess.get_sha256(out_abs.path_join(nm))
	var report := {
		"project": "Worlds Between", "milestone": "M8",
		"purpose": "TEST-ONLY real-Godot captures of the UNAPPROVED / NONRUNTIME female south compact locomotion pilot v02 (part library + test-only compositor) moved by the scenes' own _process at MOVE_SPEED 140",
		"status": "UNAPPROVED / NONRUNTIME; not art acceptance; Codex / creator visual decision pending",
		"art_approved": false, "human_reviewed": false, "runtime_integrated": false,
		"approved_scope_unchanged": "selout v8 SOUTH IDLE static frame and the 48 logical px display scale only",
		"capture_tool": "tools/rpg-2-star-ocean-the-second_protagonist-female_south-locomotion-compact-v02-godot-capture_m8-w05_20261016-200500-a29fc892.gd",
		"renderer": "Godot %s windowed, viewport texture capture" % Engine.get_version_info()["string"],
		"canvas": [640, 360], "window": [1280, 720], "sprite_scale": 0.5, "filter": "nearest (CanvasItem.TEXTURE_FILTER_NEAREST)", "shadow": "none drawn",
		"move_speed_logical_px_s": move_speeds, "sources": sources, "parity": parity, "steady_state_ticks_checked": steady_checked,
		"gates_passed": ["manifest + part / keyframe PNG + v8 hash locks", "flags false", "MOVE_SPEED 140", "1280x720",
			"GDScript compositor == v8 (neutral) and == all builder keyframes", "steady-state gait == manifest per-px table",
			"exact-RGB fidelity of the drawn image on every captured tick", "straight-south movement; hero stationary without input",
			"planted boot: 0 px world displacement of lowest row and sole x-extent, 0 visible boot texels changed (walk 30/60/144, every stop, every re-press)",
			"every stop returns to the v8 PNG with 0 changed pixels at the switch",
			"every re-press: the next touchdown is the other boot (no boot touches down twice in a row)"],
		"outputs": outputs, "scenes": report_scenes,
	}
	var rname := "%s_city-outskirts-annex_protagonist-female-south-locomotion-compact-v02-capture-receipt-h48_%s_%s-%s.json" % [SLUG, VARIANT, stamp, uid]
	var f := FileAccess.open(out_abs.path_join(rname), FileAccess.WRITE)
	f.store_string(JSON.stringify(report, " ") + "\n")
	f.close()
	print("RECEIPT " + rname)
	print("STAMP %s-%s" % [stamp, uid])
	quit(0)
