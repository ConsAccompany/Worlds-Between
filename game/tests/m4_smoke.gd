extends SceneTree


func _initialize() -> void:
	call_deferred("_run_checks")


func _run_checks() -> void:
	var app: Node = root.get_node("AppState")
	SaveStore.root_path = "user://test-saves/m4"
	app.begin_new_run()
	app.hero_state["level"] = 23
	for entry in [
		["scifi.city", "liang-xu"],
		["scifi.outskirts", "zhao-ling"],
		["scifi.ruins", "ji-cheng"],
	]:
		var area_id: String = entry[0]
		var member_id: String = entry[1]
		app.select_destination(area_id)
		change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
		await _settle()
		var area: Node2D = current_scene
		area.get("hero").position = area.get("npc_position")
		_interact(area)
		if not _check(area.get("dialogue_open"), "recruitment dialogue opens: " + member_id):
			return
		app.toggle_language()
		await process_frame
		if not _check(area.get("dialogue_text").get_line_count() <= 4, "English recruitment text fits: " + member_id):
			return
		app.toggle_language()
		if member_id == "ji-cheng":
			if not _check(area.get("invite_button").disabled, "Ji Cheng requires records investigation"):
				return
		area.get("later_button").pressed.emit()
		if not _check(not app.recruited_members.has(member_id), "declining does not recruit: " + member_id):
			return
		area.get("back_button").pressed.emit()
		await _settle()
		app.select_destination(area_id)
		change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
		await _settle()
		area = current_scene
		if member_id == "ji-cheng":
			area.get("hero").position = Vector2(320, 250)
			_interact(area)
			if not _check(app.ji_records_checked, "records investigation persists"):
				return
		area.get("hero").position = area.get("npc_position")
		_interact(area)
		if not _check(area.get("dialogue_open") and not area.get("invite_button").disabled, "return visit allows invitation: " + member_id):
			return
		area.get("invite_button").pressed.emit()
		if not _check(app.recruited_members.has(member_id) and app.active_party_ids.has(member_id), "companion joins: " + member_id):
			return
		var member: Dictionary = app.member_state(member_id)
		if not _check(member["level"] == 23 and member["job_stage"] == 3 and member["learned_skill_ids"].has("advanced"), "recruit level and job seed match hero: " + member_id):
			return
		if not _check(not area.get("npc_label").visible, "recruited companion leaves exploration view: " + member_id):
			return
	if not _check(app.active_party_ids.size() == 4 and app.PARTY_CAPACITY == 5, "four active characters within five slots"):
		return
	if not _check(not app.recruit_member("liang-xu"), "duplicate recruitment rejected"):
		return

	app.select_destination("scifi.outskirts")
	app.begin_battle("patrol", Vector2(330, 215))
	change_scene_to_file("res://scenes/battle_arena.tscn")
	await _settle()
	var battle: Node2D = current_scene
	if not _check(battle.get("fighters").size() == 4 and battle.get("party_buttons").size() == 5, "four fighters and five party slots"):
		return
	battle._choose_control(1)
	if not _check(battle.get("controlled_index") == 1, "control switches to Liang Xu"):
		return
	var swap := InputEventAction.new()
	swap.action = "battle_switch"
	swap.pressed = true
	battle._input(swap)
	if not _check(battle.get("controlled_index") == 2, "Tab action switches to the next character"):
		return
	battle._choose_control(1)
	if not _check(battle.get("quick_skill_button").text.contains("战术校准"), "quick skill follows controlled actor"):
		return
	battle._toggle_pause()
	var frozen_x: float = battle.get("enemy_x")
	var frozen_windup: float = battle.get("enemy_windup")
	battle._process(2.0)
	if not _check(battle.get("paused") and battle.get("enemy_x") == frozen_x and battle.get("enemy_windup") == frozen_windup, "pause freezes battle time"):
		return
	battle._switch_control()
	battle._toggle_auto()
	if not _check(battle.get("controlled_index") == 1 and not battle.get("auto_mode"), "pause blocks switching and auto toggle"):
		return
	if not _check(battle.get("pause_title").text.contains("梁序"), "pause menu belongs to controlled actor"):
		return
	battle._select_order_target("zhao-ling")
	battle._issue_order("defend")
	if not _check(battle.get("fighters")[2]["command"] == "defend", "temporary teammate order assigned"):
		return
	var zhao_x: float = battle.get("fighters")[2]["x"]
	battle.get("fighters")[2]["x"] = battle.get("enemy_x") - 50.0
	battle.set("enemy_windup", 0.4)
	battle._update_ai(2, 1.0 / 60.0)
	if not _check(battle.get("fighters")[2]["guard"] and battle.get("fighters")[2]["dodge_time"] == 0.0, "defend order prioritizes guarding telegraphed hit"):
		return
	battle.get("fighters")[2]["x"] = zhao_x
	battle.set("enemy_windup", 0.0)
	battle._cycle_ai_policy()
	if not _check(app.member_state("zhao-ling")["ai_policy"] == "aggressive", "configurable AI policy saved on teammate"):
		return
	battle._queue_skill()
	var liang_energy: int = app.member_state("liang-xu")["energy"]
	battle._toggle_pause()
	if not _check(not battle.get("paused") and app.member_state("liang-xu")["energy"] == liang_energy - 16, "queued controlled skill executes on resume"):
		return
	battle._toggle_auto()
	if not _check(battle.get("auto_mode"), "full auto enabled"):
		return
	for frame in 720:
		if battle.get("battle_finished"):
			break
		battle._process(1.0 / 60.0)
	if not _check(battle.get("battle_finished") and battle.get("battle_won") and battle.get("player_attack_count") > 1, "four-person AI party wins"):
		return
	battle._return_after_result()
	await _settle()
	if not _check(current_scene.name == "ScifiExplorationArea", "party returns to exploration"):
		return
	if not _check(app.active_party_ids.size() == 4 and app.member_state("liang-xu")["hp"] > 0, "party and recovered states persist"):
		return

	app.begin_battle("sentry", Vector2(340, 200))
	change_scene_to_file("res://scenes/battle_arena.tscn")
	await _settle()
	battle = current_scene
	if not _check(app.member_state("zhao-ling")["ai_policy"] == "aggressive" and battle.get("fighters")[2]["command"] == "default", "AI policy persists while temporary order expires"):
		return
	app.member_state("ji-cheng")["hp"] = 0
	battle.get("fighters")[0]["x"] = battle.get("enemy_x") - 45.0
	battle.set("enemy_hp", 1)
	battle._try_attack(0)
	if not _check(battle.get("battle_won") and app.member_state("ji-cheng")["hp"] == 8, "downed companion revives at 10 percent after victory"):
		return
	print("M4_SMOKE_OK")
	quit(0)


func _interact(area: Node2D) -> void:
	var event := InputEventAction.new()
	event.action = "interact"
	event.pressed = true
	area._unhandled_input(event)


func _settle() -> void:
	await process_frame
	await process_frame


func _check(condition: bool, label: String) -> bool:
	if condition:
		return true
	push_error("M4 smoke check failed: " + label)
	quit(1)
	return false
