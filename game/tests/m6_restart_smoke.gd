extends SceneTree


func _initialize() -> void:
	call_deferred("_run_checks")


func _run_checks() -> void:
	SaveStore.root_path = "user://test-saves/m6"
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	var manual: Dictionary = {}
	for entry in SaveStore.list_entries():
		if entry.get("kind", "") == "manual" and int(entry.get("slot", 0)) == 1:
			manual = entry
			break
	if manual.is_empty() or not app.load_save(String(manual["id"])):
		push_error("M6 cold restart could not read manual slot 1")
		quit(1)
		return
	if app.hero_state["level"] != 17 or app.member_state("liang-xu")["jp"] != 77 or app.current_destination_id != "scifi.ruins" or not app.enemy_cleared_for_return:
		push_error("M6 cold restart state mismatch")
		quit(1)
		return
	change_scene_to_file(app.loaded_scene_path())
	await process_frame
	await process_frame
	if current_scene.name != "ScifiExplorationArea" or current_scene.get("hero").position != Vector2(276, 233) or current_scene.get("enemy_visible"):
		push_error("M6 cold restart scene mismatch")
		quit(1)
		return
	print("M6_RESTART_OK")
	quit(0)
