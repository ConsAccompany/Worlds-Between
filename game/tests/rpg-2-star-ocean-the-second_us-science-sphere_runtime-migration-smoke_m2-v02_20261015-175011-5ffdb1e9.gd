extends SceneTree

# Runtime smoke for the 2026-10-15 US science-sphere migration, driven through real scenes:
#   - a new run starts 2537-05-25 08:00 in New York City; the City Hall Park scene loads with
#     Chinese and English titles, and walking there charges no calendar time;
#   - the map flies New York City -> Chicago through the route card, charging the core's
#     door-to-door minutes once, and loads the Chicago Loop placeholder scene;
#   - walking in the Loop charges no time, streets block and slide, Esc returns to the map;
#   - saving in the Loop and loading returns to the Loop at the saved clock;
#   - the Washington ruins scene keeps its survey post and patrol automaton;
#   - a v01 (Shanghai set) save with an old company key loads and keys the company to New York.
# Placeholder state: the Loop shows its art-unaccepted badge; nothing here judges art quality.
# From the repository root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --headless --path game \
#     --script res://tests/rpg-2-star-ocean-the-second_us-science-sphere_runtime-migration-smoke_m2-v02_20261015-175011-5ffdb1e9.gd

const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
const AREA_SCENE := "res://scenes/scifi_exploration_area.tscn"
const LOOP_SCENE := "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn"
const NEW_YORK := "earth.us.ny.new-york-city"
const WASHINGTON := "earth.us.dc.washington-ruins"
const CHICAGO := "earth.us.il.chicago"
const SAVE_ROOT := "user://test-saves/m2-us-science-migration"

var app: Node
var checks := 0
var failed := false


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	app = root.get_node("AppState")
	SaveStore.root_path = SAVE_ROOT
	_clear_saves()
	app.begin_new_run()
	app.show_initial_guide = false
	app.language = "zh"
	if await _start_and_city() and await _fly_to_chicago() and await _walk_and_save_in_loop() and await _washington_scene() and _old_company_key():
		_clear_saves()
		print("US_SCIENCE_MIGRATION_SMOKE_OK checks=%d" % checks)
		quit(0)


func _start_and_city() -> bool:
	if not _check(TravelCalendar.iso_text(app.calendar_minutes) == "2537-05-25 08:00" and app.current_location_id == NEW_YORK, "new run starts 2537-05-25 08:00 in New York City"):
		return false
	if not _check(app.calendar_date_text() == "2537年5月25日", "Chinese start date"):
		return false
	app.language = "en"
	if not _check(app.calendar_date_text() == "May 25, 2537", "English start date"):
		return false
	app.language = "zh"
	change_scene_to_file(MAP_SCENE)
	await _settle()
	var map: Node = current_scene
	if not _check(map.calendar_label.text.begins_with("2537年5月25日"), "map shows the 2537 calendar"):
		return false
	map.destination_buttons["scifi.city"].pressed.emit()
	await _settle()
	map.depart_button.pressed.emit()
	await _settle()
	var area: Node = current_scene
	if not _check(area.scene_file_path == AREA_SCENE and area.title_label.text == "下曼哈顿 · 市政厅公园", "City Hall Park scene loads with its Chinese title"):
		return false
	app.toggle_language()
	await _settle()
	if not _check(area.title_label.text == "Lower Manhattan · City Hall Park" and area.hint_label.text.contains("New York"), "English title and hint"):
		return false
	app.toggle_language()
	var minutes: int = app.calendar_minutes
	var before: Vector2 = area.hero.position
	await _hold("move_right", 20)
	if not _check(area.hero.position.x > before.x + 1.0 and app.calendar_minutes == minutes, "walking in City Hall Park moves the hero and charges no time"):
		return false
	area.back_button.pressed.emit()
	await _settle()
	return _check(current_scene.scene_file_path == MAP_SCENE, "back to the map")


func _fly_to_chicago() -> bool:
	var map: Node = current_scene
	var start: int = app.calendar_minutes
	map.select_place(CHICAGO)
	await _settle()
	if not _check(map.active_region_id == "us_great_lakes" and map.route_state["status"] == "ready", "Chicago card is ready in the Great Lakes view"):
		return false
	var option: Dictionary = map.route_state["options"][0]
	var text: String = map.card_options.get_child(0).text
	if not _check(option["mode"] == "air" and text.contains("飞机") and text.contains("航程") and text.contains("估算") and not text.contains("公路"), "air option shows flight distance and the estimate note: " + text.replace("\n", " | ")):
		return false
	# English shows the mode once: "Air · Flight 1177.1 km", never "Air · Air 1177.1 km".
	app.language = "en"
	var en_text: String = map.route_option_text(option)
	app.language = "zh"
	if not _check(en_text.begins_with("Air · Flight ") and en_text.count("Air") == 1, "English air option names Air once: " + en_text.replace("\n", " | ")):
		return false
	var expected := int(option["total_minutes"])
	map.depart_button.pressed.emit()
	await _settle()
	var loop: Node = current_scene
	if not _check(loop.scene_file_path == LOOP_SCENE and app.current_location_id == CHICAGO and app.current_destination_id == "scifi.loop", "departing flies to Chicago and loads the Loop scene"):
		return false
	return _check(app.calendar_minutes == start + expected and app.last_travel.get("minutes", -1) == expected, "the flight charged the core's door-to-door minutes once (%d)" % expected)


func _walk_and_save_in_loop() -> bool:
	var loop: Node = current_scene
	if not _check(loop.title_label.text == "芝加哥 · 卢普区" and loop.badge_label.text == "技术占位 · 美术未验收", "Loop scene title and its art-unaccepted badge (zh)"):
		return false
	app.toggle_language()
	await _settle()
	if not _check(loop.title_label.text == "Chicago · The Loop" and loop.badge_label.text == "Technical placeholder · Art not accepted" and loop.help_label.text.contains("no calendar time"), "Loop scene English labels"):
		return false
	if not _check(_header_clear_of_buttons(loop), "English badge and subtitle stay clear of the Save button"):
		return false
	app.toggle_language()
	await _settle()
	if not _check(_header_clear_of_buttons(loop), "Chinese badge and subtitle stay clear of the Save button"):
		return false
	var script: GDScript = loop.get_script()
	if not _check(script.walkable(Vector2(400, 180)) and not script.walkable(Vector2(440, 195)) and script.slide_position(Vector2(400, 180), Vector2(410, 190)) == Vector2(410, 180), "streets are walkable, blocks are solid, movement slides along the street"):
		return false
	var minutes: int = app.calendar_minutes
	var start: Vector2 = loop.hero.position
	await _hold("move_right", 20)
	await _hold("move_down", 20)
	if not _check(loop.hero.position != start and script.walkable(loop.hero.position) and app.calendar_minutes == minutes, "walking in the Loop stays on streets and charges no time"):
		return false
	if not _check(not app.areas_visited.has("scifi.loop"), "the Loop is not counted toward the three-place goal"):
		return false
	var saved_at: Vector2 = loop.hero.position
	loop.save_button.pressed.emit()
	await _settle()
	if not _check(current_scene.scene_file_path.ends_with("save_screen.tscn") and app.save_return_scene == LOOP_SCENE, "save opens from the Loop"):
		return false
	var id: String = app.write_manual_save(1)
	var entry := SaveStore.read_entry(id)
	if not _check(id != "" and entry["snapshot"]["scene"] == "area" and entry["snapshot"]["destination"] == "scifi.loop", "Loop save is an area save at scifi.loop"):
		return false
	current_scene._back()
	await _settle()
	if not _check(current_scene.scene_file_path == LOOP_SCENE and current_scene.hero.position.is_equal_approx(saved_at), "back from save returns to the same Loop position"):
		return false
	current_scene.back_button.pressed.emit()
	await _settle()
	var map: Node = current_scene
	map.select_place(NEW_YORK)
	await _settle()
	map.depart_button.pressed.emit()
	await _settle()
	var after_return: int = app.calendar_minutes
	if not _check(app.current_location_id == NEW_YORK and after_return > minutes, "return flight charges time and lands in New York City"):
		return false
	if not _check(app.load_save(id) and app.loaded_scene_path() == LOOP_SCENE and app.calendar_minutes == minutes and app.current_location_id == CHICAGO, "loading the Loop save restores Chicago, its scene and its clock"):
		return false
	change_scene_to_file(app.loaded_scene_path())
	await _settle()
	if not _check(current_scene.scene_file_path == LOOP_SCENE and current_scene.hero.position.is_equal_approx(saved_at) and app.calendar_minutes == minutes, "the loaded Loop scene resumes at the saved spot with no time charged"):
		return false
	current_scene.get_viewport().push_input(_action("ui_cancel"))
	await _settle()
	return _check(current_scene.scene_file_path == MAP_SCENE, "Esc in the Loop returns to the map")


func _washington_scene() -> bool:
	var map: Node = current_scene
	map.select_place(NEW_YORK)
	await _settle()
	map.depart_button.pressed.emit()
	await _settle()
	current_scene.back_button.pressed.emit()
	await _settle()
	map = current_scene
	var start: int = app.calendar_minutes
	map.select_place(WASHINGTON)
	await _settle()
	var minutes := int(map.route_state["options"][0]["total_minutes"])
	map.depart_button.pressed.emit()
	await _settle()
	var area: Node = current_scene
	if not _check(area.scene_file_path == AREA_SCENE and app.current_location_id == WASHINGTON and app.calendar_minutes == start + minutes, "the drive to Washington charges its minutes and loads the ruins scene"):
		return false
	if not _check(area.title_label.text == "华盛顿特区废墟 · 国会大厦" and area.hint_label.text.contains("勘察站") and area.enemy_visible and area.survey_label.text != "", "ruins scene: Capitol title, survey post and a patrol automaton"):
		return false
	app.toggle_language()
	await _settle()
	var ok := _check(area.title_label.text == "Washington, D.C. ruins · U.S. Capitol" and area.hint_label.text.contains("patrol automata"), "ruins scene English labels")
	app.toggle_language()
	return ok


# A v01 save with a company keyed by the retired Shanghai ID keeps its company, now under New York.
func _old_company_key() -> bool:
	app.begin_new_run()
	var snapshot: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
	var block: Dictionary = snapshot["commerce"]
	block["companies"] = {"earth.cn.shanghai": {"managerId": "", "openedWeekIndex": int(block["settledWeekIndex"]), "managerSinceWeekIndex": int(block["settledWeekIndex"]), "weeksSettled": 0, "unitsEarned": 0}}
	snapshot["travel"]["locationId"] = "earth.cn.shanghai"
	var id := SaveStore.write_entry("manual", 2, snapshot)
	if not _check(app.load_save(id), "v01 save with an old company key loads"):
		return false
	var companies: Dictionary = app.commerce_ledger_state()["companies"]
	return _check(companies.has(NEW_YORK) and not companies.has("earth.cn.shanghai") and app.current_location_id == NEW_YORK, "the company is now keyed to New York City")


# Header text must end left of the Save button and the badge must not cover the title or subtitle.
func _header_clear_of_buttons(loop: Node) -> bool:
	var save_left: float = loop.save_button.position.x
	var rects := []
	for label in [loop.title_label, loop.hint_label, loop.badge_label]:
		rects.append(Rect2(label.position, label.get_minimum_size()))
	for rect in rects:
		if rect.end.x > save_left:
			return false
	return not rects[2].intersects(rects[0]) and not rects[2].intersects(rects[1])


func _hold(action: String, frames: int) -> void:
	Input.action_press(action)
	for i in frames:
		await process_frame
	Input.action_release(action)
	await process_frame


func _action(name: String) -> InputEventAction:
	var event := InputEventAction.new()
	event.action = name
	event.pressed = true
	return event


func _settle() -> void:
	for i in 3:
		await process_frame


func _clear_saves() -> void:
	var directory := DirAccess.open(SAVE_ROOT)
	if directory == null:
		return
	for name in directory.get_files():
		directory.remove(name)


func _check(condition: bool, label: String) -> bool:
	checks += 1
	if condition:
		return true
	push_error("US science migration smoke failed: " + label)
	if not failed:
		failed = true
		quit(1)
	return false
