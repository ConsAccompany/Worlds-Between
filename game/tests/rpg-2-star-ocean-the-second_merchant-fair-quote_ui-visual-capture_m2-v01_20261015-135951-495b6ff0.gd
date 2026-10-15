extends SceneTree

# TEST-ONLY visual capture of the provisional Merchant Fair Quote slice in the real game scenes.
# Run windowed (not --headless) at --resolution 1280x720. Saves stay under an isolated test root.
# Liang Xu reaches stage-2 Merchant through the growth screen buttons (XP/JP granted directly),
# upgrades Fair Quote to rank 2, is stationed through the world map company panel, and the panel's
# Rest button passes the opening week and one full week. Liang Xu is then recalled, one NPC week passes
# and Liang Xu is stationed again, so the running week is the partial NPC-rate week. The station feedback line
# keeps the zh member name from press time, so it is cleared before the en partial-week capture (harness-only). Six separate PNGs (growth
# zh/en, full-week company zh/en, re-stationed partial-week company zh/en) plus one manifest JSON go to
# outputs/. Ledger amounts are provisional non-currency units.
# From the repo root: work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game --resolution 1280x720 --script res://tests/<this file>
# get_cmdline_args() drops --path/--resolution, so the manifest's engine_command is incomplete; record the full command by hand.

const SAVE_ROOT := "user://test-saves/merchant-fair-quote-visual-capture"
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
const GROWTH_SCENE := "res://scenes/growth_screen.tscn"
const OUTPUT_DIR := "res://../outputs/"
const SLUG := "rpg-2-star-ocean-the-second"
const FAIR := "merchant_fair_quote"
const TARGET_RANK := 2
const SIZE := Vector2i(1280, 720)

var app: Node
var stamp := ""
var captures: Array = []
var state := {}
var failures: Array[String] = []


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	app = root.get_node("AppState")
	stamp = Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	if DisplayServer.get_name() == "headless":
		_fail("renderer is headless; run windowed to capture")
		_finish()
		return
	SaveStore.root_path = SAVE_ROOT
	_clear_saves()
	app.begin_new_run()
	app.language = "zh"
	app.show_initial_guide = false
	var city_id := String(app.current_location_id)
	_require(app.commerce_city_block_reason(city_id) == "", "the run starts in a city that can host a company")
	_require(app.recruit_member("liang-xu"), "Liang Xu joins")
	if failures.is_empty():
		await _growth_part()
	if failures.is_empty():
		await _company_part(city_id)
	_clear_saves()
	_finish()


func _growth_part() -> void:
	var liang: Dictionary = app.member_state("liang-xu")
	app._grant_growth(liang, _xp_until_level(liang, 10), 0)
	change_scene_to_file(GROWTH_SCENE)
	await _settle()
	var growth: Node = current_scene
	var party: Array = app.active_party_ids
	growth.get("member_buttons")[party.find("liang-xu")].pressed.emit()
	_require(growth.get("selected_id") == "liang-xu", "the growth screen shows Liang Xu")
	growth.get("series_buttons")[growth.SERIES_IDS.find("merchant")].pressed.emit()
	liang = app.member_state("liang-xu")
	_require(liang["job_series"] == "merchant" and int(liang["job_stage"]) == 1, "Liang Xu switches to Merchant")
	app._grant_growth(liang, _xp_until_level(liang, 20), 0)
	growth._refresh()
	growth.get("promote_button").pressed.emit()
	liang = app.member_state("liang-xu")
	_require(int(liang["job_stage"]) == 2 and GrowthRules.fair_quote_rank(liang) == 1, "promotion to Contract Manager grants Fair Quote rank 1")
	app._grant_growth(liang, 0, 100)
	growth._refresh()
	var cost_2 := GrowthRules.jp_cost(liang, "merchant", 2)
	growth.get("upgrade_buttons")[1].pressed.emit()
	_require(GrowthRules.fair_quote_rank(liang) == TARGET_RANK and int(liang["jp"]) == 100 - cost_2, "the Fair Quote button upgrades to rank 2 for %d JP" % cost_2)
	state["growth"] = {
		"member": "liang-xu",
		"level": int(liang["level"]),
		"job_series": String(liang["job_series"]),
		"job_stage": int(liang["job_stage"]),
		"fair_quote_rank": GrowthRules.fair_quote_rank(liang),
		"fair_quote_bonus_percent": CommerceLedger.companion_rate_percent(TARGET_RANK) - 100,
		"jp_granted": 100,
		"jp_spent_rank_2": cost_2,
		"jp_remaining": int(liang["jp"]),
		"next_rank_3_cost": GrowthRules.jp_cost(liang, "merchant", 3),
		"pending_job_choices": int(liang.get("pending_job_choices", 0)),
	}
	if not failures.is_empty():
		return
	state["growth"]["pending_label_zh"] = String(growth.get("pending_label").text)
	await _capture("growth-ui", "fair-quote-rank2-zh", "zh")
	app.toggle_language()
	await _settle()
	state["growth"]["pending_label_en"] = String(growth.get("pending_label").text)
	await _capture("growth-ui", "fair-quote-rank2-en", "en")
	app.toggle_language()


func _company_part(city_id: String) -> void:
	app.save_return_scene = MAP_SCENE
	change_scene_to_file(MAP_SCENE)
	await _settle()
	var map: Node = current_scene
	map.open_commerce()
	await _settle()
	_require(map.get("commerce_overlay").visible, "the company panel opens")
	var candidates: Array = map.get("commerce_member_ids")
	var index := candidates.find("liang-xu")
	_require(index >= 0, "Liang Xu is offered as a station candidate")
	if not failures.is_empty():
		return
	map.get("commerce_member_buttons")[index].pressed.emit()
	_require(not app.active_party_ids.has("liang-xu") and _company(city_id).get("managerId", "") == "liang-xu", "Liang Xu opens the city company and leaves the party")
	var rest: Button = map.get("commerce_rest_button")
	rest.pressed.emit()
	var opening_units := _units()
	rest.pressed.emit()
	var company := _company(city_id)
	_require(opening_units == 0 and _units() == 110 and int(company["weeksSettled"]) == 1 and int(company["unitsEarned"]) == 110, "opening week pays 0, one full week at rank 2 pays 110")
	_require(app.commerce_companion_rate_percent("liang-xu") == 110, "the stationed rate is 110 %")
	var body: RichTextLabel = map.get("commerce_body")
	await _settle()
	_require(body.get_content_height() <= body.size.y, "company text fits without scrolling")
	state["company"] = {
		"city_id": city_id,
		"manager": "liang-xu",
		"companion_rate_percent": app.commerce_companion_rate_percent("liang-xu"),
		"opening_week_units": opening_units,
		"full_week_units": _units() - opening_units,
		"weeks_settled": int(company["weeksSettled"]),
		"units_earned": int(company["unitsEarned"]),
		"ledger_units": _units(),
		"rests_via_panel_button": 2,
		"calendar_date": "%s %s" % [app.calendar_date_text(), app.calendar_time_text_at(app.calendar_minutes)],
	}
	if not failures.is_empty():
		return
	state["company"]["body_zh"] = String(body.text)
	await _capture("company-panel", "full-week-110-zh", "zh")
	app.toggle_language()
	# The panel does not listen for language changes; re-render it in place, keeping the Rest feedback line.
	map._refresh_commerce()
	await _settle()
	state["company"]["body_en"] = String(body.text)
	_require(not _has_cjk(String(body.text)) and not _has_cjk(String(map.get("commerce_title").text)), "the full-week en panel text is fully English")
	await _capture("company-panel", "full-week-110-en", "en")
	app.toggle_language()
	await _restation_part(map, city_id)


# Recall, rest one NPC week, then station Liang Xu again through the panel buttons: the running week is
# the partial NPC-rate week, and the panel must say so next to the 110 % full-week rate.
func _restation_part(map: Node, city_id: String) -> void:
	var units_before := _units()
	map.get("commerce_recall_button").pressed.emit()
	_require(app.active_party_ids.has("liang-xu") and _company(city_id).get("managerId", "") == "", "Liang Xu is recalled through the panel")
	map.get("commerce_rest_button").pressed.emit()
	_require(_units() - units_before == CommerceLedger.NPC_EFFICIENCY_PERCENT, "the NPC-run week pays 80")
	var index: int = map.get("commerce_member_ids").find("liang-xu")
	_require(index >= 0, "Liang Xu is offered again")
	if not failures.is_empty():
		return
	map.get("commerce_member_buttons")[index].pressed.emit()
	_require(_company(city_id).get("managerId", "") == "liang-xu" and int(_company(city_id)["managerSinceWeekIndex"]) == app.calendar_week_index, "Liang Xu is stationed again this week")
	_require(app.commerce_companion_rate_percent("liang-xu") == 110 and app.commerce_current_week_rate_percent(city_id) == CommerceLedger.NPC_EFFICIENCY_PERCENT, "full-week rate 110 %, running week at the NPC 80 %")
	var body: RichTextLabel = map.get("commerce_body")
	await _settle()
	var partial_zh: String = app.text_for("commerce_week_partial") % [CommerceLedger.NPC_EFFICIENCY_PERCENT, 110]
	_require(String(body.text).contains(partial_zh), "the zh panel shows the partial-week line")
	_require(body.get_content_height() <= body.size.y, "re-stationed company text fits without scrolling (zh)")
	var company := _company(city_id)
	state["restation"] = {
		"npc_week_units": CommerceLedger.NPC_EFFICIENCY_PERCENT,
		"companion_full_week_rate_percent": app.commerce_companion_rate_percent("liang-xu"),
		"current_week_rate_percent": app.commerce_current_week_rate_percent(city_id),
		"manager_since_week_index": int(company["managerSinceWeekIndex"]),
		"calendar_week_index": app.calendar_week_index,
		"weeks_settled": int(company["weeksSettled"]),
		"units_earned": int(company["unitsEarned"]),
		"ledger_units": _units(),
		"calendar_date": "%s %s" % [app.calendar_date_text(), app.calendar_time_text_at(app.calendar_minutes)],
	}
	if not failures.is_empty():
		return
	state["restation"]["body_zh"] = String(body.text)
	await _capture("company-panel", "restationed-partial-week-npc80-zh", "zh")
	app.toggle_language()
	# The station feedback stores the member name resolved in zh at press time, so re-rendering it after this
	# harness-only language switch would read "梁序 is now stationed". Players cannot switch language while the
	# modal panel is open, so drop the stale transient line instead of changing the panel.
	map.set("commerce_feedback", [])
	map._refresh_commerce()
	await _settle()
	state["restation"]["en_stale_station_feedback_cleared"] = true
	_require(not _has_cjk(String(body.text)) and not _has_cjk(String(map.get("commerce_title").text)), "the en panel text is fully English")
	_require(String(body.text).contains(app.text_for("commerce_week_partial") % [CommerceLedger.NPC_EFFICIENCY_PERCENT, 110]), "the en panel shows the partial-week line")
	_require(body.get_content_height() <= body.size.y, "re-stationed company text fits without scrolling (en)")
	state["restation"]["body_en"] = String(body.text)
	if not failures.is_empty():
		return
	await _capture("company-panel", "restationed-partial-week-npc80-en", "en")


func _capture(purpose: String, variant: String, language: String) -> void:
	await RenderingServer.frame_post_draw
	var image := root.get_viewport().get_texture().get_image()
	var name := "%s_merchant-fair-quote_%s_%s_%s-%08x.png" % [SLUG, purpose, variant, stamp, randi()]
	if image == null:
		_fail("no image for " + name)
		return
	if image.get_size() != SIZE:
		_fail("%s is %s, expected %s" % [name, image.get_size(), SIZE])
		return
	var path := ProjectSettings.globalize_path(OUTPUT_DIR + name)
	if image.save_png(path) != OK:
		_fail("could not save " + path)
		return
	var check := Image.load_from_file(path)
	if check == null or check.get_size() != SIZE:
		_fail("reloaded %s is not %s" % [path, SIZE])
		return
	captures.append({"file": "outputs/" + name, "purpose": purpose, "variant": variant, "language": language, "width": check.get_width(), "height": check.get_height()})
	print("CAPTURED " + path)


func _finish() -> void:
	var manifest := {
		"project": SLUG,
		"status": "test-only visual capture; not production art, not approved, no game code changed",
		"slice": "provisional Merchant Fair Quote (unstaged engineering slice)",
		"harness": "game/tests/" + get_script().resource_path.get_file(),
		"engine_version": Engine.get_version_info()["string"],
		"display_server": DisplayServer.get_name(),
		"renderer": String(ProjectSettings.get_setting("rendering/renderer/rendering_method")),
		"engine_command": " ".join([OS.get_executable_path()] + Array(OS.get_cmdline_args())),
		"viewport_logical": [640, 360],
		"capture_size": [SIZE.x, SIZE.y],
		"save_root": SAVE_ROOT + " (cleared before and after)",
		"ledger_note": "ledger amounts are provisional non-currency units, not economic balance",
		"state": state,
		"captures": captures,
		"failures": failures,
	}
	var name := "%s_merchant-fair-quote_ui-visual-capture-manifest_m2-v01_%s-%08x.json" % [SLUG, stamp, randi()]
	var path := ProjectSettings.globalize_path(OUTPUT_DIR + name)
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file != null:
		file.store_string(JSON.stringify(manifest, "  ") + "\n")
		file.close()
		print("MANIFEST " + path)
	if failures.is_empty() and captures.size() == 6:
		print("FAIR_QUOTE_CAPTURE_OK captures=%d" % captures.size())
		quit(0)
	else:
		print("FAIR_QUOTE_CAPTURE_FAILED " + "; ".join(failures))
		quit(1)


func _company(city_id: String) -> Dictionary:
	return app.commerce_ledger_state()["companies"].get(city_id, {})


func _units() -> int:
	return int(app.commerce_ledger_state()["ledgerUnits"])


func _xp_until_level(member: Dictionary, target_level: int) -> int:
	var required := -int(member.get("xp", 0))
	for level in range(int(member["level"]), target_level):
		required += GrowthRules.xp_to_next(level)
	return required


func _has_cjk(text: String) -> bool:
	var regex := RegEx.create_from_string("[\\x{3000}-\\x{30FF}\\x{4E00}-\\x{9FFF}\\x{FF00}-\\x{FFEF}]")
	return regex.search(text) != null


func _settle() -> void:
	for frame in 6:
		await process_frame


func _clear_saves() -> void:
	for sub in ["", "playtests"]:
		var directory := DirAccess.open(SAVE_ROOT.path_join(sub))
		if directory == null:
			continue
		for name in directory.get_files():
			directory.remove(name)


func _require(condition: bool, label: String) -> void:
	if not condition:
		_fail(label)


func _fail(label: String) -> void:
	failures.append(label)
	push_error("Fair Quote capture: " + label)
