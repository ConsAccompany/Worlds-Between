extends SceneTree


func _initialize() -> void:
	call_deferred("_run_checks")


func _run_checks() -> void:
	SaveStore.root_path = "user://test-saves/m6"
	_clear_test_files()
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.select_destination("scifi.ruins")
	app.ji_records_checked = true
	for member_id in ["liang-xu", "zhao-ling", "ji-cheng"]:
		if not _check(app.recruit_member(member_id), "recruit before manual save: " + member_id):
			return
	app._grant_growth(app.hero_state, 630, 100)
	app.choose_job("hero", "promote")
	app.upgrade_job_skill("hero", "sword_arc")
	app.upgrade_personal_skill("hero")
	app._grant_growth(app.hero_state, 1650, 0)
	app.choose_job("hero", "switch", "firearms")
	app._grant_growth(app.hero_state, 2650, 0)
	app.choose_job("hero", "switch", "sword")
	app.hero_state["hp"] = 61
	app.member_state("zhao-ling")["ai_policy"] = "aggressive"
	change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
	await _settle()
	var area: Node2D = current_scene
	area.get("hero").position = Vector2(275, 243)
	area._open_save()
	await _settle()
	var save_screen: Control = current_scene
	if not _check(save_screen.name == "SaveScreen" and app.save_screen_mode == "save", "manual save screen opens from exploration"):
		return
	save_screen.get("manual_save_buttons")[0].pressed.emit()
	var manual := _latest("manual", 1)
	if not _check(not manual.is_empty() and manual["snapshot"]["position"] == [275.0, 243.0] and int(manual["schemaVersion"]) == 1, "manual save stores version and exact exploration position"):
		return
	if not _check(manual["snapshot"]["hero"]["job_records"]["sword"]["skills"]["sword_arc"] == 2 and manual["snapshot"]["members"].size() == 3, "manual save includes job ranks and companions"):
		return
	save_screen.get("back_button").pressed.emit()
	await _settle()
	area = current_scene
	if not _check(area.name == "ScifiExplorationArea" and area.get("hero").position == Vector2(275, 243), "back from manual save preserves area and position"):
		return

	var old_id := "manual-2-00000000.json"
	var old_entry: Dictionary = manual.duplicate(true)
	old_entry["id"] = old_id
	old_entry["slot"] = 2
	old_entry["sequence"] = 0
	old_entry["schemaVersion"] = 0
	var old_file := FileAccess.open(SaveStore.root_path.path_join(old_id), FileAccess.WRITE)
	old_file.store_string(JSON.stringify(old_entry))
	old_file.close()
	var level_before: int = app.hero_state["level"]
	if not _check(not app.load_save(old_id) and app.hero_state["level"] == level_before, "old schema is rejected without mutating game state"):
		return

	app.begin_new_run()
	change_scene_to_file("res://scenes/main_menu.tscn")
	await _settle()
	current_scene.get("load_button").pressed.emit()
	await _settle()
	save_screen = current_scene
	if not _check(save_screen.name == "SaveScreen" and save_screen.get("manual_load_buttons")[1].disabled, "main menu lists saves and disables incompatible old version"):
		return
	save_screen.get("manual_load_buttons")[0].pressed.emit()
	await _settle()
	area = current_scene
	if not _check(area.name == "ScifiExplorationArea" and area.get("hero").position == Vector2(275, 243), "main-menu load restores exact area position"):
		return
	if not _check(app.current_destination_id == "scifi.ruins" and app.ji_records_checked and app.active_party_ids.size() == 4 and app.recruited_members.size() == 3, "destination, discovery and recruit state restore"):
		return
	if not _check(app.hero_state["hp"] == 61 and app.hero_state["job_stage"] == 2 and app.hero_state["job_records"]["sword"]["skills"]["sword_arc"] == 2 and app.hero_state["job_records"].has("firearms") and app.member_state("zhao-ling")["ai_policy"] == "aggressive", "HP, cross-series job records and AI policy restore"):
		return
	if not _check(not area.get("npc_label").visible and not area.get("records_label").visible and area.get("enemy_visible"), "NPC, records and uncleared enemy render from saved state"):
		return

	var first_auto := ""
	for index in 6:
		var id: String = app.write_auto_save("area", Vector2(100 + index, 200), "before_battle")
		if not _check(id != "", "auto save writes record " + str(index)):
			return
		if index == 0:
			first_auto = id
	var autos := _autos()
	if not _check(autos.size() == 5 and autos[0]["snapshot"]["position"] == [105.0, 200.0] and not FileAccess.file_exists(SaveStore.root_path.path_join(first_auto)), "auto ring retains latest five records"):
		return

	app.select_destination("scifi.outskirts")
	change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
	await _settle()
	area = current_scene
	area.set("safe_position", Vector2(310, 210))
	area._open_encounter()
	await _settle()
	var battle: Node2D = current_scene
	var before := _latest("auto", 0)
	if not _check(before["snapshot"]["note"] == "before_battle" and before["snapshot"]["position"] == [310.0, 210.0], "encounter creates a safe prebattle checkpoint"):
		return
	battle._finish_battle(false)
	battle._return_to_menu()
	await _settle()
	if not _check(current_scene.name == "MainMenu" and _latest("auto", 0)["id"] == before["id"], "defeat returns menu without overwriting checkpoint"):
		return
	current_scene.get("load_button").pressed.emit()
	await _settle()
	current_scene.get("auto_load_buttons")[0].pressed.emit()
	await _settle()
	area = current_scene
	if not _check(area.name == "ScifiExplorationArea" and area.get("hero").position == Vector2(310, 210) and area.get("enemy_visible"), "defeat checkpoint reloads with enemy still present"):
		return

	area._open_encounter()
	await _settle()
	battle = current_scene
	battle.get("fighters")[0]["x"] = battle.get("enemy_x") - 40.0
	battle.set("enemy_hp", 1)
	battle._try_attack(0)
	var after := _latest("auto", 0)
	if not _check(after["snapshot"]["note"] == "after_battle" and after["snapshot"]["enemyCleared"] and int(after["snapshot"]["hero"]["xp"]) >= 26, "victory autosave includes rewards and cleared enemy"):
		return
	app.begin_new_run()
	if not _check(app.load_save(String(after["id"])) and app.loaded_scene_path() == "res://scenes/scifi_exploration_area.tscn", "victory save reloads after reset"):
		return
	change_scene_to_file(app.loaded_scene_path())
	await _settle()
	if not _check(not current_scene.get("enemy_visible") and current_scene.get("hero").position == Vector2(310, 210), "victory save restores cleared scene and return position"):
		return

	app.begin_new_run()
	app.select_destination("scifi.city")
	app._grant_growth(app.hero_state, 630, 0)
	app.save_return_scene = "res://scenes/scifi_exploration_area.tscn"
	app.save_return_position = Vector2(145, 188)
	var pending_id: String = app.write_manual_save(3)
	app.begin_new_run()
	if not _check(app.load_save(pending_id) and app.loaded_scene_path() == "res://scenes/growth_screen.tscn" and app.growth_return_scene.ends_with("scifi_exploration_area.tscn"), "pending ten-level choice routes loaded save through growth screen"):
		return
	app.begin_new_run()
	app.select_destination("scifi.outskirts")
	app.save_return_scene = "res://scenes/scifi_world_map.tscn"
	app.save_return_position = Vector2.ZERO
	var map_id: String = app.write_manual_save(2)
	app.begin_new_run()
	if not _check(app.load_save(map_id) and app.loaded_scene_path() == "res://scenes/scifi_world_map.tscn" and app.current_destination_id == "scifi.outskirts", "map manual save reloads to map with destination state"):
		return

	app.begin_new_run()
	app.select_destination("scifi.ruins")
	app.recruit_member("liang-xu")
	app.hero_state["level"] = 17
	app.member_state("liang-xu")["jp"] = 77
	app.enemy_cleared_for_return = true
	app.save_return_scene = "res://scenes/scifi_exploration_area.tscn"
	app.save_return_position = Vector2(276, 233)
	if not _check(app.write_manual_save(1) != "", "write sentinel for cold restart check"):
		return
	print("M6_SMOKE_OK")
	quit(0)


func _latest(kind: String, slot: int) -> Dictionary:
	for entry in SaveStore.list_entries():
		if entry.get("kind", "") == kind and (kind == "auto" or int(entry.get("slot", 0)) == slot):
			return entry
	return {}


func _autos() -> Array[Dictionary]:
	var entries: Array[Dictionary] = []
	for entry in SaveStore.list_entries():
		if entry.get("kind", "") == "auto":
			entries.append(entry)
	return entries


func _clear_test_files() -> void:
	var directory := DirAccess.open(SaveStore.root_path)
	if directory == null:
		return
	for name in directory.get_files():
		if name.ends_with(".json"):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(SaveStore.root_path.path_join(name)))


func _settle() -> void:
	await process_frame
	await process_frame


func _check(condition: bool, label: String) -> bool:
	if condition:
		return true
	push_error("M6 smoke check failed: " + label)
	quit(1)
	return false
