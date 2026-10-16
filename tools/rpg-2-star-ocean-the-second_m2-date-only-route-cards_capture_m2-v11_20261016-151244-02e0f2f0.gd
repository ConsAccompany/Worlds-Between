extends SceneTree

# m2-v11 capture: date-only player calendar (creator correction 2026-10-16: an RPG, not a travel
# simulator; players see year/month/day, never an HH:MM clock). Same flow as the m2-v10 tool, plus a
# check that neither the route card nor the map's calendar label shows a clock time, and one capture
# of the map after arriving in Chicago. From New York it captures the
# Yonkers (car 1 h), Washington (car 5 h) and Chicago (air 6 h) cards in zh and en, departs to Chicago
# through the real map path (the route core charges 6 h once), then captures the Chicago -> New York
# card (air 6 h) in zh and en. Writes 1280x720 PNGs and a manifest with each card's text, minutes,
# calendar label text, internal clock before/after and PNG sha256-bytes. Unapproved runtime
# evidence, not visual QA.
# Needs a display renderer (do not pass --headless). From the repository root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s \
#     <absolute path to this file>
# Writes only to outputs/ and to user://test-saves/m2-v11-date-only-capture. No game/ file is touched.

const OUT_DIR := "res://../outputs"
const NEW_YORK := "earth.us.ny.new-york-city"
const YONKERS := "earth.us.ny.yonkers-outskirts"
const WASHINGTON := "earth.us.dc.washington-ruins"
const CHICAGO := "earth.us.il.chicago"
const LOOP_SCENE := "rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn"
# [label, region, place, mode, minutes]
const FROM_NEW_YORK := [
	["nyc-to-yonkers", "us_northeast", YONKERS, "car", 60],
	["nyc-to-washington", "us_northeast", WASHINGTON, "car", 300],
	["nyc-to-chicago", "us_great_lakes", CHICAGO, "air", 360],
]
const FROM_CHICAGO := [["chicago-to-nyc", "us_northeast", NEW_YORK, "air", 360]]
const CLOCK_TEXT := "\\d{1,2}:\\d{2}"
const FORBIDDEN := "(?i)airport|laguardia|o'hare|check-in|baggage|timetable|估算|estimat|机场|值机|行李|候机|时刻表|\\bLGA\\b|\\bORD\\b"

var stamp := ""
var run_id := ""
var app: Node
var forbidden: RegEx
var clock: RegEx
var report := {"rule": "whole-hour-fixed-v1", "display": "date-only", "captures": [], "cards": []}


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	stamp = Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	run_id = "%08x" % randi()
	forbidden = RegEx.create_from_string(FORBIDDEN)
	clock = RegEx.create_from_string(CLOCK_TEXT)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(1280, 720)
	app = root.get_node("AppState")
	var save_store = load("res://scripts/save_store.gd")
	save_store.root_path = "user://test-saves/m2-v11-date-only-capture"
	app.begin_new_run()
	app.show_initial_guide = false
	change_scene_to_file("res://scenes/scifi_world_map.tscn")
	await _settle()
	var ok := true
	for card in FROM_NEW_YORK:
		ok = await _cards(card) and ok
	var map: Node = current_scene
	var before: int = app.calendar_minutes
	report["calendarBefore"] = map.route_adapter.calendar_text()
	report["internalClockBefore"] = TravelCalendar.iso_text(before)
	map.enter_region("us_great_lakes")
	map.select_place(CHICAGO)
	map._choose_option(String(map.route_state["options"][0]["option_id"]))
	map.depart()
	await _settle()
	report["chargedMinutes"] = app.calendar_minutes - before
	ok = ok and current_scene.scene_file_path.ends_with(LOOP_SCENE) and app.calendar_minutes - before == 360
	change_scene_to_file("res://scenes/scifi_world_map.tscn")
	await _settle()
	report["calendarAfter"] = current_scene.route_adapter.calendar_text()
	report["internalClockAfter"] = TravelCalendar.iso_text(app.calendar_minutes)
	report["calendarLabelAfter"] = current_scene.calendar_label.text
	ok = ok and current_scene.route_adapter.current_place_id() == CHICAGO and clock.search(current_scene.calendar_label.text) == null
	await _capture("arrived-chicago-%s" % app.language)
	for card in FROM_CHICAGO:
		ok = await _cards(card) and ok
	app.language = "zh"
	report["ok"] = ok
	report["runId"] = run_id
	report["stamp"] = stamp
	var manifest := ProjectSettings.globalize_path(OUT_DIR).path_join("rpg-2-star-ocean-the-second_m2-date-only-cards_manifest_m2-v11_%s-%s.json" % [stamp, run_id])
	var file := FileAccess.open(manifest, FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  ", false) + "\n")
	file.close()
	print("MANIFEST " + manifest)
	print(("M2_V11_DATE_ONLY_CAPTURE_OK captures=%d" if ok else "M2_V11_DATE_ONLY_CAPTURE_FAILED captures=%d") % report["captures"].size())
	quit(0 if ok else 1)


func _cards(card: Array) -> bool:
	var ok := true
	for language in ["zh", "en"]:
		app.language = language
		app.language_changed.emit()
		await _settle()
		var map: Node = current_scene
		map.enter_region(card[1])
		map.select_place(card[2])
		await _settle()
		var options: Array = map.route_state.get("options", [])
		var ready: bool = map.route_state.get("status", "") == "ready" and options.size() == 1 and options[0]["mode"] == card[3]
		var total := int(options[0]["total_minutes"]) if ready else -1
		var text: String = map.card_options.get_child(0).text if ready else ""
		var hours := "%d小时" % (int(card[4]) / 60) if language == "zh" else "%d h" % (int(card[4]) / 60)
		var clean := forbidden.search(text) == null
		var date_only := clock.search(text) == null and clock.search(map.calendar_label.text) == null
		ok = ok and ready and total == int(card[4]) and text.contains(hours) and clean and date_only and not map.depart_button.disabled
		report["cards"].append({"label": card[0], "language": language, "mode": card[3], "totalMinutes": total, "durationText": String(options[0]["duration_text"]) if ready else "", "cardText": text, "calendarLabel": map.calendar_label.text, "noAirportOrComponentText": clean, "dateOnly": date_only})
		print("CARD %s %s %d: %s | HUD %s" % [card[0], language, total, text.replace("\n", " / "), map.calendar_label.text])
		await _capture("%s-%s" % [card[0], language])
		map.close_route_card()
	return ok


func _capture(label: String) -> void:
	await _settle()
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	if image == null or image.get_size() != Vector2i(1280, 720):
		push_error("expected a rendered 1280x720 window (run without --headless)")
		quit(1)
		return
	var name := "rpg-2-star-ocean-the-second_m2-date-only-card_%s_m2-v11_%s-%s.png" % [label, stamp, run_id]
	var path := ProjectSettings.globalize_path(OUT_DIR).path_join(name)
	if image.save_png(path) != OK:
		push_error("capture failed: " + path)
		quit(1)
		return
	report["captures"].append({"file": "outputs/" + name, "sha256Bytes": FileAccess.get_sha256(path), "size": [image.get_width(), image.get_height()]})
	print("CAPTURED " + path)


func _settle() -> void:
	for i in 4:
		await process_frame
