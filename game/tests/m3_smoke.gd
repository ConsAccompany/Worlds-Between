extends SceneTree


func _initialize() -> void:
	call_deferred("_run_checks")


func _run_checks() -> void:
	var app: Node = root.get_node("AppState")
	SaveStore.root_path = "user://test-saves/m3"
	var survivor := BattleRules.recover_after_battle({"hp": 42, "max_hp": 105, "energy": 7, "max_energy": 55})
	if not _check(survivor["hp"] == 63 and survivor["energy"] == 18, "survivor adds 20 percent of each maximum"):
		return
	var capped := BattleRules.recover_after_battle({"hp": 99, "max_hp": 100, "energy": 58, "max_energy": 60})
	if not _check(capped["hp"] == 100 and capped["energy"] == 60, "recovery caps at maximum"):
		return
	var downed := BattleRules.recover_after_battle({"hp": 0, "max_hp": 105, "energy": 30, "max_energy": 55})
	if not _check(downed["hp"] == 11 and downed["energy"] == 6, "downed member revives at 10 percent"):
		return

	app.begin_new_run()
	app.select_destination("scifi.outskirts")
	app.begin_battle("patrol", Vector2(330, 215))
	change_scene_to_file("res://scenes/battle_arena.tscn")
	await _settle()
	var battle: Node2D = current_scene
	if not _check(battle != null and battle.name == "BattleArena", "battle scene opens"):
		return
	if not _check(battle.get("enemy_id") == "patrol" and battle.get("enemy_hp") == 64, "patrol fixed difficulty"):
		return
	app.toggle_language()
	await process_frame
	if not _check(battle.get("title_label").text.begins_with("Real-time battle"), "English battle labels"):
		return
	if not _check(battle.get("feedback_label").get_minimum_size().x <= 608.0, "English combat feedback fits viewport"):
		return
	app.toggle_language()
	if not _check(app.last_battle_transition_ms < 1000.0, "encounter transition under one second"):
		return
	if not _check(not InputMap.has_action("battle_jump"), "no battle jump action"):
		return
	var before_x: float = battle.get("fighters")[0]["x"]
	Input.action_press("move_right")
	await _settle()
	Input.action_release("move_right")
	if not _check(battle.get("fighters")[0]["x"] > before_x, "horizontal movement"):
		return
	if not _check(not battle._try_attack() and battle.get("enemy_hp") == 64, "out-of-range attack misses"):
		return
	battle.get("fighters")[0]["attack_cooldown"] = 0.0
	battle.get("fighters")[0]["x"] = battle.get("enemy_x") - 45.0
	if not _check(battle._try_attack() and battle.get("enemy_hp") == 45, "melee attack damages enemy"):
		return
	var energy_before: int = app.hero_state["energy"]
	if not _check(battle._try_dodge() and app.hero_state["energy"] == energy_before - 12, "dodge consumes energy"):
		return
	app.hero_state["hp"] = 60
	var hp_before: int = app.hero_state["hp"]
	battle._apply_enemy_hit()
	if not _check(app.hero_state["hp"] == hp_before, "dodge avoids damage"):
		return
	battle.get("fighters")[0]["dodge_time"] = 0.0
	Input.action_press("battle_guard")
	battle._apply_enemy_hit()
	Input.action_release("battle_guard")
	if not _check(app.hero_state["hp"] == hp_before - 4 and app.hero_state["energy"] == energy_before - 18, "guard reduces damage and spends energy"):
		return
	battle._apply_enemy_hit()
	if not _check(app.hero_state["hp"] == hp_before - 16, "unguarded hit uses fixed enemy damage"):
		return
	var energy_after: int = app.hero_state["energy"]
	await _settle()
	if not _check(app.hero_state["energy"] == energy_after, "energy does not recover naturally"):
		return
	battle.set("enemy_hp", 19)
	battle.get("fighters")[0]["attack_cooldown"] = 0.0
	Input.action_press("battle_attack")
	await process_frame
	Input.action_release("battle_attack")
	if not _check(battle.get("battle_finished") and battle.get("battle_won"), "attack finishes battle"):
		return
	if not _check(app.hero_state["hp"] == hp_before - 16 + 20 and app.hero_state["energy"] == energy_after + 12, "victory applies 20 percent recovery to remaining values"):
		return
	battle._return_after_result()
	await _settle()
	if not _check(current_scene.name == "ScifiExplorationArea" and not current_scene.get("enemy_visible"), "victory returns to cleared exploration scene"):
		return
	if not _check(current_scene.get("hero").position == Vector2(330, 215), "return position is restored"):
		return

	app.select_destination("scifi.ruins")
	app.begin_battle("sentry", Vector2(380, 200))
	change_scene_to_file("res://scenes/battle_arena.tscn")
	await _settle()
	battle = current_scene
	if not _check(battle.get("enemy_id") == "sentry" and battle.get("enemy_hp") == 96, "sentry has higher fixed difficulty"):
		return
	battle.get("fighters")[0]["x"] = battle.get("enemy_x") - 45.0
	app.hero_state["hp"] = 10
	battle._apply_enemy_hit()
	if not _check(battle.get("battle_finished") and not battle.get("battle_won"), "sentry can defeat the party"):
		return
	await create_timer(2.1).timeout
	await _settle()
	if not _check(current_scene.name == "MainMenu", "defeat automatically returns to main menu"):
		return
	(current_scene.get("start_button") as Button).pressed.emit()
	await _settle()
	if not _check(app.hero_state["hp"] == 100 and app.hero_state["energy"] == 60, "new run resets combat state"):
		return
	print("M3_SMOKE_OK")
	quit(0)


func _settle() -> void:
	await process_frame
	await process_frame


func _check(condition: bool, label: String) -> bool:
	if condition:
		return true
	push_error("M3 smoke check failed: " + label)
	quit(1)
	return false
