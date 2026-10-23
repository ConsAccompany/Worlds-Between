extends SceneTree

const CONTENT := preload("res://scripts/survey_content.gd")
const TALK := preload("res://scripts/party_talk_content.gd")
# Ruins anchors when the v12-based Capitol west chain (the creator-authorized ordinary default) is active.
# Loaded at run time: preloading would compile the area script before the AppState autoload exists.
const RUINS_V12_PATH := "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12_20261017-235608-66d00477.gd"


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	SaveStore.root_path = "user://test-saves/m7"
	var app: Node = root.get_node("AppState")
	var ruins_v12_anchors: Dictionary = load(RUINS_V12_PATH).get_script_constant_map()
	app.begin_new_run()
	app.play_time_seconds = 65.0
	app.playtest_events = [
		{"type": "location", "destination": "scifi.city", "atSeconds": 10.0},
		{"type": "location", "destination": "", "atSeconds": 20.0},
		{"type": "location", "destination": "scifi.ruins", "atSeconds": 25.0},
		{"type": "location", "destination": "", "atSeconds": 45.0},
		{"type": "location", "destination": "scifi.city", "atSeconds": 55.0},
	]
	var split: Dictionary = app.playtest_time_by_destination()
	if not _check(split["scifi.city"] == 20.0 and split["scifi.ruins"] == 20.0 and split["map_and_setup"] == 25.0 and split["scifi.outskirts"] == 0.0, "destination time accumulates across revisits"):
		return
	if not _check(TALK.TOPICS.size() == 6, "six companion conversation topics"):
		return
	for topic in TALK.TOPICS:
		for locale in ["zh", "en"]:
			if not _check(topic[locale]["lines"].size() >= 3 and String(topic[locale]["title"]) != "", "bilingual conversation " + String(topic["id"])):
				return
	for destination in app.DESTINATIONS:
		for locale in ["zh", "en"]:
			var content: Dictionary = CONTENT.DATA[destination][locale]
			if not _check(content["rooms"].size() == 2 and content["clues"].size() == 6 and content["links"].size() == 3 and content["options"].size() == 3 and int(content["answer"]) in [0, 1, 2], "bilingual survey content " + destination + "/" + locale):
				return
			for link in content["links"]:
				if not _check(link["pair"].size() == 2 and int(link["pair"][0]) in [0, 1, 2, 3, 4, 5] and int(link["pair"][1]) in [0, 1, 2, 3, 4, 5], "valid evidence pair " + destination + "/" + locale):
					return
			var used_clues: Array = []
			for link in content["links"]:
				for clue_index in link["pair"]:
					if not _check(not used_clues.has(clue_index), "each clue belongs to one link " + destination + "/" + locale):
						return
					used_clues.append(clue_index)
			if not _check(used_clues.size() == 6, "all six clues are linked " + destination + "/" + locale):
				return
		for index in 3:
			if not _check(CONTENT.DATA[destination]["zh"]["links"][index]["pair"] == CONTENT.DATA[destination]["en"]["links"][index]["pair"], "same bilingual evidence links " + destination):
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
		var assist_positions := {"scifi.city": Vector2(120, 187), "scifi.outskirts": Vector2(505, 258), "scifi.ruins": Vector2(505, 275)}
		var trace_positions := {"scifi.city": [Vector2(285, 267), Vector2(378, 181)], "scifi.outskirts": [Vector2(125, 240), Vector2(408, 95)], "scifi.ruins": [Vector2(115, 245), Vector2(470, 115)]}
		var assistants := {"scifi.city": "liang-xu", "scifi.outskirts": "zhao-ling", "scifi.ruins": "ji-cheng"}
		for destination in order:
			app.select_destination(destination)
			change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
			await _settle()
			var area: Node2D = current_scene
			if not _check(app.areas_visited.has(destination), "visit logged " + destination):
				return
			var ruins_v12: bool = destination == "scifi.ruins" and area.get("v12_active") == true
			if destination == "scifi.ruins":
				print("M7_RUINS_ANCHORS ", "v12" if ruins_v12 else "legacy")
			# v12 anchors mark props; stand on the nearest walkable mask point, as a player must.
			var ruins_stand := {}
			if ruins_v12:
				for anchor in ["V12_SURVEY", "V12_RECORDS", "V12_NPC", "V12_ASSIST"]:
					ruins_stand[anchor] = area._v12_safe(ruins_v12_anchors[anchor])
				assist_positions["scifi.ruins"] = ruins_stand["V12_ASSIST"]
				trace_positions["scifi.ruins"] = [area._v12_safe(ruins_v12_anchors["V12_TRACES"][0]), area._v12_safe(ruins_v12_anchors["V12_TRACES"][1])]
			match destination:
				"scifi.city":
					if route == 0:
						area.get("hero").position = Vector2(282, 180)
						area._unhandled_input(_interact())
						if not _check(_recruit_dialogue_ready(area), "city recruitment dialogue opens"):
							return
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
						if not _check(_recruit_dialogue_ready(area), "outskirts recruitment dialogue opens"):
							return
						area.get("invite_button").pressed.emit()
						if not _check(app.recruited_members.has("zhao-ling"), "outskirts companion invited"):
							return
					area.get("hero").position = Vector2(544, 150)
					Input.action_press("move_right")
					await process_frame
					await process_frame
					Input.action_release("move_right")
					if not _check(app.machine_observed, "machine observation by bypass"):
						return
				"scifi.ruins":
					area.get("hero").position = ruins_stand["V12_RECORDS"] if ruins_v12 else Vector2(320, 250)
					area._unhandled_input(_interact())
					if not _check(app.ji_records_checked, "ruin discovery"):
						return
					area.get("hero").position = ruins_stand["V12_NPC"] if ruins_v12 else Vector2(200, 145)
					area._unhandled_input(_interact())
					if not _check(_recruit_dialogue_ready(area), "ruin recruitment dialogue opens"):
						return
					area.get("invite_button").pressed.emit()
					if not _check(app.recruited_members.has("ji-cheng"), "ruin companion invited"):
						return
			area.get("hero").position = assist_positions[destination]
			area._unhandled_input(_interact())
			if not _check(area.get("dialogue_open") and area.get("dialogue_mode") == "assist", "field station opens " + destination):
				return
			var assistant_id: String = assistants[destination]
			if not _check(area.get("invite_button").disabled and not app.field_insights.has(destination), "field station requires traces before interpretation " + destination):
				return
			area.get("later_button").pressed.emit()
			for trace_index in 2:
				area.get("hero").position = trace_positions[destination][trace_index]
				area._unhandled_input(_interact())
				var trace_key := "%s:%d" % [destination, trace_index]
				if not _check(app.field_traces.has(trace_key) and area.get("dialogue_mode") == "trace" and area.get("dialogue_text").text == app.text_for("field_trace_" + destination.trim_prefix("scifi.") + "_%d" % trace_index), "bilingual trace discovery " + trace_key):
					return
				area.get("later_button").pressed.emit()
				area._unhandled_input(_interact())
				if not _check(app.field_trace_count(destination) == trace_index + 1, "trace replay does not duplicate progress " + trace_key):
					return
				area.get("later_button").pressed.emit()
			area.get("hero").position = assist_positions[destination]
			area._unhandled_input(_interact())
			if app.recruited_members.has(assistant_id):
				var assistant_jp: int = app.member_state(assistant_id)["jp"]
				var assistant_bond: int = int(app.party_bonds[assistant_id])
				area.get("invite_button").pressed.emit()
				if not _check(app.field_insights.has(destination) and int(app.member_state(assistant_id)["jp"]) == assistant_jp + 4 and int(app.party_bonds[assistant_id]) == assistant_bond + 2, "companion field skill grants one-time progress " + destination):
					return
				area.get("invite_button").pressed.emit()
				if not _check(int(app.member_state(assistant_id)["jp"]) == assistant_jp + 4 and int(app.party_bonds[assistant_id]) == assistant_bond + 2, "field skill replay cannot farm rewards " + destination):
					return
			else:
				if not _check(area.get("invite_button").disabled and not app.field_insights.has(destination), "field station waits for optional recruitment " + destination):
					return
			area.get("later_button").pressed.emit()
			var entrance: Vector2 = Vector2(558, 166) if destination == "scifi.city" else (Vector2(558, 277) if destination == "scifi.outskirts" else (ruins_stand["V12_SURVEY"] if ruins_v12 else Vector2(548, 142)))
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
			if not _check(final_annex.get("overlay_mode") == "link", "six clues open evidence links " + destination):
				return
			final_annex.get("link_buttons")[0].pressed.emit()
			final_annex.get("notes_button").pressed.emit()
			if not _check(final_annex.get("overlay_mode") == "notes" and final_annex.get("overlay_body").text.find(String(final_annex._data()["clues"][0]["text"])) >= 0, "collected clue body readable during links " + destination):
				return
			final_annex.get("next_note_button").pressed.emit()
			if not _check(final_annex.get("overlay_body").text.find(String(final_annex._data()["clues"][1]["text"])) >= 0, "clue notes can advance " + destination):
				return
			final_annex._back_room()
			if not _check(final_annex.get("overlay_mode") == "link" and final_annex.get("link_selected_index") == 0, "evidence selection survives clue review " + destination):
				return
			final_annex.get("link_buttons")[1 if destination != "scifi.ruins" else 2].pressed.emit()
			if not _check(final_annex.get("overlay_message") == app.text_for("survey_link_wrong") and final_annex._link_count() == 0, "wrong evidence pair is retryable"):
				return
			for link in final_annex._data()["links"]:
				final_annex.get("link_buttons")[int(link["pair"][0])].pressed.emit()
				final_annex.get("link_buttons")[int(link["pair"][1])].pressed.emit()
			if not _check(final_annex._link_count() == 3 and final_annex.get("close_button").text == app.text_for("survey_link_continue"), "three evidence links complete " + destination):
				return
			final_annex.get("close_button").pressed.emit()
			if not _check(final_annex.get("overlay_mode") == "question", "links unlock final judgment " + destination):
				return
			final_annex.get("notes_button").pressed.emit()
			if not _check(final_annex.get("overlay_mode") == "notes", "clue notes available during final judgment " + destination):
				return
			final_annex.get("close_button").pressed.emit()
			if not _check(final_annex.get("overlay_mode") == "question", "clue notes return to final judgment " + destination):
				return
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
				if not _check(current_scene.get("hero").position == Vector2(311, 258) and app.survey_solved.has(destination) and app.survey_clues.size() == 6 and app.survey_links.size() == 3 and app.field_insights.has(destination) and app.field_trace_count(destination) == 2, "annex position, clues, traces, field assist and links restored"):
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
		if not _check(app.playtest_receipt_path != "" and FileAccess.file_exists(app.playtest_receipt_path), "playtest receipt written"):
			return
		var report_copy: String = current_scene.get("title_label").text + "\n" + current_scene.get("note_label").text
		var report_dev_word := ""
		for word in ["试玩", "演示", "原型", "临时", "后续章节", "demo", "playtest", "prototype", "temporary", "placeholder", "later chapters"]:
			if report_copy.to_lower().contains(word):
				report_dev_word = word
		if not _check(report_dev_word == "" and report_copy.contains(app.text_for("report_title")) and report_copy.contains(app.text_for("report_receipt")), "report copy is in-world (%s)" % app.language):
			return
		var receipt: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(app.playtest_receipt_path))
		if not _check(int(receipt.get("schemaVersion", 0)) == 1 and bool(receipt.get("reportCompleted", false)), "playtest receipt schema and completion"):
			return
		var place_time: Dictionary = receipt.get("timeByDestinationSeconds", {})
		var place_sum := 0.0
		for seconds in place_time.values():
			place_sum += float(seconds)
		if not _check(place_time.size() == 4 and absf(place_sum - float(receipt["durationSeconds"])) < 0.5 and place_time["scifi.city"] > 0.0 and place_time["scifi.ruins"] > 0.0, "receipt includes complete destination time accounting"):
			return
		if not _check(receipt.get("surveysCompleted", []).size() == 3 and int(receipt.get("wrongEvidencePairs", {}).get("scifi.city", 0)) == 1 and int(receipt.get("wrongJudgments", {}).get("scifi.city", 0)) == 1, "playtest receipt surveys and retry counts"):
			return
		if not _check(receipt.get("fieldAssists", []).size() == (3 if route == 0 else 1), "receipt records optional companion fieldwork"):
			return
		if not _check(receipt.get("fieldTraces", []).size() == 6, "receipt records six optional field traces"):
			return
		var recorded_events: Array = receipt.get("events", [])
		if not _check(recorded_events.size() >= 10 and recorded_events[0]["type"] == "run_start" and recorded_events[-1]["type"] == "report", "playtest receipt event order"):
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
		if not _check(current_scene.get("field_body").text.find(app.text_for("field_assist_result_ruins")) >= 0 and current_scene.get("field_body").text.find(app.field_assist_log_text()) >= 0, "companion fieldwork readable from map"):
			return
		current_scene._open_party_talk()
		await _settle()
		var talk: Control = current_scene
		if not _check(talk.name == "PartyTalk" and talk.get("available_topics").size() == (6 if route == 0 else 1), "party talks follow recruited companions and surveys"):
			return
		if route == 0:
			talk._open_topic(0)
			talk._next_line()
			talk._back()
			if not _check(not app.party_talk_seen.has("city-liang") and int(app.party_bonds["liang-xu"]) == 2, "unfinished conversation grants nothing"):
				return
			talk._open_topic(0)
			for line in 3:
				talk._next_line()
			if not _check(app.party_talk_seen.has("city-liang") and int(app.party_bonds["liang-xu"]) == 5, "first conversation grants bond once"):
				return
			talk._open_topic(0)
			for line in 3:
				talk._next_line()
			if not _check(int(app.party_bonds["liang-xu"]) == 5, "conversation replay cannot farm bond"):
				return
			var talk_save: String = SaveStore.list_entries()[0]["id"]
			app.begin_new_run()
			if not _check(app.load_save(talk_save) and app.party_talk_seen.has("city-liang") and int(app.party_bonds["liang-xu"]) == 5, "conversation and bond survive load"):
				return
		talk._back()
		await _settle()
		if not _check(current_scene.name == "ScifiWorldMap", "party talk returns to map"):
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


func _recruit_dialogue_ready(area: Node) -> bool:
	return area.get("dialogue_open") and area.get("dialogue_mode") == "recruit" and area.get("dialogue_overlay").visible and not area.get("invite_button").disabled


func _settle() -> void:
	await process_frame
	await process_frame


func _check(condition: bool, description: String) -> bool:
	if condition:
		return true
	push_error("M7 smoke check failed: " + description)
	quit(1)
	return false
