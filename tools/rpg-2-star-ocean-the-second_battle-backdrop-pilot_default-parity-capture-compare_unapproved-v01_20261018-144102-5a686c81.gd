extends SceneTree

# Default-off pixel parity for the opt-in battle backdrop loader (`-- --battle-backdrop-pilot`; TECHNICAL capability, every band
# UNAPPROVED). Run windowed with `-s <absolute path to this file>` against any project tree (the base 0636b40 export or the
# candidate): it uses only battle API that exists in both, so the same script renders the same deterministic battle states.
#   --capture-dir=<absolute dir>   where this run's PNGs and JSON index go (required)
#   --variant=<name>               lowercase name of this run; goes into every file name (required)
#   --stamp=<YYYYMMDD-HHMMSS-id8>  shared by every run of one parity check (required)
#   --compare-to=<absolute dir>    optional: after capturing, compare every capture with the same-named one of another variant
#   --compare-variant=<name>       that other variant's name (required with --compare-to)
#   --expect=<same|differs-patrol> same: 0 differing pixels everywhere. differs-patrol: every patrol (outskirts band) capture
#                                  differs and every sentry (ruins, no band) capture is identical; this is the negative control.
# Any other user args (`--sentry-v2-pilot`, `--battle-backdrop-pilot`) pass through to the battle script unchanged.
# States: sentry (ruins) and patrol (outskirts) x zh/en x 1280x720 and native 640x360 windows x idle / wind-up / hit / defeat.
const BATTLE_SCENE_PATH := "res://scenes/battle_arena.tscn"
const PREFIX := "rpg-2-star-ocean-the-second_battle-backdrop-parity"
const STATES := ["idle", "windup", "hit", "defeat"]
const WINDOWS := {"1280": Vector2i(1280, 720), "640": Vector2i(640, 360)}

var app: Node
var args := {}
var index := []


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	if DisplayServer.get_name() == "headless":
		_fail("windowed run required")
		return
	for argument in OS.get_cmdline_user_args():
		for key in ["--capture-dir=", "--variant=", "--stamp=", "--compare-to=", "--compare-variant=", "--expect="]:
			if argument.begins_with(key):
				args[key] = argument.trim_prefix(key)
	var capture_dir: String = args.get("--capture-dir=", "")
	var variant: String = args.get("--variant=", "")
	var stamp: String = args.get("--stamp=", "")
	if capture_dir.is_empty() or RegEx.create_from_string("^[a-z0-9-]+$").search(variant) == null:
		_fail("--capture-dir= and a lowercase --variant= are required")
		return
	if RegEx.create_from_string("^[0-9]{8}-[0-9]{6}-[0-9a-f]{8}$").search(stamp) == null:
		_fail("--stamp=YYYYMMDD-HHMMSS-<8 lowercase hex> required")
		return
	DirAccess.make_dir_recursive_absolute(capture_dir)
	app = root.get_node("AppState")
	SaveStore.root_path = "user://test-saves/battle-backdrop-default-parity"
	for window_key in WINDOWS:
		root.size = WINDOWS[window_key]
		for i in 4:
			await process_frame
		for enemy_id in ["sentry", "patrol"]:
			for language in ["zh", "en"]:
				for state in STATES:
					if not await _capture(capture_dir, variant, stamp, enemy_id, language, state, window_key):
						return
	var report := {}
	if args.has("--compare-to="):
		report = _compare(capture_dir, variant, stamp)
		if report.is_empty():
			return
	var file := FileAccess.open(capture_dir.path_join("%s_%s-index_%s.json" % [PREFIX, variant, stamp]), FileAccess.WRITE)
	file.store_string(JSON.stringify({
		"battleScriptSha256": FileAccess.get_sha256("res://scripts/battle_arena.gd"),
		"battleScriptHasBackdropApi": FileAccess.get_file_as_string("res://scripts/battle_arena.gd").contains("battle_backdrop_enabled"),
		"variant": variant,
		"stamp": stamp,
		"cmdlineUserArgs": OS.get_cmdline_user_args(),
		"captures": index,
		"compare": report,
	}, "  ") + "\n")
	file.close()
	if not report.is_empty() and not bool(report["pass"]):
		_fail("compare %s vs %s: %s" % [variant, report["againstVariant"], report["failures"]])
		return
	print("BATTLE_BACKDROP_PARITY OK variant=%s stamp=%s captures=%d compared=%s" % [variant, stamp, index.size(), report.get("compared", 0)])
	quit(0)


func _capture(capture_dir: String, variant: String, stamp: String, enemy_id: String, language: String, state: String, window_key: String) -> bool:
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
	var key := "%s-%s-%s-%s" % [enemy_id, state, language, window_key]
	var name := "%s_%s-%s_%s.png" % [PREFIX, variant, key, stamp]
	var path := capture_dir.path_join(name)
	if image.save_png(path) != OK:
		_fail("save " + path)
		return false
	index.append({"key": key, "file": name, "sha256": FileAccess.get_sha256(path), "size": [image.get_width(), image.get_height()], "enemyHp": battle.enemy_hp, "battleFinished": battle.battle_finished, "backdropStatus": battle.get("battle_backdrop_status"), "backdropArena": battle.get("battle_backdrop_arena_id"), "sentryPilotTextureLoaded": battle.get("enemy_texture") != null})
	return true


func _compare(capture_dir: String, variant: String, stamp: String) -> Dictionary:
	var other_dir: String = args["--compare-to="]
	var other: String = args.get("--compare-variant=", "")
	var expect: String = args.get("--expect=", "same")
	if other.is_empty() or not expect in ["same", "differs-patrol"]:
		_fail("--compare-variant= and --expect=<same|differs-patrol> required with --compare-to=")
		return {}
	var rows := []
	var failures := []
	for entry in index:
		var key: String = entry["key"]
		var mine := Image.load_from_file(capture_dir.path_join(entry["file"]))
		var theirs := Image.load_from_file(other_dir.path_join("%s_%s-%s_%s.png" % [PREFIX, other, key, stamp]))
		var differing := -1
		if theirs != null and mine.get_size() == theirs.get_size():
			mine.convert(Image.FORMAT_RGBA8)
			theirs.convert(Image.FORMAT_RGBA8)
			differing = _differing_pixels(mine, theirs)
		var should_differ := expect == "differs-patrol" and key.begins_with("patrol-")
		var ok := differing > 0 if should_differ else differing == 0
		if not ok:
			failures.append("%s differing=%d expected_%s" % [key, differing, "differ" if should_differ else "same"])
		rows.append({"key": key, "differingPixels": differing, "expected": "differ" if should_differ else "same", "pass": ok})
	return {"againstVariant": other, "expect": expect, "compared": rows.size(), "failures": failures, "pass": failures.is_empty() and rows.size() == 32, "rows": rows}


func _differing_pixels(a: Image, b: Image) -> int:
	var da := a.get_data()
	var db := b.get_data()
	if da == db:
		return 0
	var count := 0
	for i in range(0, da.size(), 4):
		if da[i] != db[i] or da[i + 1] != db[i + 1] or da[i + 2] != db[i + 2] or da[i + 3] != db[i + 3]:
			count += 1
	return count


func _reset_pilot_visual(battle: Node2D) -> void:
	# Only trees with the sentry v2 pilot have these members, and only with its flag do they hold a strip.
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
