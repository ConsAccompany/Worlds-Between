extends SceneTree

# WDC Capitol west v12r1: capture + probe harness for the REAL exploration scene (test-only tool, not runtime).
# Run windowed (rendering needed) from the v12r1 check tool:
#   Godot --path game [--resolution 640x360] -s <this file> -- --wdc-capitol-west-v12r1
#         --wdc12r1-contract=<r1 contract json> --wdc12r1-out=<probe dir> --wdc12r1-cap=<capture dir>
#         --wdc12r1-v8=<abs path of the approved v8 south PNG> [--wdc12r1-mode=full|v8hd]
# It enters Washington through the world map's own _enter_scene(), moves with the real input actions, interacts
# through Input.parse_input_event, plays the real battle (auto mode toggled by the real battle_auto action; the
# sentry's HP is lowered as a test fixture so the run is short) and returns through the battle's own result
# button. The v8 reference sprite is added by this harness only (never by runtime code). Saves go only under
# user://test-saves/wdc-cw-v12r1; the real user://saves tree is hashed before and after.

const SCENE := "res://scenes/scifi_exploration_area.tscn"
const BASE_SCRIPT := "res://scripts/scifi_exploration_area.gd"
const V12_SELECTOR := "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12_20261017-235608-66d00477.gd"
const R1_SELECTOR := "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12r1_20261018-034933-23596520.gd"
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
const CAP_FMT := "rpg-2-star-ocean-the-second_wdc-capitol-west_%s_unapproved-v12r1_20261018-034933-23596520.png"
const MOVES := ["move_left", "move_right", "move_up", "move_down"]
const TEST_SAVES := "user://test-saves/wdc-cw-v12r1"
const REAL_SAVES := "user://saves"
const FIXTURE_ENEMY_HP := 12

var app: Node
var v12: GDScript
var r1: GDScript
var contract: Dictionary = {}
var out_dir := ""
var cap_dir := ""
var v8_path := ""
var mode := "full"
var report := {"captures": {}, "default_runtime": {}, "v12_passthrough": {}, "flow": {}, "sweeps": [], "camera": {},
	"layout": {}, "probes": {}, "saves": {}, "errors": []}
var monitor := {}


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var contract_path := ""
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--wdc12r1-contract="):
			contract_path = argument.trim_prefix("--wdc12r1-contract=")
		elif argument.begins_with("--wdc12r1-out="):
			out_dir = argument.trim_prefix("--wdc12r1-out=")
		elif argument.begins_with("--wdc12r1-cap="):
			cap_dir = argument.trim_prefix("--wdc12r1-cap=")
		elif argument.begins_with("--wdc12r1-v8="):
			v8_path = argument.trim_prefix("--wdc12r1-v8=")
		elif argument.begins_with("--wdc12r1-mode="):
			mode = argument.trim_prefix("--wdc12r1-mode=")
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(contract_path))
	if typeof(parsed) != TYPE_DICTIONARY or out_dir == "" or cap_dir == "" or v8_path == "":
		push_error("WDC v12r1 harness: missing contract or output arguments")
		quit(2)
		return
	contract = parsed
	Engine.max_fps = 60
	report["saves"]["real_before"] = _tree_hashes(REAL_SAVES)
	SaveStore.root_path = TEST_SAVES
	app = root.get_node("AppState")
	v12 = load(V12_SELECTOR)
	r1 = load(R1_SELECTOR)
	report["mode"] = mode
	report["cmdline_flag_enables_r1"] = r1.r1_enabled()
	report["viewport_size"] = [root.get_visible_rect().size.x, root.get_visible_rect().size.y]
	report["window_texture_size"] = [root.get_texture().get_width(), root.get_texture().get_height()]
	if mode == "v8hd":
		for lang in ["zh", "en"]:
			await _v8_pair(lang, "rt1280")
	else:
		await _default_runtime()
		await _v12_passthrough()
		for lang in ["zh", "en"]:
			await _captures(lang)
		await _camera_trace()
		await _layout_sweep()
		await _flow()
		await _sweeps()
		await _probes()
	report["saves"]["real_after"] = _tree_hashes(REAL_SAVES)
	report["saves"]["real_unchanged"] = report["saves"]["real_before"] == report["saves"]["real_after"]
	report["saves"]["test_root"] = TEST_SAVES
	_write_report()
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
			var path := absolute.path_join(rel).path_join(file)
			result[rel.path_join(file)] = FileAccess.get_sha256(path)
	return result


func _fresh_run(destination: String, lang: String) -> void:
	_release_moves()
	app.begin_new_run()
	app.hero_name = "Test"
	app.hero_appearance = "female"
	if app.language != lang:
		app.toggle_language()
	app.select_destination(destination)


func _settle(frames := 4) -> void:
	for index in frames:
		await process_frame


func _action_event(action: String, pressed := true) -> InputEventAction:
	var event := InputEventAction.new()
	event.action = action
	event.pressed = pressed
	return event


func _press_action(action: String) -> void:
	Input.parse_input_event(_action_event(action, true))
	await process_frame
	Input.parse_input_event(_action_event(action, false))
	await _settle(3)


func _release_moves() -> void:
	for action in MOVES:
		Input.action_release(action)


func _vec(value) -> Vector2:
	return Vector2(float(value[0]), float(value[1]))


func _enter_ruins(lang: String) -> Node:
	_fresh_run("scifi.ruins", lang)
	change_scene_to_file(MAP_SCENE)
	await _settle(8)
	current_scene._enter_scene("scifi.ruins")
	await _settle(8)
	return current_scene


func _to_screen(scene, rect: Rect2) -> Rect2:
	return Rect2(rect.position + Vector2(0, 62 - scene.v12_scroll), rect.size)


func _label_rect(label: Label) -> Rect2:
	return Rect2(label.position, label.get_combined_minimum_size())


func _hero_rect(scene) -> Rect2:
	var feet := Vector2(round(scene.hero.position.x), round(scene.hero.position.y))
	return Rect2(feet.x - 16, feet.y - 44, 32, 48)


func _layout_state(scene) -> Dictionary:
	# Screen-space rects of every visible world label and drawn glyph, plus the checks this run cares about.
	var band: Vector2 = scene._r1_band()
	var labels := []
	var names := [["npc", scene.npc_label], ["records", scene.records_label], ["survey", scene.survey_label],
		["assist", scene.assist_label], ["enemy", scene.enemy_label], ["trace0", scene.trace_labels[0]],
		["trace1", scene.trace_labels[1]]]
	for entry in names:
		var label: Label = entry[1]
		if label.is_visible_in_tree():
			var rect := _label_rect(label)
			labels.append({"name": entry[0], "text": label.text, "world": [rect.position.x, rect.position.y, rect.size.x, rect.size.y],
				"screen": _rect_list(_to_screen(scene, rect))})
	var glyphs := []
	for glyph in scene._r1_glyphs():
		var at: Vector2 = glyph["at"]
		var rect := Rect2(at - Vector2(15, 15), Vector2(30, 30))
		glyphs.append({"key": glyph["key"], "at": [at.x, at.y], "world_anchor": [glyph["world"].x, glyph["world"].y],
			"pinned": glyph["pinned"], "screen": _rect_list(_to_screen(scene, rect))})
	var hero_screen := _to_screen(scene, _hero_rect(scene))
	var overlaps := []
	var label_glyph := []
	var label_hero := []
	var outside := []
	for i in labels.size():
		var a := _rect_from(labels[i]["screen"])
		if a.position.y < 62 or a.end.y > 318 or a.position.x < 0 or a.end.x > 640:
			outside.append(labels[i]["name"])
		for j in range(i + 1, labels.size()):
			if a.intersects(_rect_from(labels[j]["screen"])):
				overlaps.append([labels[i]["name"], labels[j]["name"]])
		for glyph in glyphs:
			if a.intersects(_rect_from(glyph["screen"])):
				label_glyph.append([labels[i]["name"], glyph["key"]])
		if a.intersects(hero_screen):
			label_hero.append(labels[i]["name"])
	var glyph_outside := []
	for glyph in glyphs:
		var g := _rect_from(glyph["screen"])
		if g.position.y < 62 or g.end.y > 318 or g.position.x < 0 or g.end.x > 640:
			glyph_outside.append(glyph["key"])
	return {"scroll": scene.v12_scroll, "band": [band.x, band.y], "hero": [scene.hero.position.x, scene.hero.position.y],
		"hero_screen": _rect_list(hero_screen), "labels": labels, "glyphs": glyphs, "label_overlaps": overlaps,
		"label_glyph_overlaps": label_glyph, "label_hero_overlaps": label_hero, "labels_outside_band": outside,
		"glyphs_outside_band": glyph_outside}


func _rect_list(rect: Rect2) -> Array:
	return [rect.position.x, rect.position.y, rect.size.x, rect.size.y]


func _rect_from(values: Array) -> Rect2:
	return Rect2(float(values[0]), float(values[1]), float(values[2]), float(values[3]))


func _scene_probe(scene) -> Dictionary:
	var hero: Sprite2D = scene.hero
	var probe := {
		"script": scene.get_script().resource_path,
		"v12_active": scene.get("v12_active"),
		"r1_active": scene.get("r1_active"),
		"scroll": scene.get("v12_scroll"),
		"hero": [hero.position.x, hero.position.y],
		"hero_texture": hero.texture.resource_path,
		"hero_z": hero.z_index,
		"language": app.language,
		"feedback": scene.feedback_label.text,
		"title": scene.title_label.text,
		"hint": scene.hint_label.text,
		"hint_font_size": scene.hint_label.get_theme_font_size("font_size"),
		"hint_end_x": scene.hint_label.position.x + scene.hint_label.get_theme_font("font").get_string_size(scene.hint_label.text, HORIZONTAL_ALIGNMENT_LEFT, -1, scene.hint_label.get_theme_font_size("font_size")).x,
		"save_x": scene.save_button.position.x,
		"enemy_visible": scene.enemy_visible,
		"enemy": [scene.enemy_position.x, scene.enemy_position.y],
		"dialogue_open": scene.dialogue_open,
		"ji_records_checked": app.ji_records_checked,
	}
	if scene.field_npc != null:
		probe["npc"] = [scene.field_npc.position.x, scene.field_npc.position.y]
		probe["npc_visible"] = scene.field_npc.visible
	if scene.get("r1_active"):
		probe["layout"] = _layout_state(scene)
	return probe


func _capture(name: String) -> Dictionary:
	var image := root.get_texture().get_image()
	var path := cap_dir.path_join(CAP_FMT % name)
	var error := image.save_png(path)
	if error != OK:
		report["errors"].append("capture failed: " + name)
	return {"file": CAP_FMT % name, "size": [image.get_width(), image.get_height()], "saved": error == OK}


func _pose(scene, pose: Dictionary) -> void:
	# Face with the real input action for one frame, then stand exactly on the pose (idle frame).
	var face := {"north": "move_up", "south": "move_down", "east": "move_right", "west": "move_left"}
	var at := _vec(pose["at"])
	scene.hero.position = at
	scene._v12_sync()
	Input.action_press(face[pose["face"]])
	await process_frame
	Input.action_release(face[pose["face"]])
	await _settle(2)
	scene.hero.position = at
	scene._v12_sync()
	await _settle(3)


# ------------------------------------------------------------------ default runtime (both flags off)
func _default_runtime() -> void:
	r1.r1_override = 0
	v12.v12_override = 0
	for destination in ["scifi.city", "scifi.outskirts", "scifi.ruins"]:
		var with_selector: Dictionary = await _default_probe(destination, "")
		var with_base: Dictionary = await _default_probe(destination, BASE_SCRIPT)
		report["default_runtime"][destination] = {
			"selector_script": with_selector["script"],
			"base_script": with_base["script"],
			"selector_v12_active": with_selector["v12_active"],
			"selector_r1_active": with_selector["r1_active"],
			"entry_image_equal": with_selector["entry"] == with_base["entry"],
			"after_input_image_equal": with_selector["after"] == with_base["after"],
			"positions_equal": with_selector["positions"] == with_base["positions"],
			"texts_equal": with_selector["texts"] == with_base["texts"],
			"state_equal": with_selector["state"] == with_base["state"],
		}
	r1.r1_override = -1
	v12.v12_override = -1


# v12 flag only: the r1 selector must behave exactly like the unamended v12 selector.
func _v12_passthrough() -> void:
	r1.r1_override = 0
	v12.v12_override = 1
	var with_selector: Dictionary = await _default_probe("scifi.ruins", "")
	var with_v12: Dictionary = await _default_probe("scifi.ruins", V12_SELECTOR)
	report["v12_passthrough"] = {
		"selector_script": with_selector["script"], "v12_script": with_v12["script"],
		"selector_v12_active": with_selector["v12_active"], "selector_r1_active": with_selector["r1_active"],
		"entry_image_equal": with_selector["entry"] == with_v12["entry"],
		"after_input_image_equal": with_selector["after"] == with_v12["after"],
		"positions_equal": with_selector["positions"] == with_v12["positions"],
		"texts_equal": with_selector["texts"] == with_v12["texts"],
		"state_equal": with_selector["state"] == with_v12["state"],
		"spawn": with_selector["positions"][0],
	}
	r1.r1_override = -1
	v12.v12_override = -1


func _default_probe(destination: String, script_path: String) -> Dictionary:
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
	if destination == "scifi.ruins":
		scene.hero.position = Vector2(320, 250)
		scene._unhandled_input(_action_event("interact"))
	await _settle(4)
	var after := root.get_texture().get_image().get_data()
	var texts := [scene.title_label.text, scene.hint_label.text, scene.feedback_label.text,
		scene.hint_label.get_theme_font_size("font_size"), scene.npc_label.position, scene.survey_label.position,
		scene.hint_label.position]
	var state := [app.ji_records_checked, app.machine_observed, app.field_traces.size(), scene.enemy_visible]
	return {"script": scene.get_script().resource_path, "v12_active": scene.get("v12_active"),
		"r1_active": scene.get("r1_active"), "entry": entry, "after": after, "positions": positions,
		"texts": str(texts), "state": state}


# ------------------------------------------------------------------ review captures
func _captures(lang: String) -> void:
	var scene = await _enter_ruins(lang)
	var poses: Dictionary = contract["review_poses"]
	var captures := {}
	captures["entry"] = _capture("rt640-%s-entry" % lang)
	captures["entry"]["probe"] = _scene_probe(scene)
	await _pose(scene, poses["interaction"])
	captures["interaction_prompt"] = _capture("rt640-%s-records-prompt" % lang)
	captures["interaction_prompt"]["probe"] = _scene_probe(scene)
	await _press_action("interact")
	captures["interaction"] = _capture("rt640-%s-records-checked" % lang)
	captures["interaction"]["probe"] = _scene_probe(scene)
	await _pose(scene, poses["occlusion"])
	captures["occlusion"] = _capture("rt640-%s-occlusion" % lang)
	captures["occlusion"]["probe"] = _scene_probe(scene)
	await _pose(scene, poses["patrol_bypass"])
	captures["patrol_bypass"] = _capture("rt640-%s-patrol-bypass" % lang)
	captures["patrol_bypass"]["probe"] = _scene_probe(scene)
	await _pose(scene, poses["strata_near"])
	captures["strata_near"] = _capture("rt640-%s-strata-near" % lang)
	captures["strata_near"]["probe"] = _scene_probe(scene)
	report["captures"][lang] = captures
	await _v8_pair(lang, "rt640")


# Approved female v8 south STATIC frame (one still, 48 logical px) added beside the runtime heroine, test-only.
func _v8_pair(lang: String, prefix: String) -> void:
	var scene = await _enter_ruins(lang)
	var poses: Dictionary = contract["review_poses"]
	await _pose(scene, poses["entry"])
	var plain := _capture("%s-%s-v8ref-off" % [prefix, lang])
	var image := Image.load_from_file(v8_path)
	var sprite := Sprite2D.new()
	sprite.name = "TestOnlyV8SouthStaticReference"
	sprite.texture = ImageTexture.create_from_image(image)
	sprite.centered = false
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.scale = Vector2(0.5, 0.5)
	var anchor: Array = contract["v8_reference"]["foot_anchor_px"]
	sprite.offset = -Vector2(float(anchor[0]), float(anchor[1]) + 1.0)
	var feet := Vector2(round(scene.hero.position.x), round(scene.hero.position.y))
	sprite.position = feet + _vec(contract["v8_reference"]["offset_from_hero"]) + Vector2(0, 1)
	sprite.z_index = scene.hero.z_index
	scene.add_child(sprite)
	await _settle(3)
	var with_v8 := _capture("%s-%s-v8ref" % [prefix, lang])
	report["captures"]["%s_%s_v8ref" % [prefix, lang]] = {"off": plain, "on": with_v8, "probe": _scene_probe(scene),
		"sprite_position": [sprite.position.x, sprite.position.y], "sprite_offset": [sprite.offset.x, sprite.offset.y],
		"scale": 0.5, "source_size": [image.get_width(), image.get_height()], "hero_feet": [feet.x, feet.y]}
	sprite.queue_free()
	await _settle(2)


# ------------------------------------------------------------------ camera: real-input south and north walks
func _camera_trace() -> void:
	var scene = await _enter_ruins("zh")
	var lane := _vec(contract["camera_lane"]["from"])
	var to := _vec(contract["camera_lane"]["to"])
	scene.hero.position = lane
	scene._v12_sync()
	await _settle(2)
	var samples := []
	for leg in [["move_down", to.y], ["move_up", lane.y]]:
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
	var curve := []
	for feet in range(200, 360):
		curve.append([feet, r1.r1_scroll_for(float(feet)), v12_scroll_for(feet)])
	report["camera"] = {"lane": contract["camera_lane"], "samples": samples, "curve": curve}


static func v12_scroll_for(feet: int) -> int:
	return clampi(maxi(2 * (feet - 250), feet + 3 - 255), 0, 104)


# ------------------------------------------------------------------ layout at every walkable foot (grid)
func _layout_sweep() -> void:
	var scene = await _enter_ruins("en")
	var results := {"positions": 0, "label_overlaps": [], "label_glyph_overlaps": [], "labels_outside": [],
		"glyphs_outside": [], "label_hero_overlaps": 0, "label_hero_by_name": {}, "label_hero_samples": [], "hidden_labels": {}, "pinned_glyphs": {}}
	for state_index in 2:
		if state_index == 1:
			# Post-objective state: records checked, Ji recruited (labels change), sentry still on patrol.
			app.ji_records_checked = true
			app.recruited_members["ji-cheng"] = true
			scene._refresh_text()
		for y in range(150, 357, 6):
			for x in range(16, 624, 8):
				var at := Vector2(x, y)
				if not scene._v12_walkable(at):
					continue
				scene.hero.position = at
				scene._v12_sync()
				var state := _layout_state(scene)
				results["positions"] += 1
				var tag := [state_index, x, y, state["scroll"]]
				if not state["label_overlaps"].is_empty():
					results["label_overlaps"].append([tag, state["label_overlaps"]])
				if not state["label_glyph_overlaps"].is_empty():
					results["label_glyph_overlaps"].append([tag, state["label_glyph_overlaps"]])
				if not state["labels_outside_band"].is_empty():
					results["labels_outside"].append([tag, state["labels_outside_band"]])
				if not state["glyphs_outside_band"].is_empty():
					results["glyphs_outside"].append([tag, state["glyphs_outside_band"]])
				if not state["label_hero_overlaps"].is_empty():
					results["label_hero_overlaps"] += 1
					for name in state["label_hero_overlaps"]:
						results["label_hero_by_name"][name] = int(results["label_hero_by_name"].get(name, 0)) + 1
					if results["label_hero_samples"].size() < 40:
						results["label_hero_samples"].append([tag, state["label_hero_overlaps"]])
				for glyph in state["glyphs"]:
					if glyph["pinned"]:
						results["pinned_glyphs"][glyph["key"]] = int(results["pinned_glyphs"].get(glyph["key"], 0)) + 1
	results["label_overlaps"] = results["label_overlaps"].slice(0, 20)
	results["label_glyph_overlaps"] = results["label_glyph_overlaps"].slice(0, 20)
	results["labels_outside"] = results["labels_outside"].slice(0, 20)
	results["glyphs_outside"] = results["glyphs_outside"].slice(0, 20)
	report["layout"] = results


# ------------------------------------------------------------------ full objective flow with real input
func _reset_monitor() -> void:
	monitor = {"frames": 0, "nonwalkable": [], "outside_view": [], "min_canvas_top_screen": 9999,
		"max_canvas_bottom_screen": -9999, "min_canvas_left": 9999, "max_canvas_right": -9999, "max_scroll_step": 0}


func _monitor(scene) -> void:
	if not is_instance_valid(scene) or current_scene != scene:
		return
	var at: Vector2 = scene.hero.position
	var feet := int(round(at.y))
	var x := int(round(at.x))
	var scroll: int = scene.v12_scroll
	monitor["frames"] += 1
	if not scene._v12_walkable(at):
		monitor["nonwalkable"].append([at.x, at.y])
	var top := feet - 44 - scroll + 62
	var bottom := feet + 3 - scroll + 62
	monitor["min_canvas_top_screen"] = mini(monitor["min_canvas_top_screen"], top)
	monitor["max_canvas_bottom_screen"] = maxi(monitor["max_canvas_bottom_screen"], bottom)
	monitor["min_canvas_left"] = mini(monitor["min_canvas_left"], x - 16)
	monitor["max_canvas_right"] = maxi(monitor["max_canvas_right"], x + 15)
	if top < 62 or bottom > 317 or x - 16 < 0 or x + 15 > 639:
		monitor["outside_view"].append([at.x, at.y, scroll])
	if monitor.has("last_scroll"):
		monitor["max_scroll_step"] = maxi(monitor["max_scroll_step"], absi(scroll - int(monitor["last_scroll"])))
	monitor["last_scroll"] = scroll


func _steer(delta_vec: Vector2) -> void:
	var want := {"move_right": delta_vec.x > 1.2, "move_left": delta_vec.x < -1.2,
		"move_down": delta_vec.y > 1.2, "move_up": delta_vec.y < -1.2}
	for action in want:
		if want[action]:
			Input.action_press(action)
		else:
			Input.action_release(action)


func _walk(scene, route: Array, limit := 1500) -> Dictionary:
	var frames := 0
	monitor.erase("last_scroll")
	for point in route:
		var target := _vec(point)
		while true:
			if not is_instance_valid(scene) or current_scene != scene:
				_release_moves()
				return {"ok": true, "scene_changed": true, "frames": frames}
			var delta_vec: Vector2 = target - scene.hero.position
			if absf(delta_vec.x) <= 1.2 and absf(delta_vec.y) <= 1.2:
				break
			_steer(delta_vec)
			await process_frame
			_monitor(scene)
			frames += 1
			if frames > limit:
				_release_moves()
				return {"ok": false, "stuck_at": [scene.hero.position.x, scene.hero.position.y], "frames": frames}
	_release_moves()
	await _settle(2)
	if not is_instance_valid(scene) or current_scene != scene:
		return {"ok": true, "scene_changed": true, "frames": frames}
	return {"ok": true, "scene_changed": false, "frames": frames, "end": [scene.hero.position.x, scene.hero.position.y]}


func _step(name: String, result: Dictionary) -> void:
	report["flow"][name] = result


func _flow() -> void:
	_reset_monitor()
	var routes: Dictionary = contract["routes"]
	var scene = await _enter_ruins("zh")
	_step("enter", {"via": "scifi_world_map._enter_scene", "v12_active": scene.v12_active, "r1_active": scene.r1_active,
		"hero": [scene.hero.position.x, scene.hero.position.y], "scroll": scene.v12_scroll,
		"script": scene.get_script().resource_path})
	var walked := await _walk(scene, routes["records"])
	await _press_action("interact")
	_step("records", {"walk": walked, "ji_records_checked": app.ji_records_checked})
	walked = await _walk(scene, routes["npc"])
	await _press_action("interact")
	var opened: bool = scene.dialogue_open and scene.dialogue_mode == "recruit"
	scene.invite_button.pressed.emit()
	await _settle(3)
	_step("npc", {"walk": walked, "dialogue_opened": opened, "recruited": app.recruited_members.has("ji-cheng")})
	for index in 2:
		walked = await _walk(scene, routes["trace%d" % index])
		await _press_action("interact")
		var trace_opened: bool = scene.dialogue_open and scene.dialogue_mode == "trace" and scene.trace_index == index
		await _press_action("ui_cancel")
		_step("trace%d" % index, {"walk": walked, "dialogue_opened": trace_opened,
			"recorded": app.field_traces.has("scifi.ruins:%d" % index), "closed": not scene.dialogue_open})
	walked = await _walk(scene, routes["assist"])
	await _press_action("interact")
	var assist_opened: bool = scene.dialogue_open and scene.dialogue_mode == "assist"
	scene.invite_button.pressed.emit()
	await _settle(2)
	var insight: bool = app.field_insights.has("scifi.ruins")
	await _press_action("ui_cancel")
	_step("assist", {"walk": walked, "dialogue_opened": assist_opened, "insight": insight})
	walked = await _walk(scene, routes["bypass"])
	_step("bypass", {"walk": walked, "bypass_reached": scene.bypass_reached, "machine_observed": app.machine_observed,
		"battle_not_started": current_scene == scene})
	for exit_name in ["exit_east", "exit_south", "exit_west"]:
		walked = await _walk(scene, routes[exit_name])
		_step(exit_name, {"walk": walked, "battle_not_started": current_scene == scene})
	walked = await _walk(scene, routes["survey"])
	await _press_action("interact")
	await _settle(6)
	var annex_path := current_scene.scene_file_path
	await _press_action("ui_cancel")
	await _settle(8)
	scene = current_scene
	_step("survey", {"walk": walked, "annex_scene": annex_path, "returned_scene": scene.scene_file_path,
		"returned_r1_active": scene.get("r1_active"), "resume_position": [scene.hero.position.x, scene.hero.position.y],
		"scroll": scene.get("v12_scroll")})
	# Sentry: walk into it -> real battle_arena -> real auto-mode victory -> real result button -> back.
	walked = await _walk(scene, routes["sentry"])
	await _settle(6)
	var battle = current_scene
	var battle_path: String = battle.scene_file_path
	var return_position: Vector2 = app.battle_return_position
	var encounter := {"walk": walked, "battle_scene": battle_path, "battle_enemy": app.battle_enemy_id,
		"return_position": [return_position.x, return_position.y],
		"return_distance_to_enemy": return_position.distance_to(_vec(contract["anchors"]["enemy"]))}
	if battle_path != "res://scenes/battle_arena.tscn":
		_step("sentry", encounter)
		report["errors"].append("battle scene did not open")
		report["flow_monitor"] = monitor.duplicate(true)
		return
	var start_hp: int = battle.enemy_hp
	battle.enemy_hp = mini(battle.enemy_hp, FIXTURE_ENEMY_HP)
	encounter["enemy_hp_start"] = start_hp
	encounter["enemy_hp_fixture"] = battle.enemy_hp
	await _press_action("battle_auto")
	encounter["auto_mode_by_input"] = battle.auto_mode
	var waited := 0
	while not battle.battle_finished and waited < 1800:
		await process_frame
		waited += 1
	encounter["battle_frames"] = waited
	encounter["battle_finished"] = battle.battle_finished
	encounter["battle_won"] = battle.battle_won
	encounter["enemy_hp_end"] = battle.enemy_hp
	encounter["flags_after_finish"] = {"returning_from_battle": app.returning_from_battle,
		"enemy_cleared_for_return": app.enemy_cleared_for_return}
	encounter["result_button_focused"] = battle.result_button.has_focus()
	_step("sentry", encounter)
	await _settle(10)
	await _press_action("ui_accept")
	await _settle(10)
	var after_result: String = current_scene.scene_file_path
	var via_growth := false
	if after_result == "res://scenes/growth_screen.tscn":
		via_growth = true
		report["errors"].append("battle result routed to the growth screen; return not exercised")
	scene = current_scene
	var restored := {"scene_after_result": after_result, "via_growth_screen": via_growth}
	if scene.get("r1_active") != null:
		var feet := int(round(scene.hero.position.y))
		restored.merge({"r1_active": scene.r1_active, "hero": [scene.hero.position.x, scene.hero.position.y],
			"equals_return_position": scene.hero.position == return_position,
			"equals_return_texel": scene.hero.position == return_position.round(),
			"walkable": scene._v12_walkable(scene.hero.position), "enemy_visible": scene.enemy_visible,
			"scroll": scene.v12_scroll, "expected_scroll": r1.r1_scroll_for(scene.hero.position.y),
			"camera_y": scene.v12_camera.position.y, "camera_current": scene.v12_camera.is_current(),
			"returning_flag_consumed": not app.returning_from_battle, "layout": _layout_state(scene)})
		await _settle(4)
		restored["capture"] = _capture("rt640-zh-battle-return")
	_step("battle_return", restored)
	if scene.get("r1_active") != null:
		await _press_action("ui_cancel")
		await _settle(6)
		_step("world_map", {"scene": current_scene.scene_file_path})
	monitor.erase("last_scroll")
	report["flow_monitor"] = monitor.duplicate(true)


# ------------------------------------------------------------------ collision sweeps
func _sweeps() -> void:
	_reset_monitor()
	var scene = await _enter_ruins("zh")
	for sweep in contract["sweeps"]:
		scene.hero.position = _vec(sweep["from"])
		scene._v12_sync()
		await _settle(1)
		monitor.erase("last_scroll")
		var actions: Array = sweep["hold"]
		for action in actions:
			Input.action_press(action)
		for index in int(sweep["frames"]):
			await process_frame
			_monitor(scene)
			if current_scene != scene:
				break
		_release_moves()
		await _settle(2)
		report["sweeps"].append({"name": sweep["name"], "end": [scene.hero.position.x, scene.hero.position.y],
			"walkable": scene._v12_walkable(scene.hero.position), "scene_unchanged": current_scene == scene})
	monitor.erase("last_scroll")
	report["sweep_monitor"] = monitor.duplicate(true)


func _probes() -> void:
	var scene = await _enter_ruins("zh")
	var png := Image.load_from_file(String(contract["walkmask_abs"]))
	var mismatch := 0
	for y in 360:
		for x in 640:
			if scene._v12_walkable(Vector2(x, y)) != (png.get_pixel(x, y).a > 0.5):
				mismatch += 1
	var unsafe := []
	for y in 360:
		for x in 640:
			if png.get_pixel(x, y).a > 0.5:
				var scroll: int = r1.r1_scroll_for(float(y))
				if y - 44 - scroll + 62 < 62 or y + 3 - scroll + 62 > 317:
					unsafe.append([x, y, scroll])
	report["probes"] = {"mask_mismatch": mismatch, "unsafe_walkable_feet": unsafe.slice(0, 20),
		"unsafe_count": unsafe.size(), "camera_current": scene.v12_camera.is_current(),
		"spawn": [scene.hero.position.x, scene.hero.position.y], "spawn_scroll": scene.v12_scroll}


func _write_report() -> void:
	var file := FileAccess.open(out_dir.path_join("wdc12r1-harness-report-%s.json" % mode), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	print("WDC12R1 HARNESS DONE mode=%s errors=%d" % [mode, report["errors"].size()])
