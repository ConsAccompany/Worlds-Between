extends SceneTree
# TEST-ONLY route55 packaged-PCK science-route input check (scripted normal input; NOT a human playtest,
# normal-speed/pacing evidence, art approval or default adoption). Runs against the delivered PCK via --main-pack.
# FIXTURE (declared): the harness loads the ordinary res://scenes/main_menu.tscn as the first entry. Nothing else is
# written: no configure(), begin_new_run/load_save calls, teleports, quest/recruit/save writes or battle/AI writes.
# All progress goes through Input.parse_input_event key/mouse events on real UI controls. AppState/scene fields are
# read only (geometry, buttons, state oracle). Codex extends Claude's preserved partial source to the full route.
# Journey uses real UI quit; a second process loads the same manual slot through UI and compares saved fields.
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
var phase := "journey"
var expected_path := ""
var restart_ready := false


func _initialize() -> void:
	deadline_ms = Time.get_ticks_msec() + 280000
	call_deferred("_run")
	create_timer(1200.0).timeout.connect(func(): print("ROUTE55_WATCHDOG"); failures.append("watchdog"); _finish())


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
	for field in ["active_party_ids", "recruited_members", "survey_solved", "survey_clues", "survey_links", "relay_checked", "ji_records_checked", "machine_observed", "demo_completed"]:
		s[field] = app.get(field).duplicate(true) if app.get(field) is Dictionary or app.get(field) is Array else app.get(field)
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
	phase = args[5] if args.size() > 5 else "journey"
	expected_path = args[6] if args.size() > 6 else out.path_join("rpg-2-star-ocean-the-second_mvp_restart-expected_v01_" + tag + ".json")
	app = root.get_node_or_null("AppState")
	ck(app != null, "AppState autoload present from PCK")
	ck(ResourceLoader.exists(MENU), "packaged main_menu.tscn exists in PCK")
	ck(not OS.get_cmdline_args().has("--path"), "no --path game (packaged run)")
	change_scene_to_file(MENU)
	ck(await scene_is(MENU), "main menu entered")
	if phase == "reload":
		await reload_phase()
		return
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
	if furthest != "nyc-annex-entry":
		failures.append("route blocked before first annex")
		_finish()
		return
	await finish_journey()


func tap(k: Key) -> void:
	key(k, true)
	await tick()
	key(k, false)
	await tick()


# Greedy WASD walk over the real movement code; switches axis when an axis stalls (slide mask blocks).
func walk_to(area: Node, target: Vector2, radius: float, limit: int = 3600, encounter: bool = false) -> bool:
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
			if not walkable(area, np, encounter):
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
		if not is_instance_valid(area) or current_scene != area:
			return false
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


func write_report() -> void:
	var report := {"tag": tag, "language": language, "appearance": appearance, "frames": frame, "checks": checks,
		"failures": failures, "checkpoints": checkpoints, "readonlyQueries": trace_reads, "captures": captures, "inputs": inputs.size(), "inputLog": inputs,
		"fixtures": ["harness change_scene_to_file(main_menu.tscn) as first entry"], "acceleratedFixedFps": true,
		"humanPlaytest": false, "normalSpeedClaim": false, "phase": phase, "processId": OS.get_process_id(), "restartReady": restart_ready}
	var f := FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_route55_report_%s.json" % tag), FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(report, "  ") + "\n")
		f.close()
	var functional_ok := checks.all(func(c): return c["passed"])
	print("ROUTE55_DONE checks_ok=%s furthest=%s" % [functional_ok, checkpoints.filter(func(c): return not c.has("status")).back()["label"] if checkpoints.size() else "none"])


func _finish() -> void:
	write_report()
	var okay := failures.is_empty() and checks.all(func(c): return c["passed"])
	if okay and phase == "reload" and restart_ready:
		print("ROUTE55_ALL_PASS")
	quit(0 if okay else 1)


func finish_journey() -> void:
	await solve_survey("scifi.city")
	await travel_to("scifi.outskirts")
	var area := current_scene
	ck(await walk_to(area, area.RELAY_POSITION, 30.0), "walk to relay")
	await tap(KEY_E)
	ck(app.relay_checked, "relay checked by E")
	await recruit_here("zhao-ling")
	ck(await walk_to(area, Vector2(576, 135), 10.0), "walk into Yonkers bypass zone")
	ck(app.machine_observed, "machine bypass recorded by actual movement")
	await enter_survey(area.SURVEY_ENTRANCES["scifi.outskirts"])
	await solve_survey("scifi.outskirts")
	await travel_to("scifi.ruins")
	area = current_scene
	ck(await walk_to(area, area.V12_RECORDS, 30.0), "walk to Washington records plaque")
	await tap(KEY_E)
	ck(app.ji_records_checked, "Washington records checked by E")
	await recruit_here("ji-cheng")
	await enter_survey(area.V12_SURVEY)
	await solve_survey("scifi.ruins")
	area = current_scene
	await walk_to(area, area.enemy_position, 8.0, 3600, true)
	ck(await scene_is("res://scenes/battle_arena.tscn"), "walking proximity entered actual battle")
	var battle := current_scene
	await tap(KEY_T)
	var battle_ticks := 0
	while not battle.battle_finished and battle_ticks < 3600:
		await tick()
		battle_ticks += 1
	ck(battle.battle_finished and battle.battle_won, "normal AI battle won without HP/damage writes", battle_ticks)
	shot("battle-natural-victory")
	await click(battle.result_button)
	ck(await scene_is("res://scenes/scifi_exploration_area.tscn"), "actual result click returned to Washington")
	ck(app.enemy_cleared_for_return, "battle return cleared enemy")
	checkpoint("natural-battle-result-return")
	await travel_to("scifi.city")
	area = current_scene
	ck(app.can_submit_report(), "all normal route prerequisites satisfy report")
	ck(await walk_to(area, area.REPORT_POSITION, 30.0), "walk to NYC report marker")
	await tap(KEY_E)
	ck(await scene_is("res://scenes/demo_report.tscn"), "report endpoint entered by E")
	ck(app.demo_completed and app.survey_solved.size() == 3 and app.recruited_members.size() == 3, "report records all three surveys and recruits")
	shot("report-complete")
	checkpoint("nyc-report-submit")
	await click(current_scene.continue_button)
	await scene_is("res://scenes/scifi_exploration_area.tscn")
	area = current_scene
	var saved_position: Vector2 = area.hero.position
	await click(area.save_button)
	ck(await scene_is("res://scenes/save_screen.tscn"), "area Save button opened save UI")
	await click(current_scene.manual_save_buttons[0])
	await wait(4)
	var entry := manual_one()
	ck(not entry.is_empty() and entry.snapshot.demoCompleted, "manual slot one saved completed report via UI")
	ck(Vector2(float(entry.snapshot.position[0]), float(entry.snapshot.position[1])).distance_to(saved_position) < 0.01, "saved actual nonzero area foot position", entry.snapshot.position)
	write_json(expected_path, {"entry": entry, "processId": OS.get_process_id(), "state": state_oracle(), "savedPosition": [saved_position.x, saved_position.y]})
	shot("ui-manual-save")
	checkpoint("ui-save")
	restart_ready = true
	await click(current_scene.back_button)
	await scene_is("res://scenes/scifi_exploration_area.tscn")
	await tap(KEY_ESCAPE)
	await scene_is("res://scenes/scifi_world_map.tscn")
	await click(current_scene.back_button)
	await scene_is(MENU)
	write_report()
	print("ROUTE55_SAVED_FOR_RESTART")
	await click(current_scene.quit_button)
	await wait(20)
	push_error("ordinary Quit button did not end process")


func enter_survey(at: Vector2) -> void:
	var area := current_scene
	ck(await walk_to(area, at, 30.0), "walk to survey entrance " + app.current_destination_id)
	await tap(KEY_E)
	ck(await scene_is("res://scenes/survey_annex.tscn"), "E entered survey " + app.current_destination_id)


func recruit_here(member: String) -> void:
	var area := current_scene
	ck(await walk_to(area, area.npc_position, 35.0), "walk to " + member)
	await tap(KEY_E)
	ck(area.dialogue_open and not area.invite_button.disabled, "recruitment dialogue unlocked " + member)
	await click(area.invite_button)
	await wait(4)
	ck(app.recruited_members.has(member), "actual Invite recruited " + member)
	checkpoint("recruit-" + member)
	shot("recruit-" + member)


func solve_survey(destination: String) -> void:
	for room_number in [1, 2]:
		var annex := current_scene
		ck(annex.destination_id == destination and annex.room == room_number, "correct survey room " + destination + str(room_number))
		for index in 3:
			var spot: Vector2 = annex.CLUE_POSITIONS[index]
			if annex.yonkers_room_one:
				spot.y = 228.0
			elif annex.wdc_front != null:
				spot.y = 240.0
			elif annex.wdc_room_two:
				spot.y = 232.0
			var radius := 8.0 if annex.wdc_room_two or annex.wdc_front != null or annex.yonkers_room_one else 24.0
			ck(await walk_to(annex, spot, radius), "walk to clue " + destination + str(room_number) + str(index))
			await tap(KEY_E)
			ck(annex.overlay.visible and annex.overlay_mode == "clue", "E opened actual clue " + str(index))
			await click(annex.close_button)
		if room_number == 1:
			ck(await walk_to(annex, annex.NEXT_POSITION, 24.0), "walk to inner-room entrance")
			await tap(KEY_E)
			await wait(8)
			ck(app.current_annex_room == 2, "E entered inner room")
	var annex := current_scene
	ck(await walk_to(annex, annex.TERMINAL_POSITION, 22.0), "walk to analysis console " + destination)
	await tap(KEY_E)
	ck(annex.overlay_mode == "link", "six actual clues unlock evidence links")
	# Answer data is read to choose actual UI actions; progress is never assigned.
	var data: Dictionary = annex._data()
	for link in data.links:
		await click(annex.link_buttons[int(link.pair[0])])
		await click(annex.link_buttons[int(link.pair[1])])
	ck(annex._link_count() == 3, "three pairs linked by UI " + destination)
	await click(annex.close_button)
	ck(annex.overlay_mode == "question", "evidence UI opens final judgment")
	await click(annex.option_buttons[int(data.answer)])
	ck(app.survey_solved.has(destination), "survey solved by answer UI " + destination)
	shot("survey-solved-" + destination.trim_prefix("scifi."))
	checkpoint("survey-solved-" + destination)
	await click(annex.close_button)
	await click(annex.back_button)
	await wait(8)
	await click(current_scene.back_button)
	ck(await scene_is("res://scenes/scifi_exploration_area.tscn"), "survey UI returned to actual surface")


func travel_to(destination: String) -> void:
	await tap(KEY_ESCAPE)
	ck(await scene_is("res://scenes/scifi_world_map.tscn"), "Esc returned to travel map")
	var map := current_scene
	var button: Control = map.destination_buttons.get(destination)
	if button != null and not button.is_visible_in_tree():
		await click(map.region_button)
		await wait(4)
	ck(await click(button), "click destination marker " + destination)
	await wait(4)
	ck(map.route_card.visible and not map.depart_button.disabled, "normal route available " + destination)
	await click(map.depart_button)
	ck(await scene_is(String(app.area_scene_path(destination))), "travel entered destination " + destination)
	ck(app.current_destination_id == destination, "confirmed travel updated destination " + destination)
	checkpoint("travel-" + destination)


func manual_one() -> Dictionary:
	var store: Script = load("res://scripts/save_store.gd")
	for entry in store.list_entries():
		if entry.kind == "manual" and int(entry.slot) == 1:
			return entry
	return {}


func write_json(path: String, data: Dictionary) -> void:
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(JSON.stringify(data, "  ") + "\n")
	f.close()


func reload_phase() -> void:
	var expected: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(expected_path))
	ck(OS.get_process_id() != int(expected.processId), "distinct restarted process")
	ck(app.recruited_members.is_empty() and app.survey_solved.is_empty(), "fresh autoload before loading existing save")
	await click(current_scene.load_button)
	ck(await scene_is("res://scenes/save_screen.tscn"), "main-menu Load opened save UI")
	var entry := manual_one()
	ck(entry.id == expected.entry.id and entry.snapshot == expected.entry.snapshot, "same exact manual entry survived process quit")
	await click(current_scene.manual_load_buttons[0])
	ck(await scene_is("res://scenes/scifi_exploration_area.tscn"), "manual slot Load routed to saved actual area")
	var snap: Dictionary = entry.snapshot
	var bindings := {"heroName": "hero_name", "heroAppearance": "hero_appearance", "language": "language", "destination": "current_destination_id", "hero": "hero_state", "members": "member_states", "activeParty": "active_party_ids", "recruited": "recruited_members", "partyTalkSeen": "party_talk_seen", "partyBonds": "party_bonds", "fieldInsights": "field_insights", "fieldTraces": "field_traces", "jiRecordsChecked": "ji_records_checked", "relayChecked": "relay_checked", "areasVisited": "areas_visited", "machineObserved": "machine_observed", "demoCompleted": "demo_completed", "surveyClues": "survey_clues", "surveyLinks": "survey_links", "surveySolved": "survey_solved", "annexRoom": "current_annex_room", "wrongPairAttempts": "wrong_pair_attempts", "wrongJudgmentAttempts": "wrong_judgment_attempts", "growthFinalQuests": "cleared_final_quests"}
	for saved in bindings:
		ck(app.get(bindings[saved]) == snap[saved], "restarted state exact " + saved)
	for pair in [["calendarMinutes", "calendar_minutes"], ["calendarWeekIndex", "calendar_week_index"], ["locationId", "current_location_id"], ["discovered", "discovered_locations"], ["lastTravel", "last_travel"]]:
		ck(app.get(pair[1]) == snap.travel[pair[0]], "restarted travel exact " + pair[0])
	var expected_foot := Vector2(float(snap.position[0]), float(snap.position[1]))
	ck(current_scene.hero.position.distance_to(expected_foot) < 0.01, "restarted physical area position exact", [current_scene.hero.position, expected_foot])
	ck(app.can_submit_report() and app.demo_completed, "report and all journey prerequisites survive UI load")
	ck(app.play_time_seconds >= float(snap.playTimeSeconds) and app.play_time_seconds - float(snap.playTimeSeconds) < 2.0, "play time restored with bounded subsequent frames")
	shot("restarted-ui-load-verified")
	checkpoint("relaunch-ui-load-verify")
	restart_ready = true
	_finish()


func walkable(area: Node, at: Vector2, encounter: bool) -> bool:
	if area.scene_file_path.ends_with("survey_annex.tscn"):
		if at.x < 25 or at.x > 615 or at.y < 78 or at.y > 305:
			return false
		if area.wdc_front != null:
			return not area._wdc_blocked(at)
		if area.yonkers_room_one:
			return not area._yonkers_blocked(at)
		if area.wdc_room_two_walls:
			return not area._wdc_room_two_blocked(at)
		return true
	if not encounter and area.enemy_visible and at.distance_to(area.enemy_position) < 30.0:
		return false
	if area.get("v12_active") == true:
		return area._v12_walkable(at)
	if area.destination_id == "scifi.city":
		return area._city_walkable(at)
	return at.x >= 24 and at.x <= 616 and at.y >= 77 and at.y <= 306
