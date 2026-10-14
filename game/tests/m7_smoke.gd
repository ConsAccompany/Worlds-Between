extends SceneTree


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	SaveStore.root_path = "user://test-saves/m7"
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	change_scene_to_file("res://scenes/hero_setup.tscn")
	await _settle()
	var setup: Control = current_scene
	setup.get("name_input").text = "阿澈"
	setup.get("female_button").pressed.emit()
	setup.get("skip_button").pressed.emit()
	await _settle()
	if not _check(current_scene.name == "ScifiWorldMap" and app.hero_name == "阿澈" and app.hero_appearance == "female" and not app.show_initial_guide, "name, appearance and guide skip"):
		return
	var setup_save: String = app.write_auto_save("map", Vector2.ZERO, "manual_note")
	app.begin_new_run()
	if not _check(app.load_save(setup_save) and app.member_name("hero") == "阿澈" and app.hero_appearance == "female", "character setup survives load"):
		return
	for route in [0, 1]:
		app.begin_new_run()
		app.language = "zh" if route == 0 else "en"
		var order := ["scifi.city", "scifi.outskirts", "scifi.ruins"] if route == 0 else ["scifi.ruins", "scifi.outskirts", "scifi.city"]
		for destination in order:
			app.select_destination(destination)
			change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
			await _settle()
			var area: Node2D = current_scene
			if not _check(app.areas_visited.has(destination), "visit logged " + destination):
				return
			match destination:
				"scifi.city":
					if route == 0:
						area.get("hero").position = Vector2(282, 180)
						area._unhandled_input(_interact())
						area.get("invite_button").pressed.emit()
						if not _check(app.recruited_members.has("liang-xu"), "city companion invited"):
							return
				"scifi.outskirts":
					area.get("hero").position = Vector2(470, 128)
					area._unhandled_input(_interact())
					if not _check(app.relay_checked, "relay discovery"):
						return
					if route == 0:
						area.get("hero").position = Vector2(190, 150)
						area._unhandled_input(_interact())
						area.get("invite_button").pressed.emit()
						if not _check(app.recruited_members.has("zhao-ling"), "outskirts companion invited"):
							return
					area.get("hero").position = Vector2(550, 150)
					area._process(0.0)
					if not _check(app.machine_observed, "machine observation by bypass"):
						return
				"scifi.ruins":
					area.get("hero").position = Vector2(320, 250)
					area._unhandled_input(_interact())
					if not _check(app.ji_records_checked, "ruin discovery"):
						return
					area.get("hero").position = Vector2(200, 145)
					area._unhandled_input(_interact())
					area.get("invite_button").pressed.emit()
					if not _check(app.recruited_members.has("ji-cheng"), "ruin companion invited"):
						return
		if not _check(app.can_submit_report(), "report available after flexible order"):
			return
		app.select_destination("scifi.city")
		change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
		await _settle()
		var city: Node2D = current_scene
		city.get("hero").position = Vector2(470, 247)
		city._unhandled_input(_interact())
		await _settle()
		if not _check(current_scene.name == "DemoReport" and app.demo_completed, "report endpoint appears"):
			return
		var entries := SaveStore.list_entries()
		if not _check(not entries.is_empty(), "completion autosaved"):
			return
		var latest: Dictionary = entries[0]
		if not _check(bool(latest["snapshot"].get("demoCompleted", false)), "completion state saved"):
			return
		if not _check(app.load_save(String(latest["id"])) and app.can_submit_report() and app.demo_completed, "route state reloads"):
			return
		current_scene.get("map_button").pressed.emit()
		await _settle()
		if not _check(current_scene.name == "ScifiWorldMap" and current_scene.get("field_status").text.find("3/3") >= 0, "map log reflects completion"):
			return
		current_scene._open_field_log()
		if not _check(current_scene.get("field_body").text.find(app.text_for("archive_record")) >= 0, "discovery readable from map"):
			return
	change_scene_to_file("res://scenes/main_menu.tscn")
	await _settle()
	print("M7_SMOKE_OK")
	quit(0)


func _interact() -> InputEventAction:
	var event := InputEventAction.new()
	event.action = "interact"
	event.pressed = true
	return event


func _settle() -> void:
	await process_frame
	await process_frame


func _check(condition: bool, description: String) -> bool:
	if condition:
		return true
	push_error("M7 smoke check failed: " + description)
	quit(1)
	return false
