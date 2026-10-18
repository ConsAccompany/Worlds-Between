extends SceneTree

# WDC Capitol west v12r2: targeted harness for the sentry-encounter viewport fix (test-only tool, not runtime).
#   Godot --path game --resolution 640x360 -s <this file> -- --wdc-capitol-west-v12r2
#         --wdc12r2-contract=<json> --wdc12r2-out=<dir> --wdc12r2-cap=<dir> --wdc12r2-v8=<approved v8 PNG>
# Real scene, real world-map entry, real input. Per language it walks a real route into the sentry and keeps the
# last DRAWN frame before the encounter triggers (the trigger frame itself is never rendered: the scene change is
# deferred to the end of that frame), plays the real battle (auto mode by the real battle_auto action; sentry HP
# lowered to 12 as a fixture) and returns through the result button. A test-only sprite of the approved v8 south
# still (48 logical px) follows 44 px beside the heroine in every capture. Saves: user://test-saves/wdc-cw-v12r2.

const SCENE := "res://scenes/scifi_exploration_area.tscn"
const BASE_SCRIPT := "res://scripts/scifi_exploration_area.gd"
const V12_SELECTOR := "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12_20261017-235608-66d00477.gd"
const R1_SELECTOR := "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12r1_20261018-034933-23596520.gd"
const R2_SELECTOR := "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12r2_20261018-042200-7c1e5b39.gd"
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
const BATTLE_PATH := "res://scenes/battle_arena.tscn"
const CAP_FMT := "rpg-2-star-ocean-the-second_wdc-capitol-west_%s_unapproved-v12r2_20261018-042200-7c1e5b39.png"
const MOVES := ["move_left", "move_right", "move_up", "move_down"]
const REAL_SAVES := "user://saves"

var app: Node
var v12: GDScript
var r1: GDScript
var r2: GDScript
var contract: Dictionary = {}
var out_dir := ""
var cap_dir := ""
var v8_texture: Texture2D
var v8_sprite: Sprite2D
var report := {"passthrough": {}, "runs": {}, "camera": {}, "curve": [], "saves": {}, "errors": []}


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var contract_path := ""
	var v8_path := ""
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--wdc12r2-contract="):
			contract_path = argument.trim_prefix("--wdc12r2-contract=")
		elif argument.begins_with("--wdc12r2-out="):
			out_dir = argument.trim_prefix("--wdc12r2-out=")
		elif argument.begins_with("--wdc12r2-cap="):
			cap_dir = argument.trim_prefix("--wdc12r2-cap=")
		elif argument.begins_with("--wdc12r2-v8="):
			v8_path = argument.trim_prefix("--wdc12r2-v8=")
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(contract_path))
	if typeof(parsed) != TYPE_DICTIONARY or out_dir == "" or cap_dir == "" or v8_path == "":
		push_error("WDC v12r2 harness: missing arguments")
		quit(2)
		return
	contract = parsed
	Engine.max_fps = 60
	report["saves"]["real_before"] = _tree_hashes(REAL_SAVES)
	SaveStore.root_path = "user://test-saves/wdc-cw-v12r2"
	app = root.get_node("AppState")
	v12 = load(V12_SELECTOR)
	r1 = load(R1_SELECTOR)
	r2 = load(R2_SELECTOR)
	v8_texture = ImageTexture.create_from_image(Image.load_from_file(v8_path))
	report["cmdline_flag_enables_r2"] = r2.r2_enabled()
	report["viewport"] = [root.get_texture().get_width(), root.get_texture().get_height()]
	for feet in 360:
		report["curve"].append([feet, r2.r2_scroll_for(float(feet)), r1.r1_scroll_for(float(feet))])
	await _passthrough()
	for lang in ["zh", "en"]:
		await _language_run(lang)
	await _camera_lane()
	report["saves"]["real_after"] = _tree_hashes(REAL_SAVES)
	report["saves"]["real_unchanged"] = report["saves"]["real_before"] == report["saves"]["real_after"]
	var file := FileAccess.open(out_dir.path_join("wdc12r2-harness-report.json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	print("WDC12R2 HARNESS DONE errors=%d" % report["errors"].size())
	quit(0)


# ------------------------------------------------------------------ helpers
func _tree_hashes(root_dir: String) -> Dictionary:
	var result := {}
	var absolute := ProjectSettings.globalize_path(root_dir)
	if not DirAccess.dir_exists_absolute(absolute):
		return result
	var stack := [""]
	while not stack.is_empty():
		var rel: String = stack.pop_back()
		var dir := DirAccess.open(absolute.path_join(rel))
		if dir == null:
			continue
		for sub in dir.get_directories():
			stack.append(rel.path_join(sub))
		for file in dir.get_files():
			result[rel.path_join(file)] = FileAccess.get_sha256(absolute.path_join(rel).path_join(file))
	return result


func _settle(frames := 4) -> void:
	for index in frames:
		await process_frame


func _release_moves() -> void:
	for action in MOVES:
		Input.action_release(action)


func _press_action(action: String) -> void:
	var down := InputEventAction.new()
	down.action = action
	down.pressed = true
	Input.parse_input_event(down)
	await process_frame
	var up := InputEventAction.new()
	up.action = action
	up.pressed = false
	Input.parse_input_event(up)
	await _settle(3)


func _vec(value) -> Vector2:
	return Vector2(float(value[0]), float(value[1]))


func _fresh_run(destination: String, lang: String) -> void:
	_release_moves()
	app.begin_new_run()
	app.hero_name = "Test"
	app.hero_appearance = "female"
	if app.language != lang:
		app.toggle_language()
	app.select_destination(destination)


func _enter_ruins(lang: String):
	_fresh_run("scifi.ruins", lang)
	change_scene_to_file(MAP_SCENE)
	await _settle(8)
	current_scene._enter_scene("scifi.ruins")
	await _settle(8)
	return current_scene


func _attach_v8(scene) -> void:
	v8_sprite = Sprite2D.new()
	v8_sprite.name = "TestOnlyV8SouthStaticReference"
	v8_sprite.texture = v8_texture
	v8_sprite.centered = false
	v8_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	v8_sprite.scale = Vector2(0.5, 0.5)
	v8_sprite.offset = -Vector2(40.0, 104.0)
	scene.add_child(v8_sprite)
	_follow_v8(scene)


func _follow_v8(scene) -> void:
	# Bottom opaque row level with the heroine's feet, 44 px to one side: the first side whose 22x48 body box
	# clears every visible world label and the sentry (the runtime layout does not know about this test sprite).
	if v8_sprite == null or not is_instance_valid(v8_sprite):
		return
	var feet := Vector2(round(scene.hero.position.x), round(scene.hero.position.y))
	var sides := [-44.0, 44.0] if feet.x > 320.0 else [44.0, -44.0]
	var chosen: float = sides[0]
	for side in sides:
		var box := Rect2(feet.x + side - 14.0, feet.y - 48.0, 24.0, 49.0)
		if box.position.x < 0.0 or box.end.x > 640.0:
			continue
		var clear: bool = not (scene.enemy_visible and box.intersects(Rect2(scene.enemy_position - Vector2(24, 24), Vector2(48, 48))))
		for label in [scene.npc_label, scene.records_label, scene.survey_label, scene.assist_label, scene.enemy_label,
				scene.trace_labels[0], scene.trace_labels[1]]:
			if label.is_visible_in_tree() and box.intersects(Rect2(label.position, label.get_combined_minimum_size())):
				clear = false
		if clear:
			chosen = side
			break
	v8_sprite.position = feet + Vector2(chosen, 1)
	v8_sprite.z_index = scene.hero.z_index


func _state(scene) -> Dictionary:
	var feet := Vector2(round(scene.hero.position.x), round(scene.hero.position.y))
	var scroll: int = scene.v12_scroll
	var state := {"hero": [scene.hero.position.x, scene.hero.position.y], "scroll": scroll,
		"r2_active": scene.get("r2_active"), "enemy_visible": scene.enemy_visible,
		"enemy": [scene.enemy_position.x, scene.enemy_position.y],
		"dist_to_enemy": scene.hero.position.distance_to(scene.enemy_position),
		"hero_canvas_screen_rows": [feet.y - 44 - scroll + 62, feet.y + 3 - scroll + 62],
		"labels": [], "glyphs": []}
	if v8_sprite != null and is_instance_valid(v8_sprite):
		state["v8"] = {"position": [v8_sprite.position.x, v8_sprite.position.y]}
	for entry in [["npc", scene.npc_label], ["records", scene.records_label], ["survey", scene.survey_label],
			["assist", scene.assist_label], ["enemy", scene.enemy_label], ["trace0", scene.trace_labels[0]],
			["trace1", scene.trace_labels[1]]]:
		var label: Label = entry[1]
		if label.is_visible_in_tree():
			var size := label.get_combined_minimum_size()
			state["labels"].append({"name": entry[0], "screen": [label.position.x, label.position.y - scroll + 62, size.x, size.y]})
	for glyph in scene._r1_glyphs():
		var at: Vector2 = glyph["at"]
		state["glyphs"].append({"key": glyph["key"], "screen": [at.x - 15, at.y - 15 - scroll + 62, 30, 30]})
	return state


func _capture(name: String, image: Image = null) -> Dictionary:
	if image == null:
		image = root.get_texture().get_image()
	var error := image.save_png(cap_dir.path_join(CAP_FMT % name))
	if error != OK:
		report["errors"].append("capture failed: " + name)
	return {"file": CAP_FMT % name, "size": [image.get_width(), image.get_height()]}


func _pose(scene, at: Vector2, face: String) -> void:
	scene.hero.position = at
	scene._v12_sync()
	Input.action_press(face)
	await process_frame
	Input.action_release(face)
	await _settle(2)
	scene.hero.position = at
	scene._v12_sync()
	_follow_v8(scene)
	await _settle(3)


func _steer(delta_vec: Vector2) -> void:
	var want := {"move_right": delta_vec.x > 1.2, "move_left": delta_vec.x < -1.2,
		"move_down": delta_vec.y > 1.2, "move_up": delta_vec.y < -1.2}
	for action in want:
		if want[action]:
			Input.action_press(action)
		else:
			Input.action_release(action)


# Walks the route with real input. Frames within `watch` px of the sentry are kept (state + image) so the last
# rendered frame before the encounter is available after the scene changes.
func _walk(scene, route: Array, watch := 0.0) -> Dictionary:
	var frames := 0
	var trail := []
	var last_scroll := -1
	var max_step := 0
	for point in route:
		var target := _vec(point)
		while true:
			if not is_instance_valid(scene) or current_scene != scene:
				_release_moves()
				return {"ok": true, "scene_changed": true, "frames": frames, "trail": trail, "max_scroll_step": max_step}
			var delta_vec: Vector2 = target - scene.hero.position
			if absf(delta_vec.x) <= 1.2 and absf(delta_vec.y) <= 1.2:
				break
			_steer(delta_vec)
			# process_frame fires before this frame's _process; frame_post_draw after it has been drawn, so the
			# state read below belongs to the image grabbed below.
			await process_frame
			await RenderingServer.frame_post_draw
			frames += 1
			if not is_instance_valid(scene) or current_scene != scene:
				continue
			if last_scroll >= 0:
				max_step = maxi(max_step, absi(scene.v12_scroll - last_scroll))
			last_scroll = scene.v12_scroll
			if watch > 0.0 and scene.hero.position.distance_to(scene.enemy_position) < watch:
				trail.append({"state": _state(scene), "image": root.get_texture().get_image()})
				if trail.size() > 3:
					trail.pop_front()
			_follow_v8(scene)
			if frames > 1500:
				_release_moves()
				return {"ok": false, "stuck_at": [scene.hero.position.x, scene.hero.position.y], "frames": frames}
	_release_moves()
	await _settle(2)
	return {"ok": true, "scene_changed": not is_instance_valid(scene) or current_scene != scene, "frames": frames,
		"trail": trail, "max_scroll_step": max_step}


# ------------------------------------------------------------------ flag pass-through (defaults unchanged)
func _probe(destination: String, script_path: String) -> Dictionary:
	_fresh_run(destination, "zh")
	if script_path != "":
		var node: Node = load(SCENE).instantiate()
		node.set_script(load(script_path))
		change_scene_to_node(node)
	else:
		change_scene_to_file(SCENE)
	await _settle(8)
	var scene := current_scene
	var entry := root.get_texture().get_image().get_data()
	var positions := [[scene.hero.position.x, scene.hero.position.y]]
	for action in ["move_right", "move_down", "move_left", "move_up"]:
		Input.action_press(action)
		for step in 4:
			scene._process(0.1)
		Input.action_release(action)
		scene._process(0.1)
		positions.append([scene.hero.position.x, scene.hero.position.y, scene.v12_scroll if scene.get("v12_active") == true else -1])
	await _settle(4)
	return {"script": scene.get_script().resource_path, "entry": entry, "after": root.get_texture().get_image().get_data(),
		"positions": positions, "r2_active": scene.get("r2_active"), "r1_active": scene.get("r1_active"),
		"v12_active": scene.get("v12_active")}


func _compare(a: Dictionary, b: Dictionary) -> Dictionary:
	return {"entry_equal": a["entry"] == b["entry"], "after_equal": a["after"] == b["after"],
		"positions_equal": a["positions"] == b["positions"], "r2_active": a["r2_active"], "r1_active": a["r1_active"],
		"v12_active": a["v12_active"], "script": a["script"], "reference": b["script"]}


func _passthrough() -> void:
	r2.r2_override = 0
	r1.r1_override = 0
	v12.v12_override = 0
	for destination in ["scifi.city", "scifi.outskirts", "scifi.ruins"]:
		report["passthrough"]["off_" + destination] = _compare(await _probe(destination, ""), await _probe(destination, BASE_SCRIPT))
	r1.r1_override = 1
	report["passthrough"]["r1_only_ruins"] = _compare(await _probe("scifi.ruins", ""), await _probe("scifi.ruins", R1_SELECTOR))
	r1.r1_override = 0
	v12.v12_override = 1
	report["passthrough"]["v12_only_ruins"] = _compare(await _probe("scifi.ruins", ""), await _probe("scifi.ruins", V12_SELECTOR))
	r2.r2_override = -1
	r1.r1_override = -1
	v12.v12_override = -1


# ------------------------------------------------------------------ per-language run
func _language_run(lang: String) -> void:
	var run := {}
	var scene = await _enter_ruins(lang)
	_attach_v8(scene)
	await _settle(3)
	run["entry"] = _capture("rt640-%s-entry-v8ref" % lang)
	run["entry"]["state"] = _state(scene)
	# Actual interaction route into the sentry: zh = the v12 contract's sentry route (north-west approach),
	# en = straight down the x 566 column (pure north approach, the worst case for the camera).
	var route: Array = [contract["spawn"]] + contract["routes"]["sentry"] if lang == "zh" else contract["north_column_route"]
	var walked := await _walk(scene, route, 34.0)
	var pre: Dictionary = walked["trail"].back() if not walked["trail"].is_empty() else {}
	run["approach"] = {"walk_ok": walked["ok"], "scene_changed": walked["scene_changed"], "frames": walked["frames"],
		"max_scroll_step": walked["max_scroll_step"], "trail_states": walked["trail"].map(func(t): return t["state"])}
	if not pre.is_empty():
		run["pre_trigger"] = _capture("rt640-%s-sentry-pre-trigger" % lang, pre["image"])
		run["pre_trigger"]["state"] = pre["state"]
	await _settle(6)
	var battle = current_scene
	var encounter := {"battle_scene": battle.scene_file_path, "battle_enemy": app.battle_enemy_id,
		"return_position": [app.battle_return_position.x, app.battle_return_position.y]}
	if battle.scene_file_path != BATTLE_PATH:
		report["errors"].append("%s: battle did not open" % lang)
		run["encounter"] = encounter
		report["runs"][lang] = run
		return
	encounter["enemy_hp_start"] = battle.enemy_hp
	battle.enemy_hp = mini(battle.enemy_hp, 12)
	await _press_action("battle_auto")
	encounter["auto_mode_by_input"] = battle.auto_mode
	var waited := 0
	while not battle.battle_finished and waited < 1800:
		await process_frame
		waited += 1
	encounter["battle_won"] = battle.battle_won
	encounter["enemy_hp_end"] = battle.enemy_hp
	encounter["flags"] = [app.returning_from_battle, app.enemy_cleared_for_return]
	encounter["result_button_focused"] = battle.result_button.has_focus()
	await _settle(10)
	await _press_action("ui_accept")
	await _settle(10)
	var return_position: Vector2 = Vector2(encounter["return_position"][0], encounter["return_position"][1])
	scene = current_scene
	encounter["scene_after_result"] = scene.scene_file_path
	run["encounter"] = encounter
	if scene.get("r2_active") == true:
		_attach_v8(scene)
		await _settle(3)
		run["battle_return"] = _capture("rt640-%s-battle-return-v8ref" % lang)
		run["battle_return"]["state"] = _state(scene)
		run["battle_return"]["equals_return_texel"] = scene.hero.position == return_position.round()
		run["battle_return"]["expected_scroll"] = r2.r2_scroll_for(scene.hero.position.y)
		run["battle_return"]["camera_current"] = scene.v12_camera.is_current()
		# End of the walk: the south exit lane at full scroll.
		await _pose(scene, _vec(contract["south_end"]), "move_down")
		run["south_end"] = _capture("rt640-%s-south-end-v8ref" % lang)
		run["south_end"]["state"] = _state(scene)
	else:
		report["errors"].append("%s: battle result did not return to the r2 scene" % lang)
	report["runs"][lang] = run


# ------------------------------------------------------------------ camera lane (real input, both directions)
func _camera_lane() -> void:
	var scene = await _enter_ruins("zh")
	var from := _vec(contract["camera_lane"][0])
	var to := _vec(contract["camera_lane"][1])
	scene.hero.position = from
	scene._v12_sync()
	await _settle(2)
	var samples := []
	for leg in [["move_down", to.y], ["move_up", from.y]]:
		Input.action_press(leg[0])
		var guard := 0
		while guard < 600:
			await process_frame
			guard += 1
			samples.append([leg[0], scene.hero.position.y, scene.v12_scroll])
			if (leg[0] == "move_down" and scene.hero.position.y >= float(leg[1]) - 0.5) or (leg[0] == "move_up" and scene.hero.position.y <= float(leg[1]) + 0.5):
				break
		Input.action_release(leg[0])
		await _settle(2)
	report["camera"] = {"samples": samples}
