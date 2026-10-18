extends SceneTree

# Runtime check and captures for the OPT-IN sentry automaton sprite + animation v2 pilot (UNAPPROVED; art acceptance 0).
# Adapted from the untracked m8-anim-v02 check (ad3f9d97) with sentry assertions only: no arena band, arena ID, contact
# shadow, label outline or patrol sprite dependencies. The pilot is off by default (`-- --sentry-v2-pilot` or
# sentry_v2_override = 1 turns it on), so this script first proves the default stays the placeholder block, then sets
# the override for the v2 checks. The creator approved v2 as the action direction baseline only, not the sprite or art.
# Run windowed (not --headless) to capture; `-- --no-capture` runs the logic checks only.
#   --capture-dir=<absolute dir>  capture output dir (default: <repo>/outputs/<run dir>)
#   --cli-flag-only               with --sentry-v2-pilot: prove the command-line switch alone enables the pilot, then quit
const BATTLE_SCENE_PATH := "res://scenes/battle_arena.tscn"
const BATTLE_SCRIPT_PATH := "res://scripts/battle_arena.gd"
# File names stay at or under 121 characters (the run directory carries the unapproved-v01 tag).
const PREFIX := "rpg-2-star-ocean-the-second_sentry-v2"
const TAG := "unapproved-v01"
const CLI_FLAG := "--sentry-v2-pilot"
const DIR_ARG := "--capture-dir="
const STATIC_PATH := "res://assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-idle-left_m8-pilot-v01_20261014-221901-e3ab87f9.png"
const STRIP_PATH := "res://assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-strip-left_m8-anim-v02_20261014-230329-ffefdc6f.png"
const V1_STRIP_PATH := "res://assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-strip-left_m8-anim-v01_20261014-223820-f181f893.png"
const STATIC_SHA256 := "5ca76fe9fdedcdca549fb11597f3fc44a68b713382ffb11a8976f4282e652462"
const STRIP_SHA256 := "26d1fb1c0d13371f348ec04c27b35901bd8a06701694446374dae6f27c35e52e"
const ASSET_MANIFEST := "game/assets/enemies/sentry-automaton-pilot-0b9664e2/rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-manifest_m8-anim-v02_20261014-230329-ffefdc6f.json"
const CHECK_SCRIPT := "game/tests/rpg-2-star-ocean-the-second_sentry-automaton_v2-optin-pilot-check-capture_unapproved-v01_20261018-102800-c3f81a6d.gd"
const CELL := Vector2i(112, 62)
const STATIC_CELL := Vector2i(96, 62)
const MARGIN := 16
const ANCHOR := Vector2(46, 60)
const STATIC_ANCHOR := Vector2(48, 60)
const BODY_CENTER_X := 64.0
const FRAME_COUNT := 21
const GAIT_STEP := 4.0
const FLOOR_Y := 272.0
const STATES := {"idle": [0, 1, 2, 3], "move": [4, 5, 6, 7, 8, 9, 10, 11], "windup": [12, 13], "strike": [14, 15], "hit": [16, 17], "defeat": [18, 19, 20]}
# The v1 runtime entry, replayed through the same code for the foot-slide sensitivity measurement only.
const V1_ENTRY := {
	"path": V1_STRIP_PATH,
	"states": {"idle": [0, 1, 2, 3], "move": [4, 5, 6, 7], "windup": [8, 9], "strike": [10, 11], "hit": [12, 13], "defeat": [14, 15, 16]},
	"frame_time": {"idle": 0.22, "move": 0.12, "strike": 0.15, "hit": 0.12, "defeat": 0.16},
}
const RING_RADIUS := 30.0
const BLOCK_RING_VISIBLE_PX := 1248
# Near-foot sole rows of the static pilot, in v2 cell coordinates.
const NEAR_FRONT_SOLE := Rect2i(1 + MARGIN, 59, 16, 1)
const NEAR_REAR_SOLE := Rect2i(79 + MARGIN, 59, 16, 1)
# Head and near-front foot offsets of the contact frames (from the v2 author poses), for the eye and claw boxes.
const CONTACT_POSE := {
	12: {"head": Vector2i(2, -1), "foot": Vector2i(2, -4)},
	13: {"head": Vector2i(3, -2), "foot": Vector2i(4, -7)},
	14: {"head": Vector2i(-11, 2), "foot": Vector2i(-13, 0)},
	15: {"head": Vector2i(-5, 1), "foot": Vector2i(-6, -3)},
	16: {"head": Vector2i(3, -1), "foot": Vector2i(0, 0)},
	17: {"head": Vector2i(1, 0), "foot": Vector2i(0, 0)},
}
const WINDOWS := {"1280": Vector2i(1280, 720), "640": Vector2i(640, 360)}

var app: Node
var battle_script: GDScript
var stamp := ""
var run_id := ""
var capture_dir := ""
var records: Array = []
var crops := {}
var capture_enabled := true
var strip_image: Image
var v1_strip_image: Image
var static_image: Image
var frame_audit: Array = []
var overlap_report := {}
var parity := {}
var walk_report := {}
var visibility_report := {}
var default_report := {}
var pass_count := 0
var scale := 2


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	app = root.get_node("AppState")
	battle_script = load(BATTLE_SCRIPT_PATH)
	SaveStore.root_path = "user://test-saves/sentry-v2-optin-pilot"
	var args := OS.get_cmdline_user_args()
	capture_enabled = not args.has("--no-capture") and DisplayServer.get_name() != "headless"
	stamp = Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	run_id = "%08x" % (randi() & 0xffffffff)
	for argument in args:
		if argument.begins_with(DIR_ARG):
			capture_dir = argument.trim_prefix(DIR_ARG)
	if capture_dir.is_empty():
		capture_dir = ProjectSettings.globalize_path("res://../outputs/sentry-v2-optin-%s_%s-%s" % [TAG, stamp, run_id])
	if args.has("--cli-flag-only"):
		if await _check_cli_flag():
			print("SENTRY_V2_OPTIN CLI PASS checks=%d" % pass_count)
			quit(0)
		return
	if not _check(not args.has(CLI_FLAG), "full check runs without %s (it sets sentry_v2_override itself)" % CLI_FLAG):
		return
	if not await _check_default_off():
		return
	battle_script.sentry_v2_override = 1
	if not await _check_load_and_strip():
		return
	if not _check_frame_audit():
		return
	if not await _check_combat_unchanged():
		return
	if not await _check_simulation_parity():
		return
	if not await _check_state_selection():
		return
	if not await _check_walk_foot_lock():
		return
	if not await _check_fallbacks():
		return
	if capture_enabled:
		DirAccess.make_dir_recursive_absolute(capture_dir)
	for window_key in WINDOWS:
		if not await _run_captures(window_key):
			return
	if capture_enabled and not _write_manifest():
		return
	battle_script.sentry_v2_override = -1
	print("SENTRY_V2_OPTIN PASS checks=%d frames=%d captures=%d crops=%d" % [pass_count, FRAME_COUNT, records.size(), _crop_count()])
	quit(0)


func _crop_count() -> int:
	var total := 0
	for key in crops:
		total += Array(crops[key]).size()
	return total


func _prepare_party(destination: String) -> void:
	app.begin_new_run()
	app.hero_appearance = "male"
	app.recruit_member("liang-xu")
	app.recruit_member("zhao-ling")
	app.ji_records_checked = true
	app.recruit_member("ji-cheng")
	app.select_destination(destination)


func _open_battle(enemy_id: String, settings: Dictionary = {}) -> Node2D:
	if current_scene != null:
		current_scene.queue_free()
		current_scene = null
		await process_frame
	app.begin_battle(enemy_id, Vector2(330, 215))
	var battle: Node2D = load(BATTLE_SCENE_PATH).instantiate()
	for key in settings:
		battle.set(key, settings[key])
	root.add_child(battle)
	current_scene = battle
	await process_frame
	await process_frame
	return battle


func _check_cli_flag() -> bool:
	if not _check(OS.get_cmdline_user_args().has(CLI_FLAG) and battle_script.sentry_v2_override == -1, "CLI mode: %s given, override untouched (-1)" % CLI_FLAG):
		return false
	if not _check(battle_script.sentry_v2_enabled(), "CLI flag alone enables the pilot"):
		return false
	_prepare_party("scifi.ruins")
	var battle: Node2D = await _open_battle("sentry")
	if not _check(battle.get("enemy_texture") != null and battle.get("enemy_animation_texture") != null, "CLI flag loads the static pilot and the v2 strip for the sentry"):
		return false
	battle = await _open_battle("patrol")
	if not _check(battle.get("enemy_texture") == null and battle.get("enemy_animation_texture") == null, "CLI flag leaves the patrol on its placeholder block"):
		return false
	battle_script.sentry_v2_override = 0
	battle = await _open_battle("sentry")
	var off_ok: bool = battle.get("enemy_texture") == null and battle.get("enemy_animation_texture") == null
	battle_script.sentry_v2_override = -1
	return _check(off_ok, "sentry_v2_override = 0 wins over the CLI flag")


func _check_default_off() -> bool:
	# Default: no flag, override -1. The sentry keeps the placeholder block and the r30 ring exactly as at the base commit.
	if not _check(battle_script.sentry_v2_override == -1 and not battle_script.sentry_v2_enabled(), "pilot off by default (override -1, no %s)" % CLI_FLAG):
		return false
	var constants: Dictionary = battle_script.get_script_constant_map()
	if not _check(constants.get("SENTRY_V2_ART_APPROVED") == false and constants.get("SENTRY_V2_SPRITE_ACCEPTED") == false, "native bools: SENTRY_V2_ART_APPROVED = false, SENTRY_V2_SPRITE_ACCEPTED = false"):
		return false
	if not _check(Array(constants["ENEMY_SPRITE_PILOTS"].keys()) == ["sentry"] and Array(constants["ENEMY_SPRITE_ANIMATIONS"].keys()) == ["sentry"], "pilot tables hold the sentry only"):
		return false
	for enemy_id in ["sentry", "patrol"]:
		_prepare_party("scifi.ruins")
		var battle: Node2D = await _open_battle(enemy_id, {"paused": true})
		if not _check(battle.get("enemy_texture") == null and battle.get("enemy_animation_texture") == null, "%s default: no pilot texture loaded" % enemy_id):
			return false
		if not _check(is_equal_approx(float(battle.get("enemy_telegraph_center_y")), 240.0) and battle.get("enemy_telegraph_scale") == Vector2.ONE and is_zero_approx(battle._enemy_body_offset_x()), "%s default: r30 ring at y 240, centred on enemy_x" % enemy_id):
			return false
		battle.enemy_x = 401.3
		if not _check(is_equal_approx(battle._enemy_draw_x(), 401.0) and not battle._enemy_visual_in_front(), "%s default: draw x is round(enemy_x), drawn after the fighters" % enemy_id):
			return false
		var state: String = battle.get("enemy_visual_state")
		battle._advance_enemy_visual(0.5, true)
		if not _check(battle.get("enemy_visual_state") == state and is_zero_approx(float(battle.get("enemy_visual_clock"))), "%s default: visual state machine is inert" % enemy_id):
			return false
		battle.enemy_hp = 0
		battle.queue_redraw()
		await process_frame
		default_report[enemy_id] = {"enemyTexture": false, "animationTexture": false, "ringCenterY": 240.0, "ringScale": [1.0, 1.0]}
	# The per-instance switches only narrow the pilot: with the override off they cannot turn it on.
	_prepare_party("scifi.ruins")
	var forced: Node2D = await _open_battle("sentry", {"enemy_sprite_pilot_enabled": true, "enemy_sprite_animation_enabled": true})
	return _check(forced.get("enemy_texture") == null and forced.get("enemy_animation_texture") == null, "per-instance switches cannot enable the pilot without the flag")


func _use_v1_entry(battle: Node2D) -> void:
	# Replays the v1 strip through the current runtime: same cell and anchor as the static pilot, timed gait, heroes always on top.
	battle.enemy_animation = V1_ENTRY
	battle.enemy_animation_texture = load(V1_STRIP_PATH)
	battle.enemy_animation_cell = Vector2(STATIC_CELL)
	battle.enemy_animation_anchor = STATIC_ANCHOR
	battle.enemy_visual_state = "idle"
	battle.enemy_visual_clock = 0.0


func _cell(index: int, image: Image = null) -> Image:
	var source := strip_image if image == null else image
	var width := CELL.x if image == null else STATIC_CELL.x
	return source.get_region(Rect2i(index * width, 0, width, CELL.y))


func _static_window(cell: Image) -> Image:
	return cell.get_region(Rect2i(MARGIN, 0, STATIC_CELL.x, STATIC_CELL.y))


func _check_load_and_strip() -> bool:
	if not _check(FileAccess.get_sha256(ProjectSettings.globalize_path(STATIC_PATH)) == STATIC_SHA256 and FileAccess.get_sha256(ProjectSettings.globalize_path(STRIP_PATH)) == STRIP_SHA256, "tracked static PNG and v2 strip match their manifest SHA-256 (sha256-bytes)"):
		return false
	# The first sentry battle goes through the real scene-change path, as the encounter does.
	_prepare_party("scifi.ruins")
	app.begin_battle("sentry", Vector2(330, 215))
	change_scene_to_file(BATTLE_SCENE_PATH)
	await process_frame
	await process_frame
	await process_frame
	var battle: Node2D = current_scene
	if not _check(battle != null and battle.get("enemy_id") == "sentry", "sentry battle opens through change_scene_to_file"):
		return false
	if not _check(app.last_battle_transition_ms < 1000.0, "first transition with the v2 strip under one second (%.2f ms)" % app.last_battle_transition_ms):
		return false
	var static_texture: Texture2D = battle.get("enemy_texture")
	var strip: Texture2D = battle.get("enemy_animation_texture")
	if not _check(static_texture != null and Vector2i(static_texture.get_size()) == STATIC_CELL and battle.get("enemy_anchor") == STATIC_ANCHOR, "static pilot stays loaded as the fallback (96x62, anchor 48,60)"):
		return false
	if not _check(strip != null and Vector2i(strip.get_size()) == Vector2i(CELL.x * FRAME_COUNT, CELL.y), "v2 strip loaded (%s)" % (Vector2i(strip.get_size()) if strip != null else Vector2i.ZERO)):
		return false
	if not _check(Vector2i(battle.get("enemy_animation_cell")) == CELL and battle.get("enemy_animation_anchor") == ANCHOR and is_equal_approx(battle._enemy_body_offset_x(), BODY_CENTER_X - ANCHOR.x), "v2 cell 112x62, anchor (46, 60), body offset +18"):
		return false
	if not _check(is_equal_approx(float(battle.get("enemy_telegraph_center_y")), 241.0) and battle.get("enemy_telegraph_scale") == Vector2(2.0, 1.2), "sentry ring is the wider 2.0 x 1.2 ellipse at y 241"):
		return false
	var opening: String = battle.get("enemy_visual_state")
	if not _check(["idle", "move"].has(opening) and battle._enemy_visual_frame() == int(STATES[opening][0]), "battle opens on the first %s frame" % opening):
		return false
	strip_image = strip.get_image()
	static_image = static_texture.get_image()
	v1_strip_image = load(V1_STRIP_PATH).get_image()
	for image in [strip_image, static_image, v1_strip_image]:
		image.convert(Image.FORMAT_RGBA8)
	if not _check(_same_pixels(_static_window(_cell(0)), static_image), "idle frame 0 holds the static pilot pixel for pixel at the 16 px margin"):
		return false
	if not _check(_cell(0).get_region(Rect2i(0, 0, MARGIN, CELL.y)).is_invisible(), "idle frame 0 margin is empty"):
		return false
	var table: Dictionary = battle.ENEMY_SPRITE_ANIMATIONS["sentry"]["states"]
	return _check(table == STATES, "state table matches the v2 asset manifest")


func _same_pixels(a: Image, b: Image) -> bool:
	# The importer's alpha-border fix rewrites the colour of transparent pixels, so only alpha and opaque colour count.
	if a.get_size() != b.get_size():
		return false
	for y in a.get_height():
		for x in a.get_width():
			var pa := a.get_pixel(x, y)
			var pb := b.get_pixel(x, y)
			if (pa.a > 0.5) != (pb.a > 0.5):
				return false
			if pa.a > 0.5 and not pa.is_equal_approx(pb):
				return false
	return true


func _opaque(image: Image, x: int, y: int) -> bool:
	return image.get_pixel(x, y).a > 0.5


func _sole_planted(image: Image, sole: Rect2i) -> bool:
	for x in range(sole.position.x, sole.end.x):
		if not _opaque(image, x, sole.position.y) or not _opaque(image, x, int(ANCHOR.y)):
			return false
	return true


func _ground_runs(image: Image) -> Array:
	# Opaque runs on the anchor row (the grounded near feet; far feet end 2 px higher).
	var runs: Array = []
	var start := -1
	for x in image.get_width() + 1:
		var on := x < image.get_width() and _opaque(image, x, int(ANCHOR.y))
		if on and start < 0:
			start = x
		elif not on and start >= 0:
			runs.append(Vector2i(start, x - 1))
			start = -1
	return runs


func _centroid_x(image: Image) -> float:
	var total := 0.0
	var count := 0
	for y in image.get_height():
		for x in image.get_width():
			if _opaque(image, x, y):
				total += x
				count += 1
	return total / maxf(1.0, count)


func _check_frame_audit() -> bool:
	var static_cx := _centroid_x(static_image) + MARGIN
	for state in STATES:
		for index in STATES[state]:
			var image := _cell(index)
			var used := image.get_used_rect()
			var front := _sole_planted(image, NEAR_FRONT_SOLE)
			var rear := _sole_planted(image, NEAR_REAR_SOLE)
			var cx := _centroid_x(image)
			frame_audit.append({"frame": index, "state": state, "usedRect": [used.position.x, used.position.y, used.size.x, used.size.y], "nearFrontPlanted": front, "nearRearPlanted": rear, "centroidDriftPx": snappedf(cx - static_cx, 0.01), "anchorRowRuns": _ground_runs(image).map(func(r): return [r.x, r.y])})
			if not _check(used.end.y - 1 == int(ANCHOR.y), "frame %d (%s) last opaque row is the anchor row 60" % [index, state]):
				return false
			if not _check(used.position.x >= 0 and used.end.x <= CELL.x and used.position.y >= 0, "frame %d stays inside its 112x62 cell" % index):
				return false
			# Only the strike may use the left margin: idle, gait, wind-up, hit and defeat stay inside the static 96 px window.
			if state != "strike" and not _check(used.position.x >= MARGIN, "frame %d (%s) leaves the lunge margin empty" % [index, state]):
				return false
			match state:
				"move":
					if not _check(_ground_runs(image).size() >= 1, "frame %d (move) keeps a near foot on the anchor row" % index):
						return false
				"windup":
					if not _check(rear, "frame %d (windup) rear sole planted while the claw is raised" % index):
						return false
				"strike":
					# Impact: the claw stamps 13 px ahead of its static spot; recoil lifts it. The rear sole never moves.
					var stamped := _sole_planted(image, Rect2i(NEAR_FRONT_SOLE.position - Vector2i(13, 0), NEAR_FRONT_SOLE.size))
					if not _check(rear and (index != 14 or stamped), "frame %d (strike) rear sole planted%s" % [index, ", claw stamped 13 px ahead" if index == 14 else ""]):
						return false
				_:
					if not _check(front and rear, "frame %d (%s) near feet planted at the static soles" % [index, state]):
						return false
			var limit := 9.0 if state == "strike" else 4.0
			if not _check(absf(cx - static_cx) <= limit, "frame %d (%s) body centroid drift %.2f px within %.0f px" % [index, state, cx - static_cx, limit]):
				return false
	# Gait lock in the strip: a near foot grounded in two consecutive gait frames sits exactly one 4 px step further back.
	var gait: Array = STATES["move"]
	var compared := 0
	for i in gait.size():
		var a := _ground_runs(_cell(gait[i]))
		var b := _ground_runs(_cell(gait[(i + 1) % gait.size()]))
		for side in 2:
			var ra := a.filter(func(r): return (r.x < CELL.x / 2) == (side == 0))
			var rb := b.filter(func(r): return (r.x < CELL.x / 2) == (side == 0))
			if ra.size() == 1 and rb.size() == 1:
				compared += 1
				if not _check(rb[0] - ra[0] == Vector2i(4, 4), "gait %d -> %d %s foot moves back exactly 4 px in the cell (%s -> %s)" % [gait[i], gait[(i + 1) % gait.size()], "front" if side == 0 else "rear", ra[0], rb[0]]):
					return false
	if not _check(compared == 6, "six grounded near-foot step pairs per gait cycle (%d)" % compared):
		return false
	for state in STATES:
		var frames: Array = STATES[state]
		for i in range(1, frames.size()):
			if not _check(not _same_pixels(_cell(frames[i]), _cell(frames[i - 1])), "%s frame %d differs from frame %d" % [state, frames[i], frames[i - 1]]):
				return false
	# Reused v1 poses: idle, wind-up, hit and defeat are the v1 cells exactly (v2 only adds the margin).
	var reused := {0: 0, 1: 1, 2: 2, 3: 3, 12: 8, 13: 9, 16: 12, 17: 13, 18: 14, 19: 15, 20: 16}
	for v2 in reused:
		if not _check(_same_pixels(_static_window(_cell(v2)), _cell(reused[v2], v1_strip_image)), "v2 frame %d equals v1 frame %d" % [v2, reused[v2]]):
			return false
	print("FRAME_AUDIT %s" % JSON.stringify(frame_audit))
	return true


func _check_combat_unchanged() -> bool:
	_prepare_party("scifi.ruins")
	var battle: Node2D = await _open_battle("sentry")
	var stats: Dictionary = battle.enemy
	if not _check(battle.get("enemy_hp") == 96 and int(stats["damage"]) == 18 and is_equal_approx(float(stats["speed"]), 68.0) and is_equal_approx(float(stats["windup"]), 0.48) and is_equal_approx(float(stats["cooldown"]), 1.10), "sentry stats unchanged (96 / 18 / 68 / 0.48 / 1.10)"):
		return false
	battle.paused = true
	battle.enemy_cooldown = 0.0
	var start_x: float = battle.enemy_x
	battle._update_enemy(0.1)
	if not _check(is_equal_approx(float(battle.enemy_x), start_x - 6.8), "approach step unchanged (%.2f -> %.2f)" % [start_x, battle.enemy_x]):
		return false
	battle.fighters[0]["x"] = 300.0
	battle.enemy_x = 353.0
	battle.enemy_cooldown = 0.0
	battle._update_enemy(0.01)
	if not _check(is_equal_approx(float(battle.enemy_windup), 0.48) and battle.enemy_target_index == 0, "wind-up starts at the 53 px stop distance with 0.48 s"):
		return false
	battle.enemy_windup = 0.0
	battle.fighters[0]["attack_cooldown"] = 0.0
	battle.fighters[0]["x"] = battle.enemy_x - 45.0
	var hp_before: int = battle.enemy_hp
	if not _check(battle._try_attack() and battle.enemy_hp == hp_before - 19, "melee attack deals 19"):
		return false
	var energy_before: int = app.hero_state["energy"]
	if not _check(battle._try_dodge() and app.hero_state["energy"] == energy_before - 12, "dodge consumes 12 energy"):
		return false
	battle.fighters[0]["dodge_time"] = 0.0
	app.hero_state["hp"] = 60
	battle.fighters[0]["guard"] = true
	battle.enemy_target_index = 0
	battle._apply_enemy_hit()
	if not _check(app.hero_state["hp"] == 54, "guarded hit 60 -> 54"):
		return false
	battle.fighters[0]["guard"] = false
	app.hero_state["hp"] = 60
	battle._apply_enemy_hit()
	if not _check(app.hero_state["hp"] == 42, "unguarded hit 60 -> 42"):
		return false
	# Reach is unchanged: a fighter 70 px away is outside the 69 px hit reach, whatever the lunge frame or draw offset shows.
	app.hero_state["hp"] = 60
	battle.fighters[0]["x"] = battle.enemy_x - 70.0
	battle._apply_enemy_hit()
	if not _check(app.hero_state["hp"] == 60, "strike reach still 69 px (fighter at 70 px untouched)"):
		return false
	# Hero melee reach is measured from enemy_x as before: 61 px hits, 62 px misses.
	battle.fighters[0]["attack_cooldown"] = 0.0
	battle.fighters[0]["x"] = battle.enemy_x - 61.0
	hp_before = battle.enemy_hp
	var hit_61: bool = battle._try_attack()
	battle.fighters[0]["attack_cooldown"] = 0.0
	battle.fighters[0]["x"] = battle.enemy_x - 62.0
	var hit_62: bool = battle._try_attack()
	return _check(hit_61 and not hit_62 and battle.enemy_hp == hp_before - 19, "hero melee range still 61 px from enemy_x")


func _simulate(pilot_on: bool) -> Dictionary:
	_prepare_party("scifi.ruins")
	battle_script.sentry_v2_override = 1 if pilot_on else 0
	# Opened paused so no engine frame with a variable delta runs; the extra HP (both runs) keeps the fight going long enough to strike.
	var battle: Node2D = await _open_battle("sentry", {"paused": true})
	battle_script.sentry_v2_override = 1
	var loaded: bool = battle.get("enemy_animation_texture") != null
	battle.auto_mode = true
	battle.enemy_hp = 600
	var trace := PackedStringArray()
	var states := {}
	for step in 600:
		battle.paused = false
		battle._process(1.0 / 60.0)
		battle.paused = true
		var row := "%.4f|%d|%.4f|%.4f|%d|%d" % [battle.enemy_x, battle.enemy_hp, battle.enemy_windup, battle.enemy_cooldown, battle.enemy_attack_count, int(battle.battle_finished)]
		for index in battle.fighters.size():
			var fighter: Dictionary = battle.fighters[index]
			row += "|%.4f|%d|%d" % [fighter["x"], int(app.member_state(String(fighter["id"]))["hp"]), int(app.member_state(String(fighter["id"]))["energy"])]
		trace.append(row)
		if pilot_on:
			states[battle.get("enemy_visual_state")] = int(states.get(battle.get("enemy_visual_state"), 0)) + 1
	return {"trace": trace, "states": states, "loaded": loaded, "finished": battle.battle_finished, "enemy_hp": battle.enemy_hp, "attacks": battle.enemy_attack_count}


func _check_simulation_parity() -> bool:
	# Ten seconds of full-auto combat with the pilot flag on and off must produce identical positions, HP, timers and hits.
	var on: Dictionary = await _simulate(true)
	var off: Dictionary = await _simulate(false)
	if not _check(bool(on["loaded"]) and not bool(off["loaded"]), "simulation runs compare the pilot on against the default (off)"):
		return false
	var first_diff := -1
	for i in on["trace"].size():
		if on["trace"][i] != off["trace"][i]:
			first_diff = i
			break
	parity = {"steps": on["trace"].size(), "firstDifferentStep": first_diff, "enemyAttacks": on["attacks"], "enemyHpEnd": on["enemy_hp"], "battleFinished": on["finished"], "visualStateSteps": on["states"], "comparedAgainst": "sentry_v2_override = 0 (default placeholder)"}
	print("PARITY %s" % JSON.stringify(parity))
	if not _check(first_diff == -1, "auto-battle simulation identical with the pilot flag on and off (600 steps)"):
		return false
	var observed: Dictionary = on["states"]
	return _check(observed.has("move") and observed.has("windup") and observed.has("strike") and observed.has("hit"), "real auto combat drives move, wind-up, strike and hit states (%s)" % JSON.stringify(observed))


func _step_visual(battle: Node2D, seconds: float, moved: bool = false) -> void:
	var remaining := seconds
	while remaining > 0.0001:
		var dt := minf(remaining, 1.0 / 60.0)
		battle._advance_enemy_visual(dt, moved)
		remaining -= dt


func _check_state_selection() -> bool:
	_prepare_party("scifi.ruins")
	var battle: Node2D = await _open_battle("sentry")
	battle.paused = true
	battle.enemy_cooldown = 99.0
	battle.enemy_x = 430.0
	_step_visual(battle, 0.3)
	battle.enemy_visual_state = "idle"
	battle.enemy_visual_clock = 0.0
	# Idle loops 0-3 at 0.22 s per frame (sampled mid-frame).
	_step_visual(battle, 0.05)
	var seen: Array = []
	for i in 5:
		seen.append(battle._enemy_visual_frame())
		_step_visual(battle, 0.22)
	if not _check(seen == [0, 1, 2, 3, 0], "idle loops frames 0-3 (%s)" % [seen]):
		return false
	# Walking toward the party: one gait frame per 4 px travelled, and the drawn sprite moves in those 4 px steps.
	_step_visual(battle, 1.0 / 60.0, true)
	var origin: float = battle.get("enemy_visual_gait_origin_x")
	seen = []
	var worst_offset := 0.0
	for k in 9:
		for sub in 4:
			battle.enemy_x = origin - 4.0 * k - sub
			_step_visual(battle, 1.0 / 60.0, true)
			worst_offset = maxf(worst_offset, absf(battle._enemy_draw_x() - battle.enemy_x))
			if sub == 1:
				seen.append(battle._enemy_visual_frame())
				if not _check(is_equal_approx(battle._enemy_draw_x(), origin - 4.0 * k), "step %d draws at the step position (%.1f)" % [k, battle._enemy_draw_x()]):
					return false
	if not _check(battle.get("enemy_visual_state") == "move" and seen == [4, 5, 6, 7, 8, 9, 10, 11, 4], "walking selects gait frames 4-11 by distance (%s)" % [seen]):
		return false
	if not _check(worst_offset <= 2.0, "drawn sprite stays within 2 px of enemy_x while walking (%.2f)" % worst_offset):
		return false
	# Backing away plays the gait in reverse, so the planted feet still hold.
	seen = []
	var back_origin: float = origin - 32.0
	for k in 4:
		battle.enemy_x = back_origin + 4.0 * k
		_step_visual(battle, 1.0 / 60.0, true)
		seen.append(battle._enemy_visual_frame())
	if not _check(seen == [4, 11, 10, 9], "backing away plays the gait in reverse (%s)" % [seen]):
		return false
	# A one-frame stop keeps the gait pose; a real stop returns to idle after the 0.08 s grace.
	_step_visual(battle, 0.05, false)
	if not _check(battle.get("enemy_visual_state") == "move" and battle._enemy_visual_frame() == 9, "a 0.05 s stop holds the gait frame"):
		return false
	_step_visual(battle, 0.05, false)
	if not _check(battle.get("enemy_visual_state") == "idle" and is_equal_approx(battle._enemy_draw_x(), roundf(battle.enemy_x)), "stopping returns to idle at enemy_x"):
		return false
	# Wind-up: first half coil, second half full coil; it lasts the unchanged 0.48 s.
	battle.fighters[0]["x"] = 300.0
	battle.enemy_x = 353.0
	battle.enemy_cooldown = 0.0
	battle._update_enemy(0.01)
	_step_visual(battle, 0.01)
	var coil_a: int = battle._enemy_visual_frame()
	battle.enemy_windup = 0.2
	var coil_b: int = battle._enemy_visual_frame()
	if not _check(battle.get("enemy_visual_state") == "windup" and coil_a == 12 and coil_b == 13, "wind-up selects 12 then 13 (%d, %d)" % [coil_a, coil_b]):
		return false
	if not _check(not battle._enemy_visual_in_front(), "the wind-up draws behind the fighters"):
		return false
	battle.fighters[0]["attack_cooldown"] = 0.0
	battle.fighters[0]["x"] = battle.enemy_x - 45.0
	battle._try_attack()
	_step_visual(battle, 0.02)
	if not _check(battle.get("enemy_visual_state") == "windup", "a hit during the wind-up keeps the wind-up pose"):
		return false
	# Expiry lands the hit and plays the strike once (2 x 0.15 s) in front of the fighters, then returns to idle.
	app.hero_state["hp"] = 100
	battle.fighters[0]["x"] = battle.enemy_x - 53.0
	battle.enemy_target_index = 0
	battle.enemy_windup = 0.01
	battle._update_enemy(0.02)
	_step_visual(battle, 0.01)
	var strike_a: int = battle._enemy_visual_frame()
	if not _check(battle.get("enemy_visual_state") == "strike" and strike_a == 14 and int(app.hero_state["hp"]) == 82 and battle._enemy_visual_in_front(), "wind-up expiry plays strike frame 14 in front and the hit lands for 18"):
		return false
	battle.fighters[0]["attack_cooldown"] = 0.0
	battle._try_attack()
	_step_visual(battle, 0.2)
	var strike_b: int = battle._enemy_visual_frame()
	if not _check(battle.get("enemy_visual_state") == "strike" and strike_b == 15, "strike continues to frame 15 through a hit"):
		return false
	_step_visual(battle, 0.12)
	if not _check(battle.get("enemy_visual_state") == "idle" and not battle._enemy_visual_in_front(), "strike returns to idle behind the fighters after 0.30 s"):
		return false
	battle.fighters[0]["attack_cooldown"] = 0.0
	battle._try_attack()
	_step_visual(battle, 0.01)
	var hit_a: int = battle._enemy_visual_frame()
	var hit_behind: bool = not battle._enemy_visual_in_front()
	battle.fighters[0]["attack_cooldown"] = 0.0
	battle._try_attack()
	_step_visual(battle, 0.15)
	var hit_b: int = battle._enemy_visual_frame()
	_step_visual(battle, 0.1)
	if not _check(hit_a == 16 and hit_b == 17 and hit_behind and battle.get("enemy_visual_state") == "idle", "hit reaction plays 16, 17 behind the attacker, then idle, unrestarted by a second blow"):
		return false
	var clock: float = battle.get("enemy_visual_clock")
	battle._process(1.0)
	if not _check(is_equal_approx(float(battle.get("enemy_visual_clock")), clock), "pause freezes the animation"):
		return false
	battle.enemy_hp = 5
	battle.enemy_windup = 0.3
	battle.fighters[0]["attack_cooldown"] = 0.0
	battle._try_attack()
	if not _check(battle.battle_finished and battle.battle_won and battle.enemy_hp == 0, "killing blow finishes the battle"):
		return false
	seen = []
	for i in 4:
		seen.append(battle._enemy_visual_frame() if battle.get("enemy_visual_state") == "defeat" else -1)
		battle.paused = false
		battle._process(0.16)
		battle.paused = true
	_step_visual(battle, 5.0)
	seen.append(battle._enemy_visual_frame())
	return _check(seen == [-1, 18, 19, 20, 20], "defeat plays 18-20 and holds the last frame (%s)" % [seen])


func _walk(v1: bool) -> Dictionary:
	# Real enemy code at 60 fps: the sentry walks from its start toward a hero at x 300 and winds up at 53 px.
	_prepare_party("scifi.ruins")
	var battle: Node2D = await _open_battle("sentry", {"paused": true})
	if v1:
		_use_v1_entry(battle)
	var image: Image = v1_strip_image if v1 else strip_image
	var width: int = int(battle.enemy_animation_cell.x)
	var anchor_x: float = battle.enemy_animation_anchor.x
	for index in battle.fighters.size():
		battle.fighters[index]["x"] = 300.0 if index == 0 else 40.0 + index * 30.0
	battle.enemy_cooldown = 0.0
	var start_x: float = battle.enemy_x
	var previous := {}
	var slip := 0.0
	var worst := 0.0
	var pairs := 0
	var grounded_steps := 0
	var move_steps := 0
	var last_move_draw := INF
	var stop_snap := -1.0
	var max_offset := 0.0
	for step in 160:
		var before: float = battle.enemy_x
		battle._update_enemy(1.0 / 60.0)
		battle._advance_enemy_visual(1.0 / 60.0, absf(battle.enemy_x - before) > 0.01)
		var state: String = battle.enemy_visual_state
		var draw_x: float = battle._enemy_draw_x()
		if state != "move":
			if last_move_draw != INF and stop_snap < 0.0:
				stop_snap = absf(draw_x - last_move_draw)
			previous = {}
			continue
		move_steps += 1
		last_move_draw = draw_x
		max_offset = maxf(max_offset, absf(draw_x - battle.enemy_x))
		var cell := image.get_region(Rect2i(battle._enemy_visual_frame() * width, 0, width, CELL.y))
		var current := {}
		for run in _ground_runs(cell):
			current[0 if run.x < width / 2 else 1] = draw_x - anchor_x + run.x
		if not current.is_empty():
			grounded_steps += 1
		for side in current:
			if previous.has(side):
				var moved_px := absf(float(current[side]) - float(previous[side]))
				slip += moved_px
				worst = maxf(worst, moved_px)
				pairs += 1
		previous = current
	return {"travelPx": snappedf(start_x - battle.enemy_x, 0.01), "moveSteps": move_steps, "groundedSteps": grounded_steps, "plantedFootPairs": pairs, "plantedFootSlipPx": snappedf(slip, 0.01), "worstSlipPerFramePx": snappedf(worst, 0.01), "maxDrawOffsetFromEnemyXPx": snappedf(max_offset, 0.01), "stopSnapPx": snappedf(stop_snap, 0.01), "woundUp": battle.enemy_windup > 0.0 or battle.enemy_attack_count > 0}


func _check_walk_foot_lock() -> bool:
	var v2: Dictionary = await _walk(false)
	var v1: Dictionary = await _walk(true)
	walk_report = {"v2": v2, "v1Replay": v1}
	print("WALK %s" % JSON.stringify(walk_report))
	if not _check(bool(v2["woundUp"]) and float(v2["travelPx"]) > 100.0 and int(v2["moveSteps"]) > 100, "real approach walks %.1f px and winds up at the stop distance" % v2["travelPx"]):
		return false
	if not _check(int(v2["groundedSteps"]) == int(v2["moveSteps"]) and int(v2["plantedFootPairs"]) > 90, "a near foot is grounded on every walking frame (%d / %d)" % [v2["groundedSteps"], v2["moveSteps"]]):
		return false
	if not _check(is_zero_approx(float(v2["plantedFootSlipPx"])), "v2 planted feet never slide on the floor (%.2f px over %d frame pairs)" % [v2["plantedFootSlipPx"], v2["plantedFootPairs"]]):
		return false
	if not _check(float(v2["maxDrawOffsetFromEnemyXPx"]) <= 2.0 and float(v2["stopSnapPx"]) <= 2.0, "drawn sprite within 2 px of enemy_x and the stop snap is %.0f px" % v2["stopSnapPx"]):
		return false
	return _check(float(v1["plantedFootSlipPx"]) > 50.0, "the v1 replay through the same code does slide (%.2f px), so the measure is sensitive" % v1["plantedFootSlipPx"])


func _check_fallbacks() -> bool:
	_prepare_party("scifi.ruins")
	var battle: Node2D = await _open_battle("sentry", {"enemy_sprite_animation_enabled": false})
	if not _check(battle.get("enemy_animation_texture") == null and battle.get("enemy_texture") != null and is_zero_approx(battle._enemy_body_offset_x()), "animation switch off keeps the static pilot at its own anchor"):
		return false
	battle = await _open_battle("sentry", {"enemy_animation_override": "res://assets/enemies/sentry-automaton-pilot-0b9664e2/missing-animation-strip.png"})
	if not _check(battle.get("enemy_animation_texture") == null and battle.get("enemy_texture") != null, "missing strip keeps the static pilot"):
		return false
	battle = await _open_battle("sentry", {"enemy_animation_override": STATIC_PATH})
	if not _check(battle.get("enemy_animation_texture") == null and battle.get("enemy_texture") != null, "wrong-shaped strip (a single 96x62 cell) keeps the static pilot"):
		return false
	battle = await _open_battle("sentry", {"enemy_animation_override": V1_STRIP_PATH})
	if not _check(battle.get("enemy_animation_texture") == null and battle.get("enemy_texture") != null, "the v1 strip under the v2 entry (wrong cell width) keeps the static pilot"):
		return false
	battle = await _open_battle("sentry", {"enemy_sprite_pilot_enabled": false})
	if not _check(battle.get("enemy_animation_texture") == null and battle.get("enemy_texture") == null and battle.get("enemy_telegraph_scale") == Vector2.ONE, "pilot switch off restores the placeholder block and r30 ring"):
		return false
	_prepare_party("scifi.outskirts")
	battle = await _open_battle("patrol")
	if not _check(battle.get("enemy_animation_texture") == null and battle.get("enemy_texture") == null and battle.get("enemy_telegraph_scale") == Vector2.ONE and is_zero_approx(battle._enemy_body_offset_x()), "flag is sentry only: patrol keeps its placeholder block with the flag on"):
		return false
	_prepare_party("scifi.ruins")
	battle = await _open_battle("sentry", {"enemy_sprite_animation_enabled": false})
	battle.paused = true
	battle.enemy_hp = 1
	battle.fighters[0]["x"] = battle.enemy_x - 45.0
	battle._try_attack()
	battle.paused = false
	battle._process(0.1)
	return _check(battle.battle_finished and battle.get("enemy_visual_state") == "idle" and battle.get("enemy_animation_texture") == null, "static fallback ignores visual states on defeat")


func _place_party(battle: Node2D, hero_x: float) -> void:
	var spacing := [0.0, -48.0, -96.0, -150.0]
	for index in battle.fighters.size():
		battle.fighters[index]["x"] = hero_x + spacing[index]
		battle.fighters[index]["visual_action"] = ""


func _resize_window(window_key: String) -> void:
	root.size = WINDOWS[window_key]
	for i in 4:
		await process_frame
	scale = int(WINDOWS[window_key].x / 640)


func _run_captures(window_key: String) -> bool:
	# Logic-only runs check every case once; capture runs repeat them in both windows.
	if not capture_enabled and window_key != "1280":
		return true
	if capture_enabled:
		await _resize_window(window_key)
	var cases := [
		{"key": "idle-breathe-f0", "state": "idle", "frame": 0},
		{"key": "move-gait-f4", "state": "move", "frame": 4},
		{"key": "move-gait-f8", "state": "move", "frame": 8},
		{"key": "windup-coil-f12", "state": "windup", "frame": 12},
		{"key": "windup-full-f13", "state": "windup", "frame": 13},
		{"key": "strike-lunge-f14", "state": "strike", "frame": 14},
		{"key": "strike-recoil-f15", "state": "strike", "frame": 15},
		{"key": "hit-shutter-f16", "state": "hit", "frame": 16},
		{"key": "hit-recover-sword-thrust-f17", "state": "hit", "frame": 17},
		{"key": "defeat-hold-f20-inspect", "state": "defeat", "frame": 20, "hide_result": true},
		{"key": "defeat-hold-f20-result", "state": "defeat", "frame": 20},
		{"key": "v1-replay-windup-full", "state": "windup", "frame": 9, "v1": true},
		{"key": "v1-replay-hit-recover-sword-thrust", "state": "hit", "frame": 13, "v1": true},
		{"key": "static-fallback-windup", "state": "windup", "frame": -1, "static": true},
		{"key": "default-off-placeholder-windup", "state": "windup", "frame": -2, "default_off": true},
	]
	for entry in cases:
		for language in ["zh", "en"]:
			var localized: Dictionary = entry.duplicate()
			localized["language"] = language
			localized["window"] = window_key
			if not await _capture_case(localized):
				return false
	if not capture_enabled:
		return true
	if window_key == "1280":
		if not await _capture_walk_sequence():
			return false
		for v1 in [false, true]:
			if not await _capture_contact_sequence(v1):
				return false
	for index in FRAME_COUNT:
		if not await _capture_solo_crop(index, window_key):
			return false
	return true


func _drive_state(battle: Node2D, entry: Dictionary) -> int:
	# Reaches each pose through real combat calls, then advances only the visual clock to the wanted frame.
	var state: String = entry["state"]
	var v1: bool = entry.get("v1", false)
	var base := {"idle": 0, "move": 4, "windup": 8 if v1 else 12, "strike": 10 if v1 else 14, "hit": 12 if v1 else 16, "defeat": 14 if v1 else 18}
	var frame: int = entry["frame"]
	var phase: int = frame - int(base[state])
	battle.paused = true
	battle.enemy_cooldown = 99.0
	_place_party(battle, 300.0)
	battle.enemy_x = 430.0
	battle.enemy_windup = 0.0
	# The two live frames after opening start the approach gait; settle back to a fresh idle first (past the 0.08 s gait grace).
	battle.enemy_visual_state = "idle"
	battle.enemy_visual_clock = 0.0
	battle.enemy_visual_still_time = 1.0
	match state:
		"idle":
			_step_visual(battle, 0.22 * phase + 0.05)
		"move":
			_step_visual(battle, 1.0 / 60.0, true)
			battle.enemy_x = float(battle.enemy_visual_gait_origin_x) - GAIT_STEP * phase
			_step_visual(battle, 1.0 / 60.0, true)
		"windup":
			battle.enemy_x = 353.0
			battle.enemy_cooldown = 0.0
			battle._update_enemy(0.01)
			if phase == 1 or frame < 0:
				battle.enemy_windup = 0.2
			_step_visual(battle, 0.02)
		"strike":
			battle.enemy_x = 353.0
			app.hero_state["hp"] = 60
			battle.enemy_target_index = 0
			battle.enemy_windup = 0.01
			battle._update_enemy(0.02)
			battle.fighters[0]["visual_elapsed"] = 0.08
			_step_visual(battle, 0.15 * phase + 0.02)
		"hit":
			# The hero's blow lands as its attack starts; the second hit frame coincides with the sword thrust (attack phase 2).
			battle.enemy_x = 353.0
			battle.fighters[0]["attack_cooldown"] = 0.0
			battle._try_attack()
			battle.fighters[0]["visual_elapsed"] = 0.15 if phase == 1 else 0.06
			_step_visual(battle, 0.12 * phase + 0.02)
		"defeat":
			battle.enemy_x = 353.0
			battle.enemy_hp = 3
			battle.fighters[0]["attack_cooldown"] = 0.0
			battle._try_attack()
			_place_party(battle, 250.0)
			_step_visual(battle, 0.16 * phase + 0.02)
	if battle.get("enemy_animation_texture") != null:
		return battle._enemy_visual_frame()
	return -1 if battle.get("enemy_texture") != null else -2


func _boxes(frame: int, v1: bool) -> Dictionary:
	# Eye bezel and near-front claw boxes in cell coordinates (static plates: eye x 10-30 y 12-32, claw x 1-19 y 45-59).
	if v1:
		var v1_pose := {8: [Vector2i(2, -1), Vector2i(2, -4)], 9: [Vector2i(3, -2), Vector2i(4, -7)], 10: [Vector2i(-4, 2), Vector2i(0, 0)], 11: [Vector2i(-2, 1), Vector2i(0, 0)], 12: [Vector2i(3, -1), Vector2i(0, 0)], 13: [Vector2i(1, 0), Vector2i(0, 0)]}
		var p: Array = v1_pose[frame]
		return {"eye": Rect2i(Vector2i(10, 12) + p[0], Vector2i(21, 21)), "claw": Rect2i(Vector2i(1, 45) + p[1], Vector2i(19, 15))}
	var pose: Dictionary = CONTACT_POSE[frame]
	return {"eye": Rect2i(Vector2i(10 + MARGIN, 12) + pose["head"], Vector2i(21, 21)), "claw": Rect2i(Vector2i(1 + MARGIN, 45) + pose["foot"], Vector2i(19, 15))}


func _region_visible(image: Image, cell: Image, origin: Vector2i, box: Rect2i, tint: Color) -> float:
	# Share of the sentry's opaque pixels in the box that show on screen in the strip's own colour (not covered).
	var total := 0
	var shown := 0
	for y in range(box.position.y, box.end.y):
		for x in range(box.position.x, box.end.x):
			if x < 0 or y < 0 or x >= cell.get_width() or y >= cell.get_height():
				continue
			var source := cell.get_pixel(x, y)
			if source.a < 0.5:
				continue
			total += 1
			var screen := image.get_pixel((origin.x + x) * scale, (origin.y + y) * scale)
			if absf(screen.r - source.r * tint.r) + absf(screen.g - source.g * tint.g) + absf(screen.b - source.b * tint.b) < 0.05:
				shown += 1
	return float(shown) / maxf(1.0, total)


func _capture_case(entry: Dictionary) -> bool:
	_prepare_party("scifi.ruins")
	if app.language != entry["language"]:
		app.toggle_language()
	var v1: bool = entry.get("v1", false)
	var default_off: bool = entry.get("default_off", false)
	if default_off:
		battle_script.sentry_v2_override = -1
	var battle: Node2D = await _open_battle("sentry", {"enemy_sprite_animation_enabled": not entry.get("static", false)})
	battle_script.sentry_v2_override = 1
	if v1:
		_use_v1_entry(battle)
	var label := "%s-%s-%s" % [entry["key"], entry["language"], entry["window"]]
	var transition_ms: float = app.last_battle_transition_ms
	var frame := _drive_state(battle, entry)
	if not _check(frame == int(entry["frame"]), "%s selects frame %d (got %d)" % [label, entry["frame"], frame]):
		return false
	var hp_after := int(app.hero_state["hp"])
	if entry["state"] == "strike" and not _check(hp_after == 42, "%s hit lands for 18 (60 -> %d)" % [label, hp_after]):
		return false
	if entry.get("hide_result", false):
		battle.result_overlay.visible = false
	battle._update_hud()
	battle.queue_redraw()
	await process_frame
	await process_frame
	var winding: bool = entry["state"] == "windup"
	if not _check(battle.telegraph_label.visible == winding, "%s telegraph label visibility" % label):
		return false
	var cell: Image = _cell(frame, v1_strip_image if v1 else null) if frame >= 0 else null
	if winding and frame >= 0 and not v1:
		var label_rect: Rect2 = battle.telegraph_label.get_global_rect()
		var top := FLOOR_Y - ANCHOR.y + cell.get_used_rect().position.y
		if not _check(label_rect.end.y <= top, "%s telegraph label bottom %.0f clears the coiled sentry top %.0f" % [label, label_rect.end.y, top]):
			return false
		var ring := _visible_ring_pixels(cell, float(battle.enemy_telegraph_center_y), battle.enemy_telegraph_scale)
		overlap_report["windupFrame%dRingVisiblePx" % frame] = ring
		if not _check(int(ring["visible"]) >= BLOCK_RING_VISIBLE_PX and int(ring["above"]) > 0 and int(ring["sides"]) > 0, "%s ring stays visible around the coiled pose (%d px)" % [label, ring["visible"]]):
			return false
	if not capture_enabled:
		return true
	var image := root.get_viewport().get_texture().get_image()
	if not _check(image.get_size() == WINDOWS[entry["window"]], "%s capture is %s" % [label, WINDOWS[entry["window"]]]):
		return false
	var anchor: Vector2 = battle.enemy_animation_anchor if frame >= 0 else STATIC_ANCHOR
	var origin := Vector2i(int(battle._enemy_draw_x() - anchor.x), int(FLOOR_Y - anchor.y))
	var tint := Color(1.0, 0.70, 0.66) if winding else Color.WHITE
	var match_ratio = null
	var visibility = null
	if frame >= 0 and not (entry["state"] == "defeat" and not entry.get("hide_result", false)):
		# Whole-cell match: only hero pixels drawn on top can lower it.
		match_ratio = _region_visible(image, cell, origin, Rect2i(Vector2i.ZERO, cell.get_size()), tint)
		var floor_ratio := 0.97 if ["idle", "move", "defeat"].has(entry["state"]) else 0.5
		if not _check(match_ratio >= floor_ratio, "%s on-screen sentry matches strip frame %d at the anchor (%.3f)" % [label, frame, match_ratio]):
			return false
	if ["windup", "strike", "hit"].has(entry["state"]) and frame >= 0:
		var boxes := _boxes(frame, v1)
		visibility = {"eye": snappedf(_region_visible(image, cell, origin, boxes["eye"], tint), 0.001), "claw": snappedf(_region_visible(image, cell, origin, boxes["claw"], tint), 0.001)}
		visibility_report[label] = visibility
		if not v1 and not _check(float(visibility["eye"]) >= 0.85 and float(visibility["claw"]) >= 0.75, "%s eye %.3f and claw %.3f visible at the 53 px melee spacing" % [label, visibility["eye"], visibility["claw"]]):
			return false
	if (entry["state"] == "hit" or entry["state"] == "strike") and frame >= 0:
		var order := _overlap_order(image, battle, cell, origin)
		overlap_report[label] = order
		var front: bool = entry["state"] == "strike" and not v1
		var expected_ok: bool = int(order["overlap"]) == 0 or (int(order["sentryShown"]) == int(order["overlap"]) if front else int(order["heroShown"]) == int(order["overlap"]))
		if not _check(expected_ok, "%s %s on top where they overlap (%s)" % [label, "sentry" if front else "hero", JSON.stringify(order)]):
			return false
	var name := "%s_%s-%s-%s_%s-%s.png" % [PREFIX, entry["key"], entry["language"], entry["window"], stamp, run_id]
	var path := capture_dir.path_join(name)
	if not _check(name.length() <= 121, "%s file name %d chars (<= 121)" % [label, name.length()]):
		return false
	if not _check(image.save_png(path) == OK, "%s capture saved" % label):
		return false
	print("CAPTURED " + path)
	records.append({
		"file": name,
		"sha256": FileAccess.get_sha256(path),
		"width": image.get_width(),
		"height": image.get_height(),
		"window": "native 640x360 (1 logical px = 1 window px)" if entry["window"] == "640" else "review 1280x720 (project window, 2 window px per logical px)",
		"state": entry["state"],
		"frame": frame,
		"enemyVisual": "default-placeholder-block (flag off)" if frame == -2 else ("sentry-static-pilot-fallback" if frame == -1 else ("sentry-animation-v1-replay" if v1 else "sentry-animation-pilot-v2 (opt-in)")),
		"enemyX": battle.enemy_x,
		"drawOrigin": [origin.x, origin.y],
		"heroX": battle.fighters[0]["x"],
		"heroAction": battle.fighters[0]["visual_action"],
		"heroVisualElapsed": battle.fighters[0]["visual_elapsed"],
		"language": entry["language"],
		"transitionMs": snappedf(transition_ms, 0.01),
		"resultOverlayHiddenForInspection": entry.get("hide_result", false),
		"heroHpAfterStrike": hp_after if entry["state"] == "strike" else null,
		"renderedFrameMatchRatio": snappedf(match_ratio, 0.001) if match_ratio != null else null,
		"eyeClawVisible": visibility,
		"status": "default_off_reference" if frame == -2 else ("optin_animation_pilot_unapproved" if frame >= 0 and not v1 else ("v1_replay_comparison" if v1 else "static_fallback_comparison")),
		"artAccepted": false,
	})
	return true


func _overlap_order(image: Image, battle: Node2D, cell: Image, pilot_origin: Vector2i) -> Dictionary:
	# Where the controlled hero's frame and the sentry cell overlap, which of the two shows on screen.
	var fighter_frame: Texture2D = battle._male_combat_texture(battle.fighters[0], 0)
	var frame_image := fighter_frame.get_image()
	frame_image.convert(Image.FORMAT_RGBA8)
	var fighter_origin := Vector2i(int(roundf(float(battle.fighters[0]["x"])) - 30.0), int(FLOOR_Y - 73.0))
	var overlap := 0
	var hero_shown := 0
	var sentry_shown := 0
	for y in frame_image.get_height():
		for x in frame_image.get_width():
			var source := frame_image.get_pixel(x, y)
			if source.a < 0.99:
				continue
			var px := fighter_origin.x + x - pilot_origin.x
			var py := fighter_origin.y + y - pilot_origin.y
			if px < 0 or py < 0 or px >= cell.get_width() or py >= cell.get_height() or cell.get_pixel(px, py).a < 0.5:
				continue
			overlap += 1
			var shown := image.get_pixel((fighter_origin.x + x) * scale, (fighter_origin.y + y) * scale)
			var sentry := cell.get_pixel(px, py)
			# Counted independently: a pixel where both colours agree counts for both.
			if absf(shown.r - source.r) + absf(shown.g - source.g) + absf(shown.b - source.b) < 0.04:
				hero_shown += 1
			if absf(shown.r - sentry.r) + absf(shown.g - sentry.g) + absf(shown.b - sentry.b) < 0.04:
				sentry_shown += 1
	return {"overlap": overlap, "heroShown": hero_shown, "sentryShown": sentry_shown, "heroOpaquePx": _opaque_count(frame_image)}


func _opaque_count(image: Image) -> int:
	var count := 0
	for y in image.get_height():
		for x in image.get_width():
			if image.get_pixel(x, y).a > 0.5:
				count += 1
	return count


func _save_crop(group: String, index: int, image: Image, window: Rect2i) -> bool:
	var crop := image.get_region(Rect2i(window.position * scale, window.size * scale))
	var path := capture_dir.path_join("%s_crop-%s-%02d_%s-%s.png" % [PREFIX, group, index, stamp, run_id])
	if not _check(path.get_file().length() <= 121 and crop.save_png(path) == OK, "%s crop %d saved (%d-char name)" % [group, index, path.get_file().length()]):
		return false
	if not crops.has(group):
		crops[group] = []
	crops[group].append(path)
	return true


func _capture_walk_sequence() -> bool:
	# Real approach at 60 fps through a fixed window, one crop per gait step (16 steps = two cycles), so the floor stays put and foot lock can be judged.
	_prepare_party("scifi.ruins")
	var battle: Node2D = await _open_battle("sentry", {"paused": true})
	_place_party(battle, 120.0)
	battle.enemy_x = 470.0
	battle.enemy_cooldown = 99.0
	battle._advance_enemy_visual(1.0 / 60.0, false)
	var window := Rect2i(300, 186, 240, 94)
	var last_step := -999
	var saved := 0
	var guard := 0
	while saved < 16 and guard < 600:
		guard += 1
		var before: float = battle.enemy_x
		battle._update_enemy(1.0 / 60.0)
		battle._advance_enemy_visual(1.0 / 60.0, absf(battle.enemy_x - before) > 0.01)
		if battle.enemy_visual_state != "move" or battle._enemy_gait_step() == last_step:
			continue
		last_step = battle._enemy_gait_step()
		battle.queue_redraw()
		await process_frame
		await process_frame
		if not _save_crop("walk-1280", saved, root.get_viewport().get_texture().get_image(), window):
			return false
		saved += 1
	return _check(saved == 16, "walk sequence captured 16 real gait steps")


func _capture_contact_sequence(v1: bool) -> bool:
	# Real renders at the 53 px melee spacing: wind-up, strike on the hero, the hero's blow and the sentry's flinch, and back to idle.
	var steps := [
		{"state": "idle", "pos": 0, "hero": "", "elapsed": 0.0},
		{"state": "windup", "pos": 0, "hero": "", "elapsed": 0.0},
		{"state": "windup", "pos": 1, "hero": "", "elapsed": 0.0},
		{"state": "strike", "pos": 0, "hero": "hit", "elapsed": 0.05},
		{"state": "strike", "pos": 1, "hero": "hit", "elapsed": 0.17},
		{"state": "idle", "pos": 0, "hero": "", "elapsed": 0.0},
		{"state": "hit", "pos": 0, "hero": "attack", "elapsed": 0.06},
		{"state": "hit", "pos": 1, "hero": "attack", "elapsed": 0.18},
		{"state": "idle", "pos": 1, "hero": "attack", "elapsed": 0.30},
		{"state": "idle", "pos": 2, "hero": "", "elapsed": 0.0},
	]
	var group := "contact-v1-replay-1280" if v1 else "contact-v2-1280"
	var window := Rect2i(320, 190, 200, 90)
	for index in steps.size():
		var step: Dictionary = steps[index]
		_prepare_party("scifi.ruins")
		var battle: Node2D = await _open_battle("sentry", {"paused": true})
		if v1:
			_use_v1_entry(battle)
		_place_party(battle, 377.0)
		for other in range(1, battle.fighters.size()):
			battle.fighters[other]["x"] = 120.0 + other * 40.0
		battle.enemy_x = 430.0
		var state: String = step["state"]
		battle.enemy_visual_state = state
		var frame_time: float = battle.enemy_animation["frame_time"].get(state, 0.24)
		battle.enemy_visual_clock = frame_time * int(step["pos"]) + 0.01
		if state == "windup":
			battle.enemy_windup = 0.4 if int(step["pos"]) == 0 else 0.2
		battle.fighters[0]["visual_action"] = step["hero"]
		battle.fighters[0]["visual_elapsed"] = step["elapsed"]
		battle._update_hud()
		battle.queue_redraw()
		await process_frame
		await process_frame
		var image := root.get_viewport().get_texture().get_image()
		var frame: int = battle._enemy_visual_frame()
		if ["windup", "strike", "hit"].has(state):
			var cell: Image = _cell(frame, v1_strip_image if v1 else null)
			var origin := Vector2i(int(battle._enemy_draw_x() - battle.enemy_animation_anchor.x), int(FLOOR_Y - battle.enemy_animation_anchor.y))
			var tint := Color(1.0, 0.70, 0.66) if state == "windup" else Color.WHITE
			var boxes := _boxes(frame, v1)
			visibility_report["%s-%02d-%s-f%d-hero-%s" % [group, index, state, frame, step["hero"] if step["hero"] != "" else "idle"]] = {"eye": snappedf(_region_visible(image, cell, origin, boxes["eye"], tint), 0.001), "claw": snappedf(_region_visible(image, cell, origin, boxes["claw"], tint), 0.001)}
		if not _save_crop(group, index, image, window):
			return false
	return true


func _capture_solo_crop(index: int, window_key: String) -> bool:
	# Real Godot render of every v2 strip frame (state/clock forced) with the party out of contact; crop only, no scaling.
	_prepare_party("scifi.ruins")
	var battle: Node2D = await _open_battle("sentry")
	battle.paused = true
	_place_party(battle, 220.0)
	battle.enemy_x = 430.0
	var state_name := ""
	for state in STATES:
		var position: int = STATES[state].find(index)
		if position < 0:
			continue
		state_name = state
		battle.enemy_visual_state = state
		if state == "move":
			battle.enemy_visual_gait_origin_x = 430.0 + GAIT_STEP * position
		var frame_time: float = battle.ENEMY_SPRITE_ANIMATIONS["sentry"]["frame_time"].get(state, 0.24)
		battle.enemy_visual_clock = frame_time * position + 0.01
		if state == "windup":
			battle.enemy_windup = 0.4 if position == 0 else 0.2
		if state == "defeat":
			battle.enemy_hp = 0
	battle._update_hud()
	battle.queue_redraw()
	await process_frame
	await process_frame
	if not _check(battle._enemy_visual_frame() == index, "solo crop (%s) selects frame %d (%s)" % [window_key, index, state_name]):
		return false
	var image := root.get_viewport().get_texture().get_image()
	var origin := Vector2i(int(battle._enemy_draw_x() - ANCHOR.x), int(FLOOR_Y - ANCHOR.y))
	var tint := Color(1.0, 0.70, 0.66) if state_name == "windup" else Color.WHITE
	var ratio := _region_visible(image, _cell(index), origin, Rect2i(Vector2i.ZERO, CELL), tint)
	if not _check(ratio >= 0.97, "solo crop (%s) frame %d (%s) renders the strip cell on screen (%.3f)" % [window_key, index, state_name, ratio]):
		return false
	return _save_crop("solo-%s-f%02d-%s" % [window_key, index, state_name], 0, image, Rect2i(300, 186, 240, 94))


func _visible_ring_pixels(mask: Image, center_y: float, ring_scale: Vector2) -> Dictionary:
	# The ring is centred on the drawn body (cell x 64), as _draw_enemy places it.
	var rx := RING_RADIUS * ring_scale.x
	var ry := RING_RADIUS * ring_scale.y
	var origin_y := FLOOR_Y - ANCHOR.y
	var top := int(origin_y) + mask.get_used_rect().position.y
	var total := 0
	var visible := 0
	var above := 0
	var sides := 0
	for ly in range(int(floorf(center_y - ry)) - 1, int(ceilf(center_y + ry)) + 1):
		for lx in range(int(floorf(-rx)) - 1, int(ceilf(rx)) + 1):
			var dx := (lx + 0.5) / rx
			var dy := (ly + 0.5 - center_y) / ry
			if dx * dx + dy * dy >= 1.0:
				continue
			total += 1
			var sx := lx + int(BODY_CENTER_X)
			var sy := ly - int(origin_y)
			if sx >= 0 and sy >= 0 and sx < mask.get_width() and sy < mask.get_height() and mask.get_pixel(sx, sy).a > 0.5:
				continue
			visible += 1
			if ly < top:
				above += 1
			if sx < MARGIN or sx >= mask.get_width():
				sides += 1
	return {"total": total, "visible": visible, "above": above, "sides": sides}


func _write_manifest() -> bool:
	var path := capture_dir.path_join("%s_capture-manifest_%s-%s.json" % [PREFIX, stamp, run_id])
	var crop_hashes := {}
	for group in crops:
		for crop_path in crops[group]:
			crop_hashes[String(crop_path).get_file()] = FileAccess.get_sha256(crop_path)
	var manifest := {
		"project": "rpg-2-star-ocean-the-second",
		"batch": "sentry-automaton-v2-optin-portability",
		"revision": TAG,
		"createdAt": Time.get_datetime_string_from_system(),
		"engine": "Godot %s gl_compatibility, canvas_items stretch, 640x360 logical; review captures in the 1280x720 project window, native captures in a 640x360 window" % Engine.get_version_info()["string"],
		"battleScriptSha256": FileAccess.get_sha256(BATTLE_SCRIPT_PATH),
		"animationAssetManifest": ASSET_MANIFEST,
		"checkScript": CHECK_SCRIPT,
		"runtimeSwitch": "game/scripts/battle_arena.gd: OFF by default; `-- --sentry-v2-pilot` or battle_arena.gd sentry_v2_override = 1 turns on the sentry static pilot + v2 strip; 0 forces it off; -1 (default) follows the command line. Per-instance enemy_sprite_pilot_enabled / enemy_sprite_animation_enabled only narrow it.",
		"artApproved": false,
		"spriteAccepted": false,
		"approvalScope": "creator approved v2 as the ACTION DIRECTION baseline only; full sprite and art acceptance 0",
		"defaultOff": default_report,
		"frameAudit": frame_audit,
		"simulationParity": parity,
		"walkFootLock": walk_report,
		"eyeClawVisibility": visibility_report,
		"overlapAndRing": overlap_report,
		"captureDir": capture_dir,
		"crops": crop_hashes,
		"artAcceptanceCount": 0,
		"captures": records,
		"rule": "Opt-in runtime pilot only (off by default). The v2 frames and the static pilot remain unapproved art; no acceptance count changes.",
	}
	var file := FileAccess.open(path, FileAccess.WRITE)
	if not _check(file != null, "manifest written"):
		return false
	file.store_string(JSON.stringify(manifest, "  ") + "\n")
	file.close()
	print("MANIFEST " + path)
	return true


func _check(condition: bool, label: String) -> bool:
	if condition:
		pass_count += 1
		print("PASS " + label)
		return true
	push_error("FAIL " + label)
	quit(1)
	return false
