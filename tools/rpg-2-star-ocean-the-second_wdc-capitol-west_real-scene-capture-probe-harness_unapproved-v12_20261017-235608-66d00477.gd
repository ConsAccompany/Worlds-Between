extends SceneTree

# WDC Capitol west v12: capture + probe harness for the REAL exploration scene (test-only tool, not runtime).
# Run windowed (rendering needed) from the build-check tool:
#   Godot --path game --resolution 640x360 -s <this file> -- --wdc-capitol-west-v12
#         --wdc12-contract=<runtime contract json> --wdc12-out=<probe dir> --wdc12-cap=<capture dir>
# It enters Washington through the world map's own _enter_scene(), moves the heroine with the real input
# actions, interacts through Input.parse_input_event (so the scene's _unhandled_input handles it), and
# captures the actual viewport with the actual HUD. It never preloads AppState-using scripts (they are loaded
# at run time) and writes saves only under user://test-saves/wdc-cw-v12.

const SCENE := "res://scenes/scifi_exploration_area.tscn"
const BASE_SCRIPT := "res://scripts/scifi_exploration_area.gd"
const SELECTOR := "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12_20261017-235608-66d00477.gd"
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
const ANNEX_SCENE := "res://scenes/survey_annex.tscn"
const BATTLE_SCENE := "res://scenes/battle_arena.tscn"
const CAP_FMT := "rpg-2-star-ocean-the-second_wdc-capitol-west_%s_unapproved-v12_20261017-235608-66d00477.png"
const MOVES := ["move_left", "move_right", "move_up", "move_down"]

var app: Node
var selector: GDScript
var contract: Dictionary = {}
var out_dir := ""
var cap_dir := ""
var report := {"captures": {}, "default_runtime": {}, "flow": {}, "sweeps": [], "probes": {}, "errors": []}
var monitor := {}


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var contract_path := ""
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--wdc12-contract="):
			contract_path = argument.trim_prefix("--wdc12-contract=")
		elif argument.begins_with("--wdc12-out="):
			out_dir = argument.trim_prefix("--wdc12-out=")
		elif argument.begins_with("--wdc12-cap="):
			cap_dir = argument.trim_prefix("--wdc12-cap=")
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(contract_path))
	if typeof(parsed) != TYPE_DICTIONARY or out_dir == "" or cap_dir == "":
		push_error("WDC v12 harness: missing contract or output arguments")
		quit(2)
		return
	contract = parsed
	Engine.max_fps = 60
	SaveStore.root_path = "user://test-saves/wdc-cw-v12"
	app = root.get_node("AppState")
	selector = load(SELECTOR)
	report["cmdline_flag_enables_v12"] = selector.v12_enabled()
	report["viewport_size"] = [root.get_visible_rect().size.x, root.get_visible_rect().size.y]
	await _default_runtime()
	for lang in ["zh", "en"]:
		await _captures(lang)
	await _flow()
	await _sweeps()
	await _probes()
	_write_report()
	quit(0)


# ------------------------------------------------------------------ helpers
func _fresh_run(destination: String, lang: String) -> void:
	for action in MOVES:
		Input.action_release(action)
	app.begin_new_run()
	app.hero_name = "Test"
	app.hero_appearance = "female"
	if app.language != lang:
		app.toggle_language()
	app.select_destination(destination)


func _settle(frames := 4) -> void:
	for index in frames:
		await process_frame


func _interact_event(pressed := true) -> InputEventAction:
	var event := InputEventAction.new()
	event.action = "interact"
	event.pressed = pressed
	return event


func _cancel_event(pressed := true) -> InputEventAction:
	var event := InputEventAction.new()
	event.action = "ui_cancel"
	event.pressed = pressed
	return event


func _press(event_maker: Callable) -> void:
	Input.parse_input_event(event_maker.call(true))
	await process_frame
	Input.parse_input_event(event_maker.call(false))
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


func _screen_rect(scene: Node, item: Control) -> Array:
	var rect := item.get_global_rect()
	var shift := 0.0
	if scene.get("v12_active") and item.get_parent() == scene.get("v12_labels"):
		shift = float(scene.v12_scroll - 62)
	return [rect.position.x, rect.position.y - shift, rect.size.x, rect.size.y]


func _scene_probe(scene: Node) -> Dictionary:
	var hero: Sprite2D = scene.hero
	var probe := {
		"script": scene.get_script().resource_path,
		"v12_active": scene.get("v12_active"),
		"scroll": scene.get("v12_scroll"),
		"hero": [hero.position.x, hero.position.y],
		"hero_texture": hero.texture.resource_path,
		"hero_flip_h": hero.flip_h,
		"hero_z": hero.z_index,
		"language": app.language,
		"feedback": scene.feedback_label.text,
		"title": scene.title_label.text,
		"hint": scene.hint_label.text,
		"hint_font_size": scene.hint_label.get_theme_font_size("font_size"),
		"hint_width": scene.hint_label.get_theme_font("font").get_string_size(scene.hint_label.text, HORIZONTAL_ALIGNMENT_LEFT, -1, scene.hint_label.get_theme_font_size("font_size")).x,
		"title_width": scene.title_label.get_theme_font("font").get_string_size(scene.title_label.text, HORIZONTAL_ALIGNMENT_LEFT, -1, scene.title_label.get_theme_font_size("font_size")).x,
		"hint_rect": _screen_rect(scene, scene.hint_label),
		"title_rect": _screen_rect(scene, scene.title_label),
		"save_rect": _screen_rect(scene, scene.save_button),
		"back_rect": _screen_rect(scene, scene.back_button),
		"enemy_visible": scene.enemy_visible,
		"enemy": [scene.enemy_position.x, scene.enemy_position.y],
		"dialogue_open": scene.dialogue_open,
		"ji_records_checked": app.ji_records_checked,
		"labels": [],
	}
	if scene.field_npc != null:
		probe["npc"] = [scene.field_npc.position.x, scene.field_npc.position.y]
		probe["npc_visible"] = scene.field_npc.visible
		probe["npc_texture"] = scene.field_npc.texture.resource_path
		probe["npc_z"] = scene.field_npc.z_index
	var labels := [["npc", scene.npc_label], ["records", scene.records_label], ["survey", scene.survey_label],
		["assist", scene.assist_label], ["enemy", scene.enemy_label], ["trace0", scene.trace_labels[0]],
		["trace1", scene.trace_labels[1]]]
	for entry in labels:
		var label: Label = entry[1]
		probe["labels"].append({"name": entry[0], "text": label.text, "visible": label.is_visible_in_tree(),
			"rect": _screen_rect(scene, label)})
	return probe


func _capture(name: String) -> Dictionary:
	var image := root.get_texture().get_image()
	var path := cap_dir.path_join(CAP_FMT % name)
	var error := image.save_png(path)
	if error != OK:
		report["errors"].append("capture failed: " + name)
	return {"file": CAP_FMT % name, "size": [image.get_width(), image.get_height()], "saved": error == OK}


func _pose(scene: Node, pose: Dictionary) -> void:
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


# ------------------------------------------------------------------ default runtime (flag off)
func _default_runtime() -> void:
	selector.v12_override = 0
	for destination in ["scifi.city", "scifi.outskirts", "scifi.ruins"]:
		var with_selector: Dictionary = await _default_probe(destination, false)
		var with_base: Dictionary = await _default_probe(destination, true)
		report["default_runtime"][destination] = {
			"selector_script": with_selector["script"],
			"base_script": with_base["script"],
			"selector_v12_active": with_selector["v12_active"],
			"entry_image_equal": with_selector["entry"] == with_base["entry"],
			"after_input_image_equal": with_selector["after"] == with_base["after"],
			"positions_equal": with_selector["positions"] == with_base["positions"],
			"texts_equal": with_selector["texts"] == with_base["texts"],
			"state_equal": with_selector["state"] == with_base["state"],
			"positions": with_selector["positions"],
			"state": with_selector["state"],
		}
	selector.v12_override = -1


func _default_probe(destination: String, use_base: bool) -> Dictionary:
	_fresh_run(destination, "zh")
	if use_base:
		var node: Node = load(SCENE).instantiate()
		node.set_script(load(BASE_SCRIPT))
		change_scene_to_node(node)
	else:
		change_scene_to_file(SCENE)
	await _settle(8)
	var scene := current_scene
	var entry := root.get_texture().get_image().get_data()
	var positions := [[scene.hero.position.x, scene.hero.position.y]]
	# Deterministic drive through the real _process: fixed deltas inside one frame.
	for action in ["move_right", "move_down", "move_left", "move_up"]:
		Input.action_press(action)
		for step in 4:
			scene._process(0.1)
		Input.action_release(action)
		scene._process(0.1)
		positions.append([scene.hero.position.x, scene.hero.position.y])
	if destination == "scifi.ruins":
		scene.hero.position = Vector2(320, 250)
		scene._unhandled_input(_interact_event())
	await _settle(4)
	var after := root.get_texture().get_image().get_data()
	var texts := [scene.title_label.text, scene.hint_label.text, scene.feedback_label.text,
		scene.hint_label.get_theme_font_size("font_size"), scene.npc_label.position, scene.survey_label.position,
		scene.hint_label.position]
	var state := [app.ji_records_checked, app.machine_observed, app.field_traces.size(), scene.enemy_visible]
	return {"script": scene.get_script().resource_path, "v12_active": scene.get("v12_active"), "entry": entry,
		"after": after, "positions": positions, "texts": str(texts), "state": state}


# ------------------------------------------------------------------ review captures
func _captures(lang: String) -> void:
	var scene := await _enter_ruins(lang)
	var captures := {}
	captures["entry"] = _capture("rt640-%s-entry" % lang)
	captures["entry"]["probe"] = _scene_probe(scene)
	var poses: Dictionary = contract["review_poses"]
	await _pose(scene, poses["vista"])
	captures["vista"] = _capture("rt640-%s-vista" % lang)
	captures["vista"]["probe"] = _scene_probe(scene)
	await _pose(scene, poses["interaction"])
	captures["interaction_prompt"] = _capture("rt640-%s-interact-prompt" % lang)
	captures["interaction_prompt"]["probe"] = _scene_probe(scene)
	await _press(_interact_event)
	captures["interaction"] = _capture("rt640-%s-interact" % lang)
	captures["interaction"]["probe"] = _scene_probe(scene)
	await _pose(scene, poses["occlusion"])
	captures["occlusion"] = _capture("rt640-%s-occlusion" % lang)
	captures["occlusion"]["probe"] = _scene_probe(scene)
	await _pose(scene, poses["patrol_extra"])
	captures["patrol_extra"] = _capture("rt640-%s-patrol-scrolled" % lang)
	captures["patrol_extra"]["probe"] = _scene_probe(scene)
	report["captures"][lang] = captures


# ------------------------------------------------------------------ full objective flow with real input
func _reset_monitor() -> void:
	monitor = {"frames": 0, "nonwalkable": [], "outside_view": [], "min_canvas_top_screen": 9999,
		"max_canvas_bottom_screen": -9999, "min_canvas_left": 9999, "max_canvas_right": -9999,
		"scroll_values": {}, "dome_visible_frames": 0}


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
	monitor["scroll_values"][str(scroll)] = true
	if scroll <= int(contract["dome"]["top"]):
		monitor["dome_visible_frames"] += 1


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
	var scene := await _enter_ruins("zh")
	_step("enter", {"via": "scifi_world_map._enter_scene", "v12_active": scene.v12_active,
		"hero": [scene.hero.position.x, scene.hero.position.y], "scroll": scene.v12_scroll,
		"script": scene.get_script().resource_path})
	# 1 records desk (survey terminal)
	var walked := await _walk(scene, routes["records"])
	await _press(_interact_event)
	_step("records", {"walk": walked, "ji_records_checked": app.ji_records_checked, "feedback": scene.feedback_label.text})
	# 2 Ji Cheng: recruit dialogue through the real buttons
	walked = await _walk(scene, routes["npc"])
	await _press(_interact_event)
	var opened: bool = scene.dialogue_open and scene.dialogue_mode == "recruit"
	scene.invite_button.pressed.emit()
	await _settle(3)
	_step("npc", {"walk": walked, "dialogue_opened": opened, "recruited": app.recruited_members.has("ji-cheng"),
		"npc_hidden_after": not scene.field_npc.visible})
	# 3, 4 traces
	for index in 2:
		walked = await _walk(scene, routes["trace%d" % index])
		await _press(_interact_event)
		var trace_opened: bool = scene.dialogue_open and scene.dialogue_mode == "trace" and scene.trace_index == index
		await _press(_cancel_event)
		_step("trace%d" % index, {"walk": walked, "dialogue_opened": trace_opened,
			"recorded": app.field_traces.has("scifi.ruins:%d" % index), "closed": not scene.dialogue_open})
	# 5 strata panel (field assist)
	walked = await _walk(scene, routes["assist"])
	await _press(_interact_event)
	var assist_opened: bool = scene.dialogue_open and scene.dialogue_mode == "assist"
	var enabled: bool = not scene.invite_button.disabled
	scene.invite_button.pressed.emit()
	await _settle(2)
	var insight: bool = app.field_insights.has("scifi.ruins")
	await _press(_cancel_event)
	_step("assist", {"walk": walked, "dialogue_opened": assist_opened, "use_enabled": enabled, "insight": insight})
	# 6 bypass the patrol to the east side, then the three walk-edge exit zones
	walked = await _walk(scene, routes["bypass"])
	_step("bypass", {"walk": walked, "bypass_reached": scene.bypass_reached, "machine_observed": app.machine_observed,
		"feedback": scene.feedback_label.text, "battle_not_started": current_scene == scene})
	for exit_name in ["exit_east", "exit_south", "exit_west"]:
		walked = await _walk(scene, routes[exit_name])
		_step(exit_name, {"walk": walked, "battle_not_started": current_scene == scene})
	# 7 survey entrance -> real annex scene -> real cancel back to the surface
	walked = await _walk(scene, routes["survey"])
	var before := Vector2(scene.hero.position)
	await _press(_interact_event)
	await _settle(6)
	var annex_path := current_scene.scene_file_path
	await _press(_cancel_event)
	await _settle(8)
	scene = current_scene
	_step("survey", {"walk": walked, "annex_scene": annex_path, "returned_scene": scene.scene_file_path,
		"returned_v12_active": scene.get("v12_active"), "resume_position": [scene.hero.position.x, scene.hero.position.y],
		"left_from": [before.x, before.y]})
	# 8 patrol: walk into the sentry -> real battle hand-off
	walked = await _walk(scene, routes["sentry"])
	await _settle(6)
	var battle_path := current_scene.scene_file_path
	var return_position: Vector2 = app.battle_return_position
	_step("sentry", {"walk": walked, "battle_scene": battle_path, "battle_enemy": app.battle_enemy_id,
		"return_position": [return_position.x, return_position.y],
		"return_distance_to_enemy": return_position.distance_to(_vec(contract["anchors"]["enemy"]))})
	# 9 return from battle (as battle_arena does on victory) -> back at the safe position, patrol cleared
	app.returning_from_battle = true
	app.enemy_cleared_for_return = true
	change_scene_to_file(SCENE)
	await _settle(8)
	scene = current_scene
	_step("battle_return", {"v12_active": scene.get("v12_active"), "hero": [scene.hero.position.x, scene.hero.position.y],
		"walkable": scene._v12_walkable(scene.hero.position), "enemy_visible": scene.enemy_visible,
		"scroll": scene.v12_scroll})
	# 10 world map through the real cancel action
	await _press(_cancel_event)
	await _settle(6)
	_step("world_map", {"scene": current_scene.scene_file_path})
	report["flow_monitor"] = monitor.duplicate(true)


# ------------------------------------------------------------------ collision sweeps
func _sweeps() -> void:
	_reset_monitor()
	var scene := await _enter_ruins("zh")
	for sweep in contract["sweeps"]:
		scene.hero.position = _vec(sweep["from"])
		scene._v12_sync()
		await _settle(1)
		var actions: Array = sweep["hold"]
		for action in actions:
			Input.action_press(action)
		var frames := int(sweep["frames"])
		for index in frames:
			await process_frame
			_monitor(scene)
			if current_scene != scene:
				break
		_release_moves()
		await _settle(2)
		report["sweeps"].append({"name": sweep["name"], "from": sweep["from"], "hold": actions,
			"end": [scene.hero.position.x, scene.hero.position.y], "walkable": scene._v12_walkable(scene.hero.position),
			"scene_unchanged": current_scene == scene})
	report["sweep_monitor"] = monitor.duplicate(true)


# ------------------------------------------------------------------ static probes inside the live scene
func _probes() -> void:
	var scene := await _enter_ruins("zh")
	var png := Image.load_from_file(String(contract["walkmask_abs"]))
	var mismatch := 0
	var walkable := 0
	for y in 360:
		for x in 640:
			var expected := png.get_pixel(x, y).a > 0.5
			if expected:
				walkable += 1
			if scene._v12_walkable(Vector2(x, y)) != expected:
				mismatch += 1
	var layers := []
	for child in scene.get_children():
		if child is Sprite2D and String(child.name).begins_with("WdcV12_"):
			layers.append({"name": String(child.name), "z": child.z_index, "size": [child.texture.get_width(), child.texture.get_height()],
				"filter": child.texture_filter})
	report["probes"] = {"mask_mismatch": mismatch, "mask_walkable": walkable, "layers": layers,
		"hero_z_rule": "2 * feet + 1 (actor wins ties)", "camera_current": scene.v12_camera.is_current(),
		"labels_parent": String(scene.v12_labels.name), "root_texture_filter": scene.texture_filter}


func _write_report() -> void:
	var file := FileAccess.open(out_dir.path_join("wdc12-harness-report.json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	print("WDC12 HARNESS DONE errors=%d" % report["errors"].size())
