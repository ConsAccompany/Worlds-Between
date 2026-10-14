extends SceneTree


func _initialize() -> void:
	call_deferred("_run_checks")


func _run_checks() -> void:
	var app := root.get_node("AppState")
	change_scene_to_file("res://scenes/main_menu.tscn")
	await process_frame
	await process_frame
	var menu: Node = current_scene
	if not _check(menu != null, "menu scene loads"):
		return
	if not _check(menu.get("start_button").text == "开始探索", "Chinese menu label"):
		return
	app.toggle_language()
	await process_frame
	if not _check(menu.get("start_button").text == "Start exploring", "English menu label"):
		return
	if not _check(InputMap.has_action("move_left") and InputMap.has_action("move_right"), "movement actions"):
		return
	var start_button: Button = menu.get("start_button")
	start_button.pressed.emit()
	await process_frame
	await process_frame
	var setup: Control = current_scene
	if not _check(setup.name == "HeroSetup", "menu enters character setup"):
		return
	setup.get("skip_button").pressed.emit()
	await process_frame
	await process_frame
	var map: Node2D = current_scene
	if not _check(map != null and map.name == "ScifiWorldMap", "menu enters world map"):
		return
	change_scene_to_file("res://scenes/prototype_room.tscn")
	await process_frame
	await process_frame
	var room: Node2D = current_scene
	if not _check(room != null and room.name == "PrototypeRoom", "foundation room loads"):
		return
	if not _check(room.get("hero").texture != null, "temporary hero sprite"):
		return
	if not _check(room.get("title_label").text.begins_with("Foundation prototype"), "English room label"):
		return
	var before_x: float = room.get("hero").position.x
	Input.action_press("move_right")
	await process_frame
	await process_frame
	Input.action_release("move_right")
	if not _check(room.get("hero").position.x > before_x, "hero movement"):
		return
	var back_button: Button = room.get("back_button")
	back_button.pressed.emit()
	await process_frame
	await process_frame
	if not _check(current_scene != null and current_scene.name == "MainMenu", "prototype returns to menu"):
		return
	print("M1_SMOKE_OK")
	quit(0)


func _check(condition: bool, label: String) -> bool:
	if condition:
		return true
	push_error("M1 smoke check failed: " + label)
	quit(1)
	return false

