extends SceneTree

# Enemy battle actual motion capture v01 (TEST HARNESS ONLY; no art approval, no default change).
# Records the real current battle scene for the two produced opt-in enemies (sentry v2 strip, patrol animation v01)
# against the current ordinary FEMALE heroine alone (initial new-run party). Both enemy defaults stay placeholders;
# the creator must authorize each future default separately.
# Run windowed (never --headless) with a fresh isolated APPDATA:
#   godot --path game -s <absolute path to this file> -- --sentry-v2-pilot --patrol-battle-animation-pilot
#         --output-dir=<absolute empty dir> [--tag=actual-motion-v01_20261022-191350-b9786fd1]
# Clips: sentry-zh, sentry-en, patrol-zh, patrol-en. Each instantiates res://scenes/battle_arena.tscn directly and keeps its
# own _process running at real engine delta (max_fps 30, time_scale 1). The only inputs are one synthetic T press
# (battle_auto, keycode + physical) at 0.25 s and one Enter press (ui_accept) on the focused result button 0.4 s after the
# result overlay is visible. No HP, timer, movement, sprite-frame, result-flag or simulation writes; no durability hold.
# Every viewport frame is kept in memory with a monotonic wall timestamp and saved as PNG after the clip.
# Prints ENEMY49_MOTION_ALL_OK only when all four clips show animated enemy textures, an accepted T press, a visible
# battle result and an ordinary scene return; otherwise ENEMY49_MOTION_FAIL with a failures array in the report.
const PROJECT := "rpg-2-star-ocean-the-second"
const DEFAULT_TAG := "actual-motion-v01_20261022-191350-b9786fd1"
const SCENE := "res://scenes/battle_arena.tscn"
const ARENA := "res://scripts/battle_arena.gd"
const APP := "res://scripts/app_state.gd"
const SAVE_STORE := "res://scripts/save_store.gd"
const REQUIRED_FLAGS := ["--sentry-v2-pilot", "--patrol-battle-animation-pilot"]
const CLIPS := [["sentry", "zh"], ["sentry", "en"], ["patrol", "zh"], ["patrol", "en"]]
# Same mapping as scifi_exploration_area._open_encounter: outskirts spawns the patrol, ruins (non-outskirts) the sentry.
const DESTINATION_BY_ENEMY := {"sentry": "scifi.ruins", "patrol": "scifi.outskirts"}
const BATTLE_RETURN := Vector2(330, 215)
const AUTO_PRESS_AT := 0.25
const CONTINUE_AFTER_RESULT := 0.4
const RETURN_TAIL := 0.4
const MAX_CLIP_SECONDS := 22.0
const MAX_TOTAL_RECORDING := 90.0
const TARGET_FPS := 30
const RETURN_SCENES := ["res://scenes/scifi_exploration_area.tscn", "res://scenes/growth_screen.tscn", "res://scenes/main_menu.tscn"]

var app: Node
var output_dir := ""
var tag := DEFAULT_TAG
var failures: Array[String] = []
var total_recording := 0.0
var report := {
	"project": PROJECT,
	"kind": "enemy-battle-actual-motion-capture",
	"artApproval": "none (test capture only; sentry and patrol remain opt-in pilots, ordinary defaults stay placeholders)",
	"hashNormalization": "sha256-bytes (FileAccess.get_sha256 of the file bytes as loaded by Godot)",
	"testFixtureDeclarations": [
		"Scene entered by instantiating res://scenes/battle_arena.tscn directly (exploration encounter and its change_scene_to_packed skipped).",
		"Party set up with AppState.begin_new_run() then hero_appearance = female (the hero_setup._depart write); no recruit, NPC or member injection.",
		"Destination via AppState.select_destination (ruins for sentry, outskirts for patrol), then AppState.begin_battle(enemy, Vector2(330, 215)).",
		"Language set through AppState.toggle_language only when it differs.",
		"SaveStore.root_path redirected to user://test-saves/enemy49-motion-v01 (the post-victory auto-save stays inside the supplied APPDATA).",
		"Harness sets Engine.max_fps = 30, Engine.time_scale = 1.0 and root.size = 640x360.",
		"Inputs: one synthetic KEY_T press+release (keycode + physical) at 0.25 s; one KEY_ENTER press (next frame release) 0.4 s after result_overlay.visible.",
		"No writes to HP, timers, positions, sprite frames, visual state, result flags or simulation; no durability hold.",
		"Frame image is the viewport texture read at each process_frame (the most recently rendered frame).",
	],
	"clips": [],
}


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	if DisplayServer.get_name() == "headless":
		_fail_now("windowed run required (headless has no rendered frames)")
		return
	var args := OS.get_cmdline_user_args()
	for argument in args:
		if argument.begins_with("--output-dir="):
			output_dir = argument.trim_prefix("--output-dir=").replace("\\", "/")
		elif argument.begins_with("--tag="):
			tag = argument.trim_prefix("--tag=")
	if output_dir.is_empty() or not output_dir.is_absolute_path():
		_fail_now("missing or relative --output-dir=<absolute dir>")
		return
	if not RegEx.create_from_string("^[a-z0-9][a-z0-9._-]*$").search(tag):
		_fail_now("tag must be lowercase [a-z0-9._-]: " + tag)
		return
	for flag in REQUIRED_FLAGS:
		if not args.has(flag):
			_fail_now("required existing flag missing: " + flag)
			return
	if FileAccess.file_exists(_report_path()):
		_fail_now("report already exists, refusing to overwrite: " + _report_path())
		return
	for clip in CLIPS:
		var frame_dir := _frame_dir(clip[0], clip[1])
		if DirAccess.dir_exists_absolute(frame_dir) and not DirAccess.get_files_at(frame_dir).is_empty():
			_fail_now("frame folder not empty, refusing to overwrite: " + frame_dir)
			return
	app = root.get_node("AppState")
	Engine.max_fps = TARGET_FPS
	Engine.time_scale = 1.0
	SaveStore.root_path = "user://test-saves/enemy49-motion-v01"
	root.size = Vector2i(640, 360)
	report["tag"] = tag
	report["args"] = Array(args)
	report["userDataDir"] = OS.get_user_data_dir()
	report["sourceSha256AtStart"] = _source_hashes()
	for path in report["sourceSha256AtStart"]:
		if String(report["sourceSha256AtStart"][path]).is_empty():
			failures.append("source hash unavailable: " + path)
	for i in 6:
		await process_frame
	report["engine"] = {"version": Engine.get_version_info()["string"], "renderer": RenderingServer.get_current_rendering_driver_name(), "maxFps": Engine.max_fps, "timeScale": Engine.time_scale, "vsync": DisplayServer.window_get_vsync_mode(), "physicsTicks": Engine.physics_ticks_per_second, "screenRefresh": DisplayServer.screen_get_refresh_rate(), "rootSize": [root.size.x, root.size.y]}
	if Engine.time_scale != 1.0:
		failures.append("Engine.time_scale is %s" % Engine.time_scale)
	for clip in CLIPS:
		await _clip(clip[0], clip[1])
	report["totalRecordingSeconds"] = snappedf(total_recording, 0.000001)
	if total_recording > MAX_TOTAL_RECORDING:
		failures.append("total recording %.3f s exceeds %.0f s" % [total_recording, MAX_TOTAL_RECORDING])
	_finish()


func _source_hashes() -> Dictionary:
	var paths: Array[String] = [ARENA, APP, SAVE_STORE, SCENE]
	var arena_script: Script = load(ARENA)
	var constants: Dictionary = arena_script.get_script_constant_map()
	paths.append(String(constants["ENEMY_SPRITE_PILOTS"]["sentry"]["path"]))
	paths.append(String(constants["ENEMY_SPRITE_ANIMATIONS"]["sentry"]["path"]))
	paths.append(String(constants["PATROL_ANIMATION_LOADER"]))
	paths.append(String(constants["PATROL_ANIMATION_PACKAGE"]))
	var harness: Script = get_script()
	if harness != null and not harness.resource_path.is_empty():
		paths.append(harness.resource_path)
	var hashes := {}
	for path in paths:
		hashes[path] = FileAccess.get_sha256(path)
	return hashes


func _press_key(key: Key, pressed: bool) -> void:
	var event := InputEventKey.new()
	event.keycode = key
	event.physical_keycode = key
	event.pressed = pressed
	Input.parse_input_event(event)


func _battle_row(battle) -> Dictionary:
	var animated: bool = battle.enemy_animation_texture != null
	var party := []
	for fighter in battle.fighters:
		var member_id := String(fighter["id"])
		party.append({"id": member_id, "hp": int(fighter.get("hp", -1)), "x": snappedf(float(fighter["x"]), 0.01), "visualAction": String(fighter["visual_action"])})
	return {
		"enemyState": String(battle.enemy_visual_state),
		"enemyFrame": int(battle._enemy_visual_frame()) if animated else -1,
		"enemyX": snappedf(float(battle.enemy_x), 0.01),
		"enemyDrawX": snappedf(float(battle._enemy_draw_x()), 0.01),
		"enemyHp": int(battle.enemy_hp),
		"enemyWindup": snappedf(float(battle.enemy_windup), 0.000001),
		"enemyAttackCount": int(battle.enemy_attack_count),
		"playerAttackCount": int(battle.player_attack_count),
		"party": party,
		"auto": bool(battle.auto_mode),
		"paused": bool(battle.paused),
		"finished": bool(battle.battle_finished),
		"won": bool(battle.battle_won),
		"resultVisible": bool(battle.result_overlay.visible),
		"resultButtonEnabled": not bool(battle.result_button.disabled),
		"resultButtonFocused": bool(battle.result_button.has_focus()),
		"patrolResultPending": bool(battle.patrol_result_pending),
		"heroineResultPending": bool(battle.heroine_result_pending),
		"heroineDefeatResultPending": bool(battle.heroine_defeat_result_pending),
	}


func _clip(enemy_id: String, language: String) -> void:
	var name := "%s-%s" % [enemy_id, language]
	var clip := {"name": name, "enemy": enemy_id, "language": language, "destination": DESTINATION_BY_ENEMY[enemy_id]}
	app.begin_new_run()
	app.hero_appearance = "female"
	if not app.select_destination(DESTINATION_BY_ENEMY[enemy_id]):
		failures.append(name + ": select_destination failed")
	if app.language != language:
		app.toggle_language()
	if not app.begin_battle(enemy_id, BATTLE_RETURN):
		failures.append(name + ": begin_battle failed")
	clip["party"] = Array(app.active_party_ids)
	clip["heroAppearance"] = app.hero_appearance
	if Array(app.active_party_ids) != ["hero"]:
		failures.append(name + ": party is not the initial heroine alone: %s" % [clip["party"]])
	var battle = load(SCENE).instantiate()
	root.add_child(battle)
	current_scene = battle
	clip["arenaEnemyId"] = String(battle.enemy_id)
	clip["heroineDefaultActive"] = bool(battle.heroine_default_active)
	clip["enemyTexturePath"] = battle.enemy_texture.resource_path if battle.enemy_texture != null else ""
	clip["enemyAnimationTexturePath"] = battle.enemy_animation_texture.resource_path if battle.enemy_animation_texture != null else ""
	clip["enemyAnimationStates"] = Dictionary(battle.enemy_animation.get("states", {})).keys()
	clip["titleAtEntry"] = String(battle.title_label.text)
	clip["helpAtEntry"] = String(battle.help_label.text)
	var textures_ok := true
	if String(battle.enemy_id) != enemy_id:
		failures.append(name + ": arena loaded enemy " + String(battle.enemy_id))
		textures_ok = false
	if enemy_id == "sentry" and battle.enemy_texture == null:
		failures.append(name + ": sentry enemy_texture not loaded")
		textures_ok = false
	if battle.enemy_animation_texture == null:
		failures.append(name + ": enemy_animation_texture not loaded")
		textures_ok = false
	if String(battle.title_label.text).is_empty() or String(battle.help_label.text).is_empty():
		failures.append(name + ": title/help text empty at entry")
	var images: Array[Image] = []
	var rows := []
	var started := Time.get_ticks_usec()
	var last := started
	var auto_pressed_at := -1.0
	var auto_seen_at := -1.0
	var finished_at := -1.0
	var result_visible_at := -1.0
	var continue_pressed_at := -1.0
	var continue_release_pending := false
	var returned_at := -1.0
	var return_scene := ""
	var first_strike_index := -1
	var last_result_index := -1
	var entry_index := 0
	var timed_out := false
	while true:
		await process_frame
		var now := Time.get_ticks_usec()
		var t := (now - started) / 1000000.0
		var image := root.get_texture().get_image()
		images.append(image)
		var alive: bool = is_instance_valid(battle) and battle.is_inside_tree()
		var scene_path := ""
		if current_scene != null and is_instance_valid(current_scene):
			scene_path = current_scene.scene_file_path
		var row := {"index": rows.size(), "t": snappedf(t, 0.000001), "wallDelta": snappedf((now - last) / 1000000.0, 0.000001), "processDelta": snappedf(root.get_process_delta_time(), 0.000001), "framesDrawn": Engine.get_frames_drawn(), "processFrames": Engine.get_process_frames(), "scene": scene_path, "battleInTree": alive, "size": [image.get_width(), image.get_height()]}
		last = now
		if alive:
			row.merge(_battle_row(battle))
			if bool(row["auto"]) and auto_seen_at < 0.0:
				auto_seen_at = t
			if bool(row["finished"]) and finished_at < 0.0:
				finished_at = t
			if bool(row["resultVisible"]):
				last_result_index = rows.size()
				if result_visible_at < 0.0:
					result_visible_at = t
			if String(row["enemyState"]) == "strike" and first_strike_index < 0:
				first_strike_index = rows.size()
			if t < AUTO_PRESS_AT:
				entry_index = rows.size()
		rows.append(row)
		if continue_release_pending:
			_press_key(KEY_ENTER, false)
			continue_release_pending = false
		if auto_pressed_at < 0.0 and t >= AUTO_PRESS_AT:
			_press_key(KEY_T, true)
			_press_key(KEY_T, false)
			auto_pressed_at = t
		if alive and result_visible_at >= 0.0 and continue_pressed_at < 0.0 and t - result_visible_at >= CONTINUE_AFTER_RESULT:
			clip["resultButtonAtContinue"] = {"enabled": not bool(battle.result_button.disabled), "focused": bool(battle.result_button.has_focus()), "text": String(battle.result_button.text), "title": String(battle.result_title.text), "note": String(battle.result_note.text), "help": String(battle.help_label.text)}
			_press_key(KEY_ENTER, true)
			continue_release_pending = true
			continue_pressed_at = t
		if returned_at < 0.0 and finished_at >= 0.0 and not alive and not scene_path.is_empty():
			returned_at = t
			return_scene = scene_path
		if returned_at >= 0.0 and t - returned_at >= RETURN_TAIL:
			break
		if t >= MAX_CLIP_SECONDS:
			timed_out = true
			failures.append(name + ": clip not complete (result + return) within %.0f s" % MAX_CLIP_SECONDS)
			break
	var recorded := (Time.get_ticks_usec() - started) / 1000000.0
	total_recording += recorded
	if continue_release_pending:
		_press_key(KEY_ENTER, false)
	if is_instance_valid(battle):
		battle.free()
	if current_scene != null and is_instance_valid(current_scene):
		current_scene.free()
	current_scene = null
	await process_frame
	await process_frame
	# Save frames after recording so disk writes never stall the recorded frames.
	var frame_dir := _frame_dir(enemy_id, language)
	DirAccess.make_dir_recursive_absolute(frame_dir)
	var rep_dir := output_dir.path_join("representative")
	DirAccess.make_dir_recursive_absolute(rep_dir)
	var states := {}
	var frames_seen := {}
	var prev_t := -1.0
	for i in images.size():
		var file_name := "%s_%s_%s-frame-%06d_%s.png" % [PROJECT, enemy_id, language, i + 1, tag]
		var file := frame_dir.path_join(file_name)
		if images[i].get_size() != Vector2i(640, 360):
			failures.append("%s frame %d size %s" % [name, i + 1, images[i].get_size()])
		if images[i].save_png(file) != OK:
			failures.append(name + ": save failed " + file)
		rows[i]["file"] = "frames/%s/%s" % [name, file_name]
		rows[i]["sha256"] = FileAccess.get_sha256(file)
		if float(rows[i]["t"]) <= prev_t:
			failures.append("%s: non-monotonic timestamp at frame %d" % [name, i + 1])
		prev_t = float(rows[i]["t"])
		if rows[i].has("enemyState"):
			states[rows[i]["enemyState"]] = int(states.get(rows[i]["enemyState"], 0)) + 1
			frames_seen[rows[i]["enemyFrame"]] = int(frames_seen.get(rows[i]["enemyFrame"], 0)) + 1
	var representative := {}
	for pick in [["entry", entry_index], ["first-strike", first_strike_index], ["final-result", last_result_index]]:
		if int(pick[1]) < 0 or int(pick[1]) >= images.size():
			representative[pick[0]] = {"present": false}
			continue
		var rep_name := "%s_%s_%s-representative-%s_%s.png" % [PROJECT, enemy_id, language, pick[0], tag]
		var rep_file := rep_dir.path_join(rep_name)
		if images[int(pick[1])].save_png(rep_file) != OK:
			failures.append(name + ": representative save failed " + rep_file)
		representative[pick[0]] = {"present": true, "frameIndex": int(pick[1]), "t": rows[int(pick[1])]["t"], "file": "representative/" + rep_name, "sha256": FileAccess.get_sha256(rep_file)}
	images.clear()
	var animated := textures_ok and frames_seen.size() >= 2
	if not animated:
		failures.append("%s: enemy texture not animated (distinct frames %d)" % [name, frames_seen.size()])
	if auto_seen_at < 0.0:
		failures.append(name + ": T (battle_auto) press never reached the arena")
	if finished_at < 0.0:
		failures.append(name + ": battle never finished")
	if result_visible_at < 0.0:
		failures.append(name + ": result overlay never visible")
	if returned_at < 0.0:
		failures.append(name + ": no ordinary scene return")
	elif not RETURN_SCENES.has(return_scene):
		failures.append(name + ": unexpected return scene " + return_scene)
	var deltas := []
	for i in range(1, rows.size()):
		deltas.append(float(rows[i]["t"]) - float(rows[i - 1]["t"]))
	var max_delta := 0.0
	var hitches := 0
	for d in deltas:
		max_delta = maxf(max_delta, d)
		if d > 1.5 / TARGET_FPS:
			hitches += 1
	var expected_states: Array = clip["enemyAnimationStates"]
	var absent := []
	for state in expected_states:
		if not states.has(state):
			absent.append(state)
	clip.merge({
		"timedOut": timed_out,
		"recordedSeconds": snappedf(recorded, 0.000001),
		"frames": rows.size(),
		"meanFrameSeconds": snappedf(recorded / maxf(1.0, rows.size()), 0.000001),
		"maxFrameDeltaSeconds": snappedf(max_delta, 0.000001),
		"framesOver1_5xTarget": hitches,
		"autoPressedAt": auto_pressed_at,
		"autoSeenAt": auto_seen_at,
		"finishedAt": finished_at,
		"resultVisibleAt": result_visible_at,
		"continuePressedAt": continue_pressed_at,
		"continueInputUsed": continue_pressed_at >= 0.0,
		"returnedAt": returned_at,
		"returnScene": return_scene,
		"won": rows.size() > 0 and _last_battle_value(rows, "won"),
		"animated": animated,
		"distinctEnemyFrames": frames_seen.size(),
		"statesFrameCount": states,
		"statesAbsent": absent,
		"representative": representative,
		"rows": rows,
	})
	report["clips"].append(clip)


func _last_battle_value(rows: Array, key: String) -> bool:
	for i in range(rows.size() - 1, -1, -1):
		if rows[i].has(key):
			return bool(rows[i][key])
	return false


func _frame_dir(enemy_id: String, language: String) -> String:
	return output_dir.path_join("frames").path_join("%s-%s" % [enemy_id, language])


func _report_path() -> String:
	return output_dir.path_join("%s_enemy-battle_motion-report_%s.json" % [PROJECT, tag])


func _finish() -> void:
	report["sourceSha256AtEnd"] = _source_hashes()
	if report["sourceSha256AtEnd"] != report["sourceSha256AtStart"]:
		failures.append("source hashes changed during the run")
	report["failures"] = failures
	report["allOk"] = failures.is_empty()
	DirAccess.make_dir_recursive_absolute(output_dir)
	var file := FileAccess.open(_report_path(), FileAccess.WRITE)
	if file == null:
		push_error("FAIL cannot write report " + _report_path())
		print("ENEMY49_MOTION_FAIL report-write")
		quit(1)
		return
	file.store_string(JSON.stringify(report, " ") + "\n")
	file.close()
	print("ENEMY49_MOTION_REPORT " + _report_path())
	if failures.is_empty():
		print("ENEMY49_MOTION_ALL_OK clips=%d" % report["clips"].size())
		quit(0)
	else:
		for f in failures:
			push_error("FAIL " + f)
		print("ENEMY49_MOTION_FAIL count=%d" % failures.size())
		quit(1)


func _fail_now(message: String) -> void:
	push_error("FAIL " + message)
	print("ENEMY49_MOTION_FAIL " + message)
	quit(1)
