extends SceneTree

# MVP settings check (language, master volume, movement preset, F10 overlay). Windowed, isolated APPDATA,
# run as four processes in order so persistence is tested across real restarts:
#   Godot --path game -s <this file> -- --phase=<fresh|restart|corrupt|invalid> --baseline=<json> --user-dir-contains=<isolated
#   APPDATA folder name, refuses to run against a real profile> [--capture-dir=<dir> --stamp=<id>]
# --baseline is the InputMap/Master-bus dump of the tree without settings code (origin/main), made by
# tools/rpg-2-star-ocean-the-second_mvp-settings_input-audio-baseline-dump_check-v01_20261018-150534-201f58ff.gd.
# fresh: no prefs -> exact defaults; title + exploration + battle flows; leaves en / 40 / arrows saved.
# restart: those prefs applied at startup; reset restores defaults; leaves a corrupt file.
# corrupt: unreadable file -> exact defaults, file not rewritten; leaves a wrong-typed file.
# invalid: wrong types -> exact defaults; clamping; removes the file.
const PREFIX := "rpg-2-star-ocean-the-second_mvp-settings"
const MENU := "res://scenes/main_menu.tscn"
const BATTLE := "res://scenes/battle_arena.tscn"

var app: Node
var settings: GameSettings
var args := {}
var baseline := {}
var checks := 0
var captures := []


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	for argument in OS.get_cmdline_user_args():
		var parts := argument.trim_prefix("--").split("=", true, 1)
		if parts.size() == 2:
			args[parts[0]] = parts[1]
	if DisplayServer.get_name() == "headless":
		_fail("windowed run required")
		return
	var isolated_marker := String(args.get("user-dir-contains", ""))
	if isolated_marker.is_empty() or not OS.get_user_data_dir().contains(isolated_marker):
		_fail("user data dir is not the isolated one: " + OS.get_user_data_dir())
		return
	baseline = JSON.parse_string(FileAccess.get_file_as_string(args.get("baseline", "")))
	if baseline == null or not baseline.has("actions"):
		_fail("--baseline json required")
		return
	app = root.get_node("AppState")
	settings = app.settings
	SaveStore.root_path = "user://test-saves/mvp-settings-check"
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(640, 360)
	for i in 4:
		await process_frame
	var ok := false
	match args.get("phase", ""):
		"fresh":
			ok = await _phase_fresh()
		"restart":
			ok = await _phase_restart()
		"corrupt":
			ok = _phase_corrupt()
		"invalid":
			ok = _phase_invalid()
		_:
			_fail("--phase=<fresh|restart|corrupt|invalid> required")
			return
	if not ok:
		return
	if args.has("capture-dir"):
		var file := FileAccess.open(String(args["capture-dir"]).path_join("%s_check-%s-index_%s.json" % [PREFIX, args["phase"], args.get("stamp", "x")]), FileAccess.WRITE)
		file.store_string(JSON.stringify({"phase": args["phase"], "checks": checks, "captures": captures, "userDataDir": OS.get_user_data_dir()}, "  ") + "\n")
		file.close()
	print("MVP_SETTINGS_PHASE_OK phase=%s checks=%d captures=%d" % [args["phase"], checks, captures.size()])
	quit(0)


# --- phases -------------------------------------------------------------------------------------

func _phase_fresh() -> bool:
	if not _check(settings.load_status == "missing" and not FileAccess.file_exists(settings.config_path), "no prefs file at first start"):
		return false
	if not _check_defaults("fresh start"):
		return false

	# Title screen: new Settings button, language toggle there does not write prefs.
	change_scene_to_file(MENU)
	await _frames(3)
	var menu: Control = current_scene
	var settings_button: Button = menu.get("settings_button")
	if not _check(settings_button != null and settings_button.text == "设置", "title Settings button (zh)"):
		return false
	if not _check(_fits_viewport(menu), "title screen fits 640x360 with no clipped button text (zh)"):
		return false
	if not await _capture("title-zh"):
		return false
	app.toggle_language()
	await _frames(2)
	if not _check(settings_button.text == "Settings" and _fits_viewport(menu), "title Settings button fits (en)"):
		return false
	if not await _capture("title-en"):
		return false
	app.toggle_language()
	if not _check(not FileAccess.file_exists(settings.config_path), "title language toggle keeps prefs untouched"):
		return false

	# Open from the title button (real mouse click).
	settings_button.grab_focus()
	await _click(settings_button)
	var overlay: CanvasLayer = settings.overlay
	if not _check(settings.is_open() and paused, "title button opens overlay and pauses the tree"):
		return false
	if not _check(root.gui_get_focus_owner() == overlay.get("zh_button"), "overlay takes focus"):
		return false
	if not _check(not FileAccess.file_exists(settings.config_path), "opening writes nothing"):
		return false
	if not _check(_overlay_fits(overlay), "overlay layout fits (zh)"):
		return false
	if not await _capture("title-settings-zh"):
		return false

	# Language through the existing AppState machinery.
	await _click(overlay.get("en_button"))
	if not _check(app.language == "en" and _config_value("language") == "en", "English applies and persists"):
		return false
	if not _check(settings_button.text == "Settings" and (overlay.get("title_label") as Label).text == "Settings", "screen under overlay relabels"):
		return false
	if not _check(_overlay_fits(overlay), "overlay layout fits (en)"):
		return false
	if not await _capture("title-settings-en"):
		return false

	# Master volume.
	var slider: HSlider = overlay.get("volume_slider")
	slider.value = 0
	if not _check(AudioServer.is_bus_mute(0) and _config_value("master_volume") == 0, "volume 0 mutes Master"):
		return false
	slider.grab_focus()
	await _key(KEY_RIGHT)
	if not _check(settings.master_volume == 5 and not AudioServer.is_bus_mute(0) and is_equal_approx(AudioServer.get_bus_volume_db(0), linear_to_db(0.05)), "keyboard step on slider while paused (5%)"):
		return false
	slider.value = 40
	if not _check(is_equal_approx(AudioServer.get_bus_volume_db(0), linear_to_db(0.4)) and _config_value("master_volume") == 40, "volume 40 sets Master gain and persists"):
		return false
	if not _check((overlay.get("volume_value") as Label).text == "40%", "volume readout"):
		return false

	# Movement preset.
	await _click(overlay.get("arrows_button"))
	if not _check(settings.movement_preset == "arrows" and _config_value("movement_preset") == "arrows", "arrow preset applies and persists"):
		return false
	if not _check(_arrow_only_movement(), "arrow preset: movement actions arrow keys only, all other actions unchanged"):
		return false
	if not _check(app.text_for("area_help") == "Arrows move · E interact · Esc map" and app.text_for("battle_help").begins_with("←/→ move · J attack"), "hints follow the preset (en)"):
		return false
	if not _check((overlay.get("current_label") as Label).text.ends_with("Arrows move · E interact · Esc map"), "overlay shows current hint"):
		return false
	if not _check(_overlay_fits(overlay), "overlay layout fits after preset (en)"):
		return false

	# Reset defaults: exact original bindings and gain; language is kept.
	await _click(overlay.get("reset_button"))
	if not _check(_input_map_matches_baseline() and settings.master_volume == 100 and AudioServer.get_bus_volume_db(0) == 0.0 and not AudioServer.is_bus_mute(0), "reset restores exact default bindings and 0 dB"):
		return false
	if not _check(app.language == "en" and _config_value("movement_preset") == "default" and _config_value("master_volume") == 100, "reset persists, keeps language"):
		return false
	if not _check(app.text_for("area_help") == "WASD move · E interact · Esc map", "default hint back"):
		return false
	await _click(overlay.get("arrows_button"))
	slider.value = 40

	# F10 closes and restores the previous pause and focus.
	await _key(KEY_F10)
	if not _check(not settings.is_open() and not paused and root.gui_get_focus_owner() == settings_button, "F10 closes, unpauses, restores title focus"):
		return false
	await _key(KEY_F10)
	if not _check(settings.is_open() and paused, "F10 reopens on title"):
		return false
	await _key(KEY_ESCAPE)
	if not _check(not settings.is_open() and not paused and current_scene == menu, "Esc closes; title stays"):
		return false

	if not await _exploration_guard():
		return false
	if not await _battle_guard():
		return false

	# Tab and Left in the battle step moved overlay focus to the slider and lowered it (UI keys work there).
	settings.set_master_volume(40)
	settings.set_language("en")
	if not _check(_config_value("language") == "en" and _config_value("movement_preset") == "arrows" and _config_value("master_volume") == 40, "prefs left for restart"):
		return false
	if not _check(_prefs_file_is_preferences_only(), "prefs file holds only preferences; no save written"):
		return false
	return true


func _exploration_guard() -> bool:
	app.begin_new_run()
	app.select_destination("scifi.outskirts")
	change_scene_to_file(app.area_scene_path("scifi.outskirts"))
	await _frames(3)
	var area: Node2D = current_scene
	var hero: Sprite2D = area.get("hero")
	hero.position = area.get("npc_position") + Vector2(30, 0)
	await _frames(2)
	var help: Label = area.get("help_label")
	if not _check(help.text == "Arrows move · E interact · Esc map" and help.get_minimum_size().x <= help.size.x + 0.5, "exploration hint shows arrow preset and fits"):
		return false
	if not await _capture("exploration-arrows-hint-en"):
		return false
	await _key(KEY_F10)
	if not _check(settings.is_open() and paused, "F10 opens over exploration"):
		return false
	if not await _capture("exploration-settings-en"):
		return false
	var before := hero.position
	for key in [KEY_E, KEY_RIGHT, KEY_D, KEY_J]:
		_send_key(key, true)
	await _frames(8)
	for key in [KEY_E, KEY_RIGHT, KEY_D, KEY_J]:
		_send_key(key, false)
	await _frames(2)
	if not _check(hero.position == before and not area.get("dialogue_open"), "no movement or interaction under the overlay"):
		return false
	await _key(KEY_ESCAPE)
	await _frames(3)
	if not _check(not settings.is_open() and not paused and current_scene == area, "Esc closes overlay and does not leave the area"):
		return false
	await _key(KEY_E)
	if not _check(area.get("dialogue_open"), "positive control: E interacts after closing"):
		return false
	area.call("_close_dialogue")
	_send_key(KEY_RIGHT, true)
	await _frames(6)
	_send_key(KEY_RIGHT, false)
	await _frames(1)
	if not _check(hero.position.x > before.x, "positive control: arrow movement after closing"):
		return false
	_send_key(KEY_D, true)
	var x_before_d := hero.position.x
	await _frames(6)
	_send_key(KEY_D, false)
	await _frames(1)
	if not _check(hero.position.x == x_before_d, "arrow preset: D no longer moves"):
		return false
	return true


func _battle_guard() -> bool:
	app.begin_new_run()
	app.select_destination("scifi.outskirts")
	app.begin_battle("patrol", Vector2(330, 215))
	change_scene_to_file(BATTLE)
	await _frames(3)
	var battle: Node2D = current_scene
	battle.set("enemy_cooldown", 99.0)
	battle.fighters[0]["x"] = float(battle.get("enemy_x")) - 40.0
	await _frames(2)
	var help: Label = battle.get("help_label")
	if not _check(help.text.begins_with("←/→ move") and help.get_minimum_size().x <= help.size.x + 0.5, "battle hint shows arrow preset and fits"):
		return false

	# Running battle.
	await _key(KEY_F10)
	if not _check(settings.is_open() and paused and not battle.get("paused"), "F10 opens over running battle"):
		return false
	var attacks: int = battle.get("player_attack_count")
	var hp: int = battle.get("enemy_hp")
	var x: float = battle.fighters[0]["x"]
	for key in [KEY_J, KEY_K, KEY_P, KEY_TAB, KEY_T, KEY_LEFT]:
		_send_key(key, true)
	await _frames(8)
	for key in [KEY_J, KEY_K, KEY_P, KEY_TAB, KEY_T, KEY_LEFT]:
		_send_key(key, false)
	await _frames(2)
	if not _check(battle.get("player_attack_count") == attacks and battle.get("enemy_hp") == hp and battle.fighters[0]["x"] == x and not battle.get("paused") and not battle.get("auto_mode") and battle.get("controlled_index") == 0, "no attack/dodge/pause/swap/auto/move under the overlay"):
		return false
	if not await _capture("battle-settings-en"):
		return false
	await _click(settings.overlay.get("zh_button"))
	if not _check(app.language == "zh" and help.text.begins_with("←/→ 移动"), "battle HUD relabels to zh under overlay"):
		return false
	if not _check(_overlay_fits(settings.overlay), "overlay layout fits over battle (zh)"):
		return false
	if not await _capture("battle-settings-zh"):
		return false
	await _key(KEY_F10)
	if not _check(not settings.is_open() and not paused and not battle.get("paused"), "closing returns to the running battle"):
		return false
	await _key(KEY_J)
	await _frames(1)
	if not _check(battle.get("player_attack_count") == attacks + 1, "positive control: J attacks after closing"):
		return false

	# Battle already paused by its own pause menu.
	battle.call("_toggle_pause")
	await _frames(2)
	var focus_before := root.gui_get_focus_owner()
	await _key(KEY_F10)
	if not _check(settings.is_open() and paused, "F10 opens over paused battle"):
		return false
	await _key(KEY_F10)
	if not _check(not settings.is_open() and not paused and battle.get("paused") and (battle.get("pause_overlay") as Control).visible and root.gui_get_focus_owner() == focus_before, "closing keeps the battle pause menu and its focus"):
		return false
	battle.call("_toggle_pause")

	# Tree already paused by someone else stays paused.
	paused = true
	await _key(KEY_F10)
	await _key(KEY_F10)
	if not _check(paused and not settings.is_open(), "previous tree pause restored"):
		return false
	paused = false
	return true


func _phase_restart() -> bool:
	if not _check(settings.load_status == "" and app.language == "en" and settings.master_volume == 40 and settings.movement_preset == "arrows", "prefs applied at startup after restart"):
		return false
	if not _check(is_equal_approx(AudioServer.get_bus_volume_db(0), linear_to_db(0.4)) and not AudioServer.is_bus_mute(0), "restart: Master gain 40%"):
		return false
	if not _check(_arrow_only_movement() and app.text_for("survey_help").begins_with("Arrows move"), "restart: arrow preset bindings and hints"):
		return false
	change_scene_to_file(MENU)
	await _frames(3)
	var menu: Control = current_scene
	await _click(menu.get("settings_button"))
	await _click(settings.overlay.get("reset_button"))
	await _key(KEY_F10)
	if not _check(_input_map_matches_baseline() and AudioServer.get_bus_volume_db(0) == 0.0 and not settings.is_open(), "restart: reset restores exact defaults"):
		return false
	_write_text(settings.config_path, "[settings\nlanguage=\"en\nmaster_volume=?? corrupt\n")
	return true


func _phase_corrupt() -> bool:
	var written := FileAccess.get_file_as_string(settings.config_path)
	if not _check(settings.load_status == "corrupt", "corrupt file detected"):
		return false
	if not _check(_check_defaults("corrupt file"), "corrupt file: exact defaults"):
		return false
	if not _check(written == "[settings\nlanguage=\"en\nmaster_volume=?? corrupt\n", "corrupt file not rewritten at startup"):
		return false
	_write_text(settings.config_path, "[settings]\nlanguage=\"fr\"\nmaster_volume=\"loud\"\nmovement_preset=\"wasd\"\n")
	return true


func _phase_invalid() -> bool:
	if not _check(settings.load_status == "invalid" and _check_defaults("wrong-typed values"), "wrong-typed values: exact defaults"):
		return false
	_write_text(settings.config_path, "[settings]\nmaster_volume=250\n")
	settings.load_preferences()
	if not _check(settings.master_volume == 100 and AudioServer.get_bus_volume_db(0) == 0.0, "volume above range clamps to 100"):
		return false
	_write_text(settings.config_path, "[settings]\nmaster_volume=-30\n")
	settings.load_preferences()
	if not _check(settings.master_volume == 0 and AudioServer.is_bus_mute(0), "volume below range clamps to 0 (muted)"):
		return false
	settings.reset_defaults()
	if not _check(_check_defaults("after reset"), "reset after clamping: exact defaults"):
		return false
	DirAccess.remove_absolute(ProjectSettings.globalize_path(settings.config_path))
	return true


# --- helpers ------------------------------------------------------------------------------------

func _check_defaults(label: String) -> bool:
	return _check(app.language == baseline["language"] and settings.movement_preset == "default" and settings.master_volume == 100, label + ": default language/preset/volume") \
		and _check(AudioServer.get_bus_volume_db(0) == float(baseline["masterVolumeDb"]) and AudioServer.is_bus_mute(0) == bool(baseline["masterMuted"]) and AudioServer.bus_count == int(baseline["busCount"]), label + ": Master bus identical to baseline") \
		and _check(_input_map_matches_baseline(), label + ": every InputMap action identical to baseline")


func _describe(event: InputEvent) -> Dictionary:
	if event is InputEventKey:
		return {"type": "key", "keycode": event.keycode, "physical": event.physical_keycode, "unicode": event.unicode, "mods": event.get_modifiers_mask()}
	if event is InputEventJoypadButton:
		return {"type": "joy_button", "button": event.button_index, "device": event.device}
	if event is InputEventJoypadMotion:
		return {"type": "joy_motion", "axis": event.axis, "value": event.axis_value, "device": event.device}
	if event is InputEventMouseButton:
		return {"type": "mouse", "button": event.button_index}
	return {"type": event.get_class()}


func _current_actions() -> Dictionary:
	var actions := {}
	for action in InputMap.get_actions():
		var events := []
		for event in InputMap.action_get_events(action):
			events.append(_describe(event))
		actions[String(action)] = events
	return JSON.parse_string(JSON.stringify(actions))


func _input_map_matches_baseline() -> bool:
	return _current_actions() == baseline["actions"]


func _arrow_only_movement() -> bool:
	var current := _current_actions()
	var expected: Dictionary = baseline["actions"].duplicate(true)
	var arrows := {"move_left": KEY_LEFT, "move_right": KEY_RIGHT, "move_up": KEY_UP, "move_down": KEY_DOWN}
	for action in arrows:
		var kept := []
		for event in expected[action]:
			if int(event["physical"]) == arrows[action]:
				kept.append(event)
		if kept.size() != 1:
			return false
		expected[action] = kept
	return current == expected


func _config_value(key: String) -> Variant:
	var config := ConfigFile.new()
	if config.load(settings.config_path) != OK:
		return null
	return config.get_value("settings", key, null)


func _prefs_file_is_preferences_only() -> bool:
	var config := ConfigFile.new()
	if config.load(settings.config_path) != OK or config.get_sections() != PackedStringArray(["settings"]):
		return false
	var keys := Array(config.get_section_keys("settings"))
	keys.sort()
	if keys != ["language", "master_volume", "movement_preset", "version"]:
		return false
	var saves := ProjectSettings.globalize_path(SaveStore.root_path)
	if DirAccess.dir_exists_absolute(saves):
		for file in DirAccess.get_files_at(saves):
			var text := FileAccess.get_file_as_string(saves.path_join(file))
			if text.contains("movement_preset") or text.contains("master_volume"):
				return false
	return not DirAccess.dir_exists_absolute(ProjectSettings.globalize_path("user://saves"))


func _overlay_fits(overlay: CanvasLayer) -> bool:
	var panel_rect := Rect2(overlay.PANEL_RECT.position, overlay.PANEL_RECT.size)
	if not Rect2(0, 0, 640, 360).encloses(panel_rect):
		return false
	return _controls_fit(overlay.get("blocker"), panel_rect.grow(0.5))


func _fits_viewport(node: Control) -> bool:
	return _controls_fit(node, Rect2(0, 0, 640, 360))


# Every visible label, button and slider lies inside `bounds`, and no button or one-line label is
# narrower than its text.
func _controls_fit(node: Node, bounds: Rect2) -> bool:
	for child in node.get_children():
		if child is Control and (child as Control).is_visible_in_tree():
			var control := child as Control
			if (control is Label or control is Button or control is HSlider) and not bounds.encloses(control.get_global_rect()):
				push_error("outside bounds: %s %s" % [control.get_path(), control.get_global_rect()])
				return false
			if (control is Button or (control is Label and (control as Label).autowrap_mode == TextServer.AUTOWRAP_OFF)) and control.get_minimum_size().x > control.size.x + 0.5:
				push_error("text clipped: %s min %s size %s" % [control.get_path(), control.get_minimum_size(), control.size])
				return false
			if not _controls_fit(control, bounds):
				return false
	return true


func _frames(count: int) -> void:
	for i in count:
		await process_frame


func _send_key(key: Key, pressed_down: bool) -> void:
	var event := InputEventKey.new()
	event.keycode = key
	event.physical_keycode = key
	event.pressed = pressed_down
	Input.parse_input_event(event)


func _key(key: Key) -> void:
	_send_key(key, true)
	await _frames(2)
	_send_key(key, false)
	await _frames(2)


func _click(control: Control) -> void:
	var at := control.get_global_rect().get_center()
	for down in [true, false]:
		var event := InputEventMouseButton.new()
		event.button_index = MOUSE_BUTTON_LEFT
		event.position = at
		event.global_position = at
		event.pressed = down
		Input.parse_input_event(event)
		await _frames(2)


func _write_text(path: String, text: String) -> void:
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(text)
	file.close()


func _capture(name: String) -> bool:
	if not args.has("capture-dir"):
		return true
	await _frames(2)
	await RenderingServer.frame_post_draw
	var image := root.get_viewport().get_texture().get_image()
	if not _check(image.get_size() == Vector2i(640, 360), "capture %s is 640x360" % name):
		return false
	var file_name := "%s_%s-640_%s.png" % [PREFIX, name, args.get("stamp", "x")]
	var path := String(args["capture-dir"]).path_join(file_name)
	if not _check(image.save_png(path) == OK, "save " + file_name):
		return false
	captures.append({"name": name, "file": file_name, "sha256": FileAccess.get_sha256(path), "language": app.language, "preset": settings.movement_preset, "overlayOpen": settings.is_open()})
	return true


func _check(condition: bool, label: String) -> bool:
	if condition:
		checks += 1
		print("MVP_SETTINGS_CHECK ok %s" % label)
		return true
	push_error("MVP settings check failed: " + label)
	print("MVP_SETTINGS_CHECK FAIL %s" % label)
	quit(1)
	return false


func _fail(message: String) -> void:
	push_error(message)
	print("MVP_SETTINGS_FAIL " + message)
	quit(1)
