extends SceneTree

# Patrol battle animation pilot v01 (UNAPPROVED) -- windowed evidence harness. Run with `-s <absolute path>` and
#   --capture-dir=<absolute dir> --head-script=<absolute path to the HEAD battle_arena.gd text>
# 1. Simulation parity: patrol and sentry battles stepped at a fixed 1/60 s for 40 s with auto mode, using the HEAD
#    script (compiled in memory) and this tree's script with each flag combination. Every tick's combat tuple must match.
# 2. Loader / fallback: malformed packages and type mutations must return {} and keep the placeholder.
# 3. 640x360 (actual 1x) captures in EN and ZH: patrol pilot states, plus default and sentry-on pixel parity with HEAD.
# 4. Normal-speed loop: the real _process at engine delta, logging every frame's visual state/frame for the timing record.
# Prints PATROL_ANIM_HARNESS OK only if every predicate passed.
const SCENE := "res://scenes/battle_arena.tscn"
const PREFIX := "rpg-2-star-ocean-the-second_patrol_battle-animation-"
const STAMP := "v01_20261019-194007-a4b10a85"
const LOADER := "res://assets/enemies/patrol-anim-v01/rpg-2-star-ocean-the-second_patrol_battle-animation-loader_v01_20261019-194007-a4b10a85.gd"
const PACKAGE := "res://assets/enemies/patrol-anim-v01/rpg-2-star-ocean-the-second_patrol_battle-animation-runtime-package_v01_20261019-194007-a4b10a85.json"

var app: Node
var capture_dir := ""
var head_script: GDScript
var Arena: GDScript
var failures: Array[String] = []
var report := {"sim": [], "loader": [], "captures": [], "parity": [], "loop": {}}


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	if DisplayServer.get_name() == "headless":
		_fail_now("windowed run required")
		return
	var head_path := ""
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--capture-dir="):
			capture_dir = argument.trim_prefix("--capture-dir=")
		elif argument.begins_with("--head-script="):
			head_path = argument.trim_prefix("--head-script=")
	if capture_dir.is_empty() or head_path.is_empty() or not FileAccess.file_exists(head_path):
		_fail_now("missing --capture-dir or --head-script")
		return
	DirAccess.make_dir_recursive_absolute(capture_dir)
	app = root.get_node("AppState")
	SaveStore.root_path = "user://test-saves/patrol-anim-v01"
	Arena = load("res://scripts/battle_arena.gd")
	head_script = GDScript.new()
	head_script.source_code = FileAccess.get_file_as_string(head_path)
	if head_script.reload() != OK:
		_fail_now("HEAD script failed to compile")
		return
	root.size = Vector2i(640, 360)
	for i in 4:
		await process_frame
	_sim_parity(false)
	_sim_parity(true)
	_loader_checks()
	await _captures()
	await _normal_speed_loop()
	_finish()


func _set_flags(patrol: int, sentry: int) -> void:
	Arena.patrol_animation_override = patrol
	Arena.patrol_animation_package_override = ""
	Arena.sentry_v2_override = sentry
	head_script.sentry_v2_override = sentry


func _setup_run(enemy_id: String, language: String) -> void:
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


func _make_battle(use_head: bool) -> Node2D:
	var battle: Node2D = load(SCENE).instantiate()
	if use_head:
		battle.set_script(head_script)
	return battle


func _tuple(battle: Node2D) -> String:
	var parts := [battle.enemy_x, battle.enemy_hp, battle.enemy_windup, battle.enemy_cooldown, battle.enemy_attack_count, battle.enemy_target_index, battle.battle_finished]
	for fighter in battle.fighters:
		parts.append(fighter["x"])
		parts.append(fighter["attack_cooldown"])
		parts.append(int(app.member_state(String(fighter["id"]))["hp"]))
	return var_to_str(parts)


func _sim_parity(hold: bool) -> void:
	# hold: the same deterministic HP hold (40+ until three enemy strikes) in every variant, so wind-up/strike/party damage run.
	for enemy_id in ["patrol", "sentry"]:
		var digests := {}
		var states_seen := {}
		for variant in ["head", "off", "patrol-on", "sentry-on", "both-on"]:
			_set_flags(1 if variant in ["patrol-on", "both-on"] else 0, 1 if variant in ["sentry-on", "both-on"] else 0)
			_setup_run(enemy_id, "en")
			var battle := _make_battle(variant == "head" or variant == "sentry-on-head")
			battle.set_process(false)
			root.add_child(battle)
			battle.auto_mode = true
			var ctx := HashingContext.new()
			ctx.start(HashingContext.HASH_SHA256)
			var seen := {}
			var ticks := 0
			for tick in 2400:
				if hold and battle.enemy_attack_count < 3 and battle.enemy_hp < 40:
					battle.enemy_hp = 40
				battle._process(1.0 / 60.0)
				ctx.update(_tuple(battle).to_utf8_buffer())
				ticks += 1
				if battle.get("enemy_animation_texture") != null:
					seen[battle.enemy_visual_state] = true
				if battle.battle_finished:
					break
			var stats: Dictionary = battle.enemy
			digests[variant] = ctx.finish().hex_encode()
			states_seen[variant] = seen.keys()
			report["sim"].append({"enemy": enemy_id, "hold": hold, "attacks": battle.enemy_attack_count, "variant": variant, "ticks": ticks, "digest": digests[variant], "finished": battle.battle_finished, "visualStates": seen.keys(), "stats": [stats["max_hp"], stats["damage"], stats["speed"], stats["windup"], stats["cooldown"]], "pilotLoaded": battle.get("enemy_animation_texture") != null})
			battle.free()
		for variant in digests:
			if digests[variant] != digests["head"]:
				failures.append("sim %s %s hold=%s digest differs from HEAD" % [enemy_id, variant, hold])
	_set_flags(0, 0)
	var patrol_stats: Dictionary = Arena.ENEMIES["patrol"]
	if [patrol_stats["max_hp"], patrol_stats["damage"], patrol_stats["speed"], patrol_stats["windup"], patrol_stats["cooldown"]] != [64, 12, 55.0, 0.65, 1.35]:
		failures.append("patrol stats changed")


func _loader_checks() -> void:
	var loader: Script = load(LOADER)
	var good: Dictionary = loader.load_package(PACKAGE)
	_expect(not good.is_empty(), "loader accepts the shipped package")
	if not good.is_empty():
		var anim: Dictionary = good["animation"]
		_expect(anim["cell"] == Vector2(112, 72) and anim["anchor"] == Vector2(56, 66), "package cell/anchor")
		_expect(Array(anim["states"]["windup"]).size() == 3 and anim["windup_phases"] == true, "three windup phases")
	for bad_path in ["", "res://nope.json", "user://x.json", PACKAGE.replace(".json", "-missing.json"), PACKAGE.replace("patrol-anim-v01/", "patrol-anim-v01/../patrol-anim-v01/"), PACKAGE.replace("patrol-anim-v01/", "patrol-anim-v01//"), "res://assets/enemies/patrol-anim-v01/../../../project.godot"]:
		_expect(loader.load_package(bad_path).is_empty(), "rejects path " + bad_path)
	var base: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PACKAGE))
	var mutations := {
		"schema": "x", "enemy": "sentry", "cell": [112], "anchor": "56,66", "frame_count": 25, "body_center_x": -1,
		"gait_step_px": "4", "move_grace": null, "telegraph_center_y": 9999, "telegraph_scale": [0, 1], "windup_phases": 1,
		"front_states": ["fly"], "states": {"idle": [0]}, "frame_time": {"idle": 0}, "strip": "res://icon.svg", "strip_sha256": "0".repeat(64),
	}
	for key in mutations:
		var data := base.duplicate(true)
		data[key] = mutations[key]
		_expect(_validate_mutation(loader, data).is_empty(), "rejects mutated " + key)
	var strip_traversal := base.duplicate(true)
	strip_traversal["strip"] = String(base["strip"]).replace("patrol-anim-v01/", "patrol-anim-v01/../patrol-anim-v01/")
	_expect(_validate_mutation(loader, strip_traversal).is_empty(), "rejects existing strip traversal")
	var missing_hash := base.duplicate(true)
	missing_hash.erase("strip_sha256")
	_expect(_validate_mutation(loader, missing_hash).is_empty(), "rejects missing strip hash")
	var cell_mismatch := base.duplicate(true)
	cell_mismatch["cell"] = [111, 72]
	_expect(_validate_mutation(loader, cell_mismatch).is_empty(), "rejects strip/cell size mismatch")
	_expect(not _validate_mutation(loader, base.duplicate(true)).is_empty(), "shim accepts the unmodified package")
	# Battle-level fallback: a bad package keeps the placeholder block and the battle runs.
	_set_flags(1, 0)
	Arena.patrol_animation_package_override = "res://assets/enemies/patrol-anim-v01/missing.json"
	_setup_run("patrol", "en")
	var battle := _make_battle(false)
	root.add_child(battle)
	_expect(battle.enemy_texture == null and battle.enemy_animation_texture == null, "battle falls back on missing package")
	battle._process(1.0 / 60.0)
	battle.free()
	_set_flags(0, 0)


func _validate_mutation(loader: Script, data: Dictionary) -> Dictionary:
	# Writes the candidate into the package directory under a unique temporary name, loads it, then deletes it.
	var path := "res://assets/enemies/patrol-anim-v01/rpg-2-star-ocean-the-second_patrol_harness-temp-mutation_v01_%s-%08x.json" % [Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-"), Time.get_ticks_usec()]
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		failures.append("cannot write temp mutation")
		return {"error": true}
	f.store_string(JSON.stringify(data))
	f.close()
	var result: Dictionary = loader.load_package(path)
	DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	return result


func _expect(condition: bool, label: String) -> void:
	report["loader"].append({"check": label, "ok": condition})
	if not condition:
		failures.append(label)


func _stage(enemy_id: String, language: String, use_head: bool) -> Node2D:
	if current_scene != null:
		current_scene.free()
		current_scene = null
	_setup_run(enemy_id, language)
	var battle := _make_battle(use_head)
	battle.paused = true
	root.add_child(battle)
	current_scene = battle
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
	if battle.get("enemy_animation_texture") != null:
		battle.enemy_visual_state = "idle"
		battle.enemy_visual_clock = 0.05
		battle.enemy_visual_still_time = 1.0
		battle.enemy_visual_last_hp = battle.enemy_hp
		battle.enemy_visual_last_attack_count = battle.enemy_attack_count
	return battle


func _pose(battle: Node2D, state: String) -> void:
	var anim := battle.get("enemy_animation_texture") != null
	match state:
		"idle":
			if anim:
				battle._advance_enemy_visual(0.25, false)
		"move":
			if anim:
				battle._advance_enemy_visual(0.02, true)
				for step in 3:
					battle.enemy_x -= 4.0
					battle._advance_enemy_visual(0.073, true)
		"windup-a", "windup-b", "windup-c":
			battle.enemy_x = 353.0
			battle.enemy_windup = {"windup-a": 0.6, "windup-b": 0.35, "windup-c": 0.1}[state]
			if anim:
				battle._advance_enemy_visual(0.02, false)
		"strike":
			battle.enemy_x = 353.0
			battle.fighters[0]["x"] = 300.0
			battle.enemy_target_index = 0
			battle._apply_enemy_hit()
			if anim:
				battle._advance_enemy_visual(0.02, false)
		"hit":
			battle.enemy_x = 353.0
			battle.fighters[0]["x"] = 353.0 - 45.0
			battle._try_attack()
			battle.fighters[0]["visual_elapsed"] = 0.06
			if anim:
				battle._advance_enemy_visual(0.02, false)
		"defeat":
			battle.enemy_x = 353.0
			battle.fighters[0]["x"] = 353.0 - 45.0
			battle.enemy_hp = 3
			battle._try_attack()
			if anim:
				for i in 50:
					battle._advance_enemy_visual(0.02, false)


func _shot(battle: Node2D, name: String) -> Image:
	battle._update_hud()
	battle.queue_redraw()
	await process_frame
	await process_frame
	var image := root.get_viewport().get_texture().get_image()
	if image.get_size() != Vector2i(640, 360):
		failures.append("capture size %s for %s" % [image.get_size(), name])
	if name != "":
		var path := capture_dir.path_join(name)
		if image.save_png(path) != OK:
			failures.append("save " + path)
		report["captures"].append({"file": name, "sha256": FileAccess.get_sha256(path), "state": battle.get("enemy_visual_state"), "frame": battle._enemy_visual_frame() if battle.get("enemy_animation_texture") != null else -1})
	return image


func _captures() -> void:
	for language in ["en", "zh"]:
		_set_flags(1, 0)
		for state in ["idle", "move", "windup-a", "windup-b", "windup-c", "strike", "hit", "defeat"]:
			var battle := _stage("patrol", language, false)
			if battle.enemy_animation_texture == null:
				failures.append("patrol pilot not loaded for capture")
				return
			_pose(battle, state)
			await _shot(battle, "%sactual1x-%s-%s-640_%s.png" % [PREFIX, state, language, STAMP])
		# Default-off and sentry-on must match the HEAD script pixel for pixel; patrol-on must differ from the default.
		for combo in [["patrol", 0, 0], ["sentry", 0, 0], ["sentry", 0, 1], ["sentry", 1, 1]]:
			for state in ["idle", "windup-b", "hit", "defeat"]:
				_set_flags(combo[1], combo[2])
				var head := _stage(combo[0], language, true)
				_pose(head, state)
				var a := await _shot(head, "")
				var candidate := _stage(combo[0], language, false)
				_pose(candidate, state)
				var b := await _shot(candidate, "")
				var same := a.get_data() == b.get_data()
				var label := "%s p%d s%d %s %s" % [combo[0], combo[1], combo[2], state, language]
				report["parity"].append({"case": label, "pixelIdenticalToHead": same, "sha256": _image_sha(b)})
				if not same:
					failures.append("pixel parity " + label)
				if combo[0] == "patrol" and state == "idle":
					b.save_png(capture_dir.path_join("%sdefault-off-patrol-idle-%s-640_%s.png" % [PREFIX, language, STAMP]))
				if combo[0] == "sentry" and combo[2] == 1 and combo[1] == 0 and state == "idle":
					b.save_png(capture_dir.path_join("%ssentry-on-unchanged-idle-%s-640_%s.png" % [PREFIX, language, STAMP]))
	if current_scene != null:
		current_scene.free()
		current_scene = null
	_set_flags(0, 0)


func _image_sha(image: Image) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(image.get_data())
	return ctx.finish().hex_encode()


func _normal_speed_loop() -> void:
	# Real engine frames and real deltas; the battle runs its own _process. Logs the visual state/frame each frame.
	_set_flags(1, 0)
	_setup_run("patrol", "en")
	var battle := _make_battle(false)
	root.add_child(battle)
	current_scene = battle
	battle.auto_mode = true
	var rows := []
	var started := Time.get_ticks_usec()
	var saved := {}
	while Time.get_ticks_usec() - started < 20_000_000:
		await process_frame
		# Evidence-loop only (not the parity runs): the auto party can destroy the patrol before it ever attacks, so its HP is
		# held at 40+ until it has struck twice, then released so the defeat plays. Every other value is the real battle.
		if battle.enemy_attack_count < 2 and battle.enemy_hp < 40:
			battle.enemy_hp = 40
		var t := (Time.get_ticks_usec() - started) / 1_000_000.0
		var state: String = battle.enemy_visual_state
		var frame: int = battle._enemy_visual_frame() if battle.enemy_animation_texture != null else -1
		rows.append([snappedf(t, 0.001), state, frame, snappedf(battle.enemy_x, 0.01), battle.enemy_hp])
		if not saved.has(state) and state in ["move", "windup", "strike", "hit", "defeat"]:
			saved[state] = true
			var image := root.get_viewport().get_texture().get_image()
			image.save_png(capture_dir.path_join("%snormal-speed-first-%s-en-640_%s.png" % [PREFIX, state, STAMP]))
		if battle.battle_finished and t > 0 and saved.has("defeat") and rows.size() > 0 and float(rows[-1][0]) - float(_first_time(rows, "defeat")) > 1.2:
			break
	var transitions := []
	for i in rows.size():
		if i == 0 or rows[i][1] != rows[i - 1][1] or rows[i][2] != rows[i - 1][2]:
			transitions.append(rows[i])
	report["loop"] = {"hpHeldUntilTwoStrikes": true, "frames": rows.size(), "seconds": rows[-1][0] if rows.size() else 0.0, "statesSeen": saved.keys(), "transitions": transitions}
	for state in ["move", "windup", "strike", "defeat"]:
		if not saved.has(state):
			failures.append("normal-speed loop never showed " + state)
	battle.free()
	current_scene = null
	_set_flags(0, 0)


func _first_time(rows: Array, state: String) -> float:
	for row in rows:
		if row[1] == state:
			return float(row[0])
	return 0.0


func _finish() -> void:
	report["failures"] = failures
	var file := FileAccess.open(capture_dir.path_join("%sharness-report_%s.json" % [PREFIX, STAMP]), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  ") + "\n")
	file.close()
	if failures.is_empty():
		print("PATROL_ANIM_HARNESS OK sim=%d loader=%d captures=%d parity=%d" % [report["sim"].size(), report["loader"].size(), report["captures"].size(), report["parity"].size()])
		quit(0)
	else:
		for f in failures:
			push_error("FAIL " + f)
		print("PATROL_ANIM_HARNESS FAIL count=%d" % failures.size())
		quit(1)


func _fail_now(message: String) -> void:
	push_error("FAIL " + message)
	quit(1)
