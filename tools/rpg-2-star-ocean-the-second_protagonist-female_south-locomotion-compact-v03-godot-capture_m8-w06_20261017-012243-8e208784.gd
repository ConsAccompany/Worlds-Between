extends SceneTree

# TEST-ONLY real-Godot capture of the UNAPPROVED / NONRUNTIME female SOUTH RUN motion pilot v03 (m8-w06, single direction).
# Review evidence only: not art acceptance, not runtime integration, not a production sprite.  The creator approved only
# the selout v8 SOUTH IDLE static frame and the 48 logical px display scale; motion is not approved.  Lives in tools/
# (outside res://), so no game/ file is added or edited, and no runtime script is changed.  Run windowed from the
# repository root (the project renders its 640x360 canvas into the 1280x720 window, integer canvas_items stretch):
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path of this file> -- --motion-dir=<abs scratch>
#
# Started as a copy of the v02 capture tool (tools/...south-locomotion-compact-v02-godot-capture_m8-w05_20261016-200500-a29fc892.gd).
# The hidden runtime hero is moved by each scene's OWN _process(delta) with "move_down" held (MOVE_SPEED 140, asserted).
# A TEST-ONLY compositor (PartCompositor, a port of compose() in the v03 builder) stacks the v03 part PNGs every tick; a
# TEST-ONLY gait driver (Loco) decides foot / torso / arm states from the manifest's gait keys, stop rule and re-press rule:
#   * body at the logical position (no root lock); a boot in contact keeps the window row fixed when it landed and rolls
#     strike -> v8 -> heelup -> toe on that row; swing lift <= 3 rows;
#   * shoulders / torso / scarf / arms shift 1 texel toward the planted boot; head steady; cape follows the shift late;
#   * a separate contact-shadow sprite (single ink colour, opacity from the manifest) is drawn UNDER the character, also
#     under the v8 idle, so it never pops at the stop;
#   * release: airborne boots land on their v8 spots (lift <= 2), then off-spot planted boots take one low step, with a
#     torso weight shift and a 1-row settle dip; then the v8 PNG itself;
#   * re-press: the boot that landed LAST stays planted; the other one is re-planned from where it is.
# Gates (exit 1): manifest sha256-text-lf-v1 + every PNG + v8 sha256-bytes; flags false; MOVE_SPEED 140; 1280x720 window;
# GDScript compositor == builder keyframe PNGs and shadow PNGs (all 12) and == v8 at the neutral state; steady-state gait ==
# the manifest's per-px table; exact-RGB fidelity of the drawn character on every captured tick; straight-south movement;
# hero stationary without input; MEASURED ON CAPTURED PIXELS: a boot in contact on two consecutive ticks keeps its lowest
# window row (and, while its view does not change, its sole-row x-extent and every visible boot texel); every stop returns
# to the v8 PNG with 0 changed character pixels; no boot stays raised longer than the stop limit; re-press alternation.
const ASSET_DIR := "res://assets/characters/run-v03-unapproved/"
const MANIFEST := "rpg-2-star-ocean-the-second_protagonist-female_south-run-v03-manifest_unapproved-nonruntime_20261017-012243-3a29a732.json"
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
	"annex-dark": ["annex", "scifi.city", 2, Vector2(240, 150), "city survey annex room 2, darkest annex floor"],
}
const WALK_MODES := {"walk-60fps": [50, 60], "walk-30fps": [25, 30], "walk-144fps": [120, 144]}   # 0.83 s, 117 logical px
const OUTPUT_DIR := "res://../outputs"
const SLUG := "rpg-2-star-ocean-the-second"
const VARIANT := "unapproved-nonruntime"
const STILL_STOP_CASES := {30: "stance", 36: "flight"}   # 60 fps release ticks saved as full 1280x720 stills
const STOP_RAISED_LIMIT_MS := 100.0     # gate: after a release no boot stays off the floor longer than this
const STANCE := ["strike", "v8", "heelup", "toe"]
const POSES := ["B2", "B1", "N", "F1", "F2"]

var app: Node
var manifest: Dictionary
var comp: PartCompositor
var v8_image: Image
var v8_tex: Texture2D
var v8_shadow_image: Image
var v8_shadow_tex: Texture2D
var shadow_alpha := 0.38


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


	static func in_contact(foot: Dictionary) -> bool:
		return int(foot["lift"]) == 0 and String(foot["view"]) in ["strike", "v8", "heelup", "toe"]


# =====================================================================================================================
# TEST-ONLY part compositor: port of compose() / compose_leg() / leg_rows_plan() / pinhole_fill() / seam_fill() in the
# v03 builder.
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
		var full := T.size() + K.size() + S.size()
		if n < full:
			if n < knee_min + 2:
				return []
			var nk := maxi(knee_min, IM.rdiv(n * K.size(), full))
			var nt := maxi(1, IM.rdiv((n - nk) * T.size(), T.size() + S.size()))
			var ns := n - nk - nt
			if ns < 1:
				nt -= 1 - ns
				ns = 1
			if nt < 1:
				return []
			return [IM.pick(T, nt), IM.pick(K, nk), IM.pick(S, ns)]
		var rest := n - K.size()
		var nt2 := maxi(1, mini(rest - 1, IM.rdiv(rest * T.size(), T.size() + S.size())))
		return [IM.pick(T, nt2), K, IM.pick(S, rest - nt2)]

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

	func near_leg(feet: Dictionary) -> String:
		var cl := IM.in_contact(feet["vl"])
		var cr := IM.in_contact(feet["vr"])
		if cl != cr:
			return "vl" if not cl else "vr"
		return "vl" if int(feet["vl"]["o"]) > int(feet["vr"]["o"]) else "vr"

	func _put(g: Dictionary, role: String, dx: int, b: int) -> void:
		for p in parts[role]:
			g[p[0] + Vector2i(dx, b)] = p[1]

	# -> {"image", "shadow", "boots", "soles", "near"} or {"error": ...}
	func compose(state: Dictionary) -> Dictionary:
		var b: int = int(state["bob"])
		var h: int = int(state["hdy"])
		var sx: int = int(state["sx"])
		var csx: int = int(state["csx"])
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
		_put(g, "cape-hdy-" + String(hdy_tag[h]), csx, b)
		_put(g, "arm-vl-%s-back" % R, sx, b)
		_put(g, "arm-vr-%s-back" % L, sx, b)
		var legmask := {}
		for p in parts["hips"]:
			legmask[p[0] + Vector2i(0, b)] = true
		_put(g, "hips", 0, b)
		for q in legs[far]:
			g[q] = legs[far][q]
			legmask[q] = true
		for q in legs[near]:
			g[q] = legs[near][q]
			legmask[q] = true
		_put(g, "coat-skirt", sx, b)
		_put(g, "torso", sx, b)
		_put(g, "arm-vl-%s-seam" % R, sx, b)
		_put(g, "arm-vr-%s-seam" % L, sx, b)
		_put(g, "head", 0, b)
		_put(g, "hair-hdy-" + String(hdy_tag[h]), 0, b)
		_put(g, "arm-vl-%s-front" % R, sx, b)
		_put(g, "arm-vr-%s-front" % L, sx, b)
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
		if sx != 0:
			var seams := []
			for y in range(28 + b, 41 + b):
				for x in range(1, W - 1):
					var q := Vector2i(x, y)
					if not g.has(q) and g.has(Vector2i(x - 1, y)) and g.has(Vector2i(x + 1, y)) and g.has(Vector2i(x, y - 1)):
						seams.append(q)
			for q in seams:
				g[q] = IM.INK
		var img := Image.create_empty(W, H, false, Image.FORMAT_RGBA8)
		for q in g:
			if q.x < 0 or q.y < 0 or q.x >= W or q.y >= H:
				return {"error": "texel outside the cell " + str(q)}
			img.set_pixelv(q, g[q])
		var shimg := Image.create_empty(W, H, false, Image.FORMAT_RGBA8)
		for side in ["vl", "vr"]:
			var f: Dictionary = state["feet"][side]
			for p in parts["shadow-%s-l%d" % [side, mini(int(f["lift"]), 3)]]:
				var q: Vector2i = p[0] + Vector2i(0, int(f["o"]))
				if q.x < 0 or q.y < 0 or q.x >= W or q.y >= H:
					return {"error": "shadow texel outside the cell " + str(q)}
				shimg.set_pixelv(q, p[1])
		return {"image": img, "shadow": shimg, "boots": boots, "soles": soles, "near": near}


# =====================================================================================================================
# TEST-ONLY gait driver (event-driven per foot; the manifest's gait keys, stop rule and re-press rule).
class Loco:
	var g: Dictionary          # manifest["gait"]
	var st: Dictionary         # manifest["stop"]
	var rs: Dictionary         # manifest["restart"]
	var inward := {"vl": 1, "vr": -1}
	var SD := 96
	var E := 22
	var A := 6
	var BK := -16
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
	var sx := 0
	var csx := 0
	var sx_t := -1e9
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

	func stance_view(q: int) -> String:
		var v := ""
		for k in g["stance_roll"]:
			if q >= int(k[0]):
				v = String(k[1])
		return v

	func _arm(side: String, phase: int) -> String:
		var f := posmod(phase - int(g["arm_peak_px"][side]), SD)
		var d := mini(f, SD - f)
		var b: Array = g["arm_pose_bands_px"]
		if d <= int(b[0]):
			return "F2"
		if d <= int(b[1]):
			return "F1"
		if d < int(b[2]):
			return "N"
		if d < int(b[3]):
			return "B1"
		return "B2"

	static func land_keys(o0: int, l0: int, v0: String, k0: int) -> Array:
		return [[0, o0, l0, v0, k0], [500, IM.rdiv(o0, 2), maxi(1, mini(2, l0)), "reach", 0], [1000, 0, 1, "strike", 0]]

	static func shuffle_keys(o0: int) -> Array:
		return [[0, o0, 1, "heelup", 0], [500, IM.rdiv(o0, 2), mini(2, 1 + absi(o0) / 4), "hang", 1], [1000, 0, 1, "strike", 0]]

	func replan_keys(o0: int, l0: int, v0: String, k0: int, hs: int) -> Array:
		return [[0, o0, maxi(1, l0), "toe" if v0 in ["strike", "v8", "heelup", "toe"] else v0, k0],
			[500, IM.rdiv(o0 + A, 2), maxi(l0, hs), "hang", 1], [800, A - 1, maxi(1, IM.rdiv(hs, 2)), "reach", 0],
			[1000, A, 1, "strike", 0]]

	func _set_pose(f: Dictionary, p: Dictionary) -> void:
		f["o"] = p["o"]
		f["lift"] = p["lift"]
		f["view"] = p["view"]
		f["kin"] = p["kin"]

	func _contact_pose(f: Dictionary, o: int) -> void:
		f["o"] = o
		f["lift"] = 0
		f["view"] = stance_view(A - o)
		f["kin"] = 1 if A - o < int(g["stance_knee_bend_px"]) else 0

	func _land_contact(s: String, y: int, o: int) -> void:
		var f: Dictionary = feet[s]
		f["mode"] = "contact"
		f["wo"] = y + o
		_contact_pose(f, o)
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
		var hs := clampi(IM.rdiv(3 * rem, SD - E), int(rs["replan_lift_min"]), int(rs["replan_lift_max"]))
		f["keys"] = replan_keys(int(f["o"]), int(f["lift"]), String(f["view"]), int(f["kin"]), hs)
		f["mode"] = "swing"
		f["d0"] = dist
		f["d1"] = dist + rem
		f["replanned"] = true
		var p := IM.interp_keys(f["keys"], 0)
		_set_pose(f, p)

	func _lift(s: String, d0: int) -> void:
		var f: Dictionary = feet[s]
		f["mode"] = "swing"
		f["keys"] = g["swing_keys"]
		f["d0"] = d0
		f["d1"] = d0 + SD - E
		f["replanned"] = false
		events.append(["lift", s])

	func _step_sx(target: int) -> void:
		# torso shift moves at most one texel per tick
		if target != sx:
			sx += 1 if target > sx else -1
			sx_t = clock

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
						_contact_pose(f, o)
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
			var want_bob := 0
			var want_sx := 0
			for s in ["vl", "vr"]:
				if feet[s]["mode"] == "contact":
					var q: int = A - int(feet[s]["o"])
					if q >= int(g["bob_stance_q"][0]) and q < int(g["bob_stance_q"][1]):
						want_bob = 1
					if q >= int(g["torso_shift_stance_q"][0]) and q < int(g["torso_shift_stance_q"][1]):
						want_sx = -int(inward[s])
			if was_moving:          # on the re-press tick the bob / torso hold (one change fewer in that tick)
				bob = want_bob
				_step_sx(want_sx)
			var target := {"R": _arm("R", dist - ref), "L": _arm("L", dist - ref)}
			if arms_synced:
				arms = target
			elif events.is_empty() and bob == prev_bob and views_before == [String(feet["vl"]["view"]), String(feet["vr"]["view"])]:
				# after a re-press: one arm, one pose step per tick, until both match the gait; never on a tick where a
				# boot lifts, lands or changes its view, or the bob changes
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
			bob_t = clock
			prev_bob = bob
		var hdy := hdy_val if clock - bob_t < float(st["hair_lag_ms"]) - 1e-6 else 0
		hdy = clampi(hdy, hdy_shown - 1, hdy_shown + 1)      # the hair / cape lag moves at most one row per tick
		hdy_shown = hdy
		# the cape follows the torso shift hair_lag_ms late, one texel per tick
		if clock - sx_t >= float(st["hair_lag_ms"]) - 1e-6 and csx != sx:
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

	const POSES_ORDER := ["B2", "B1", "N", "F1", "F2"]

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
		# arms: both arms one pose step toward N per arm_step_ms, only on a tick where no boot changes its view
		if not boot_changed and clock - last_arm_t >= float(st["arm_step_ms"]) - 1e-6:
			for side in ["R", "L"]:
				if arms[side] != "N":
					var a := POSES_ORDER.find(arms[side])
					arms[side] = POSES_ORDER[a + (1 if a < 2 else -1)]
					last_arm_t = clock
		var all_spot := moving_feet == 0
		var planted := ""
		for s in ["vl", "vr"]:
			all_spot = all_spot and feet[s]["mode"] == "contact" and int(feet[s]["wo"]) == y
			if feet[s]["mode"] == "contact":
				planted = s if planted == "" else "both"
		if all_spot:
			# settle: a 1-row dip for settle_ms after the last touchdown, then the torso shift returns (one change per tick)
			if settle_t < 0.0:
				settle_t = clock
			if clock - settle_t < float(st["settle_ms"]) - 1e-6:
				bob = 1
			else:
				bob = 0
				_step_sx(0)
		else:
			bob = stop_bob
			# weight shift: the torso leans over the boot that carries the weight while the other one moves
			if planted == "vl" or planted == "vr":
				_step_sx(-int(inward[planted]))


# =====================================================================================================================
func _initialize() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("RUN_V03_CAPTURE FAIL: " + reason)
	print("RUN_V03_CAPTURE FAIL: " + reason)
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


# Character mask = window pixels where the capture shows the drawn character texel's exact colour (the shadow sprite is
# under the character and never counted).  Per leg band (cell x < 38 = vl): lowest window row and its x extent.  Shadow:
# window pixels of the shadow mask not covered by the character, and how many of them are darker than the sprite-free
# background capture in every channel.
func _measure(cap: Image, bg: Image, origin: Vector2i, img: Image, shimg: Image) -> Dictionary:
	var head := -1
	var low := {"vl": -1, "vr": -1}
	var mask := {}
	var cmask := {}      # the same pixels in cell coordinates (body frame)
	for y in img.get_height():
		for x in img.get_width():
			var t := img.get_pixel(x, y)
			if t.a8 == 0:
				continue
			var px := origin + Vector2i(x, y)
			if px.x < 0 or px.y < 0 or px.x >= cap.get_width() or px.y >= cap.get_height():
				continue
			var a := cap.get_pixel(px.x, px.y)
			if a.r8 != t.r8 or a.g8 != t.g8 or a.b8 != t.b8:
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
	var sh_vis := 0
	var sh_dark := 0
	for y in shimg.get_height():
		for x in shimg.get_width():
			if shimg.get_pixel(x, y).a8 == 0 or (y < img.get_height() and img.get_pixel(x, y).a8 != 0):
				continue
			var px := origin + Vector2i(x, y)
			sh_vis += 1
			var a := cap.get_pixel(px.x, px.y)
			var b := bg.get_pixel(px.x, px.y)
			if a.r8 < b.r8 and a.g8 < b.g8 and a.b8 < b.b8:
				sh_dark += 1
	return {"head_top_window_y": head, "sole_window_y": low, "sole_x_extent": ext, "mask": mask, "cell_mask": cmask,
		"shadow_px_outside_character": sh_vis, "shadow_px_darker_than_background": sh_dark}


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
	var shadow := Sprite2D.new()
	shadow.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	shadow.centered = false
	shadow.offset = -Vector2(PIN)
	shadow.scale = Vector2(0.5, 0.5)
	shadow.modulate = Color(1, 1, 1, shadow_alpha)
	shadow.visible = false
	host.add_child(shadow)
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
	shadow.visible = true
	return [host, hero, pilot, ground_off, bg, shadow]


func _pin(hero: Sprite2D, ground_off: float) -> Vector2i:
	return Vector2i(int(round(hero.position.x * 2.0)), int(round((hero.position.y + ground_off) * 2.0)))


func _draw_capture(su: Array, tex: Texture2D, stex: Texture2D) -> Array:
	var hero: Sprite2D = su[1]
	var pilot: Sprite2D = su[2]
	var shadow: Sprite2D = su[5]
	hero.visible = false
	var p := _pin(hero, su[3])
	pilot.texture = tex
	pilot.position = Vector2(p.x * 0.5, p.y * 0.5)
	pilot.z_index = int(hero.position.y)
	shadow.texture = stex
	shadow.position = pilot.position
	shadow.z_index = pilot.z_index - 1
	var cap := await _capture()
	return [cap, p - PIN]


func _free(host: Node) -> void:
	host.queue_free()
	await process_frame
	await process_frame


func _out_name(scene_key: String, what: String, stamp: String, uid: String, ext: String) -> String:
	var n := "%s_%s_protagonist-female-south-run-v03-%s-h48_%s_%s-%s.%s" % [SLUG, scene_key, what, VARIANT, stamp, uid, ext]
	if n.length() > 150:
		push_error("output name too long (%d): %s" % [n.length(), n])
	return n


var v8_boot := {}     # side -> {Vector2i cell: Color}


# Drives one sequence.  plan: Array of {"input": bool, "dt": float}.  Returns per-tick records.
func _drive(su: Array, plan: Array, motion_dir: String, tag: String, crop: Rect2i, full_saves: Dictionary = {}) -> Array:
	var host: Node2D = su[0]
	var hero: Sprite2D = su[1]
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
		# planted boots: expected world texels (window pos -> rgb) and how many of them are visible with that colour
		var boots_w := {}
		for s in ["vl", "vr"]:
			if r["modes"][s] == "contact":
				var src: Dictionary = info["boots"][s] if not info.is_empty() else v8_boot[s]
				# world texels of the boot, and the subset the capture actually shows with the boot's colour; the lowest row
				# and its x-extent are measured on that visible subset (captured pixels)
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
		ticks.append({"tick": t, "input": bool(step["input"]), "dt": float(step["dt"]), "show_v8": bool(r["show_v8"]),
			"modes": r["modes"], "state": r["state"], "events": r["events"], "phase": r["phase"], "dist": r["dist"],
			"hero_logical": [hero.position.x, hero.position.y], "origin": origin, "meas": meas, "boots_w": boots_w,
			"cell_h": img.get_height()})
	Input.action_release("move_down")
	return ticks


# Per-tick summary: planted-boot world displacement (pixels), airborne steps, silhouette XOR, crown step.
func _summ(ticks: Array) -> Array:
	var out := []
	var prev: Dictionary = {}
	for tk in ticks:
		var m: Dictionary = tk["meas"]
		var e := {"tick": tk["tick"], "input": tk["input"], "show_v8": tk["show_v8"], "modes": tk["modes"], "state": tk["state"],
			"events": tk["events"], "phase": tk["phase"], "hero_logical": tk["hero_logical"], "pin_window_y": tk["origin"].y + PIN.y,
			"head_top_window_y": m["head_top_window_y"], "sole_window_y": m["sole_window_y"], "sole_x_extent": m["sole_x_extent"],
			"lowest_cell_row": maxi(m["sole_window_y"]["vl"], m["sole_window_y"]["vr"]) - tk["origin"].y,
			"shadow_px_outside_character": m["shadow_px_outside_character"],
			"shadow_px_darker_than_background": m["shadow_px_darker_than_background"]}
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
					var pa: Dictionary = prev["boots_w"][s]
					var pb: Dictionary = tk["boots_w"][s]
					pl[s] = {"sole_row_d": int(pb["lowest_row"]) - int(pa["lowest_row"]),
						"sole_x0_d": int(pb["sole_x"][0]) - int(pa["sole_x"][0]),
						"sole_x1_d": int(pb["sole_x"][1]) - int(pa["sole_x"][1]),
						"view_prev": String(pa["view"]), "view_now": String(pb["view"]),
						"view_changed": String(pa["view"]) != String(pb["view"]),
						"boot_texels_prev": a.size(), "boot_texels_now": b.size(), "boot_texels_same_world_pos_and_rgb": same,
						"boot_texels_visible_now": pb["visible"]}
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
	var n_roll := 0
	var row_max := 0
	var x_max := 0
	var x_roll_max := 0
	var tex_lost := 0
	var tex_total := 0
	var vis_total := 0
	var air_max := 0
	var xor_max := 0
	var cxor_max := 0
	var head_max := 0
	var sh_min := 1 << 30
	for i in range(maxi(1, from_i), mini(summ.size(), to_i)):
		var e: Dictionary = summ[i]
		xor_max = maxi(xor_max, int(e.get("silhouette_xor", 0)))
		cxor_max = maxi(cxor_max, int(e.get("cell_silhouette_xor", 0)))
		head_max = maxi(head_max, absi(int(e.get("head_step", 0))))
		sh_min = mini(sh_min, int(e["shadow_px_darker_than_background"]))
		for s in e.get("planted", {}):
			var p: Dictionary = e["planted"][s]
			n += 1
			row_max = maxi(row_max, absi(int(p["sole_row_d"])))
			var xd := maxi(absi(int(p["sole_x0_d"])), absi(int(p["sole_x1_d"])))
			if bool(p["view_changed"]):
				n_roll += 1
				x_roll_max = maxi(x_roll_max, xd)
			else:
				x_max = maxi(x_max, xd)
				tex_total += int(p["boot_texels_now"])
				tex_lost += maxi(int(p["boot_texels_now"]), int(p["boot_texels_prev"])) - int(p["boot_texels_same_world_pos_and_rgb"])
			vis_total += int(p["boot_texels_visible_now"])
		for s in e.get("unplanted_sole_row_step", {}):
			air_max = maxi(air_max, absi(int(e["unplanted_sole_row_step"][s])))
	return {"planted_tick_pairs": n, "planted_sole_row_world_disp_max_px": row_max,
		"planted_same_view_pairs": n - n_roll, "planted_sole_x_world_disp_max_px_same_view": x_max,
		"planted_boot_texels_compared_same_view": tex_total, "planted_boot_texels_changed_same_view": tex_lost,
		"planted_roll_view_change_pairs": n_roll, "planted_roll_sole_x_extent_change_max_px": x_roll_max,
		"planted_boot_texels_visible_on_screen": vis_total,
		"unplanted_sole_row_step_max_px": air_max, "silhouette_xor_max_per_tick": xor_max, "cell_silhouette_xor_max_per_tick": cxor_max,
		"head_step_max_px": head_max, "shadow_px_darker_than_background_min": sh_min}


func _planted_ok(s: Dictionary) -> bool:
	return int(s["planted_sole_row_world_disp_max_px"]) == 0 and int(s["planted_sole_x_world_disp_max_px_same_view"]) == 0 \
		and int(s["planted_boot_texels_changed_same_view"]) == 0 and int(s["planted_roll_sole_x_extent_change_max_px"]) <= 2


# After a release: per boot, the longest run of ticks with the boot off the floor (state lift > 0 or not in contact),
# and the highest sole above its floor row measured on pixels.
func _raised_after(ticks: Array, rel: int, dt: float) -> Dictionary:
	var out := {}
	for s in ["vl", "vr"]:
		var run := 0
		var best := 0
		var lift_max := 0
		for i in range(rel, ticks.size()):
			var tk: Dictionary = ticks[i]
			var raised: bool = (not bool(tk["show_v8"])) and String(tk["modes"][s]) != "contact"
			if raised:
				run += 1
				best = maxi(best, run)
				lift_max = maxi(lift_max, int(tk["state"]["feet"][s]["lift"]))
			else:
				run = 0
		out[s] = {"longest_raised_ms": 1000.0 * best * dt, "max_lift_rows": lift_max}
	return out


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
	var quick := _user_arg("quick") == "1"
	var mpath := ASSET_DIR + MANIFEST
	var mdigest := _sha_text_lf(mpath)
	manifest = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path(mpath)))
	for flag in ["art_approved", "human_reviewed", "runtime_integrated", "walk_animation_approved", "run_animation_approved",
			"stop_animation_approved", "counts_toward_art_acceptance"]:
		if bool(manifest[flag]):
			_fail("manifest flag %s must stay false" % flag)
			return
	var disp: Dictionary = manifest["display"]
	if float(disp["scale"]) != 0.5 or int(disp["logical_height_px"]) != 48 or bool(disp["flip_h"]):
		_fail("display block is not 48 px / 0.5 / no flip")
		return
	shadow_alpha = float(disp["shadow"]["opacity"])
	var sources := {"manifest": {"path": mpath, "sha256_text_lf_v1": mdigest}}
	for e in manifest["parts"] + manifest["keyframes"]:
		var dg := FileAccess.get_sha256(ProjectSettings.globalize_path(ASSET_DIR + String(e["file"])))
		if dg != String(e["sha256"]):
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
	var neutral := {"bob": 0, "hdy": 0, "sx": 0, "csx": 0, "arms": {"R": "N", "L": "N"},
		"feet": {"vl": {"o": 0, "lift": 0, "view": "v8", "kin": 0}, "vr": {"o": 0, "lift": 0, "view": "v8", "kin": 0}}}
	var nc := comp.compose(neutral)
	var nimg: Image = nc["image"]
	var v8_pad := Image.create_empty(80, 120, false, Image.FORMAT_RGBA8)
	v8_pad.blit_rect(v8_image, Rect2i(0, 0, 80, 112), Vector2i.ZERO)
	if nimg.get_data() != v8_pad.get_data():
		_fail("GDScript neutral composition != v8")
		return
	# the v8 idle is shown with the neutral (two v8-spot) contact shadow, so the stop switch never changes the shadow
	v8_shadow_image = nc["shadow"]
	v8_shadow_tex = ImageTexture.create_from_image(v8_shadow_image)
	parity["neutral_equals_v8"] = true
	for k in manifest["keyframes"]:
		var ref_img := _load_rgba(ASSET_DIR + String(k["file"]))
		var ref_sh := _load_rgba(ASSET_DIR + String(k["shadow_file"]))
		var c := comp.compose(k["state"])
		if c.has("error") or (c["image"] as Image).get_data() != ref_img.get_data():
			_fail("GDScript compositor != builder keyframe " + String(k["key"]))
			return
		if (c["shadow"] as Image).get_data() != ref_sh.get_data():
			_fail("GDScript shadow != builder keyframe shadow " + String(k["key"]))
			return
	parity["keyframes_and_shadows_equal_builder_pngs"] = (manifest["keyframes"] as Array).size()
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
	var out_abs := _user_arg("out-dir") if _user_arg("out-dir") != "" else ProjectSettings.globalize_path(OUTPUT_DIR)   # --out-dir: scratch debug runs
	var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var uid := "%08x" % (randi() & 0xffffffff)
	SaveStore.root_path = "user://test-saves/m8-south-run-v03-capture"
	app = root.get_node("AppState")
	var outputs := {}
	var report_scenes := {}
	var steady_checked := 0
	for scene_key in SCENES.keys():
		if only != "" and scene_key != only:
			continue
		var spec: Array = SCENES[scene_key]
		var sr := {"kind": spec[0], "destination": spec[1], "annex_room": spec[2], "note": spec[4], "walk": {}, "stops": {}, "repress": {}}
		# ---------------------------------------------------------------- stills at one pin: v8 + the 12 keyframes (with shadows)
		var su: Array = await _setup(spec)
		if su.is_empty():
			return
		var stills := []
		var items := [["v8-idle-shadow", v8_image, v8_tex, v8_shadow_tex]]
		for k in manifest["keyframes"]:
			var im := _load_rgba(ASSET_DIR + String(k["file"]))
			var sm := _load_rgba(ASSET_DIR + String(k["shadow_file"]))
			items.append(["key-%02dpx" % int(k["phase_px"]), im, ImageTexture.create_from_image(im), ImageTexture.create_from_image(sm)])
		for it in items:
			var dc: Array = await _draw_capture(su, it[2], it[3])
			var cap: Image = dc[0]
			var fid := _fidelity(it[1], dc[1], cap)
			if fid["exact_rgb_matches"] != fid["opaque_texels"]:
				_fail("%s still %s fidelity %s" % [scene_key, it[0], str(fid)])
				return
			var name := _out_name(scene_key, "still-" + String(it[0]), stamp, uid, "png")
			cap.save_png(out_abs.path_join(name))
			outputs[name] = {"kind": "still", "scene": scene_key}
			stills.append({"frame": it[0], "fidelity": fid, "capture": name})
		sr["stills"] = stills
		await _free(su[0])
		# ---------------------------------------------------------------- runs at 30 / 60 / 144 fps
		for mode in WALK_MODES.keys():
			if quick and mode != "walk-60fps":
				continue
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
			if not _planted_ok(stats):
				_fail("%s %s planted boot moved in world space %s" % [scene_key, mode, str(stats)])
				return
			# steady state (after the first full stride) must equal the manifest's per-px table
			for tk in ticks:
				if not bool(tk["input"]) or int(tk["dist"]) < int(manifest["gait"]["stride_px"]) + 48:
					continue
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
			stats["logical_px_per_s_measured"] = (su[1].position.y - start_y) / (float(int(wm[0])) / float(wm[1]))
			stats["crop"] = [crop.position.x, crop.position.y, crop.size.x, crop.size.y]
			stats["ticks"] = summ
			var contacts := []     # world rows per contact run (pixels)
			var air_ticks := 0
			var moving_ticks := 0
			for e in summ:
				if bool(e["input"]):
					moving_ticks += 1
					if e["modes"]["vl"] != "contact" and e["modes"]["vr"] != "contact":
						air_ticks += 1
			for s in ["vl", "vr"]:
				var run := []
				for e in summ:
					if e["modes"][s] == "contact" and bool(e["input"]):
						run.append(int(e["sole_window_y"][s]))
					elif not run.is_empty():
						contacts.append({"side": s, "ticks": run.size(), "world_row_min": run.min(), "world_row_max": run.max()})
						run = []
			stats["contact_runs"] = contacts
			stats["airborne_ticks_while_moving"] = air_ticks
			stats["moving_ticks"] = moving_ticks
			sr["walk"][mode] = stats
			print("RUN %s %s ticks %d speed %.3f planted pairs %d (roll %d) row-disp %d x-disp %d roll-x %d texels-changed %d air %d/%d cell-xor-max %d shadow-dark-min %d" % [scene_key, mode,
				ticks.size(), stats["logical_px_per_s_measured"], stats["planted_tick_pairs"], stats["planted_roll_view_change_pairs"],
				stats["planted_sole_row_world_disp_max_px"], stats["planted_sole_x_world_disp_max_px_same_view"],
				stats["planted_roll_sole_x_extent_change_max_px"], stats["planted_boot_texels_changed_same_view"], air_ticks, moving_ticks,
				stats["cell_silhouette_xor_max_per_tick"], stats["shadow_px_darker_than_background_min"]])
			await _free(su[0])
		# ---------------------------------------------------------------- immediate stops from every tick of one stride
		var fps_list := [60] if (scene_key != "city-bright" or quick) else [60, 30, 144]
		for fps in fps_list:
			var dt: float = 1.0 / fps
			var per_tick_px: float = 280.0 / fps
			var first := int(ceil((96.0 + 8.0) / per_tick_px))         # release inside the 2nd stride
			var count := int(ceil(96.0 / per_tick_px))
			var step := 1 if fps != 144 else 3
			if quick:
				step = 4
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
					for pk in [[rel0 - 1, "1-last-move"], [rel0 + 2, "2-plus2"], [rel0 + 5, "3-plus5"], [plan.size() - 1, "4-v8"]]:
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
				if not _planted_ok(ws) or not _planted_ok(ss):
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
				var raised := _raised_after(ticks, rel, dt)
				var last: Dictionary = ticks[rel - 1]
				var rec := {"fps": fps, "release_tick": rel, "released_at_phase_px": posmod(int(last["phase"]), 96),
					"modes_at_release": last["modes"], "state_at_release": last["state"],
					"v8_after_ms": 1000.0 * (v8_at - rel + 1) * dt, "switch_to_v8_xor": pop, "raised_after_release": raised,
					"walk": ws, "stop": ss, "events": [], "crop": [crop.position.x, crop.position.y, crop.size.x, crop.size.y]}
				for i in range(rel, v8_at + 1):
					for ev in ticks[i]["events"]:
						rec["events"].append([i - rel] + ev)
				rec["ticks"] = summ.slice(maxi(0, rel - 8), mini(summ.size(), v8_at + 3))
				sr["stops"][tag] = rec
				print("STOP %s phase %d modes %s -> v8 after %.0f ms, raised vl %.0f ms vr %.0f ms, stop cell-xor-max %d walk cell-xor-max %d, switch xor %d" % [tag,
					rec["released_at_phase_px"], str(last["modes"]), rec["v8_after_ms"], raised["vl"]["longest_raised_ms"], raised["vr"]["longest_raised_ms"],
					ss["cell_silhouette_xor_max_per_tick"], ws["cell_silhouette_xor_max_per_tick"], pop])
				if pop != 0:
					_fail("%s: switch to v8 changed %d pixels" % [tag, pop])
					return
				for s in ["vl", "vr"]:
					if float(raised[s]["longest_raised_ms"]) > STOP_RAISED_LIMIT_MS:
						_fail("%s: boot %s stayed raised %.0f ms after the release" % [tag, s, raised[s]["longest_raised_ms"]])
						return
				await _free(su[0])
		# ---------------------------------------------------------------- re-press: release at several phases x re-press after k ticks
		var rel_walk := [12, 16, 20, 24, 28, 32] if scene_key == "city-bright" else [16, 24, 32]
		var gaps := [1, 2, 3, 5, 8, 14, 30] if scene_key == "city-bright" else [1, 3, 8, 30]
		if quick:
			rel_walk = [16, 28]
			gaps = [1, 8]
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
				if not _planted_ok(all_st):
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
		"purpose": "TEST-ONLY real-Godot captures of the UNAPPROVED / NONRUNTIME female SOUTH RUN motion pilot v03 (part library + test-only compositor + test-only contact shadow) moved by the scenes' own _process at MOVE_SPEED 140",
		"status": "UNAPPROVED / NONRUNTIME; not art acceptance; Codex / creator visual decision pending",
		"art_approved": false, "human_reviewed": false, "runtime_integrated": false, "quick_debug_run": quick,
		"approved_scope_unchanged": "selout v8 SOUTH IDLE static frame and the 48 logical px display scale only",
		"capture_tool": "tools/rpg-2-star-ocean-the-second_protagonist-female_south-locomotion-compact-v03-godot-capture_m8-w06_20261017-012243-8e208784.gd",
		"renderer": "Godot %s windowed, viewport texture capture" % Engine.get_version_info()["string"],
		"canvas": [640, 360], "window": [1280, 720], "sprite_scale": 0.5, "filter": "nearest (CanvasItem.TEXTURE_FILTER_NEAREST)",
		"shadow": {"drawn": "separate Sprite2D under the character, z - 1, modulate alpha", "opacity": shadow_alpha, "under_v8_idle": true},
		"move_speed_logical_px_s": move_speeds, "sources": sources, "parity": parity, "steady_state_ticks_checked": steady_checked,
		"gates_passed": ["manifest + part / keyframe / shadow PNG + v8 hash locks", "flags false", "MOVE_SPEED 140", "1280x720",
			"GDScript compositor == v8 (neutral) and == all builder keyframes and keyframe shadows", "steady-state gait == manifest per-px table",
			"exact-RGB fidelity of the drawn character on every captured tick", "straight-south movement; hero stationary without input",
			"planted boot: 0 px world displacement of its lowest row on every tick; while its view is unchanged 0 px sole x-extent change and 0 boot texels changed; roll view changes move the sole-row x-extent by <= 2 px (walk 30/60/144, every stop, every re-press)",
			"every stop returns to the v8 PNG with 0 changed character pixels at the switch",
			"after every release no boot stays off the floor longer than %d ms" % int(STOP_RAISED_LIMIT_MS),
			"every re-press: the next touchdown is the other boot (no boot touches down twice in a row)"],
		"outputs": outputs, "scenes": report_scenes,
	}
	var rname := "%s_city-annex_protagonist-female-south-run-v03-capture-receipt-h48_%s_%s-%s.json" % [SLUG, VARIANT, stamp, uid]
	var f := FileAccess.open(out_abs.path_join(rname), FileAccess.WRITE)
	f.store_string(JSON.stringify(report, " ") + "\n")
	f.close()
	print("RECEIPT " + rname)
	print("STAMP %s-%s" % [stamp, uid])
	quit(0)
