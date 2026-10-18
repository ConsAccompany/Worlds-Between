extends SceneTree

# TEST-ONLY real-Godot capture of the UNAPPROVED / NONRUNTIME female SOUTH RUN motion pilot v06 (m8-w09, single direction).
# v06 is a copy of the v05 capture tool (tools/...south-run-v05-godot-capture_m8-w08_20261017-055617-257bf083.gd, untouched).
# ONE bounded correction: v05's stop settle counted frames (each body change after the last touchdown took its own tick, and
# the one-boot-change hold cost a whole tick), so 30 fps stops took 267-333 ms (60 fps 150-200 ms).  v06's Loco runs the
# stop on an EVENT CLOCK in ms (manifest stop.settle_clock / settle_gap_ms / hold_shift_ms / no_pose_skip): the settle
# changes keep v05's order and spacing in time (>= settle_gap_ms = one 60 fps frame apart, the hair lag counted from the
# scheduled body change) and each frame draws the state at its own time; a held boot loses at most hold_shift_ms; a moving
# boot never jumps from its start pose to touchdown in one frame.  Art, gait, compositor and re-press rule are v05's.
# New evidence: stops from every 30 fps tick of one stride in BOTH scenes (frames saved), re-press at 30 and 144 fps,
# a 30 fps normal-speed showreel per scene next to the 60 fps one, and --sim=1: a window-free, deterministic sweep of the
# gait driver alone over 14 frame rates and a jittered frame time (state-level timing only, no pixels).
# New gates: 30 fps release -> v8 <= 233 ms; body changes per tick after the last touchdown <= 1 at frame times <=
# settle_gap_ms (60 / 144 fps) and <= 2 at 30 fps, with 0 neck shear on every captured tick.
# (v05 header:)
# Review evidence only: not art acceptance, not runtime integration, not a production sprite.  The creator approved only
# the selout v8 SOUTH IDLE static frame and the 48 logical px display scale; motion is not approved.  Lives in tools/
# (outside res://), so no game/ file is added or edited, and no runtime script is changed.  Run windowed from the
# repository root (the project renders its 640x360 canvas into the 1280x720 window, integer canvas_items stretch):
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path of this file> -- --motion-dir=<abs scratch>
#
# v05 is a copy of the v04 capture tool (tools/...south-run-v04-godot-capture_m8-w07_20261017-015826-9d3f6c18.gd, untouched).
# v05 changes: (1) the 84 px cycle comes from the manifest (v04 hard-coded 96 px in the stop / re-press sweeps); (2) the stop
# settle makes at most ONE body change per tick after the last touchdown (hair, then torso, then arms, then the dip release,
# then the hair) and the arms never step on a tick where a boot or the torso changes; (3) NORMAL-SPEED SHOWREELS per scene
# (idle, start, sustained run, release to v8, quick re-press, reversal to north and back, final stop) captured as full
# 1280x720 window frames; (4) a REVERSAL sweep: south run released into move_up at every 3rd 60 fps tick of one stride,
# then back to south.  There is no north pilot art (out of scope): while move_up is held the scene's own RUNTIME hero
# sprite (its existing placeholder north walk) is shown and the pilot is hidden; when south is pressed again the pilot
# re-enters with the start rule from the v8 idle pose.  Those north ticks are labelled runtime_north and excluded from
# the pilot gates; (5) new gates: one body change per tick in every settle, captured floor gap recorded.
# (v04 header:) v04 is a copy of the v03 capture tool (tools/...south-locomotion-compact-v03-godot-capture_m8-w06_20261017-012243-8e208784.gd,
# untouched) with the v04 builder's three targeted fixes ported: (1) a leg longer than v8's keeps v8's thigh rows 1:1 and
# its shin slopes from the knee lean to the boot cuff, knee lean from the manifest's stance_knee_kin; (2) the head and
# hair lock shift with the torso (sx); (3) after a release the hair lags one tick (stop_hair_lag_ms) and the cape returns
# with the torso (stop_cape_lag_ms).  A boot planted in the toe view starts its stop shuffle in that view.  New gates
# measured on captured pixels: head-vs-torso lateral offset (neck shear) 0 on every tick; post-contact settle recorded.
# (v03 header:) Started as a copy of the v02 capture tool (tools/...south-locomotion-compact-v02-godot-capture_m8-w05_20261016-200500-a29fc892.gd).
# The hidden runtime hero is moved by each scene's OWN _process(delta) with "move_down" held (MOVE_SPEED 140, asserted).
# A TEST-ONLY compositor (PartCompositor, a port of compose() in the v04 builder) stacks the v04 part PNGs every tick; a
# TEST-ONLY gait driver (Loco) decides foot / torso / arm states from the manifest's gait keys, stop rule and re-press rule:
#   * body at the logical position (no root lock); a boot in contact keeps the window row fixed when it landed and rolls
#     strike -> v8 -> heelup -> toe on that row; swing lift <= 3 rows;
#   * shoulders / torso / scarf / arms AND head shift 1 texel toward the planted boot (v04); cape follows the shift late;
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
const ASSET_DIR := "res://assets/characters/run-v06-unapproved/"
const MANIFEST := "rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-manifest_unapproved-nonruntime_20261017-211600-c619ea83.json"
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
# v05: 60 fps release ticks saved as full 1280x720 stills, one per stop ENTRY PHASE (chosen from the 84 px cycle: the phase
# at release is recorded in the receipt; the labels are checked against the release state there)
const STILL_STOP_CASES := {27: "landing", 29: "mid-stance", 30: "late-stance", 34: "flight"}
const STOP_RAISED_LIMIT_MS := 100.0     # gate: after a release no boot stays off the floor longer than this
const STOP_V8_LIMIT_MS_30FPS := 700.0 / 3.0   # v06 gate (Codex "at most 233 ms"): 7 frames at 30 fps = 233.3 ms
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
var neck_head := []      # v04: v8 head texels (rows 8..28, x >= 25: crown / face, not the lagging hair lock) [Vector2i, Color]
var neck_torso := []     # v04: v8 scarf / chest texels (rows 36..40, x 28..44) [Vector2i, Color]
var SDM := 84            # v05: stride_px from the manifest (set in _run)


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
# v04 builder.
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
		# v04: a leg longer than v8's keeps v8's thigh rows 1:1 + the whole knee band; the shin takes the extra rows
		var rest := n - K.size()
		var nt2 := maxi(1, mini(rest - 1, T.size()))
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
		# v04: on a leg longer than v8's the shin slopes from the knee lean to the boot cuff (whole texels)
		var end := 0
		if sh.size() > boot_top - 1 - int(knee[side][1]):
			var bx0 := 1 << 30
			var bx1 := -(1 << 30)
			for q in boot:
				if q.y == bt:
					bx0 = mini(bx0, q.x)
					bx1 = maxi(bx1, q.x)
			var sx0 := 1 << 30
			var sx1 := -(1 << 30)
			for e in src.get(boot_top - 1, []):
				sx0 = mini(sx0, int(e[0]))
				sx1 = maxi(sx1, int(e[0]))
			end = IM.rdiv(bx0 + bx1 - sx0 - sx1, 2)
		for i in sh.size():
			var dx := kdx + IM.rdiv((end - kdx) * (i + 1), sh.size() + 1)
			for e in src.get(sh[i], []):
				out[Vector2i(int(e[0]) + dx, y)] = e[1]
			y += 1
		for q in boot:
			out[q] = boot[q]
		return {"texels": out, "boot": boot, "sole": int(ground[side]) + dy, "hip_to_sole": int(ground[side]) + dy - (hip + bob) + 1,
			"trouser_rows": bt - (hip + bob)}

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
		var legm := {}
		for side in ["vl", "vr"]:
			var l := leg(side, b, state["feet"][side])
			if l.has("error"):
				return l
			legs[side] = l["texels"]
			boots[side] = l["boot"]
			soles[side] = l["sole"]
			legm[side] = {"hip_to_sole": l["hip_to_sole"], "trouser_rows": l["trouser_rows"]}
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
		_put(g, "head", sx, b)                                   # v04: with the torso (v03: 0)
		_put(g, "hair-hdy-" + String(hdy_tag[h]), sx, b)
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
		var n_seams := 0
		if sx != 0:
			var seams := []
			for y in range(28 + b, 41 + b):
				for x in range(1, W - 1):
					var q := Vector2i(x, y)
					if not g.has(q) and g.has(Vector2i(x - 1, y)) and g.has(Vector2i(x + 1, y)) and g.has(Vector2i(x, y - 1)):
						seams.append(q)
			for q in seams:
				g[q] = IM.INK
			n_seams = seams.size()
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
		return {"image": img, "shadow": shimg, "boots": boots, "soles": soles, "near": near, "legs": legm, "seams": n_seams}


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
	# v06 event clock (ms) for the stop: prev_clock = time of the previous frame; ev_t = event time of the last settle
	# change; hair_due = event time at which the hair catches up the last bob change; bob_evt = event time of a bob change
	# made by the stop this frame (the hair lag counts from it); multi_ok = this frame is longer than settle_gap_ms, so two
	# scheduled changes can fall inside it
	var prev_clock := 0.0
	var ev_t := -1e9
	var hair_due := -1e9
	var bob_evt := -1.0
	var gap_ms := 16.667
	var hold_ms := 16.667
	var no_skip := true
	var multi_ok := false
	var settle_log := []       # [frame clock, change, event time] for the receipt

	func setup(m: Dictionary, y: int) -> void:
		g = m["gait"]
		st = m["stop"]
		rs = m["restart"]
		gap_ms = float(st["settle_gap_ms"])
		hold_ms = float(st["hold_shift_ms"])
		no_skip = bool(st["no_pose_skip"])
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

	static func shuffle_keys(o0: int, v0: String) -> Array:
		# v04: a boot planted in the toe view lifts in that view (v03: always heel-up)
		return [[0, o0, 1, "toe" if v0 == "toe" else "heelup", 0], [500, IM.rdiv(o0, 2), mini(2, 1 + absi(o0) / 4), "hang", 1],
			[1000, 0, 1, "strike", 0]]

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
		var kin := 0
		for k in g["stance_knee_kin"]:
			if A - o >= int(k[0]):
				kin = int(k[1])
		f["kin"] = kin

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
		ev_t = -1e9
		hair_due = -1e9
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
			bob_t = bob_evt if bob_evt >= 0.0 else clock      # v06: a stop bob change carries its event time
			prev_bob = bob
		# v04: once stopped (after a release) the hair lags stop_hair_lag_ms and the cape stop_cape_lag_ms (v03: hair_lag_ms both)
		var stopped := (not moving) and started
		var hair_lag := float(st["stop_hair_lag_ms"]) if stopped else float(st["hair_lag_ms"])
		var cape_lag := float(st["stop_cape_lag_ms"]) if stopped else float(st["hair_lag_ms"])
		var hdy := hdy_val if clock - bob_t < hair_lag - 1e-6 else 0
		hdy = clampi(hdy, hdy_shown - 1, hdy_shown + 1)      # the hair / cape lag moves at most one row per tick
		hdy_shown = hdy
		# the cape follows the torso shift cape_lag late, one texel per tick
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
			f["keys"] = shuffle_keys(o, String(f["view"]))
			dur = clampf(float(st["shuffle_ms_base"]) + float(st["shuffle_ms_per_px"]) * absi(o), float(st["shuffle_ms_base"]), float(st["shuffle_ms_max"]))
		f["mode"] = kind
		f["t0"] = t0
		f["dur"] = dur
		f["seg"] = -1           # v06: highest key segment drawn so far (0: start key .. 500, 1: mid key .. touchdown)
		events.append([kind + "-move-start", s, o, l, dur])

	# v06: the key parameter u (0..1000) of a moving boot at this frame's time; a boot that has not been drawn in its mid
	# segment yet never jumps to touchdown (u 1000) in one frame - it shows the mid key (u 500) first
	func _move_u(f: Dictionary) -> int:
		var u := clampi(int(floor(1000.0 * (clock - float(f["t0"])) / float(f["dur"]) + 1e-6)), 0, 1000)
		if no_skip and u >= 1000 and int(f["seg"]) < 1:
			u = 500
		return u

	func _stop_step(y: int, dt: float) -> void:
		var landed_now := false
		var moving_feet := 0
		var prop := {}
		for s in ["vl", "vr"]:
			var f: Dictionary = feet[s]
			if f["mode"] == "land" or f["mode"] == "shuffle":
				var u := _move_u(f)
				prop[s] = {"land": true} if u >= 1000 else {"land": false, "pose": IM.interp_keys(f["keys"], u), "u": u}
		# at most one boot changes its view (or touches down) per tick; the other holds one tick.  v06: the held boot's clock
		# moves by min(frame time, hold_shift_ms) (v05: a whole frame, 33 ms at 30 fps)
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
			feet[hold]["t0"] = float(feet[hold]["t0"]) + minf(dt * 1000.0, hold_ms)
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

	func _settle_events() -> void:
		var applied := 0
		while true:
			var due := 0.0
			var what := ""
			if hair_due > ev_t + 1e-6:
				due = hair_due
				what = "hair"
			elif sx != 0:
				due = ev_t + gap_ms
				what = "sx"
			elif arms["R"] != "N" or arms["L"] != "N":
				due = maxf(ev_t + gap_ms, last_arm_t + float(st["arm_step_ms"]))
				what = "arms"
			elif bob != 0:
				due = maxf(ev_t + gap_ms, settle_t + float(st["settle_ms"]))
				what = "bob"
			else:
				return
			if due > clock + 1e-6 or (applied > 0 and not multi_ok):
				return
			if what == "sx":
				_step_sx(0)
			elif what == "arms":
				_arm_step()
				last_arm_t = due
			elif what == "bob":
				bob = 0
				bob_evt = due
				hair_due = due + float(st["stop_hair_lag_ms"])
			# "hair": the lag in tick() draws the hair caught up from hair_due on (hdy from bob_t = the bob event time)
			ev_t = due
			applied += 1
			settle_log.append([clock, what, due])

	func _arm_step_due() -> bool:
		return (arms["R"] != "N" or arms["L"] != "N") and clock - last_arm_t >= float(st["arm_step_ms"]) - 1e-6

	func _arm_step() -> void:
		for side in ["R", "L"]:
			if arms[side] != "N":
				var a := POSES_ORDER.find(arms[side])
				arms[side] = POSES_ORDER[a + (1 if a < 2 else -1)]
		last_arm_t = clock

# =====================================================================================================================
# v06 --sim=1: a window-free, deterministic sweep of the TEST-ONLY gait driver alone (no scene, no compositor, no
# pixels).  The hero's logical y advances by MOVE_SPEED 140 x dt per moving frame (as the scenes' _process does) and the
# window pin row is round(2 y).  For each frame rate: a stop from every frame of one stride (released inside the 2nd
# stride), and re-presses after 1..8 idle frames from every 2nd frame of one stride; plus a jittered frame-time run (fixed
# seed).  Recorded per stop: release -> first v8 PNG frame, last touchdown, post-contact, longest raised boot, settle
# changes per frame.  State-level timing evidence only; the captured Godot runs are the pixel evidence.
const SIM_FPS := [24, 30, 40, 48, 50, 60, 72, 75, 90, 100, 120, 144, 165, 240]


func _sim_changes(a: Dictionary, b: Dictionary) -> Array:
	var what := []
	if int(a["bob"]) != int(b["bob"]):
		what.append("bob")
	elif int(a["hdy"]) != int(b["hdy"]):
		what.append("hdy")
	if int(a["sx"]) != int(b["sx"]):
		what.append("sx")
	if a["arms"]["R"] != b["arms"]["R"] or a["arms"]["L"] != b["arms"]["L"]:
		what.append("arms")
	return what


# frames: Array of {"input": bool, "dt": float}; returns per-frame records
func _sim_drive(frames: Array) -> Array:
	var loco := Loco.new()
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


func _sim_stop(rec: Array, rel: int) -> Dictionary:
	var v8_at := -1
	for i in range(rel, rec.size()):
		if bool(rec[i]["input"]):
			break
		if bool(rec[i]["show_v8"]):
			v8_at = i
			break
	if v8_at < 0:
		return {"error": "never returned to v8"}
	var t_rel: float = float(rec[rel - 1]["clock"])
	var last_down := rel - 1
	for i in range(rel, v8_at + 1):
		for ev in rec[i]["events"]:
			if String(ev[0]) == "land":
				last_down = i
	var raised := 0.0
	for s in ["vl", "vr"]:
		var run := 0.0
		for i in range(rel, v8_at):
			if String(rec[i]["modes"][s]) != "contact":
				run += float(rec[i]["dt"]) * 1000.0
				raised = maxf(raised, run)
			else:
				run = 0.0
	var max_ch := 0
	var max_ch_touch := 0
	var at_rest := last_down
	for i in range(last_down + 1, v8_at):
		var w := _sim_changes(rec[i - 1]["state"], rec[i]["state"])
		max_ch = maxi(max_ch, w.size())
		if not w.is_empty():
			at_rest = i
	if last_down >= rel:
		max_ch_touch = _sim_changes(rec[last_down - 1]["state"], rec[last_down]["state"]).size()
	var arms_at_release: Dictionary = rec[rel - 1]["state"]["arms"]
	var log := []
	for e in rec[-1].get("settle_log", []):
		if float(e[0]) > t_rel:
			log.append([snappedf(float(e[0]) - t_rel, 0.1), e[1], snappedf(float(e[2]) - t_rel, 0.1)])
	return {"phase_px": posmod(int(rec[rel - 1]["phase"]), SDM), "v8_ms": float(rec[v8_at]["clock"]) - t_rel,
		"arms_at_release": arms_at_release, "settle_log_ms_after_release": log,
		"feet_down_ms": float(rec[last_down]["clock"]) - t_rel, "post_contact_ms": float(rec[v8_at]["clock"]) - float(rec[last_down]["clock"]),
		"at_rest_ms": float(rec[at_rest]["clock"]) - t_rel, "raised_max_ms": raised, "settle_changes_per_frame_max": max_ch,
		"body_changes_on_touchdown_frame": max_ch_touch}


func _sim_range(vals: Array) -> Array:
	return [vals.min(), vals.max()] if not vals.is_empty() else []


func _sim(out_abs: String, stamp: String, uid: String) -> void:
	var report := {"purpose": "v06 deterministic gait-driver timing sweep (state level, no pixels, no scene); hero y advances by 140 logical px/s",
		"art_approved": false, "human_reviewed": false, "runtime_integrated": false, "fps": {}, "jitter": {}}
	var ok := true
	for fps in SIM_FPS:
		var dt := 1.0 / float(fps)
		var per_tick := 280.0 / float(fps)
		var first := int(ceil((float(SDM) + 8.0) / per_tick))
		var count := int(ceil(float(SDM) / per_tick))
		var stops := []
		for k in count:
			var plan := [{"input": false, "dt": dt}]
			for i in first + k:
				plan.append({"input": true, "dt": dt})
			for i in int(0.6 * fps):
				plan.append({"input": false, "dt": dt})
			var rec := _sim_drive(plan)
			var sr := _sim_stop(rec, first + k + 1)
			if sr.has("error"):
				ok = false
				print("SIM %d fps release %d: %s" % [fps, first + k, sr["error"]])
				continue
			stops.append(sr)
		var rep_bad := 0
		var rep_n := 0
		for k in range(0, count, 2):
			for gap in [1, 2, 3, 5, 8]:
				var plan := [{"input": false, "dt": dt}]
				for i in first + k:
					plan.append({"input": true, "dt": dt})
				for i in gap:
					plan.append({"input": false, "dt": dt})
				for i in int(0.3 * fps):
					plan.append({"input": true, "dt": dt})
				var rec := _sim_drive(plan)
				var rp: int = first + k + 1 + gap
				var last_land := ""
				for i in range(1, rp):
					for ev in rec[i]["events"]:
						if String(ev[0]) == "land":
							last_land = String(ev[1])
				var next_land := ""
				for i in range(rp, rec.size()):
					for ev in rec[i]["events"]:
						if next_land == "" and String(ev[0]) == "land":
							next_land = String(ev[1])
				rep_n += 1
				if last_land != "" and next_land == last_land:
					rep_bad += 1
		var v8s := stops.map(func(e): return e["v8_ms"])
		var posts := stops.map(func(e): return e["post_contact_ms"])
		var downs := stops.map(func(e): return e["feet_down_ms"])
		var rests := stops.map(func(e): return e["at_rest_ms"])
		var raised := stops.map(func(e): return e["raised_max_ms"])
		var chs := stops.map(func(e): return e["settle_changes_per_frame_max"])
		var tch := stops.map(func(e): return e["body_changes_on_touchdown_frame"])
		report["fps"][str(fps)] = {"stops": stops.size(), "release_to_v8_ms": _sim_range(v8s), "feet_down_ms": _sim_range(downs),
			"post_contact_to_v8_ms": _sim_range(posts), "release_to_at_rest_ms": _sim_range(rests), "raised_max_ms": raised.max(),
			"settle_changes_per_frame_max": chs.max(), "body_changes_on_touchdown_frame_max": tch.max(),
			"repress_cases": rep_n, "repress_alternation_failures": rep_bad, "per_stop": stops}
		print("SIM %3d fps: %2d stops  release->v8 %s ms  feet down %s  post-contact %s  at rest %s  raised max %.0f  changes/frame max %d (touchdown frame %d)  re-press %d (alternation fails %d)" % [fps, stops.size(),
			str(_sim_range(v8s).map(func(v): return snappedf(v, 0.1))), str(_sim_range(downs).map(func(v): return snappedf(v, 0.1))),
			str(_sim_range(posts).map(func(v): return snappedf(v, 0.1))), str(_sim_range(rests).map(func(v): return snappedf(v, 0.1))),
			raised.max(), chs.max(), tch.max(), rep_n, rep_bad])
		if fps >= 30 and (rep_bad > 0 or float(raised.max()) > STOP_RAISED_LIMIT_MS + 1e-3):   # gate from 30 fps up (24 fps: recorded only)
			ok = false
	# jittered frame times (fixed seed): 30 / 45 / 60 / 144 fps frames in random order
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
		if sr.has("error"):
			ok = false
			continue
		jit.append(sr)
	report["jitter"] = {"seed": 6061, "frame_rates_mixed": [30, 45, 60, 144], "stops": jit.size(),
		"release_to_v8_ms": _sim_range(jit.map(func(e): return e["v8_ms"])),
		"raised_max_ms": jit.map(func(e): return e["raised_max_ms"]).max(), "per_stop": jit}
	print("SIM jitter: %d stops  release->v8 %s ms  raised max %.0f" % [jit.size(), str(report["jitter"]["release_to_v8_ms"].map(func(v): return snappedf(v, 0.1))), report["jitter"]["raised_max_ms"]])
	report["gates_ok"] = ok
	var rname := "%s_gait-driver_protagonist-female-south-run-v06-sim-timing-receipt_%s_%s-%s.json" % [SLUG, VARIANT, stamp, uid]
	if out_abs != "":
		var f := FileAccess.open(out_abs.path_join(rname), FileAccess.WRITE)
		f.store_string(JSON.stringify(report, " ") + "\n")
		f.close()
		print("SIM RECEIPT " + rname)
	quit(0 if ok else 1)


# =====================================================================================================================
func _initialize() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("RUN_V06_CAPTURE FAIL: " + reason)
	print("RUN_V06_CAPTURE FAIL: " + reason)
	Input.action_release("move_up")
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


# v04 neck alignment, measured on CAPTURED pixels: the (dx, dy) offset at which the v8 head texels (crown / face) and the
# v8 scarf / chest texels best match the capture relative to the drawn origin.  A neck shear is a head offset that differs
# from the torso offset (v03: the head stayed at dx 0 while the torso moved by sx).
func _best_offset(cap: Image, origin: Vector2i, texels: Array) -> Array:
	var best := [-99, -99, -1]
	for dy in range(-1, 3):
		for dx in range(-2, 3):
			var n := 0
			for t in texels:
				var w: Vector2i = origin + t[0] + Vector2i(dx, dy)
				var c := cap.get_pixelv(w)
				var e: Color = t[1]
				if c.r8 == e.r8 and c.g8 == e.g8 and c.b8 == e.b8:
					n += 1
			if n > int(best[2]):
				best = [dx, dy, n]
	return best


func _neck(cap: Image, origin: Vector2i) -> Dictionary:
	var h := _best_offset(cap, origin, neck_head)
	var t := _best_offset(cap, origin, neck_torso)
	return {"head": h, "torso": t, "shear_dx": int(h[0]) - int(t[0]), "shear_dy": int(h[1]) - int(t[1]),
		"head_match": float(h[2]) / neck_head.size(), "torso_match": float(t[2]) / neck_torso.size()}


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


# v05 reversal: capture the scene's own runtime hero (placeholder north walk) with the pilot and its shadow hidden.
func _draw_runtime(su: Array) -> Array:
	var hero: Sprite2D = su[1]
	var pilot: Sprite2D = su[2]
	var shadow: Sprite2D = su[5]
	pilot.visible = false
	shadow.visible = false
	hero.visible = true
	var cap := await _capture()
	hero.visible = false
	pilot.visible = true
	shadow.visible = true
	return [cap, _pin(hero, su[3]) - PIN]


func _free(host: Node) -> void:
	host.queue_free()
	await process_frame
	await process_frame


func _out_name(scene_key: String, what: String, stamp: String, uid: String, ext: String) -> String:
	var n := "%s_%s_protagonist-female-south-run-v06-%s-h48_%s_%s-%s.%s" % [SLUG, scene_key, what, VARIANT, stamp, uid, ext]
	if n.length() > 150:
		push_error("output name too long (%d): %s" % [n.length(), n])
	return n


var v8_boot := {}     # side -> {Vector2i cell: Color}
var last_settle_log := []   # v06: the gait driver's settle event log of the last _drive() call


# v06: settle changes allowed on one frame: 1 when the frame is not longer than settle_gap_ms (60 fps and above), else 2
func _change_limit(dt: float) -> int:
	return 1 if dt * 1000.0 <= float(manifest["stop"]["settle_gap_ms"]) + 1e-6 else 2


# Drives one sequence.  plan: Array of {"input": bool, "dt": float}.  Returns per-tick records.
func _drive(su: Array, plan: Array, motion_dir: String, tag: String, crop: Rect2i, full_saves: Dictionary = {}) -> Array:
	var host: Node2D = su[0]
	var hero: Sprite2D = su[1]
	var ground_off: float = su[3]
	var bg: Image = su[4]
	var loco := Loco.new()
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
			# v05 reversal: no north pilot art exists (out of scope), so the scene's own RUNTIME hero sprite (its existing
			# placeholder north walk) is shown while move_up is held; the pilot and its test shadow are hidden.  Not gated as
			# pilot art; the pilot re-enters with the start rule from v8 when south is pressed again.
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
			# re-entry after a reversal: a fresh gait driver at the current position (both boots on their v8 spots), so the
			# next south tick restarts exactly like a start from the v8 idle
			loco = Loco.new()
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
		ticks.append({"tick": t, "input": bool(step["input"]), "dir": "down" if bool(step["input"]) else "", "dt": float(step["dt"]), "show_v8": bool(r["show_v8"]),
			"modes": r["modes"], "state": r["state"], "events": r["events"], "phase": r["phase"], "dist": r["dist"],
			"hero_logical": [hero.position.x, hero.position.y], "origin": origin, "meas": meas, "boots_w": boots_w,
			"cell_h": img.get_height(), "neck": neck, "legs": info.get("legs", {})})
	Input.action_release("move_down")
	last_settle_log = loco.settle_log.duplicate(true)
	return ticks


# Per-tick summary: planted-boot world displacement (pixels), airborne steps, silhouette XOR, crown step.
func _summ(ticks: Array) -> Array:
	var out := []
	var prev: Dictionary = {}
	for tk in ticks:
		if bool(tk.get("runtime_north", false)):
			out.append({"tick": tk["tick"], "input": true, "dir": "up", "runtime_north": true, "show_v8": false, "modes": tk["modes"],
				"events": tk["events"], "hero_logical": tk["hero_logical"], "pin_window_y": tk["origin"].y + PIN.y})
			prev = {}
			continue
		var m: Dictionary = tk["meas"]
		var e := {"tick": tk["tick"], "input": tk["input"], "show_v8": tk["show_v8"], "modes": tk["modes"], "state": tk["state"],
			"events": tk["events"], "phase": tk["phase"], "hero_logical": tk["hero_logical"], "pin_window_y": tk["origin"].y + PIN.y,
			"head_top_window_y": m["head_top_window_y"], "sole_window_y": m["sole_window_y"], "sole_x_extent": m["sole_x_extent"],
			"lowest_cell_row": maxi(m["sole_window_y"]["vl"], m["sole_window_y"]["vr"]) - tk["origin"].y,
			"shadow_px_outside_character": m["shadow_px_outside_character"],
			"shadow_px_darker_than_background": m["shadow_px_darker_than_background"],
			"neck_head_offset": [tk["neck"]["head"][0], tk["neck"]["head"][1]], "neck_torso_offset": [tk["neck"]["torso"][0], tk["neck"]["torso"][1]],
			"legs": tk["legs"]}
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
	var shear_max := 0
	var head_dx_nonzero := 0
	var fwd_len := {}
	var gap_n := 0
	var gap_sum := 0
	var gap_max := 0
	var gap2 := 0
	var gap3 := 0
	for i in range(maxi(1, from_i), mini(summ.size(), to_i)):
		var e: Dictionary = summ[i]
		if bool(e.get("runtime_north", false)):
			continue
		if bool(e["input"]):
			# v05 floor gap on CAPTURED pixels: rows between each boot's v8 ground row and its lowest visible pixel, the
			# smaller of the two (0 when a boot reaches its floor row): both boots drawn above the floor = a hop look
			var gl := int(manifest["rig"]["ground_rows"]["vl"]) - (int(e["sole_window_y"]["vl"]) - (int(e["pin_window_y"]) - PIN.y))
			var gr := int(manifest["rig"]["ground_rows"]["vr"]) - (int(e["sole_window_y"]["vr"]) - (int(e["pin_window_y"]) - PIN.y))
			var gap := maxi(0, mini(gl, gr))
			gap_n += 1
			gap_sum += gap
			gap_max = maxi(gap_max, gap)
			gap2 += 1 if gap >= 2 else 0
			gap3 += 1 if gap >= 3 else 0
		xor_max = maxi(xor_max, int(e.get("silhouette_xor", 0)))
		cxor_max = maxi(cxor_max, int(e.get("cell_silhouette_xor", 0)))
		head_max = maxi(head_max, absi(int(e.get("head_step", 0))))
		sh_min = mini(sh_min, int(e["shadow_px_darker_than_background"]))
		shear_max = maxi(shear_max, absi(int(e["neck_head_offset"][0]) - int(e["neck_torso_offset"][0])))
		head_dx_nonzero += 1 if int(e["neck_head_offset"][0]) != 0 else 0
		for s in e.get("legs", {}):
			if int(e["state"]["feet"][s]["o"]) > 0:
				fwd_len[s] = maxi(int(fwd_len.get(s, 0)), int(e["legs"][s]["hip_to_sole"]))
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
		"head_step_max_px": head_max, "shadow_px_darker_than_background_min": sh_min,
		"neck_shear_max_px": shear_max, "ticks_with_head_shifted_with_torso": head_dx_nonzero,
		"forward_leg_hip_to_sole_rows_max": fwd_len,
		"floor_gap_moving_ticks": gap_n, "floor_gap_rows_max": gap_max,
		"floor_gap_rows_mean": (float(gap_sum) / gap_n) if gap_n > 0 else 0.0,
		"floor_gap_share_ge_2_rows": (float(gap2) / gap_n) if gap_n > 0 else 0.0,
		"floor_gap_share_ge_3_rows": (float(gap3) / gap_n) if gap_n > 0 else 0.0}


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


# v05: after release tick rel: the first v8 tick, the switch XOR, raised boots, post-contact settle and the number of body
# changes (bob, hair, torso shift, arms) per tick after the last touchdown (gate: <= 1).
func _release_checks(ticks: Array, rel: int, dt: float) -> Dictionary:
	var v8_at := -1
	for i in range(rel, ticks.size()):
		if bool(ticks[i].get("runtime_north", false)) or bool(ticks[i]["input"]):
			break
		if bool(ticks[i]["show_v8"]):
			v8_at = i
			break
	if v8_at < 0:
		return {"error": "never returned to v8"}
	var pop := _xor(ticks[v8_at]["meas"]["mask"], ticks[v8_at - 1]["meas"]["mask"])
	var raised := _raised_after(ticks.slice(0, v8_at + 1), rel, dt)
	var last_down := rel - 1
	for i in range(rel, v8_at + 1):
		for ev in ticks[i]["events"]:
			if String(ev[0]) == "land":
				last_down = i
	var last_change := last_down
	for i in range(last_down + 1, v8_at + 1):
		if _xor(ticks[i]["meas"]["cell_mask"], ticks[i - 1]["meas"]["cell_mask"]) != 0 or ticks[i]["meas"]["head_top_window_y"] != ticks[i - 1]["meas"]["head_top_window_y"]:
			last_change = i
	var max_changes := 0
	var change_ticks := []
	for i in range(last_down + 1, v8_at):
		var a: Dictionary = ticks[i - 1]["state"]
		var b: Dictionary = ticks[i]["state"]
		var n := 0
		var what := []
		# the hair lag offset (hdy) that appears on a bob tick holds the hair where it was (the body moves under it): one
		# change; hdy counts on its own only when the hair moves without a bob change
		if int(a["bob"]) != int(b["bob"]):
			n += 1
			what.append("bob")
		elif int(a["hdy"]) != int(b["hdy"]):
			n += 1
			what.append("hdy")
		if int(a["sx"]) != int(b["sx"]):
			n += 1
			what.append("sx")
		if a["arms"]["R"] != b["arms"]["R"] or a["arms"]["L"] != b["arms"]["L"]:
			n += 1
			what.append("arms")
		max_changes = maxi(max_changes, n)
		if n > 0:
			change_ticks.append([i - last_down, what])
	# v06: body changes on the frame that shows the last touchdown (the dip lands with the boot; nothing else may change)
	var touch_what := []
	if last_down >= rel:
		var a0: Dictionary = ticks[last_down - 1]["state"]
		var b0: Dictionary = ticks[last_down]["state"]
		if int(a0["sx"]) != int(b0["sx"]):
			touch_what.append("sx")
		if a0["arms"]["R"] != b0["arms"]["R"] or a0["arms"]["L"] != b0["arms"]["L"]:
			touch_what.append("arms")
	return {"v8_at": v8_at, "switch_to_v8_xor": pop, "raised_after_release": raised,
		"v8_after_ms": 1000.0 * (v8_at - rel + 1) * dt,
		"release_to_at_rest_ms": 1000.0 * (last_change - rel + 1) * dt,
		"settle_change_limit_per_tick": _change_limit(dt), "torso_or_arm_change_on_touchdown_tick": touch_what,
		"settle": {"feet_down_ms_after_release": 1000.0 * (last_down - rel + 1) * dt,
			"post_contact_to_v8_ms": 1000.0 * (v8_at - last_down) * dt,
			"post_contact_last_visible_change_ms": 1000.0 * (last_change - last_down) * dt,
			"body_changes_per_tick_max_after_touchdown": max_changes, "body_change_ticks_after_touchdown": change_ticks}}


func _plan_walk(n: int, fps: int) -> Array:
	var plan := [{"input": false, "dt": 1.0 / fps}]
	for i in n:
		plan.append({"input": true, "dt": 1.0 / fps})
	return plan


func _crop_for(su: Array, travel_px: int) -> Rect2i:
	var p := _pin(su[1], su[3])
	return Rect2i(p.x - 80, p.y - 140, 160, 140 + travel_px + 40)


func _run() -> void:
	var sim := _user_arg("sim") == "1"      # v06: window-free gait-driver timing sweep only (no capture)
	if DisplayServer.get_name() == "headless" and not sim:
		_fail("windowed run required")
		return
	var motion_dir := _user_arg("motion-dir")
	if not sim and (motion_dir == "" or DirAccess.make_dir_recursive_absolute(motion_dir) != OK):
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
	SDM = int(manifest["gait"]["stride_px"])
	if sim:
		var sim_out := _user_arg("out-dir") if _user_arg("out-dir") != "" else ProjectSettings.globalize_path(OUTPUT_DIR)
		var sim_stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
		_sim(sim_out, sim_stamp, "%08x" % (randi() & 0xffffffff))
		return
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
	SaveStore.root_path = "user://test-saves/m8-south-run-v06-capture"
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
				if not bool(tk["input"]) or int(tk["dist"]) < int(manifest["gait"]["stride_px"]) * 3 / 2:
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
			print("RUN %s %s ticks %d speed %.3f neck-shear-max %d head-shifted ticks %d fwd-leg %s planted pairs %d (roll %d) row-disp %d x-disp %d roll-x %d texels-changed %d air %d/%d cell-xor-max %d shadow-dark-min %d" % [scene_key, mode,
				ticks.size(), stats["logical_px_per_s_measured"], stats["neck_shear_max_px"], stats["ticks_with_head_shifted_with_torso"],
				str(stats["forward_leg_hip_to_sole_rows_max"]), stats["planted_tick_pairs"], stats["planted_roll_view_change_pairs"],
				stats["planted_sole_row_world_disp_max_px"], stats["planted_sole_x_world_disp_max_px_same_view"],
				stats["planted_roll_sole_x_extent_change_max_px"], stats["planted_boot_texels_changed_same_view"], air_ticks, moving_ticks,
				stats["cell_silhouette_xor_max_per_tick"], stats["shadow_px_darker_than_background_min"]])
			await _free(su[0])
		# ---------------------------------------------------------------- immediate stops from every tick of one stride
		# v06: 30 fps stops in BOTH scenes (frames saved), 144 fps in city-bright
		var fps_list := [60, 30] if scene_key != "city-bright" else [60, 30, 144]
		if quick:
			fps_list = [60, 30]
		for fps in fps_list:
			var dt: float = 1.0 / fps
			var per_tick_px: float = 280.0 / fps
			var first := int(ceil((float(SDM) + 8.0) / per_tick_px))         # release inside the 2nd stride
			var count := int(ceil(float(SDM) / per_tick_px))
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
				var save_motion: bool = fps == 60 or fps == 30
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
				# v04: post-contact settle = from the tick after the last touchdown (or the release, if no boot moved) to the v8 PNG;
				# "visible" = to the last tick whose drawn character differs from the tick before it
				var last_down := rel - 1
				for i in range(rel, v8_at + 1):
					for ev in ticks[i]["events"]:
						if String(ev[0]) == "land":
							last_down = i
				var last_change := last_down
				for i in range(last_down + 1, v8_at + 1):
					if _xor(ticks[i]["meas"]["cell_mask"], ticks[i - 1]["meas"]["cell_mask"]) != 0 or ticks[i]["meas"]["head_top_window_y"] != ticks[i - 1]["meas"]["head_top_window_y"]:
						last_change = i
				var rc := _release_checks(ticks, rel, dt)
				if rc.has("error"):
					_fail("%s: %s" % [tag, rc["error"]])
					return
				var settle: Dictionary = rc["settle"]
				if int(settle["body_changes_per_tick_max_after_touchdown"]) > _change_limit(dt):
					_fail("%s: %d body changes on one settle tick %s" % [tag, int(settle["body_changes_per_tick_max_after_touchdown"]), str(settle["body_change_ticks_after_touchdown"])])
					return
				if not (rc["torso_or_arm_change_on_touchdown_tick"] as Array).is_empty():
					_fail("%s: torso / arm change on the touchdown tick %s" % [tag, str(rc["torso_or_arm_change_on_touchdown_tick"])])
					return
				if fps == 30 and float(rc["v8_after_ms"]) > STOP_V8_LIMIT_MS_30FPS + 1e-3:
					_fail("%s: 30 fps release -> v8 %.0f ms > %.0f ms" % [tag, float(rc["v8_after_ms"]), STOP_V8_LIMIT_MS_30FPS])
					return
				var last: Dictionary = ticks[rel - 1]
				var rec := {"fps": fps, "release_tick": rel, "released_at_phase_px": posmod(int(last["phase"]), SDM),
					"modes_at_release": last["modes"], "state_at_release": last["state"],
					"v8_after_ms": 1000.0 * (v8_at - rel + 1) * dt, "switch_to_v8_xor": pop, "raised_after_release": raised, "settle": settle,
					"release_to_at_rest_ms": rc["release_to_at_rest_ms"], "settle_change_limit_per_tick": rc["settle_change_limit_per_tick"],
					"settle_event_log": last_settle_log,
					"walk": ws, "stop": ss, "events": [], "crop": [crop.position.x, crop.position.y, crop.size.x, crop.size.y]}
				for i in range(rel, v8_at + 1):
					for ev in ticks[i]["events"]:
						rec["events"].append([i - rel] + ev)
				rec["ticks"] = summ.slice(maxi(0, rel - 8), mini(summ.size(), v8_at + 3))
				sr["stops"][tag] = rec
				print("STOP %s phase %d modes %s -> v8 after %.0f ms (feet down %.0f, post-contact %.0f, last change +%.0f), raised vl %.0f ms vr %.0f ms, stop cell-xor-max %d walk cell-xor-max %d, switch xor %d, settle changes %s" % [tag,
					rec["released_at_phase_px"], str(last["modes"]), rec["v8_after_ms"], settle["feet_down_ms_after_release"], settle["post_contact_to_v8_ms"],
					settle["post_contact_last_visible_change_ms"], raised["vl"]["longest_raised_ms"], raised["vr"]["longest_raised_ms"],
					ss["cell_silhouette_xor_max_per_tick"], ws["cell_silhouette_xor_max_per_tick"], pop, str(settle["body_change_ticks_after_touchdown"])])
				if pop != 0:
					_fail("%s: switch to v8 changed %d pixels" % [tag, pop])
					return
				for s in ["vl", "vr"]:
					if float(raised[s]["longest_raised_ms"]) > STOP_RAISED_LIMIT_MS:
						_fail("%s: boot %s stayed raised %.0f ms after the release" % [tag, s, raised[s]["longest_raised_ms"]])
						return
				await _free(su[0])
		# ---------------------------------------------------------------- re-press: release at several phases x re-press after k ticks
		# v06: re-press at 60 fps (v05's cases) and at 30 and 144 fps (release frames and gaps at about the same times)
		var rep_sets := []      # [fps, release frames, gaps in frames, saved gaps]
		if scene_key == "city-bright":
			rep_sets = [[60, [12, 16, 20, 24, 28, 32], [1, 2, 3, 5, 8, 14, 30], [1, 3, 8, 30]],
				[30, [6, 8, 10, 12, 14, 16], [1, 2, 4, 7, 15], [1, 4]],
				[144, [29, 38, 48, 58, 67, 77], [1, 3, 7, 12, 19, 34], []]]
		else:
			rep_sets = [[60, [16, 24, 32], [1, 3, 8, 30], [1, 8]], [30, [8, 12, 16], [1, 4, 15], [1, 4]]]
		if quick:
			rep_sets = [[60, [16, 28], [1, 8], [1, 8]], [30, [8, 14], [1, 4], [1]]]
		var rep_cases := []
		for rset in rep_sets:
			for n_walk0 in rset[1]:
				for gap0 in rset[2]:
					rep_cases.append([rset[0], n_walk0, gap0, gap0 in rset[3]])
		for cs in rep_cases:
			var rfps: int = cs[0]
			var n_walk: int = cs[1]
			var gap: int = cs[2]
			su = await _setup(spec)
			if su.is_empty():
				return
			var dt := 1.0 / float(rfps)
			var n_run := int(round(0.3 * rfps))          # 300 ms of running after the re-press (v05: 18 ticks at 60 fps)
			var plan := _plan_walk(n_walk, rfps)
			for i in gap:
				plan.append({"input": false, "dt": dt})
			for i in n_run:
				plan.append({"input": true, "dt": dt})
			for i in maxi(2, int(round(4.0 * rfps / 60.0))):
				plan.append({"input": false, "dt": dt})
			var tag := ("%s_repress-%03d-gap-%02d" % [scene_key, n_walk, gap]) if rfps == 60 else ("%s_repress-%dfps-%03d-gap-%02d" % [scene_key, rfps, n_walk, gap])
			var save_motion: bool = bool(cs[3])
			var crop := _crop_for(su, int((n_walk + n_run) * 280.0 / float(rfps)) + 10) if save_motion else Rect2i()
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
			var rr := _planted_stats(summ, rp, mini(summ.size(), rp + int(round(0.2 * rfps))))
			var rec := {"fps": rfps, "release_tick": rel, "repress_tick": rp, "gap_ticks": gap, "released_at_phase_px": posmod(int(ticks[rel - 1]["phase"]), SDM),
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
		# ---------------------------------------------------------------- NORMAL-SPEED SHOWREELS (v05: 60 fps; v06: + 30 fps)
		# idle -> start -> sustained run (2 cycles) -> quick release / re-press (50 ms at 60 fps, 67 ms at 30) -> run -> reversal
		# (move_up; runtime placeholder north walk) -> south again (pilot re-enters from v8) -> release to v8 -> short run ->
		# release to v8.  Segment lengths are v05's 60 fps tick counts scaled to the frame rate.
		for reel_fps in ([] if quick else [60, 30]):
			su = await _setup(spec)
			if su.is_empty():
				return
			var dt60 := 1.0 / float(reel_fps)
			var reel := []
			var segs := [["idle", 18], ["down", 36], ["idle", 3], ["down", 12], ["up", 24], ["down", 24], ["idle", 30], ["down", 10], ["idle", 30]]
			var seg_marks := []
			for sg in segs:
				var n_seg := maxi(1, int(round(float(sg[1]) * reel_fps / 60.0)))
				seg_marks.append([String(sg[0]), reel.size(), n_seg])
				for i in n_seg:
					reel.append({"input": String(sg[0]) != "idle", "dir": String(sg[0]) if String(sg[0]) != "idle" else "", "dt": dt60})
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
					var rc := _release_checks(rticks, i, dt60)
					var interrupted: bool = rc.has("error")
					if not interrupted:
						if int(rc["switch_to_v8_xor"]) != 0 or int(rc["settle"]["body_changes_per_tick_max_after_touchdown"]) > _change_limit(dt60) \
								or not (rc["torso_or_arm_change_on_touchdown_tick"] as Array).is_empty() \
								or (reel_fps == 30 and float(rc["v8_after_ms"]) > STOP_V8_LIMIT_MS_30FPS + 1e-3):
							_fail("%s release at tick %d: %s" % [rtag, i, str(rc)])
							return
						for s in ["vl", "vr"]:
							if float(rc["raised_after_release"][s]["longest_raised_ms"]) > STOP_RAISED_LIMIT_MS:
								_fail("%s release at tick %d: boot %s raised too long" % [rtag, i, s])
								return
					releases.append({"release_tick": i, "released_at_phase_px": posmod(int(rticks[i - 1].get("phase", 0)), SDM),
						"interrupted_by_input_before_v8": interrupted, "checks": rc if not interrupted else {}})
			var rframes := []
			for tk in rticks:
				rframes.append({"tick": tk["tick"], "dir": String(tk.get("dir", "")), "runtime_north": bool(tk.get("runtime_north", false)),
					"show_v8": bool(tk["show_v8"]), "pin_window": [int(round(float(tk["hero_logical"][0]) * 2.0)), int(tk["origin"].y) + PIN.y]})
			sr["showreel" if reel_fps == 60 else "showreel_%dfps" % reel_fps] = {"fps": reel_fps, "segments": seg_marks, "frames_dir_tag": rtag, "ticks": rticks.size(), "releases": releases,
				"pilot_stats": rstats, "frames": rframes,
				"note": "full 1280x720 window frames, one per %d fps tick (normal speed); runtime_north ticks show the scene's own runtime hero sprite (placeholder north walk), not the pilot" % reel_fps}
			print("SHOWREEL %s ticks %d releases %s floor-gap max %d mean %.2f >=3 %.3f planted pairs %d" % [rtag, rticks.size(),
				str(releases.map(func(r): return [r["release_tick"], r["interrupted_by_input_before_v8"], r["checks"].get("v8_after_ms", -1)])),
				rstats["floor_gap_rows_max"], rstats["floor_gap_rows_mean"], rstats["floor_gap_share_ge_3_rows"], rstats["planted_tick_pairs"]])
			await _free(su[0])
		# ---------------------------------------------------------------- v05 REVERSAL sweep: south run -> move_up (runtime
		# placeholder north) at every 3rd 60 fps tick of one stride -> south again (pilot re-entry from v8) -> release to v8
		var rev_first := int(ceil((float(SDM) + 8.0) / (280.0 / 60.0)))
		var rev_count := int(ceil(float(SDM) / (280.0 / 60.0)))
		var rev_step := 3 if scene_key == "city-bright" else 6
		if quick:
			rev_step = 9
		sr["reversal"] = {}
		for k in range(0, rev_count, rev_step):
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
			var save_motion: bool = k == 0 or k == 9
			var crop := _crop_for(su, int(n_walk * 280.0 / 60.0) + 10) if save_motion else Rect2i()
			var ticks := await _drive(su, plan, motion_dir if save_motion else "", tag, crop)
			if ticks.is_empty():
				return
			var summ := _summ(ticks)
			var st_all := _planted_stats(summ, 1, summ.size())
			if not _planted_ok(st_all):
				_fail("%s planted boot moved %s" % [tag, str(st_all)])
				return
			var back: int = n_walk + 1 + 12            # first south tick after the reversal
			var rel: int = back + 24
			var rc := _release_checks(ticks, rel, dt)
			if rc.has("error") or int(rc["switch_to_v8_xor"]) != 0 or int(rc["settle"]["body_changes_per_tick_max_after_touchdown"]) > _change_limit(dt) \
					or not (rc["torso_or_arm_change_on_touchdown_tick"] as Array).is_empty():
				_fail("%s final stop %s" % [tag, str(rc)])
				return
			# re-entry: which boot lifts first and which lands first after the pilot comes back
			var first_lift := ""
			var first_land := ""
			var first_land_ms := -1.0
			for i in range(back, rel):
				for ev in ticks[i]["events"]:
					if first_lift == "" and String(ev[0]) == "restart":
						first_lift = String(ev[4]) if ev.size() > 4 else ""
					if first_land == "" and String(ev[0]) == "land":
						first_land = String(ev[1])
						first_land_ms = 1000.0 * (i - back) * dt
			var rec := {"turn_tick": n_walk + 1, "turned_at_phase_px": posmod(int(ticks[n_walk]["phase"]), SDM),
				"modes_at_turn": ticks[n_walk]["modes"], "runtime_north_ticks": 12, "reentry_tick": back,
				"reentry_lifts_first": first_lift, "reentry_first_touchdown": first_land, "reentry_first_touchdown_ms": first_land_ms,
				"final_stop": rc, "pilot_stats": st_all, "crop": [crop.position.x, crop.position.y, crop.size.x, crop.size.y]}
			rec["ticks"] = summ.slice(maxi(0, n_walk - 4), mini(summ.size(), back + 12))
			sr["reversal"][tag] = rec
			print("REVERSAL %s turn phase %d modes %s; re-entry lifts %s, first touchdown %s at %.0f ms; final stop v8 after %.0f ms" % [tag,
				rec["turned_at_phase_px"], str(rec["modes_at_turn"]), first_lift, first_land, first_land_ms, rc["v8_after_ms"]])
			await _free(su[0])
		report_scenes[scene_key] = sr
	for nm in outputs:
		outputs[nm]["sha256_bytes"] = FileAccess.get_sha256(out_abs.path_join(nm))
	var report := {
		"project": "Worlds Between", "milestone": "M8",
		"purpose": "TEST-ONLY real-Godot captures of the UNAPPROVED / NONRUNTIME female SOUTH RUN motion pilot v06 (v05 art and gait - 42 px step at 6.67 steps/s, landing 2 rows below the v8 spot, low early-forward swing - with ONE correction: the stop runs on a time-based event clock instead of counting frames; part library + test-only compositor + test-only contact shadow) moved by the scenes' own _process at MOVE_SPEED 140; stops from every frame of one stride at 60 / 30 fps (both scenes) and 144 fps (city-bright); re-press at 60 / 30 / 144 fps; normal-speed showreels at 60 and 30 fps (start, sustained run, release, quick re-press, reversal) and a reversal sweep",
		"status": "UNAPPROVED / NONRUNTIME; not art acceptance; Codex / creator visual decision pending",
		"art_approved": false, "human_reviewed": false, "runtime_integrated": false, "quick_debug_run": quick,
		"approved_scope_unchanged": "selout v8 SOUTH IDLE static frame and the 48 logical px display scale only",
		"capture_tool": "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-godot-capture_m8-w09_20261017-211600-ff47ce98.gd",
		"reversal_note": "no north pilot art exists (out of scope, creator review first): while move_up is held the scene's own runtime hero sprite (placeholder north walk) is shown and the pilot is hidden; those ticks are labelled runtime_north and are not pilot evidence; the pilot re-enters from v8 with the start rule",
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
			"every re-press: the next touchdown is the other boot (no boot touches down twice in a row)",
			"v04: on every captured tick the v8 head (crown / face) and the v8 scarf / chest match the capture at the same (dx, dy) (no neck shear) and no neck seam texel was filled",
			"v06: after the last touchdown of every stop (sweep, showreel, reversal) at most one body change (dip, hair, torso shift, arms) per tick at 60 / 144 fps and at most two at 30 fps (frames longer than settle_gap_ms); no torso or arm change on the frame that shows the last touchdown",
			"v06: every 30 fps release (stop sweeps in both scenes, 30 fps showreels) reaches the v8 PNG within %d ms" % int(STOP_V8_LIMIT_MS_30FPS),
			"v06: re-press at 60 / 30 / 144 fps: the next touchdown is the other boot; planted boot pinned",
			"v05: showreel and reversal sequences: planted boot, fidelity, neck and v8-switch gates on every pilot tick; every uninterrupted release returns to the v8 PNG with 0 changed pixels"],
		"outputs": outputs, "scenes": report_scenes,
	}
	var rname := "%s_city-annex_protagonist-female-south-run-v06-capture-receipt-h48_%s_%s-%s.json" % [SLUG, VARIANT, stamp, uid]
	var f := FileAccess.open(out_abs.path_join(rname), FileAccess.WRITE)
	f.store_string(JSON.stringify(report, " ") + "\n")
	f.close()
	print("RECEIPT " + rname)
	print("STAMP %s-%s" % [stamp, uid])
	quit(0)
