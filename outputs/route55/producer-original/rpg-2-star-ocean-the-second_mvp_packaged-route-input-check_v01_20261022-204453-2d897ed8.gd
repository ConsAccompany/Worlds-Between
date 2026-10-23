extends SceneTree
# TEST-ONLY route55 packaged-PCK science-route input check (scripted normal input; NOT a human playtest,
# normal-speed/pacing evidence, art approval or default adoption). Runs against the delivered PCK via --main-pack.
# FIXTURE (declared): the harness loads the ordinary res://scenes/main_menu.tscn as the first entry. Nothing else is
# written: no configure(), begin_new_run/load_save calls, teleports, quest/recruit/save writes or battle/AI writes.
# All progress goes through Input.parse_input_event key/mouse events on real UI controls. AppState/scene fields are
# read only (geometry, buttons, state oracle). Phases implemented in v01: menu -> setup -> map -> NYC -> recruit Liang.
# Later phases (Liang, surveys, travel, battle, save/relaunch/load) are reported NOT_REACHED, never faked.
# Args: <out_dir> <tag> <language zh|en> <appearance female|male> <hero_name ascii>
const MENU := "res://scenes/main_menu.tscn"
var app: Node
var out := ""
var tag := ""
var language := "zh"
var appearance := "female"
var hero_name := "Lin"
var checks: Array = []
var failures: Array = []
var inputs: Array = []
var captures: Array = []
var checkpoints: Array = []
var raw_errors: Array = []
var trace_reads: Array = []
var stalls := 0
var frame := 0
var deadline_ms := 0


func _initialize() -> void:
	deadline_ms = Time.get_ticks_msec() + 150000
	call_deferred("_run")
	create_timer(160.0).timeout.connect(func(): print("ROUTE55_WATCHDOG"); failures.append("watchdog"); _finish())


func ck(ok: bool, label: String, detail: Variant = null) -> void:
	checks.append({"check": label, "passed": ok, "detail": detail})
	print("ROUTE55 ", "PASS " if ok else "FAIL ", label, "" if detail == null else " " + str(detail))
	if not ok:
		failures.append(label)


func tick() -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	frame += 1
	if Time.get_ticks_msec() > deadline_ms:
		push_error("ROUTE55 inner deadline")


func wait(n: int) -> void:
	for i in n:
		await tick()


func key(k: Key, pressed: bool, unicode: int = 0) -> void:
	var ev := InputEventKey.new()
	ev.keycode = k
	ev.physical_keycode = k
	ev.unicode = unicode
	ev.pressed = pressed
	Input.parse_input_event(ev)
	inputs.append({"frame": frame, "key": OS.get_keycode_string(k), "pressed": pressed})


func type_text(text: String) -> void:
	for ch in text:
		var code := ch.unicode_at(0)
		var k: Key = OS.find_keycode_from_string(ch.to_upper())
		key(k, true, code)
		await tick()
		key(k, false)
		await tick()


func click(control: Control) -> bool:
	if control == null or not is_instance_valid(control) or not control.is_visible_in_tree():
		return false
	var center: Vector2 = root.get_final_transform() * control.get_global_rect().get_center()
	for pressed in [true, false]:
		var ev := InputEventMouseButton.new()
		ev.button_index = MOUSE_BUTTON_LEFT
		ev.pressed = pressed
		ev.position = center
		ev.global_position = center
		Input.parse_input_event(ev)
		inputs.append({"frame": frame, "mouse": "left", "pressed": pressed, "pos": [center.x, center.y], "target": String(control.name)})
		await tick()
	return true


func shot(label: String) -> void:
	var img: Image = root.get_texture().get_image()
	var file := "rpg-2-star-ocean-the-second_route55_%s-%s_%s_capture-640_%s.png" % [language, appearance, label, tag]
	var err := img.save_png(out.path_join(file))
	ck(err == OK and img.get_size() == Vector2i(640, 360), "capture %s native 640x360" % label, [img.get_width(), img.get_height()])
	captures.append({"label": label, "file": file, "frame": frame, "sha256": FileAccess.get_sha256(out.path_join(file)),
		"provenance": "actual scripted-input journey state"})


func scene_is(path: String, limit: int = 240) -> bool:
	var n := 0
	while n < limit and (current_scene == null or current_scene.scene_file_path != path):
		await tick()
		n += 1
	await wait(3)
	return current_scene != null and current_scene.scene_file_path == path


func state_oracle() -> Dictionary:
	var s := {"heroName": app.hero_name, "appearance": app.hero_appearance, "language": app.language,
		"destination": app.current_destination_id, "calendarMinutes": app.calendar_minutes, "scene": current_scene.scene_file_path if current_scene else ""}
	for field in ["party", "recruited_members", "survey_state", "quest_flags"]:
		if field in app:
			s[field] = str(app.get(field))
	if current_scene != null and "hero" in current_scene and current_scene.hero != null:
		s["heroPosition"] = [current_scene.hero.position.x, current_scene.hero.position.y]
	return s


func checkpoint(label: String) -> void:
	checkpoints.append({"label": label, "frame": frame, "state": state_oracle()})
	print("ROUTE55 CHECKPOINT ", label)


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 5:
		push_error("ROUTE55 bad args")
		print("ROUTE55_ERROR bad args")
		quit(3)
		return
	out = args[0]; tag = args[1]; language = args[2]; appearance = args[3]; hero_name = args[4]
	app = root.get_node_or_null("AppState")
	ck(app != null, "AppState autoload present from PCK")
	ck(ResourceLoader.exists(MENU), "packaged main_menu.tscn exists in PCK")
	ck(not OS.get_cmdline_args().has("--path"), "no --path game (packaged run)")
	change_scene_to_file(MENU)
	ck(await scene_is(MENU), "main menu entered")
	var menu := current_scene
	# Language through the real language button only if the fresh profile is not already zh.
	var lang_clicks := 0
	while app.language != language and lang_clicks < 2:
		await click(menu.language_button)
		await wait(2)
		lang_clicks += 1
	ck(app.language == language, "language %s via UI" % language, {"clicks": lang_clicks})
	shot("01-main-menu")
	checkpoint("main-menu")
	ck(await click(menu.start_button), "click Start")
	ck(await scene_is("res://scenes/hero_setup.tscn"), "hero setup entered")
	var setup := current_scene
	await click(setup.name_input)
	await type_text(hero_name)
	await click(setup.female_button if appearance == "female" else setup.male_button)
	ck(setup.name_input.text == hero_name, "name typed through key events", setup.name_input.text)
	ck(setup.appearance == appearance, "appearance chosen by click", setup.appearance)
	shot("02-hero-setup")
	await click(setup.skip_button)
	ck(await scene_is("res://scenes/scifi_world_map.tscn"), "world map entered")
	ck(app.hero_name == hero_name and app.hero_appearance == appearance, "setup applied by real departure", [app.hero_name, app.hero_appearance])
	await wait(10)
	shot("03-world-map")
	checkpoint("world-map")
	var map := current_scene
	var nyc_button: Control = map.destination_buttons.get("scifi.city")
	ck(nyc_button != null, "NYC destination button present")
	if nyc_button != null and not nyc_button.is_visible_in_tree():
		# Region buttons are real UI; enter the region holding NYC first.
		for rb in map.region_buttons.values():
			if rb.is_visible_in_tree():
				await click(rb)
				await wait(5)
				if nyc_button.is_visible_in_tree():
					break
	ck(await click(nyc_button), "click NYC marker")
	await wait(5)
	ck(map.route_card.visible, "route card visible", map.route_state.get("status", ""))
	shot("04-nyc-route-card")
	ck(await click(map.depart_button), "click Depart/Enter")
	var area_path := String(app.area_scene_path("scifi.city"))
	ck(await scene_is(area_path, 300), "NYC area entered", area_path)
	await wait(20)
	shot("05-nyc-entry")
	checkpoint("nyc-entry")
	# Read-only geometry inventory for the next phase (Liang + clue sites); no movement is claimed here.
	var area := current_scene
	var sites := []
	for prop in ["npcs", "interactables", "clue_sites", "objects"]:
		if prop in area:
			sites.append({"field": prop, "value": str(area.get(prop)).left(4000)})
	trace_reads.append({"label": "nyc-readonly-site-fields", "frame": frame, "fields": sites,
		"npcPosition": [area.npc_position.x, area.npc_position.y], "recruitId": area.recruit_id})
	# Phase: recruit Liang by WASD walking to the actual NPC site (read from the scene), E, real Invite click.
	var reached := await walk_to(area, area.npc_position, 46.0)
	ck(reached, "walked within 46 px of Liang NPC", [area.hero.position.x, area.hero.position.y, area.npc_position.x, area.npc_position.y])
	if not reached:
		failures.append("blocked: could not reach Liang NPC by greedy WASD over the actual city slide mask")
		_not_reached(["recruit-liang"])
		_finish()
		return
	await tap(KEY_E)
	await wait(5)
	ck(area.dialogue_open, "E opened Liang dialogue")
	shot("06-liang-dialogue")
	ck(not area.invite_button.disabled, "Invite enabled")
	await click(area.invite_button)
	await wait(10)
	ck(app.recruited_members.has("liang-xu"), "Liang recruited through Invite click", str(app.recruited_members))
	shot("07-liang-recruited")
	checkpoint("recruit-liang")
	# Partial survey phase: walk to the actual NYC survey entrance (scene const, read only) and press E.
	var entrance: Vector2 = area.SURVEY_ENTRANCES["scifi.city"]
	var at_entrance := await walk_to(area, entrance, 40.0)
	ck(at_entrance, "walked within 40 px of NYC survey entrance", [area.hero.position.x, area.hero.position.y, entrance.x, entrance.y])
	var furthest := "recruit-liang"
	if at_entrance:
		await tap(KEY_E)
		if await scene_is("res://scenes/survey_annex.tscn", 240):
			await wait(15)
			ck(true, "E entered NYC survey annex room 1")
			shot("08-nyc-annex-entry")
			checkpoint("nyc-annex-entry")
			furthest = "nyc-annex-entry"
		else:
			ck(false, "E entered NYC survey annex room 1", current_scene.scene_file_path if current_scene else "")
	_not_reached([])
	failures.append("route incomplete: furthest real checkpoint " + furthest)
	_finish()


func tap(k: Key) -> void:
	key(k, true)
	await tick()
	key(k, false)
	await tick()


# Greedy WASD walk over the real movement code; switches axis when an axis stalls (slide mask blocks).
func walk_to(area: Node, target: Vector2, radius: float, limit: int = 3600) -> bool:
	# Plan: BFS on a 4 px grid using the scene's own read-only _city_walkable (actual STYLE46 mask), then
	# drive the axis-aligned segments with held WASD keys through the normal movement code.
	var step := 4.0
	var origin: Vector2 = area.hero.position
	var start := Vector2i(0, 0)
	var prev := {start: start}
	var queue := [start]
	var goal = null
	var head := 0
	while head < queue.size() and head < 40000:
		var c: Vector2i = queue[head]
		head += 1
		var p := origin + Vector2(c) * step
		if p.distance_to(target) <= radius - 4.0:
			goal = c
			break
		for d in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var nc: Vector2i = c + d
			if prev.has(nc):
				continue
			var np := origin + Vector2(nc) * step
			if np.x < 24 or np.x > 616 or np.y < 77 or np.y > 306 or not area._city_walkable(np):
				continue
			prev[nc] = c
			queue.append(nc)
	trace_reads.append({"label": "bfs", "from": [origin.x, origin.y], "to": [target.x, target.y], "expanded": head, "found": goal != null})
	if goal == null:
		return false
	var cells := [goal]
	while cells[0] != start:
		cells.push_front(prev[cells[0]])
	# Compress to corner waypoints.
	var waypoints: Array = []
	for i in range(1, cells.size()):
		if i == cells.size() - 1 or (cells[i + 1] - cells[i]) != (cells[i] - cells[i - 1]):
			waypoints.append(origin + Vector2(cells[i]) * step)
	trace_reads.append({"label": "waypoints", "points": waypoints.map(func(w): return [w.x, w.y])})
	var n := 0
	for w in waypoints:
		var d: Vector2 = w - area.hero.position
		var axis := 0 if absf(d.x) >= absf(d.y) else 1
		var k: Key = (KEY_D if d.x > 0 else KEY_A) if axis == 0 else (KEY_S if d.y > 0 else KEY_W)
		var sgn := signf(d[axis])
		key(k, true)
		var last: Vector2 = area.hero.position
		var still := 0
		while n < limit and current_scene == area and (w[axis] - area.hero.position[axis]) * sgn > 1.0:
			await tick()
			n += 1
			still = still + 1 if area.hero.position.distance_to(last) < 0.05 else 0
			last = area.hero.position
			if still > 20:
				break
		key(k, false)
		await tick()
		if still > 20:
			stalls += 1
			trace_reads.append({"label": "stall", "at": [area.hero.position.x, area.hero.position.y], "waypoint": [w.x, w.y]})
			break
	return area.hero.position.distance_to(target) <= radius


func _not_reached(skip: Array) -> void:
	for phase in ["recruit-liang", "nyc-survey-6clues-3links-answer", "yonkers-relay-zhao-survey", "washington-records-ji-survey",
			"natural-battle-result-return", "nyc-report-submit", "ui-save", "relaunch-ui-load-verify"]:
		if phase == "recruit-liang" and skip.is_empty():
			continue
		checkpoints.append({"label": phase, "status": "NOT_REACHED", "reason": "not implemented in v01 within the 11-minute bound" if not skip.has(phase) else "blocked"})


func _finish() -> void:
	var report := {"tag": tag, "language": language, "appearance": appearance, "frames": frame, "checks": checks,
		"failures": failures, "checkpoints": checkpoints, "readonlyQueries": trace_reads, "captures": captures, "inputs": inputs.size(), "inputLog": inputs,
		"fixtures": ["harness change_scene_to_file(main_menu.tscn) as first entry"], "acceleratedFixedFps": true,
		"humanPlaytest": false, "normalSpeedClaim": false}
	var f := FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_route55_report_%s.json" % tag), FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(report, "  ") + "\n")
		f.close()
	var functional_ok := checks.all(func(c): return c["passed"])
	print("ROUTE55_DONE checks_ok=%s furthest=%s" % [functional_ok, checkpoints.filter(func(c): return not c.has("status")).back()["label"] if checkpoints.size() else "none"])
	quit(0 if functional_ok else 1)
