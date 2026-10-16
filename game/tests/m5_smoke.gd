extends SceneTree


func _initialize() -> void:
	call_deferred("_run_checks")


func _run_checks() -> void:
	var app: Node = root.get_node("AppState")
	SaveStore.root_path = "user://test-saves/m5"
	app.begin_new_run()
	var hero: Dictionary = app.hero_state
	if not _check(hero["level"] == 1 and hero["aptitudes"] == [60, 60, 60, 60], "hero begins at level 1 with four 60 aptitudes"):
		return
	if not _check(GrowthRules.can_enter(hero, "sword") and GrowthRules.can_enter(hero, "firearms") and GrowthRules.can_enter(hero, "tactics") and GrowthRules.can_enter(hero, "relics"), "hero can enter four MVP series"):
		return
	if not _check(GrowthRules.jp_cost(hero, "sword", 2) == 35, "60 aptitude uses base JP cost"):
		return
	app._grant_growth(hero, 630, 100)
	if not _check(hero["level"] == 10 and hero["pending_job_choices"] == 1 and hero["hp"] == hero["max_hp"] and hero["energy"] == hero["max_energy"], "level 10 requires a choice and levels restore full state"):
		return
	app._grant_growth(hero, 500, 0)
	if not _check(hero["level"] == 10 and hero["xp"] == 500, "XP banks while job choice is pending"):
		return
	if not _check(app.choose_job("hero", "promote") and hero["job_stage"] == 2 and hero["level"] > 10, "promotion unlocks stage 2 and resumes XP"):
		return
	var stage_skill: String = GrowthRules.current_skill_id(hero)
	if not _check(stage_skill == "sword_arc" and GrowthRules.skill_rank(hero, stage_skill) == 1, "stage 2 skill unlocks"):
		return
	var before_jp: int = hero["jp"]
	if not _check(app.upgrade_job_skill("hero", stage_skill) and GrowthRules.skill_rank(hero, stage_skill) == 2 and hero["jp"] == before_jp - 35, "JP upgrades the unlocked job skill"):
		return
	if not _check(app.upgrade_personal_skill("hero") and hero["personal_skill_rank"] == 2 and hero["jp"] == before_jp - 70, "JP also upgrades a personal skill"):
		return
	app._grant_growth(hero, _xp_until_level(hero, 20), 0)
	if not _check(hero["level"] == 20 and hero["pending_job_choices"] == 1, "next ten-level threshold is mandatory"):
		return
	if not _check(app.choose_job("hero", "switch", "firearms") and hero["job_series"] == "firearms" and hero["job_stage"] == 1, "switch to a new eligible series starts at stage 1"):
		return
	app._grant_growth(hero, _xp_until_level(hero, 30), 0)
	if not _check(app.choose_job("hero", "stay") and hero["job_series"] == "firearms" and hero["job_stage"] == 1, "staying is a valid choice"):
		return
	app._grant_growth(hero, _xp_until_level(hero, 40), 0)
	if not _check(app.choose_job("hero", "switch", "sword") and hero["job_stage"] == 2 and GrowthRules.skill_rank(hero, "sword_arc") == 2 and hero["personal_skill_rank"] == 2, "returning restores stage and JP ranks while personal skill persists"):
		return
	if not _check(hero["level"] == 40 and hero["pending_job_choices"] == 0, "growth data has no level cap at MVP boundary"):
		return

	app.begin_new_run()
	app.hero_state["level"] = 23
	if not _check(app.recruit_member("liang-xu") and app.recruit_member("zhao-ling"), "two companions join at hero level"):
		return
	var liang: Dictionary = app.member_state("liang-xu")
	var zhao: Dictionary = app.member_state("zhao-ling")
	if not _check(liang["level"] == 23 and liang["job_stage"] == 3 and GrowthRules.skill_rank(liang, "tactics_rally") == 1 and GrowthRules.skill_rank(liang, "tactics_s3a") == 1, "recruit has level-matched job progress"):
		return
	if not _check(GrowthRules.jp_cost(liang, "tactics", 2) < GrowthRules.jp_cost(app.hero_state, "sword", 2), "high aptitude gives lower JP demand"):
		return
	if not _check(not GrowthRules.can_enter(liang, "sword") and not GrowthRules.can_enter(zhao, "relics"), "aptitudes below 60 block a series"):
		return
	app.active_party_ids.erase("zhao-ling")
	var rewards: Dictionary = app.award_battle_rewards("patrol")
	if not _check(rewards == {"xp": 26, "jp": 12} and liang["xp"] == 26 and liang["jp"] == 12 and zhao["xp"] == 7 and zhao["jp"] == 3, "reserve receives rounded quarter XP and JP"):
		return
	if not _check(app.hero_state["xp"] == 26 and app.hero_state["jp"] == 12, "active hero receives full rewards independently"):
		return

	app.begin_new_run()
	app._grant_growth(app.hero_state, 630, 0)
	app.growth_return_scene = "res://scenes/scifi_world_map.tscn"
	change_scene_to_file("res://scenes/growth_screen.tscn")
	await process_frame
	await process_frame
	var growth: Control = current_scene
	if not _check(growth.get("back_button").disabled and growth.get("promote_button").disabled == false, "mandatory job selection is shown in playable screen"):
		return
	growth.get("promote_button").pressed.emit()
	if not _check(app.hero_state["job_stage"] == 2 and not growth.get("back_button").disabled, "playable promotion unlocks return"):
		return
	growth.get("back_button").pressed.emit()
	await process_frame
	await process_frame
	if not _check(current_scene.name == "ScifiWorldMap", "growth screen returns to world map"):
		return
	app.begin_battle("patrol", Vector2(330, 215))
	change_scene_to_file("res://scenes/battle_arena.tscn")
	await process_frame
	await process_frame
	var promoted_battle: Node2D = current_scene
	promoted_battle.get("fighters")[0]["x"] = promoted_battle.get("enemy_x") - 40.0
	promoted_battle._toggle_pause()
	var skill_buttons: Array = promoted_battle.get("pause_job_skill_buttons")
	if not _check(skill_buttons[0].visible and skill_buttons[1].visible, "both learned stages are selectable in pause menu"):
		return
	promoted_battle._queue_job_skill("sword_slash")
	promoted_battle._toggle_pause()
	if not _check(promoted_battle.get("enemy_hp") == 64 - 15, "first-stage skill remains usable after promotion"):
		return
	promoted_battle.get("fighters")[0]["skill_cooldown"] = 0.0
	promoted_battle._toggle_pause()
	promoted_battle._queue_job_skill("sword_arc")
	promoted_battle._toggle_pause()
	if not _check(promoted_battle.get("enemy_hp") == 64 - 15 - 18, "second-stage skill is usable in the same job tree"):
		return
	promoted_battle.get("fighters")[0]["skill_cooldown"] = 0.0
	if not _check(promoted_battle._use_skill(0) and promoted_battle.get("next_attack_bonus") == 5, "personal skill remains usable after promotion"):
		return

	app.begin_new_run()
	app.hero_state["level"] = 9
	app.hero_state["xp"] = GrowthRules.xp_to_next(9) - 1
	app.hero_state["hp"] = 40
	app.hero_state["energy"] = 20
	app.select_destination("scifi.outskirts")
	app.begin_battle("patrol", Vector2(330, 215))
	change_scene_to_file("res://scenes/battle_arena.tscn")
	await process_frame
	await process_frame
	var battle: Node2D = current_scene
	battle.get("fighters")[0]["x"] = battle.get("enemy_x") - 40.0
	battle.set("enemy_hp", 10)
	if not _check(battle._use_job_skill(0, "sword_slash") and battle.get("battle_won"), "unlocked job skill wins a battle"):
		return
	if not _check(app.hero_state["level"] == 10 and app.hero_state["pending_job_choices"] == 1 and app.hero_state["hp"] == app.hero_state["max_hp"], "victory grants XP and level-up restores state"):
		return
	battle._return_after_result()
	await process_frame
	await process_frame
	if not _check(current_scene.name == "GrowthScreen" and current_scene.get("back_button").disabled, "battle victory routes mandatory job choice to growth screen"):
		return
	print("M5_SMOKE_OK")
	quit(0)


func _xp_until_level(member: Dictionary, target_level: int) -> int:
	var required := -int(member.get("xp", 0))
	for level in range(int(member["level"]), target_level):
		required += GrowthRules.xp_to_next(level)
	return required


func _check(condition: bool, label: String) -> bool:
	if condition:
		return true
	push_error("M5 smoke check failed: " + label)
	quit(1)
	return false
