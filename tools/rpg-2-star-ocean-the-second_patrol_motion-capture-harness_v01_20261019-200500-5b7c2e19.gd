extends SceneTree

# Patrol battle animation pilot v01 (UNAPPROVED, off by default) -- real-time 640x360 viewport motion capture.
# Run windowed with `-s <absolute path> -- --patrol-battle-animation-pilot --capture-dir=<absolute dir>`.
# The pilot is enabled only by the real CLI flag (no static override). Each clip runs the real battle scene's own
# _process at real engine delta. The only input is one synthetic battle_auto key press (KEY_T, physical + keycode)
# through Input.parse_input_event, which reaches the arena's real _input handler.
#   normal-<lang>: unmodified combat. No state, HP or timer writes.
#   held-<lang>:   TEST-ONLY durability hold. Patrol HP is reset to 40 whenever it drops below 40 until it has struck twice,
#                  then released. Nothing else is written. This is not normal gameplay.
# Every viewport frame is copied into memory during the clip (saved to PNG afterwards) with its wall-clock timestamp,
# the engine process delta, Engine frame counters and the enemy visual state/frame. Prints PATROL_MOTION_CAPTURE OK.
const SCENE := "res://scenes/battle_arena.tscn"
const STAMP := "v01_20261019-200500-5b7c2e19"
const LOADER := "res://assets/enemies/patrol-anim-v01/rpg-2-star-ocean-the-second_patrol_battle-animation-loader_v01_20261019-194007-a4b10a85.gd"
const PACKAGE := "res://assets/enemies/patrol-anim-v01/rpg-2-star-ocean-the-second_patrol_battle-animation-runtime-package_v01_20261019-194007-a4b10a85.json"
const ARENA := "res://scripts/battle_arena.gd"
const MAX_SECONDS := 25.0
const TAIL_SECONDS := 1.5

var app: Node
var capture_dir := ""
var failures: Array[String] = []
var report := {"stamp": STAMP, "clips": [], "sourceSha256AtStart": {}}


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	if DisplayServer.get_name() == "headless":
		_fail_now("windowed run required")
		return
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--capture-dir="):
			capture_dir = argument.trim_prefix("--capture-dir=")
	if capture_dir.is_empty():
		_fail_now("missing --capture-dir")
		return
	if not OS.get_cmdline_user_args().has("--patrol-battle-animation-pilot"):
		_fail_now("pilot CLI flag missing")
		return
	for path in [ARENA, LOADER, PACKAGE]:
		report["sourceSha256AtStart"][path] = FileAccess.get_sha256(path)
	app = root.get_node("AppState")
	SaveStore.root_path = "user://test-saves/patrol-motion-v01"
	root.size = Vector2i(640, 360)
	report["engine"] = {"version": Engine.get_version_info()["string"], "renderer": RenderingServer.get_current_rendering_driver_name(), "maxFps": Engine.max_fps, "vsync": DisplayServer.window_get_vsync_mode(), "physicsTicks": Engine.physics_ticks_per_second, "timeScale": Engine.time_scale, "screenRefresh": DisplayServer.screen_get_refresh_rate()}
	for i in 6:
		await process_frame
	for language in ["en", "zh"]:
		await _clip("normal", language, false)
	for language in ["en", "zh"]:
		await _clip("held", language, true)
	_finish()


func _setup_run(language: String) -> void:
	app.begin_new_run()
	app.hero_appearance = "male"
	app.recruit_member("liang-xu")
	app.recruit_member("zhao-ling")
	app.ji_records_checked = true
	app.recruit_member("ji-cheng")
	app.select_destination("scifi.outskirts")
	if app.language != language:
		app.toggle_language()
	app.begin_battle("patrol", Vector2(330, 215))


func _press_auto() -> void:
	for pressed in [true, false]:
		var event := InputEventKey.new()
		event.keycode = KEY_T
		event.physical_keycode = KEY_T
		event.pressed = pressed
		Input.parse_input_event(event)


func _clip(kind: String, language: String, hold: bool) -> void:
	var name := "%s-%s" % [kind, language]
	_setup_run(language)
	var battle: Node2D = load(SCENE).instantiate()
	root.add_child(battle)
	current_scene = battle
	if battle.enemy_animation_texture == null:
		failures.append(name + ": pilot animation texture not loaded")
	var images: Array[Image] = []
	var rows := []
	var holds := 0
	var auto_pressed_at := -1.0
	var auto_seen := false
	var finished_at := -1.0
	var started := Time.get_ticks_usec()
	var last := started
	while true:
		await process_frame
		var now := Time.get_ticks_usec()
		var t := (now - started) / 1_000_000.0
		if auto_pressed_at < 0.0 and t >= 0.25:
			_press_auto()
			auto_pressed_at = t
		if battle.auto_mode:
			auto_seen = true
		if hold and battle.enemy_attack_count < 2 and battle.enemy_hp < 40:
			battle.enemy_hp = 40
			holds += 1
		var image := root.get_viewport().get_texture().get_image()
		images.append(image)
		rows.append({"t": snappedf(t, 0.000001), "wallDelta": snappedf((now - last) / 1_000_000.0, 0.000001), "processDelta": snappedf(root.get_process_delta_time(), 0.000001), "framesDrawn": Engine.get_frames_drawn(), "processFrames": Engine.get_process_frames(), "state": battle.enemy_visual_state, "frame": battle._enemy_visual_frame(), "enemyHp": battle.enemy_hp, "enemyX": snappedf(battle.enemy_x, 0.01), "attacks": battle.enemy_attack_count, "auto": battle.auto_mode, "finished": battle.battle_finished, "size": [image.get_width(), image.get_height()]})
		last = now
		if battle.battle_finished and finished_at < 0.0:
			finished_at = t
		if finished_at >= 0.0 and t - finished_at >= TAIL_SECONDS:
			break
		if t >= MAX_SECONDS:
			failures.append(name + ": battle not finished within %.0f s" % MAX_SECONDS)
			break
	battle.free()
	current_scene = null
	var frame_dir := capture_dir.path_join("frames").path_join(name)
	DirAccess.make_dir_recursive_absolute(frame_dir)
	var states := {}
	for i in images.size():
		var file := frame_dir.path_join("f%05d.png" % i)
		if images[i].get_size() != Vector2i(640, 360):
			failures.append("%s frame %d size %s" % [name, i, images[i].get_size()])
		if images[i].save_png(file) != OK:
			failures.append("save " + file)
		rows[i]["file"] = "frames/%s/f%05d.png" % [name, i]
		rows[i]["sha256"] = FileAccess.get_sha256(file)
		states[rows[i]["state"]] = int(states.get(rows[i]["state"], 0)) + 1
	images.clear()
	if not auto_seen:
		failures.append(name + ": battle_auto key press never reached the arena")
	report["clips"].append({"name": name, "kind": kind, "language": language, "durabilityHold": hold, "holdWrites": holds, "autoPressedAt": auto_pressed_at, "finishedAt": finished_at, "frames": rows.size(), "statesFrameCount": states, "rows": rows})


func _finish() -> void:
	report["sourceSha256AtEnd"] = {}
	for path in [ARENA, LOADER, PACKAGE]:
		report["sourceSha256AtEnd"][path] = FileAccess.get_sha256(path)
	report["failures"] = failures
	var file := FileAccess.open(capture_dir.path_join("rpg-2-star-ocean-the-second_patrol_motion-capture-raw_%s.json" % STAMP), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, " ") + "\n")
	file.close()
	if failures.is_empty():
		print("PATROL_MOTION_CAPTURE OK clips=%d" % report["clips"].size())
		quit(0)
	else:
		for f in failures:
			push_error("FAIL " + f)
		print("PATROL_MOTION_CAPTURE FAIL count=%d" % failures.size())
		quit(1)


func _fail_now(message: String) -> void:
	push_error("FAIL " + message)
	quit(1)
