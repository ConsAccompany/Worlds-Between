extends SceneTree


func _initialize() -> void:
	call_deferred("_run_checks")


func _run_checks() -> void:
	var app: Node = root.get_node("AppState")
	SaveStore.root_path = "user://test-saves/m2"
	change_scene_to_file("res://scenes/main_menu.tscn")
	await _settle()
	var menu: Node = current_scene
	(menu.get("start_button") as Button).pressed.emit()
	await _settle()
	if not _check(current_scene != null and current_scene.name == "ScifiWorldMap", "menu opens world map"):
		return
	var world_map: Node = current_scene
	if not _check(world_map.get("destination_buttons").size() == 3, "three selectable map destinations"):
		return
	if not _check(world_map.get("title_label").text.contains("科技板块"), "Chinese map title"):
		return
	app.toggle_language()
	await process_frame
	if not _check(world_map.get("title_label").text.contains("Science region"), "English map title"):
		return
	app.toggle_language()
	for id in app.DESTINATIONS:
		world_map = current_scene
		var button: Button = world_map.get("destination_buttons")[id]
		button.pressed.emit()
		await _settle()
		var area: Node2D = current_scene
		if not _check(area != null and area.name == "ScifiExplorationArea", "destination opens area: " + id):
			return
		if not _check(area.get("destination_id") == id, "area ID: " + id):
			return
		if not _check(area.get("hero").texture != null, "exploration sprite: " + id):
			return
		var before_x: float = area.get("hero").position.x
		Input.action_press("move_right")
		await process_frame
		await process_frame
		Input.action_release("move_right")
		if not _check(area.get("hero").position.x > before_x, "free movement: " + id):
			return
		area.get("hero").position = area.get("npc_position")
		var interact := InputEventAction.new()
		interact.action = "interact"
		interact.pressed = true
		area._unhandled_input(interact)
		if not _check(area.get("dialogue_open"), "NPC interaction: " + id):
			return
		area.get("later_button").pressed.emit()
		if id != "scifi.city":
			if not _check(area.get("enemy_visible"), "enemy visible: " + id):
				return
			area.get("hero").position = Vector2(565, 170)
			await process_frame
			if not _check(area.get("bypass_reached") and area.get("encounter_count") == 0, "enemy bypass: " + id):
				return
			area.get("hero").position = area.get("enemy_position")
			Input.action_press("move_right")
			await process_frame
			Input.action_release("move_right")
			await _settle()
			if not _check(current_scene != null and current_scene.name == "BattleArena", "enemy contact opens battle: " + id):
				return
			current_scene._finish_battle(true)
			current_scene._return_after_result()
			await _settle()
			area = current_scene
			if not _check(not area.get("enemy_visible"), "victory clears enemy until leaving: " + id):
				return
		area.get("back_button").pressed.emit()
		await _settle()
		if not _check(current_scene != null and current_scene.name == "ScifiWorldMap", "area returns to map: " + id):
			return
		if id != "scifi.city":
			(current_scene.get("destination_buttons")[id] as Button).pressed.emit()
			await _settle()
			if not _check(current_scene.get("encounter_count") == 0 and current_scene.get("enemy_visible"), "enemy resets on reentry: " + id):
				return
			current_scene.get("back_button").pressed.emit()
			await _settle()
	print("M2_SMOKE_OK")
	quit(0)


func _settle() -> void:
	await process_frame
	await process_frame


func _check(condition: bool, label: String) -> bool:
	if condition:
		return true
	push_error("M2 smoke check failed: " + label)
	quit(1)
	return false
