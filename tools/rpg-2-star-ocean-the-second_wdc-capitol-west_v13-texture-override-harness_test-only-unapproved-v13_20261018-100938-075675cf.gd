extends SceneTree

# WDC Capitol west v13 ruin/material pass: TEST-ONLY texture-override harness (not runtime, nothing in game/ refers to it).
#   Godot --path game --resolution 640x360 -s <this file> -- --wdc-capitol-west-v12r2 --wdc13-mode=v13|v12ref
#         --wdc13-tex=<abs v13 rt-base PNG> --wdc13-contract=<json> --wdc13-out=<dir> --wdc13-cap=<dir>
# Mode v13: before any scene loads, an ImageTexture of the v13 rt-base takes over the v12 rt-base res:// path in
# memory, so the real v12r2 selector (real scene, real HUD, real input, real battle) draws the v13 art without any
# file in game/ changing. Mode v12ref runs the identical script without the override, as the byte reference.
# Per language: world-map entry, a real-input traversal under the breach, records prompt + real interact,
# occlusion, and a real-input walk into the sentry, the real battle (auto mode by the real battle_auto action;
# sentry HP lowered to 12 as a fixture) and the return through the result button.
# Saves go to user://test-saves/wdc-cw-v13; the real user://saves is hashed before and after.

const SCENE := "res://scenes/scifi_exploration_area.tscn"
const BASE_SCRIPT := "res://scripts/scifi_exploration_area.gd"
const V12_SELECTOR := "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12_20261017-235608-66d00477.gd"
const R1_SELECTOR := "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12r1_20261018-034933-23596520.gd"
const R2_SELECTOR := "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12r2_20261018-042200-7c1e5b39.gd"
const V12_BASE_RES := "res://assets/environments/candidates/wdc-cw-v12_20261017-235608-66d00477/rpg-2-star-ocean-the-second_wdc-capitol-west_rt-base_unapproved-v12_20261017-235608-66d00477.png"
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
const BATTLE_PATH := "res://scenes/battle_arena.tscn"
const CAP_FMT := "rpg-2-star-ocean-the-second_wdc-capitol-west_%s_%s_20261018-100938-075675cf.png"
const MOVES := ["move_left", "move_right", "move_up", "move_down"]
const REAL_SAVES := "user://saves"

var app: Node
var v12: GDScript
var r1: GDScript
var r2: GDScript
var mode := ""
var tag := ""
var contract: Dictionary = {}
var out_dir := ""
var cap_dir := ""
var override_texture: ImageTexture
var override_sha := ""
var report := {"override": {}, "passthrough": {}, "runs": {}, "saves": {}, "errors": []}


func _initialize() -> void:
	var tex_path := ""
	var contract_path := ""
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--wdc13-mode="):
			mode = argument.trim_prefix("--wdc13-mode=")
		elif argument.begins_with("--wdc13-tex="):
			tex_path = argument.trim_prefix("--wdc13-tex=")
		elif argument.begins_with("--wdc13-contract="):
			contract_path = argument.trim_prefix("--wdc13-contract=")
		elif argument.begins_with("--wdc13-out="):
			out_dir = argument.trim_prefix("--wdc13-out=")
		elif argument.begins_with("--wdc13-cap="):
			cap_dir = argument.trim_prefix("--wdc13-cap=")
	tag = "test-only-%s" % ("v13" if mode == "v13" else "v12ref")
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(contract_path))
	if typeof(parsed) != TYPE_DICTIONARY or out_dir == "" or cap_dir == "" or not mode in ["v13", "v12ref"]:
		push_error("WDC v13 harness: missing arguments")
		quit(2)
		return
	contract = parsed
	report["mode"] = mode
	report["override"]["v12_base_cached_before"] = ResourceLoader.has_cached(V12_BASE_RES)
	if mode == "v13":
		# Must happen before anything loads the v12 rt-base: the selector's load() then returns this texture.
		var image := Image.load_from_file(tex_path)
		if image == null or image.is_empty() or image.get_size() != Vector2i(640, 360):
			push_error("WDC v13 harness: cannot load the v13 rt-base")
			quit(2)
			return
		override_texture = ImageTexture.create_from_image(image)
		override_texture.take_over_path(V12_BASE_RES)
		override_sha = _sha(image.get_data())
		report["override"]["installed"] = ResourceLoader.has_cached(V12_BASE_RES)
		report["override"]["image_sha256"] = override_sha
		print("WDC13_OVERRIDE_INSTALLED path=%s" % V12_BASE_RES)
	call_deferred("_run")


func _run() -> void:
	Engine.max_fps = 60
	report["saves"]["real_before"] = _tree_hashes(REAL_SAVES)
	SaveStore.root_path = "user://test-saves/wdc-cw-v13"
	app = root.get_node("AppState")
	v12 = load(V12_SELECTOR)
	r1 = load(R1_SELECTOR)
	r2 = load(R2_SELECTOR)
	report["cmdline_flag_enables_r2"] = r2.r2_enabled()
	report["viewport"] = [root.get_texture().get_width(), root.get_texture().get_height()]
	await _passthrough()
	for lang in ["zh", "en"]:
		await _language_run(lang)
	report["saves"]["real_after"] = _tree_hashes(REAL_SAVES)
	report["saves"]["real_unchanged"] = report["saves"]["real_before"] == report["saves"]["real_after"]
	var file := FileAccess.open(out_dir.path_join("wdc13-harness-report-%s.json" % mode), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	print("WDC13 HARNESS DONE mode=%s errors=%d" % [mode, report["errors"].size()])
	quit(0)


# ------------------------------------------------------------------ helpers
func _sha(data: PackedByteArray) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(data)
	return ctx.finish().hex_encode()


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


func _base_layer(scene) -> Dictionary:
	# The selector's base Sprite2D: which texture object it draws, and the bytes of that texture's image.
	var sprite: Sprite2D = scene.get_node_or_null("WdcV12_rt_base")
	if sprite == null:
		return {"found": false}
	var texture := sprite.texture
	return {"found": true, "is_override": texture == override_texture and override_texture != null,
		"class": texture.get_class(), "resource_path": texture.resource_path,
		"image_sha256": _sha(texture.get_image().get_data()), "z_index": sprite.z_index}


func _state(scene) -> Dictionary:
	var feet := Vector2(round(scene.hero.position.x), round(scene.hero.position.y))
	var scroll: int = scene.v12_scroll
	var state := {"hero": [scene.hero.position.x, scene.hero.position.y], "scroll": scroll,
		"r2_active": scene.get("r2_active"), "enemy_visible": scene.enemy_visible,
		"records_checked": app.ji_records_checked,
		"hero_canvas_screen_rows": [feet.y - 44 - scroll + 62, feet.y + 3 - scroll + 62],
		"feedback": scene.feedback_label.text if scene.get("feedback_label") != null else "",
		"labels": [], "glyphs": []}
	for entry in [["npc", scene.npc_label], ["records", scene.records_label], ["survey", scene.survey_label],
			["assist", scene.assist_label], ["enemy", scene.enemy_label], ["trace0", scene.trace_labels[0]],
			["trace1", scene.trace_labels[1]]]:
		var label: Label = entry[1]
		if label.is_visible_in_tree():
			var size := label.get_combined_minimum_size()
			state["labels"].append({"name": entry[0], "text": label.text,
				"screen": [label.position.x, label.position.y - scroll + 62, size.x, size.y]})
	for glyph in scene._r1_glyphs():
		var at: Vector2 = glyph["at"]
		state["glyphs"].append({"key": glyph["key"], "screen": [at.x - 15, at.y - 15 - scroll + 62, 30, 30]})
	return state


func _capture(name: String, scene) -> Dictionary:
	var image := root.get_texture().get_image()
	var file := CAP_FMT % [name, tag]
	var error := image.save_png(cap_dir.path_join(file))
	if error != OK:
		report["errors"].append("capture failed: " + name)
	return {"file": file, "size": [image.get_width(), image.get_height()], "state": _state(scene),
		"base_layer": _base_layer(scene)}


func _pose(scene, at: Vector2, face: String) -> void:
	scene.hero.position = at
	scene._v12_sync()
	Input.action_press(face)
	await process_frame
	Input.action_release(face)
	await _settle(2)
	scene.hero.position = at
	scene._v12_sync()
	await _settle(3)


func _steer(delta_vec: Vector2) -> void:
	var want := {"move_right": delta_vec.x > 1.2, "move_left": delta_vec.x < -1.2,
		"move_down": delta_vec.y > 1.2, "move_up": delta_vec.y < -1.2}
	for action in want:
		if want[action]:
			Input.action_press(action)
		else:
			Input.action_release(action)


# Real-input walk. `keep_x` > 0 keeps the first drawn frame whose feet are at or west of that column (the
# traversal shot under the breach); the image and state are read after frame_post_draw so they belong together.
func _walk(scene, route: Array, keep_x := -1.0) -> Dictionary:
	var frames := 0
	var kept := {}
	for point in route:
		var target := _vec(point)
		while true:
			if not is_instance_valid(scene) or current_scene != scene:
				_release_moves()
				return {"ok": true, "scene_changed": true, "frames": frames, "kept": kept}
			var delta_vec: Vector2 = target - scene.hero.position
			if absf(delta_vec.x) <= 1.2 and absf(delta_vec.y) <= 1.2:
				break
			_steer(delta_vec)
			await process_frame
			await RenderingServer.frame_post_draw
			frames += 1
			if not is_instance_valid(scene) or current_scene != scene:
				continue
			if keep_x > 0.0 and kept.is_empty() and scene.hero.position.x <= keep_x:
				kept = {"image": root.get_texture().get_image(), "state": _state(scene), "base_layer": _base_layer(scene)}
			if frames > 1500:
				_release_moves()
				return {"ok": false, "stuck_at": [scene.hero.position.x, scene.hero.position.y], "frames": frames}
	_release_moves()
	await _settle(2)
	return {"ok": true, "scene_changed": not is_instance_valid(scene) or current_scene != scene, "frames": frames,
		"kept": kept}


# ------------------------------------------------------------------ flag pass-through with the override installed
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
		positions.append([scene.hero.position.x, scene.hero.position.y])
	await _settle(4)
	return {"script": scene.get_script().resource_path, "entry": _sha(entry),
		"after": _sha(root.get_texture().get_image().get_data()), "positions": positions,
		"v12_active": scene.get("v12_active")}


func _passthrough() -> void:
	# All three opt-in flags forced off: the shared scene must equal the base script for every destination,
	# whether or not the v13 texture is sitting in the resource cache.
	r2.r2_override = 0
	r1.r1_override = 0
	v12.v12_override = 0
	for destination in ["scifi.city", "scifi.outskirts", "scifi.ruins"]:
		var a: Dictionary = await _probe(destination, "")
		var b: Dictionary = await _probe(destination, BASE_SCRIPT)
		report["passthrough"]["off_" + destination] = {"entry_equal": a["entry"] == b["entry"],
			"after_equal": a["after"] == b["after"], "positions_equal": a["positions"] == b["positions"],
			"v12_active": a["v12_active"], "entry_sha256": a["entry"], "after_sha256": a["after"]}
	r2.r2_override = -1
	r1.r1_override = -1
	v12.v12_override = -1


# ------------------------------------------------------------------ per-language run
func _language_run(lang: String) -> void:
	var run := {}
	var scene = await _enter_ruins(lang)
	await _settle(3)
	run["entry"] = _capture("rt640-%s-entry" % lang, scene)
	# Real-input traversal west along the walk under the breach (records route, then on toward Ji Cheng).
	var walked := await _walk(scene, contract["routes"]["records"] + contract["routes"]["npc"] + contract["routes"]["trace0"], float(contract["traversal_keep_x"]))
	run["traversal_walk"] = {"ok": walked["ok"], "frames": walked["frames"]}
	if not walked["kept"].is_empty():
		var file := CAP_FMT % ["rt640-%s-traversal" % lang, tag]
		walked["kept"]["image"].save_png(cap_dir.path_join(file))
		run["traversal"] = {"file": file, "state": walked["kept"]["state"], "base_layer": walked["kept"]["base_layer"]}
	else:
		report["errors"].append("%s: no traversal frame" % lang)
	run["traversal_end"] = _capture("rt640-%s-traversal-end" % lang, scene)
	# Records: stand at the interaction pose, prompt, then the real interact action.
	var poses: Dictionary = contract["review_poses"]
	await _pose(scene, _vec(poses["interaction"]["at"]), "move_left")
	run["records_prompt"] = _capture("rt640-%s-records-prompt" % lang, scene)
	await _press_action("interact")
	run["records_checked"] = _capture("rt640-%s-records-checked" % lang, scene)
	await _pose(scene, _vec(poses["occlusion"]["at"]), "move_up")
	run["occlusion"] = _capture("rt640-%s-occlusion" % lang, scene)
	await _pose(scene, _vec(poses["breach_view"]["at"]), "move_up")
	run["breach_view"] = _capture("rt640-%s-breach-view" % lang, scene)
	# Sentry: real walk from the spawn along the contract's sentry route into the encounter.
	await _pose(scene, _vec(contract["spawn"]), "move_down")
	var to_sentry := await _walk(scene, contract["routes"]["sentry"])
	run["approach"] = {"walk_ok": to_sentry["ok"], "scene_changed": to_sentry["scene_changed"], "frames": to_sentry["frames"]}
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
	encounter["flags"] = [app.returning_from_battle, app.enemy_cleared_for_return]
	encounter["result_button_focused"] = battle.result_button.has_focus()
	await _settle(10)
	await _press_action("ui_accept")
	await _settle(10)
	var return_position := Vector2(encounter["return_position"][0], encounter["return_position"][1])
	scene = current_scene
	encounter["scene_after_result"] = scene.scene_file_path
	run["encounter"] = encounter
	if scene.get("r2_active") == true:
		await _settle(3)
		run["battle_return"] = _capture("rt640-%s-battle-return" % lang, scene)
		run["battle_return"]["equals_return_texel"] = scene.hero.position == return_position.round()
		run["battle_return"]["expected_scroll"] = r2.r2_scroll_for(scene.hero.position.y)
		run["battle_return"]["camera_current"] = scene.v12_camera.is_current()
	else:
		report["errors"].append("%s: battle result did not return to the r2 scene" % lang)
	report["runs"][lang] = run
