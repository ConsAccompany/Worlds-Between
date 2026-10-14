extends SceneTree

const CONTENT := preload("res://scripts/survey_content.gd")


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	SaveStore.root_path = "user://test-saves/m7"
	var app: Node = root.get_node("AppState")
	for destination in app.DESTINATIONS:
		for locale in ["zh", "en"]:
			var content: Dictionary = CONTENT.DATA[destination][locale]
			if not _check(content["rooms"].size() == 2 and content["clues"].size() == 6 and content["options"].size() == 3 and int(content["answer"]) in [0, 1, 2], "bilingual survey content " + destination + "/" + locale):
				return
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
	app.play_time_seconds = 125.0
	var setup_save: String = app.write_auto_save("map", Vector2.ZERO, "manual_note")
	app.begin_new_run()
	if not _check(app.load_save(setup_save) and app.member_name("hero") == "阿澈" and app.hero_appearance == "female" and app.play_time_seconds >= 125.0, "character setup and run time survive load"):
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
			var entrance := Vector2(558, 143) if destination == "scifi.city" else (Vector2(558, 277) if destination == "scifi.outskirts" else Vector2(548, 142))
			area.get("hero").position = entrance
			area._unhandled_input(_interact())
			await _settle()
			if not _check(current_scene.name == "SurveyAnnex" and app.current_annex_room == 1, "survey entrance " + destination):
				return
			for room_index in [1, 2]:
				var annex: Node2D = current_scene
				for local_index in 3:
					annex.get("hero").position = Vector2(163 + local_index * 157, 165)
					annex._unhandled_input(_interact())
					if not _check(annex.get("overlay").visible, "clue can be read"):
						return
					annex.get("close_button").pressed.emit()
				if room_index == 1:
					annex.get("hero").position = Vector2(580, 257)
					annex._unhandled_input(_interact())
					await _settle()
					if not _check(current_scene.name == "SurveyAnnex" and app.current_annex_room == 2, "inner survey room"):
						return
			var final_annex: Node2D = current_scene
			final_annex.get("hero").position = Vector2(320, 263)
			final_annex._unhandled_input(_interact())
			var correct: int = final_annex._data()["answer"]
			final_annex.get("option_buttons")[(correct + 1) % 3].pressed.emit()
			if not _check(not app.survey_solved.has(destination) and final_annex.get("overlay_message") != "", "wrong answer is retryable"):
				return
			var jp_before: int = app.hero_state["jp"]
			final_annex.get("option_buttons")[correct].pressed.emit()
			if not _check(app.survey_solved.has(destination) and int(app.hero_state["jp"]) == jp_before + 8, "survey solved and JP awarded once " + destination):
				return
			final_annex._close_overlay()
			final_annex._open_question()
			if not _check(int(app.hero_state["jp"]) == jp_before + 8 and final_annex.get("overlay_mode") == "message", "survey replay gives no extra JP"):
				return
			final_annex._close_overlay()
			if route == 0 and destination == "scifi.city":
				final_annex.get("hero").position = Vector2(311, 258)
				final_annex._open_save()
				await _settle()
				if not _check(current_scene.name == "SaveScreen", "annex opens manual save"):
					return
				var annex_save: String = app.write_manual_save(1)
				app.begin_new_run()
				if not _check(app.load_save(annex_save) and app.loaded_scene_path() == "res://scenes/survey_annex.tscn" and app.current_annex_room == 2, "annex save loads correct room"):
					return
				change_scene_to_file(app.loaded_scene_path())
				await _settle()
				if not _check(current_scene.get("hero").position == Vector2(311, 258) and app.survey_solved.has(destination) and app.survey_clues.size() == 6, "annex position and clues restored"):
					return
				final_annex = current_scene
			final_annex._back_room()
			await _settle()
			current_scene._back_room()
			await _settle()
			if not _check(current_scene.name == "ScifiExplorationArea" and current_scene.get("hero").position == entrance, "survey returns to entrance"):
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
