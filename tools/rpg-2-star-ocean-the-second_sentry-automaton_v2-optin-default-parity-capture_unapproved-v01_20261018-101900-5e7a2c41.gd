extends SceneTree

# Default-off pixel parity capture for the opt-in sentry v2 pilot (`-- --sentry-v2-pilot`; UNAPPROVED, art acceptance 0).
# Run windowed with `-s <absolute path to this file>` against any project tree (the base eb70de1 export or the candidate
# worktree): it uses only battle API that exists in both, so the same script renders the same deterministic battle states.
#   --capture-dir=<absolute dir>   where the PNGs and the JSON index go (required)
#   --variant=<base|off|on>        which run this is; goes into every file name (required)
#   --stamp=<YYYYMMDD-HHMMSS-id8>  timestamp + unique 8-hex ID shared by the three runs of one parity check (required)
#   --sentry-v2-pilot              (candidate tree only) render the opt-in pilot instead of the default
# File names: <PREFIX>_<variant>-<enemy>-<state>-<language>-<window>_<stamp>.png and <PREFIX>_<variant>-index_<stamp>.json,
# so the three runs of one stamp can share one directory without a name collision.
# States: sentry and patrol x zh/en x 1280x720 and native 640x360 windows x idle / wind-up ring / hit taken / defeat result.
# The companion Python check compares two capture dirs pixel by pixel.
const BATTLE_SCENE_PATH := "res://scenes/battle_arena.tscn"
const PREFIX := "rpg-2-star-ocean-the-second_sentry-v2-parity"
const DIR_ARG := "--capture-dir="
const VARIANT_ARG := "--variant="
const STAMP_ARG := "--stamp="
const VARIANTS := ["base", "off", "on"]
const STATES := ["idle", "windup", "hit", "defeat"]
const WINDOWS := {"1280": Vector2i(1280, 720), "640": Vector2i(640, 360)}

var app: Node
var capture_dir := ""
var variant := ""
var stamp := ""
var index := []


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	if DisplayServer.get_name() == "headless":
		_fail("windowed run required")
		return
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with(DIR_ARG):
			capture_dir = argument.trim_prefix(DIR_ARG)
		elif argument.begins_with(VARIANT_ARG):
			variant = argument.trim_prefix(VARIANT_ARG)
		elif argument.begins_with(STAMP_ARG):
			stamp = argument.trim_prefix(STAMP_ARG)
	if capture_dir.is_empty():
		_fail("missing " + DIR_ARG)
		return
	if not variant in VARIANTS:
		_fail("%s must be one of %s" % [VARIANT_ARG, VARIANTS])
		return
	if RegEx.create_from_string("^[0-9]{8}-[0-9]{6}-[0-9a-f]{8}$").search(stamp) == null:
		_fail(STAMP_ARG + "YYYYMMDD-HHMMSS-<8 lowercase hex> required")
		return
	DirAccess.make_dir_recursive_absolute(capture_dir)
	app = root.get_node("AppState")
	SaveStore.root_path = "user://test-saves/sentry-v2-optin-default-parity"
	var script_text := FileAccess.get_file_as_string("res://scripts/battle_arena.gd")
	var has_flag_api := script_text.contains("sentry_v2_enabled")
	for window_key in WINDOWS:
		root.size = WINDOWS[window_key]
		for i in 4:
			await process_frame
		for enemy_id in ["sentry", "patrol"]:
			for language in ["zh", "en"]:
				for state in STATES:
					if not await _capture(enemy_id, language, state, window_key):
						return
	var file := FileAccess.open(capture_dir.path_join("%s_%s-index_%s.json" % [PREFIX, variant, stamp]), FileAccess.WRITE)
	file.store_string(JSON.stringify({
		"battleScriptSha256": FileAccess.get_sha256("res://scripts/battle_arena.gd"),
		"battleScriptHasFlagApi": has_flag_api,
		"variant": variant,
		"stamp": stamp,
		"cmdlineUserArgs": OS.get_cmdline_user_args(),
		"captures": index,
	}, "  ") + "\n")
	file.close()
	print("SENTRY_V2_PARITY_CAPTURE OK variant=%s stamp=%s captures=%d script_has_flag_api=%s" % [variant, stamp, index.size(), has_flag_api])
	quit(0)


func _capture(enemy_id: String, language: String, state: String, window_key: String) -> bool:
	if current_scene != null:
		current_scene.queue_free()
		current_scene = null
		await process_frame
	app.begin_new_run()
	app.hero_appearance = "male"
	app.recruit_member("liang-xu")
	app.recruit_member("zhao-ling")
	app.ji_records_checked = true
	app.recruit_member("ji-cheng")
	app.select_destination("scifi.ruins" if enemy_id == "sentry" else "scifi.outskirts")
	if app.language != language:
		app.toggle_language()
	app.begin_battle(enemy_id, Vector2(330, 215))
	var battle: Node2D = load(BATTLE_SCENE_PATH).instantiate()
	battle.paused = true
	root.add_child(battle)
	current_scene = battle
	await process_frame
	await process_frame
	# Fixed layout: every live-frame side effect (positions, loop clocks) is overwritten before the capture.
	var spacing := [0.0, -48.0, -96.0, -150.0]
	for i in battle.fighters.size():
		var fighter: Dictionary = battle.fighters[i]
		fighter["x"] = 300.0 + spacing[i]
		fighter["visual_action"] = ""
		fighter["visual_elapsed"] = 0.0
		fighter["visual_loop_kind"] = "idle"
		fighter["visual_loop_clock"] = 0.0
		fighter["visual_moving"] = false
		fighter["attack_cooldown"] = 0.0
	battle.enemy_cooldown = 99.0
	battle.enemy_windup = 0.0
	battle.enemy_x = 430.0
	_reset_pilot_visual(battle)
	match state:
		"windup":
			battle.enemy_x = 353.0
			battle.enemy_windup = 0.2
		"hit":
			battle.enemy_x = 353.0
			battle.fighters[0]["x"] = 353.0 - 45.0
			battle._try_attack()
			battle.fighters[0]["visual_elapsed"] = 0.06
		"defeat":
			battle.enemy_x = 353.0
			battle.fighters[0]["x"] = 353.0 - 45.0
			battle.enemy_hp = 3
			battle._try_attack()
	_advance_pilot_visual(battle)
	battle._update_hud()
	battle.queue_redraw()
	await process_frame
	await process_frame
	var image := root.get_viewport().get_texture().get_image()
	if image.get_size() != WINDOWS[window_key]:
		_fail("%s %s %s %s capture size %s" % [enemy_id, language, state, window_key, image.get_size()])
		return false
	var name := "%s_%s-%s-%s-%s-%s_%s.png" % [PREFIX, variant, enemy_id, state, language, window_key, stamp]
	var path := capture_dir.path_join(name)
	if image.save_png(path) != OK:
		_fail("save " + path)
		return false
	index.append({"file": name, "sha256": FileAccess.get_sha256(path), "enemy": enemy_id, "state": state, "language": language, "window": window_key, "size": [image.get_width(), image.get_height()], "enemyHp": battle.enemy_hp, "battleFinished": battle.battle_finished, "pilotVisualState": battle.get("enemy_visual_state"), "pilotTextureLoaded": battle.get("enemy_texture") != null})
	return true


func _reset_pilot_visual(battle: Node2D) -> void:
	# Only the candidate script has these members; the base script ignores the calls.
	if battle.get("enemy_animation_texture") == null:
		return
	battle.set("enemy_visual_state", "idle")
	battle.set("enemy_visual_clock", 0.05)
	battle.set("enemy_visual_still_time", 1.0)
	battle.set("enemy_visual_last_hp", battle.enemy_hp)
	battle.set("enemy_visual_last_attack_count", battle.enemy_attack_count)


func _advance_pilot_visual(battle: Node2D) -> void:
	if battle.get("enemy_animation_texture") == null:
		return
	battle.call("_advance_enemy_visual", 0.02, false)


func _fail(message: String) -> void:
	push_error("FAIL " + message)
	quit(1)
