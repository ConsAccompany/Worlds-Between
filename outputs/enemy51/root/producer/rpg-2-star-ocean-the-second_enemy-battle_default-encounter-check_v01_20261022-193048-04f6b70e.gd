extends "res://../tools/rpg-2-star-ocean-the-second_enemy-battle_actual-motion-capture_v01_20261022-191350-b9786fd1.gd"

# Enemy battle DEFAULT encounter check v01 (TEST HARNESS ONLY; no art approval, captions unchanged).
# Bounded adapter over the enemy49 actual-motion tool (inherits _press_key, _battle_row, _source_hashes). It checks that the
# ordinary no-flag game reaches the creator-authorized sentry/patrol MVP defaults through the real exploration encounter
# and returns to the world. Run windowed in the integration checkout with a fresh isolated APPDATA and NO game flags:
#   godot --path game -s <absolute path to this file> -- --out=<absolute empty dir> --tag=<unique tag ending YYYYMMDD-HHMMSS-xxxxxxxx>
# Cases sentry/patrol x zh/en, current ordinary FEMALE heroine alone. The battle is opened only by holding a real KEY_D
# (keycode + physical) towards the visible world enemy (exploration _process -> _open_encounter). In battle: one KEY_T,
# actual _process at real wall time (max_fps 60, time_scale 1), no HP/timer/frame/visual/position writes, no durability
# hold; Enter on the normally focused result button returns. <= 4 captures per case (entry, first windup/strike, result,
# returned world), 640x360. Prints ENEMY51_DEFAULT_ENCOUNTERS_ALL_OK only if all four cases pass.
const OWN_KIND := "enemy-battle-default-encounter-check"
const EXPLORATION_SCENE := "res://scenes/scifi_exploration_area.tscn"
const EXPLORATION_SCRIPT := "res://scripts/scifi_exploration_area.gd"
const START_OFFSET := Vector2(55, 0)
const ENTRY_DEADLINE := 4.0
const RESULT_DEADLINE := 20.0
const RETURN_DEADLINE := 4.0
const RESULT_SETTLE := 0.4
const HARD_DEADLINE := 230.0
const OWN_FPS := 60
const ALLOWED_USER_ARGS := ["--out=", "--tag="]

var run_start_usec := 0


func _run() -> void:
	run_start_usec = Time.get_ticks_usec()
	report = {
		"project": PROJECT,
		"kind": OWN_KIND,
		"artApproval": "none; creator authorized sentry and patrol as MVP defaults only, final art approval is separate",
		"hashNormalization": "sha256-bytes (FileAccess.get_sha256 of the file bytes as loaded by Godot)",
		"testFixtureDeclarations": [
			"Party via AppState.begin_new_run() then hero_appearance = female; language via AppState.toggle_language only when it differs.",
			"Destination via AppState.select_destination (scifi.ruins -> sentry, scifi.outskirts -> patrol).",
			"NORMAL res://scenes/scifi_exploration_area.tscn instantiated, added to root and set as current_scene.",
			"Hero placed once at world enemy_position - (55, 0) after _ready (fixture start); everything after is real input.",
			"Battle opened only by holding KEY_D (keycode + physical) until the exploration's own _open_encounter changes scene; no harness call to begin_battle or change_scene.",
			"SaveStore.root_path redirected to user://test-saves/enemy51-default-v01 (auto-saves stay inside the supplied APPDATA).",
			"No game CLI flags; no battle_arena static overrides written; Engine.max_fps = 60, time_scale = 1, root.size = 640x360.",
			"In battle: one KEY_T press+release; KEY_ENTER press, next frame release, once the result button is focused and settled 0.4 s.",
			"No writes to HP, timers, positions, sprite frames, visual state, result flags or simulation during battle; no durability hold.",
		],
		"cases": [],
	}
	if DisplayServer.get_name() == "headless":
		_fail_own("windowed run required (captures need rendered frames)")
		return
	var args := OS.get_cmdline_user_args()
	for argument in args:
		var known := false
		for prefix in ALLOWED_USER_ARGS:
			if String(argument).begins_with(prefix):
				known = true
		if not known:
			_fail_own("unexpected user arg (no game flags allowed): " + String(argument))
			return
		if String(argument).begins_with("--out="):
			output_dir = String(argument).trim_prefix("--out=").replace("\\", "/")
		elif String(argument).begins_with("--tag="):
			tag = String(argument).trim_prefix("--tag=")
	if output_dir.is_empty() or not output_dir.is_absolute_path():
		_fail_own("missing or relative --out=<absolute dir>")
		return
	if not RegEx.create_from_string("^[a-z0-9][a-z0-9._-]*_[0-9]{8}-[0-9]{6}-[0-9a-f]{8}$").search(tag):
		_fail_own("tag must be lowercase and end _YYYYMMDD-HHMMSS-xxxxxxxx: " + tag)
		return
	if DirAccess.dir_exists_absolute(output_dir) and not DirAccess.get_files_at(output_dir).is_empty():
		_fail_own("output dir not empty, refusing to overwrite: " + output_dir)
		return
	DirAccess.make_dir_recursive_absolute(output_dir)
	app = root.get_node("AppState")
	Engine.max_fps = OWN_FPS
	Engine.time_scale = 1.0
	SaveStore.root_path = "user://test-saves/enemy51-default-v01"
	root.size = Vector2i(640, 360)
	report["tag"] = tag
	report["args"] = Array(args)
	report["userDataDir"] = OS.get_user_data_dir()
	report["sourceSha256AtStart"] = _own_hashes()
	for path in report["sourceSha256AtStart"]:
		if String(report["sourceSha256AtStart"][path]).is_empty():
			failures.append("source hash unavailable: " + String(path))
	var constants: Dictionary = (load(ARENA) as Script).get_script_constant_map()
	report["defaults"] = {"SENTRY_MVP_DEFAULT": constants.get("SENTRY_MVP_DEFAULT"), "PATROL_MVP_DEFAULT": constants.get("PATROL_MVP_DEFAULT")}
	if constants.get("SENTRY_MVP_DEFAULT") != true or constants.get("PATROL_MVP_DEFAULT") != true:
		failures.append("MVP default consts not both true: %s" % str(report["defaults"]))
	for flag in [String(constants.get("SENTRY_V2_CLI_FLAG", "--sentry-v2-pilot")), String(constants.get("PATROL_ANIMATION_CLI_FLAG", "--patrol-battle-animation-pilot"))]:
		if args.has(flag):
			failures.append("enemy flag present: " + flag)
	for i in 6:
		await process_frame
	report["engine"] = {"version": Engine.get_version_info()["string"], "renderer": RenderingServer.get_current_rendering_driver_name(), "maxFps": Engine.max_fps, "timeScale": Engine.time_scale, "vsync": DisplayServer.window_get_vsync_mode(), "rootSize": [root.size.x, root.size.y]}
	for clip in CLIPS:
		if _elapsed_run() > HARD_DEADLINE:
			failures.append("hard deadline reached before case %s-%s" % [clip[0], clip[1]])
			break
		await _case(String(clip[0]), String(clip[1]))
	report["runSeconds"] = snappedf(_elapsed_run(), 0.001)
	_finish_own()


func _case(enemy_id: String, language: String) -> void:
	var case_name := "%s-%s" % [enemy_id, language]
	var destination := String(DESTINATION_BY_ENEMY[enemy_id])
	var row := {"name": case_name, "enemy": enemy_id, "language": language, "destination": destination, "captures": [], "events": [], "failures": []}
	report["cases"].append(row)
	var t0 := Time.get_ticks_usec()
	var old_scene := current_scene
	if old_scene != null:
		old_scene.queue_free()
		await process_frame
		await process_frame
	app.begin_new_run()
	app.hero_appearance = "female"
	if String(app.language) != language:
		app.toggle_language()
	row["languageAfterSetup"] = String(app.language)
	row["partyIds"] = Array(app.active_party_ids)
	if String(app.language) != language:
		_case_fail(row, "language setup failed")
		return
	if not bool(app.select_destination(destination)):
		_case_fail(row, "select_destination refused " + destination)
		return
	var area: Node = (load(EXPLORATION_SCENE) as PackedScene).instantiate()
	root.add_child(area)
	current_scene = area
	if not bool(area.enemy_visible):
		_case_fail(row, "world enemy not visible at entry")
		return
	var enemy_world: Vector2 = area.enemy_position
	area.hero.position = enemy_world - START_OFFSET
	row["worldEnemyPosition"] = [enemy_world.x, enemy_world.y]
	row["heroStart"] = [area.hero.position.x, area.hero.position.y]
	row["safePositionAtStart"] = [area.safe_position.x, area.safe_position.y]
	await process_frame
	# Real input: hold D towards the enemy until the exploration's own encounter switches to the battle scene.
	_event(row, t0, "hold KEY_D")
	_press_key(KEY_D, true)
	var hold_start := Time.get_ticks_usec()
	var last_encounter_count := -1
	var last_safe := Vector2.ZERO
	var reached := false
	while _since(hold_start) < ENTRY_DEADLINE:
		if is_instance_valid(area) and current_scene == area:
			last_encounter_count = int(area.encounter_count)
			last_safe = area.safe_position
		if current_scene != null and current_scene.scene_file_path == SCENE:
			reached = true
			break
		await process_frame
	_press_key(KEY_D, false)
	_event(row, t0, "release KEY_D")
	row["entrySeconds"] = snappedf(_since(hold_start), 0.001)
	row["safePositionBeforeBattle"] = [last_safe.x, last_safe.y]
	row["encounterCountBeforeSwitch"] = last_encounter_count
	row["battleReturnPosition"] = [app.battle_return_position.x, app.battle_return_position.y]
	if not reached:
		_case_fail(row, "battle not reached by held KEY_D within %.1f s" % ENTRY_DEADLINE)
		return
	var battle: Node = current_scene
	row["battleCreatedBy"] = "exploration _open_encounter (held KEY_D)"
	row["arenaEnemyId"] = String(battle.enemy_id)
	row["enemyAnimationTextureNonNull"] = battle.enemy_animation_texture != null
	row["heroineDefaultActive"] = bool(battle.heroine_default_active)
	row["overrides"] = {"sentry_v2_override": int(battle.sentry_v2_override), "patrol_animation_override": int(battle.patrol_animation_override)}
	if String(battle.enemy_id) != enemy_id:
		_case_fail(row, "wrong arena enemy " + String(battle.enemy_id))
	if battle.enemy_animation_texture == null:
		_case_fail(row, "default enemy_animation_texture is null")
	if not bool(battle.heroine_default_active):
		_case_fail(row, "heroine_default_active false")
	if int(battle.sentry_v2_override) != -1 or int(battle.patrol_animation_override) != -1:
		_case_fail(row, "enemy override not -1: %s" % str(row["overrides"]))
	row["entryRow"] = _battle_row(battle)
	await _own_capture(row, "battle-entry", enemy_id, language)
	_press_key(KEY_T, true)
	_press_key(KEY_T, false)
	_event(row, t0, "press KEY_T")
	await process_frame
	row["autoAfterT"] = bool(battle.auto_mode)
	if not bool(battle.auto_mode):
		_case_fail(row, "KEY_T did not enable auto mode")
	var states: Dictionary = {}
	var last_state := ""
	var action_captured := false
	var result_at := -1
	var ready_at := -1
	var battle_start := Time.get_ticks_usec()
	var ready := false
	while _since(battle_start) < RESULT_DEADLINE and _elapsed_run() < HARD_DEADLINE:
		if not is_instance_valid(battle) or current_scene != battle:
			_case_fail(row, "battle scene left before result")
			break
		var state := String(battle.enemy_visual_state)
		states[state] = int(states.get(state, 0)) + 1
		if state != last_state:
			_event(row, t0, "enemy state " + state)
			last_state = state
		if not action_captured and (state == "windup" or state == "strike"):
			action_captured = true
			await _own_capture(row, "enemy-" + state, enemy_id, language)
			continue
		if bool(battle.result_overlay.visible):
			if result_at < 0:
				result_at = Time.get_ticks_usec()
				_event(row, t0, "result visible")
			var settled := bool(battle.result_button.has_focus()) and not bool(battle.result_button.disabled) and not bool(battle.patrol_result_pending) and not bool(battle.heroine_result_pending) and not bool(battle.heroine_defeat_result_pending)
			if settled and ready_at < 0:
				ready_at = Time.get_ticks_usec()
			elif not settled:
				ready_at = -1
			if ready_at >= 0 and _since(ready_at) >= RESULT_SETTLE:
				ready = true
				break
		await process_frame
	row["stateFrameCounts"] = states
	row["statesSeen"] = states.keys()
	row["battleSeconds"] = snappedf(_since(battle_start), 0.001)
	if not ready:
		_case_fail(row, "result not visible/focused within %.0f s" % RESULT_DEADLINE)
		if is_instance_valid(battle):
			row["lastRow"] = _battle_row(battle)
		return
	row["resultRow"] = _battle_row(battle)
	row["won"] = bool(battle.battle_won)
	if not bool(battle.battle_won):
		_case_fail(row, "battle lost (result returns to menu)")
	await _own_capture(row, "battle-result", enemy_id, language)
	_press_key(KEY_ENTER, true)
	_event(row, t0, "press KEY_ENTER")
	await process_frame
	_press_key(KEY_ENTER, false)
	var return_start := Time.get_ticks_usec()
	var returned := false
	while _since(return_start) < RETURN_DEADLINE:
		if current_scene != null and is_instance_valid(current_scene) and current_scene.scene_file_path != SCENE and not current_scene.is_queued_for_deletion():
			returned = true
			break
		await process_frame
	if not returned:
		_case_fail(row, "no scene change within %.1f s of Enter" % RETURN_DEADLINE)
		return
	var world: Node = current_scene
	row["returnScene"] = world.scene_file_path
	_event(row, t0, "returned " + world.scene_file_path)
	if world.scene_file_path != EXPLORATION_SCENE:
		_case_fail(row, "returned to " + world.scene_file_path)
		return
	await process_frame
	await process_frame
	row["returnDestination"] = String(world.destination_id)
	row["returnHero"] = [world.hero.position.x, world.hero.position.y]
	row["returnEnemyVisible"] = bool(world.enemy_visible)
	row["enemyClearedForReturn"] = bool(app.enemy_cleared_for_return)
	if String(world.destination_id) != destination:
		_case_fail(row, "return destination " + String(world.destination_id))
	var hero_position: Vector2 = world.hero.position
	if hero_position.distance_to(app.battle_return_position) > 0.1:
		_case_fail(row, "hero %s != battle_return_position %s" % [str(hero_position), str(app.battle_return_position)])
	if bool(world.enemy_visible):
		_case_fail(row, "enemy still visible after cleared return")
	await _own_capture(row, "returned-world", enemy_id, language)
	row["caseSeconds"] = snappedf(_since(t0), 0.001)


func _own_capture(row: Dictionary, purpose: String, enemy_id: String, language: String) -> void:
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	var path := output_dir.path_join("%s_enemy-battle_default-encounter-%s_%s-%s_%s.png" % [PROJECT, purpose, enemy_id, language, tag])
	var err := image.save_png(path)
	var entry := {"purpose": purpose, "file": path.get_file(), "size": [image.get_width(), image.get_height()], "sha256": FileAccess.get_sha256(path) if err == OK else ""}
	row["captures"].append(entry)
	if err != OK:
		_case_fail(row, "capture save failed %s (%d)" % [purpose, err])
	elif image.get_width() != 640 or image.get_height() != 360:
		_case_fail(row, "capture %s not 640x360: %dx%d" % [purpose, image.get_width(), image.get_height()])


func _own_hashes() -> Dictionary:
	var hashes: Dictionary = _source_hashes()
	for path in [EXPLORATION_SCRIPT, EXPLORATION_SCENE, get_script().get_base_script().resource_path]:
		hashes[path] = FileAccess.get_sha256(path)
	return hashes


func _event(row: Dictionary, t0: int, text: String) -> void:
	row["events"].append({"t": snappedf(_since(t0), 0.001), "e": text})


func _case_fail(row: Dictionary, message: String) -> void:
	row["failures"].append(message)
	failures.append("%s: %s" % [row["name"], message])


func _since(usec: int) -> float:
	return float(Time.get_ticks_usec() - usec) / 1000000.0


func _elapsed_run() -> float:
	return _since(run_start_usec)


func _own_report_path() -> String:
	return output_dir.path_join("%s_enemy-battle_default-encounter-report_v01_%s.json" % [PROJECT, tag])


func _finish_own() -> void:
	report["sourceSha256AtEnd"] = _own_hashes()
	if report["sourceSha256AtEnd"] != report["sourceSha256AtStart"]:
		failures.append("source hashes changed during the run")
	if report["cases"].size() != CLIPS.size():
		failures.append("cases run %d of %d" % [report["cases"].size(), CLIPS.size()])
	report["failures"] = failures
	report["allOk"] = failures.is_empty()
	var file := FileAccess.open(_own_report_path(), FileAccess.WRITE)
	if file == null:
		push_error("FAIL cannot write report " + _own_report_path())
		print("ENEMY51_DEFAULT_ENCOUNTERS_FAIL report-write")
		quit(1)
		return
	file.store_string(JSON.stringify(report, " ") + "\n")
	file.close()
	print("ENEMY51_DEFAULT_ENCOUNTERS_REPORT " + _own_report_path())
	if failures.is_empty():
		print("ENEMY51_DEFAULT_ENCOUNTERS_ALL_OK cases=%d" % report["cases"].size())
		quit(0)
	else:
		for f in failures:
			push_error("FAIL " + f)
		print("ENEMY51_DEFAULT_ENCOUNTERS_FAIL count=%d" % failures.size())
		quit(1)


func _fail_own(message: String) -> void:
	push_error("FAIL " + message)
	print("ENEMY51_DEFAULT_ENCOUNTERS_FAIL " + message)
	quit(1)
