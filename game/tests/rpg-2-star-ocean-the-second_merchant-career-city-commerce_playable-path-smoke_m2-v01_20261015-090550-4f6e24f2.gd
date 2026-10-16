extends SceneTree

# Playable path for the Merchant (行商) job and the city company panel, driven through the real scenes:
# recruit Liang Xu in the city, win repeat battles in the outskirts until level 10, choose Merchant on
# the growth screen, check that no Merchant job skill can be shown or spend energy in battle, travel
# back to the city, open a company from the world map, rest weeks, save/load, recall and reassign.
# Battles are won by setting the enemy to 1 HP and attacking once; only the result path is under test.
# Ledger amounts are the provisional non-currency units of CommerceLedger, not economic balance.

const SAVE_ROOT := "user://test-saves/merchant-city-commerce-path"
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
const AREA_SCENE := "res://scenes/scifi_exploration_area.tscn"
const BATTLE_SCENE := "res://scenes/battle_arena.tscn"
const BASE := CommerceLedger.PROVISIONAL_BASE_WEEKLY_INCOME
const NPC := CommerceLedger.PROVISIONAL_BASE_WEEKLY_INCOME * CommerceLedger.NPC_EFFICIENCY_PERCENT / 100

var app: Node
var checks := 0
var failures := 0


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	app = root.get_node("AppState")
	SaveStore.root_path = SAVE_ROOT
	_clear_saves()
	_test_job_rules()
	if failures == 0:
		await _test_playable_path()
	_clear_saves()
	if failures > 0:
		print("MERCHANT_CITY_COMMERCE_PATH_FAILED failures=%d checks=%d" % [failures, checks])
		quit(1)
		return
	print("MERCHANT_CITY_COMMERCE_PATH_OK checks=%d" % checks)
	quit(0)


func _test_job_rules() -> void:
	var series: Dictionary = GrowthRules.SERIES.get("merchant", {})
	_check(not series.is_empty() and CommerceLedger.MERCHANT_SERIES_ID == "merchant", "Merchant is a growth series whose id is the ledger's merchant id")
	_check(series.get("aptitude", "") == "adaptive", "Merchant uses the Adaptive aptitude")
	_check(GrowthRules.stage_name("merchant", 1, "zh") == "行商" and GrowthRules.stage_name("merchant", 2, "zh") == "契约经理", "canonical first two stage names")
	_check(GrowthRules.stage_name("merchant", 1, "en") == "Merchant" and GrowthRules.stage_name("merchant", 2, "en") == "Contract Manager", "English stage names")
	_check(GrowthRules.stage_count("merchant") == 5 and GrowthRules.stage_name("merchant", 5, "zh") == "万路协调者", "all five stage names come from the approved roster; none are invented")
	_check(not GrowthRules.job_skills_have_effect("merchant") and GrowthRules.job_skills_have_effect("sword") and GrowthRules.job_skills_have_effect("tactics") and not GrowthRules.job_skills_have_effect("unknown"), "only Merchant job skills are placeholders")
	for member_id in ["liang-xu", "zhao-ling"]:
		_check(GrowthRules.can_enter(app.MEMBER_DEFS[member_id], "merchant"), "existing recruit qualifies for Merchant: " + member_id)
	_check(GrowthRules.can_enter({"aptitudes": [60, 60, 60, 60]}, "merchant") and not GrowthRules.can_enter({"aptitudes": [90, 59, 90, 90]}, "merchant"), "entry threshold is Adaptive 60")

	app.begin_new_run()
	var hero: Dictionary = app.hero_state
	hero["aptitudes"] = [90, 59, 90, 90]
	app._grant_growth(hero, _xp_until_level(hero, 10), 0)
	_check(not app.choose_job("hero", "switch", "merchant") and hero["job_series"] == "sword", "below-threshold switch to Merchant is refused")
	hero["aptitudes"] = [60, 60, 60, 60]
	_check(app.choose_job("hero", "switch", "merchant") and hero["job_series"] == "merchant" and hero["job_stage"] == 1, "the hero may switch to Merchant at a level-10 choice")
	_check(hero["job_records"].has("sword") and hero["job_records"]["merchant"]["skills"].get("merchant_supply_pact", 0) == 1, "switching keeps the old record and seeds the Merchant record")
	hero["jp"] = 500
	_check(not app.upgrade_job_skill("hero", "merchant_supply_pact") and hero["jp"] == 500, "JP is never spent on a placeholder Merchant skill")
	_check(app.upgrade_personal_skill("hero") and hero["personal_skill_rank"] == 2, "personal skill stays upgradable while in Merchant")
	_check(app._valid_snapshot(app.make_snapshot("map", Vector2.ZERO, "manual_note")), "a save with the hero in Merchant is valid")
	_check(app.commerce_manager_block_reason("hero") == "hero-cannot-station", "the hero still cannot run a company")


func _test_playable_path() -> void:
	app.begin_new_run()
	app.language = "zh"
	var city_id := _science_city_id()
	_check(city_id != "" and city_id == app.current_location_id, "the run starts in the science region's discovered city (from TravelRegistry)")

	# Recruit Liang Xu in the city scene.
	_check(app.enter_current_location_scene(), "the city scene is the party's current place")
	change_scene_to_file(AREA_SCENE)
	await _settle()
	var area: Node = current_scene
	area.get("hero").position = area.get("npc_position")
	_interact(area)
	_check(area.get("dialogue_open") and not area.get("invite_button").disabled, "Liang Xu's recruitment dialogue opens")
	area.get("invite_button").pressed.emit()
	_check(app.recruited_members.has("liang-xu") and app.active_party_ids.has("liang-xu") and int(app.member_state("liang-xu")["level"]) == 1, "Liang Xu joins at level 1")

	# Not a city: no company access in the outskirts.
	_check(app.confirm_travel("scifi.outskirts"), "travel to the outskirts")
	change_scene_to_file(MAP_SCENE)
	await _settle()
	var map: Node = current_scene
	_check(map.commerce_city_id() == "" and not map.get("commerce_button").visible, "the company button is hidden outside cities")
	map.open_commerce()
	_check(not map.get("commerce_overlay").visible, "the company panel cannot open outside cities")

	# Repeat battles until the level-10 job choice.
	var battles := 0
	while battles < 40:
		battles += 1
		app.begin_battle("patrol", Vector2(330, 215))
		change_scene_to_file(BATTLE_SCENE)
		await _settle()
		var battle: Node = current_scene
		battle.get("fighters")[0]["x"] = battle.get("enemy_x") - 40.0
		battle.set("enemy_hp", 1)
		battle._try_attack(0)
		if not battle.get("battle_won"):
			_check(false, "repeat battle %d is won" % battles)
			return
		battle._return_after_result()
		await _settle()
		if current_scene.name == "GrowthScreen":
			break
	_check(current_scene.name == "GrowthScreen" and int(app.hero_state["level"]) == 10 and int(app.member_state("liang-xu")["level"]) == 10, "repeat battles reach level 10 and open the growth screen (%d battles)" % battles)
	var growth: Node = current_scene
	var merchant_index: int = growth.SERIES_IDS.find("merchant")
	var series_buttons: Array = growth.get("series_buttons")
	_check(merchant_index == series_buttons.size() - 1 and series_buttons[merchant_index].visible and String(series_buttons[merchant_index].text).contains("行商"), "the growth screen offers Merchant (行商)")
	await _check_growth_layout(growth, "zh")
	app.toggle_language()
	await process_frame
	await _check_growth_layout(growth, "en")
	app.toggle_language()
	await process_frame
	growth.get("stay_button").pressed.emit()
	_check(growth.get("selected_id") == "liang-xu" and app.hero_state["job_series"] == "sword", "the hero stays a Swordsman; the screen moves on to Liang Xu")
	_check(not series_buttons[merchant_index].disabled, "Liang Xu (Adaptive 67) may enter Merchant")
	var liang: Dictionary = app.member_state("liang-xu")
	var liang_personal_rank := int(liang["personal_skill_rank"])
	series_buttons[merchant_index].pressed.emit()
	liang = app.member_state("liang-xu")
	_check(liang["job_series"] == "merchant" and liang["job_stage"] == 1 and liang["job_records"].has("tactics") and int(liang["pending_job_choices"]) == 0, "Liang Xu becomes a stage-1 Merchant and keeps his Tactics record")
	_check(String(growth.get("job_label").text).contains("行商") and String(growth.get("skill_label").text).contains("暂无战斗效果"), "the growth screen names the job and marks its skills as non-battle")
	var upgrades: Array = growth.get("upgrade_buttons")
	_check(upgrades[0].visible and upgrades[0].disabled and String(upgrades[0].text).contains("补给协议") and not upgrades[1].visible, "the stage-1 Merchant skill is shown as a placeholder and cannot be upgraded")
	_check(String(growth.get("pending_label").text) == app.text_for("growth_merchant_note"), "the growth screen points Merchants to the city company")
	var jp_before := int(liang["jp"])
	growth.get("personal_upgrade_button").pressed.emit()
	_check(int(app.member_state("liang-xu")["personal_skill_rank"]) == liang_personal_rank + 1 and int(app.member_state("liang-xu")["jp"]) < jp_before, "Liang Xu's personal skill is preserved and still upgradable")
	_check(not growth.get("back_button").disabled, "all choices made; the growth screen can be left")
	growth.get("back_button").pressed.emit()
	await _settle()
	_check(current_scene.name != "GrowthScreen", "leaving the growth screen returns to play")

	await _test_merchant_battle_guard()

	# Back to the city; the company panel is reachable from the world map.
	_check(app.confirm_travel(city_id) and app.current_location_id == city_id, "travel back to the city")
	change_scene_to_file(MAP_SCENE)
	await _settle()
	map = current_scene
	var commerce_button: Button = map.get("commerce_button")
	var field_status: Label = map.get("field_status")
	_check(commerce_button.visible and commerce_button.text == "商会", "the company button shows in the city")
	_check(_inside_screen(commerce_button) and field_status.get_global_rect().end.x <= commerce_button.get_global_rect().position.x and field_status.get_global_rect().end.y <= 360.0, "the field status line stays clear of the company button (zh)")
	# The company panel never stacks over the field log.
	map.get("field_button").pressed.emit()
	commerce_button.pressed.emit()
	map.open_commerce()
	_check(map.get("field_overlay").visible and not map.get("commerce_overlay").visible, "the company panel cannot open over the field log")
	map.get("field_close").pressed.emit()
	commerce_button.pressed.emit()
	await process_frame
	_check(map.get("commerce_overlay").visible and String(map.get("commerce_title").text).contains(app.travel_location_name(city_id)), "the company panel opens for the current city")
	var member_buttons: Array = map.get("commerce_member_buttons")
	_check(member_buttons[0].visible and String(member_buttons[0].text).contains("梁序") and not member_buttons[1].visible and not map.get("commerce_recall_button").visible, "the Merchant companion can open a company")
	await _check_commerce_layout(map, "zh")
	await _check_commerce_modal(map)

	member_buttons[0].pressed.emit()
	var company: Dictionary = _company(city_id)
	_check(company.get("managerId", "") == "liang-xu" and not app.active_party_ids.has("liang-xu") and app.recruited_members.has("liang-xu"), "opening a company stations Liang Xu, who leaves the party")
	_check(not member_buttons[0].visible and map.get("commerce_recall_button").visible and String(map.get("commerce_recall_button").text).contains("梁序"), "a stationed companion can be recalled; no second post is offered")
	_check(app.open_commerce_company(city_id, "liang-xu")["reason"] == "company-exists" and app.commerce_ledger_state()["companies"].size() == 1, "one company per city")
	_check(app.commerce_manager_block_reason("liang-xu") == "already-stationed", "one post per companion")

	# Rest a week at a time: the calendar advances and the ledger settles.
	var minutes := int(app.calendar_minutes)
	var week := int(app.calendar_week_index)
	map.get("commerce_rest_button").pressed.emit()
	_check(int(app.calendar_minutes) == minutes + 7 * 24 * 60 and int(app.calendar_week_index) == week + 1, "resting advances the calendar by one week")
	_check(_units() == 0 and String(map.get("commerce_body").text).contains(app.text_for("commerce_rested") % [1, 0]), "the opening week settles with nothing owed")
	var autosaves := SaveStore.list_entries()
	_check(not autosaves.is_empty() and autosaves[0]["kind"] == "auto" and autosaves[0]["snapshot"]["note"] == "commerce_rest", "resting writes an autosave")
	map.get("commerce_rest_button").pressed.emit()
	_check(_units() == BASE and int(_company(city_id)["weeksSettled"]) == 1 and String(map.get("commerce_body").text).contains(app.text_for("commerce_ledger") % BASE), "a full week with the companion pays the full rate and the panel shows the total")

	# Save, change state, load: the ledger and the post come back exactly and nothing settles twice.
	app.save_return_scene = MAP_SCENE
	var save_id: String = app.write_manual_save(1)
	_check(save_id != "", "manual save written from the map")
	map.get("commerce_rest_button").pressed.emit()
	_check(_units() == 2 * BASE, "one more week after saving")
	_check(app.load_save(save_id) and _units() == BASE and not app.active_party_ids.has("liang-xu") and _company(city_id).get("managerId", "") == "liang-xu", "loading restores the ledger and the stationed companion")
	change_scene_to_file(app.loaded_scene_path())
	await _settle()
	map = current_scene
	_check(map.get("commerce_button").visible, "the loaded map still offers the company")
	map.open_commerce()
	map.get("commerce_rest_button").pressed.emit()
	_check(_units() == 2 * BASE and int(_company(city_id)["weeksSettled"]) == 2, "after loading, the next week settles once")

	# Recall: Liang Xu rejoins and an NPC keeps the company at the reduced rate.
	map.get("commerce_recall_button").pressed.emit()
	_check(app.active_party_ids.has("liang-xu") and _company(city_id).get("managerId", "x") == "", "recall returns Liang Xu to the party and the company stays open")
	_check(String(map.get("commerce_body").text).contains(app.text_for("commerce_recalled") % app.member_name("liang-xu")), "the panel reports the recall")
	member_buttons = map.get("commerce_member_buttons")
	_check(member_buttons[0].visible and String(member_buttons[0].text) == app.text_for("commerce_assign") % app.member_name("liang-xu") and not map.get("commerce_recall_button").visible, "the NPC-run company can take a Merchant again")
	map.get("commerce_rest_button").pressed.emit()
	_check(_units() == 2 * BASE + NPC, "an NPC-run week pays %d%%" % CommerceLedger.NPC_EFFICIENCY_PERCENT)

	# Reassign: the first week back pays the NPC rate, full weeks after that pay the companion rate.
	member_buttons[0].pressed.emit()
	_check(_company(city_id).get("managerId", "") == "liang-xu" and not app.active_party_ids.has("liang-xu"), "Liang Xu is stationed again")
	map.get("commerce_rest_button").pressed.emit()
	map.get("commerce_rest_button").pressed.emit()
	_check(_units() == 2 * BASE + NPC + NPC + BASE, "after reassignment the partial week pays the NPC rate, then the full rate")
	await _check_commerce_layout(map, "zh")
	app.toggle_language()
	await process_frame
	_check(map.get("commerce_button").text == "Company" and String(map.get("commerce_body").text).contains("not money"), "the panel switches to English")
	await _check_commerce_layout(map, "en")
	field_status = map.get("field_status")
	_check(field_status.get_global_rect().end.x <= map.get("commerce_button").get_global_rect().position.x and field_status.get_global_rect().end.y <= 360.0, "the field status line stays clear of the company button (en)")
	app.toggle_language()
	map.close_commerce()
	_check(not map.get("commerce_overlay").visible, "the company panel closes")
	_check(map.get("save_button").get_focus_mode_with_override() == Control.FOCUS_ALL and root.gui_get_focus_owner() == map.get("commerce_button"), "closing the company panel makes the map controls focusable again")


func _test_merchant_battle_guard() -> void:
	app.begin_battle("patrol", Vector2(330, 215))
	change_scene_to_file(BATTLE_SCENE)
	await _settle()
	var battle: Node = current_scene
	var fighters: Array = battle.get("fighters")
	var liang_index := -1
	for index in fighters.size():
		if fighters[index]["id"] == "liang-xu":
			liang_index = index
	_check(liang_index > 0, "the Merchant fights in the party")
	battle.set("enemy_windup", 0.0)
	battle._choose_control(liang_index)
	battle._toggle_pause()
	var job_buttons: Array = battle.get("pause_job_skill_buttons")
	_check(battle.get("paused") and not job_buttons[0].visible and not job_buttons[1].visible, "no Merchant job skill is shown in the pause menu")
	_check(battle.get("pause_skill_button").visible, "the personal skill stays in the pause menu")
	var liang: Dictionary = app.member_state("liang-xu")
	var energy := int(liang["energy"])
	var enemy_hp := int(battle.get("enemy_hp"))
	battle._queue_job_skill("merchant_supply_pact")
	battle._toggle_pause()
	_check(int(app.member_state("liang-xu")["energy"]) == energy and float(fighters[liang_index]["skill_cooldown"]) == 0.0 and int(battle.get("enemy_hp")) == enemy_hp, "a queued Merchant skill does nothing and spends no energy")
	_check(not battle._use_job_skill() and not battle._use_job_skill(liang_index, "merchant_fair_quote") and int(app.member_state("liang-xu")["energy"]) == energy, "the job-skill key and direct calls refuse Merchant skills")
	# A Merchant ordered to use skills falls back to the personal skill instead of a silent no-op.
	fighters[liang_index]["command"] = "skill"
	battle.set("enemy_windup", 0.0)
	battle._update_ai(liang_index, 0.016)
	_check(int(app.member_state("liang-xu")["energy"]) == energy - 16 and String(battle.get("feedback_message")).contains(app.text_for("battle_skill_liang")), "AI skill orders use the personal skill (Tactical Calibration)")
	fighters[0]["x"] = battle.get("enemy_x") - 40.0
	battle._choose_control(0)
	battle._toggle_pause()
	_check(job_buttons[0].visible, "a non-Merchant job skill is still shown")
	battle._toggle_pause()
	var hp_before := int(battle.get("enemy_hp"))
	_check(battle._use_job_skill(0, "sword_slash") and int(battle.get("enemy_hp")) < hp_before, "a non-Merchant job skill still works")
	battle.set("enemy_hp", 1)
	fighters[0]["attack_cooldown"] = 0.0
	battle._try_attack(0)
	_check(battle.get("battle_won"), "the guard battle is won")
	battle._return_after_result()
	await _settle()


func _check_growth_layout(growth: Node, language: String) -> void:
	await process_frame
	var rects: Array[Rect2] = []
	for button in growth.get("series_buttons"):
		_check(_inside_screen(button) and button.get_combined_minimum_size().x <= 116.5 and button.get_combined_minimum_size().y <= 41.5 and button.get_global_rect().end.y <= growth.get("personal_upgrade_button").get_global_rect().position.y, "series button fits (%s): %s min=%s" % [language, button.text, button.get_combined_minimum_size()])
		rects.append(button.get_global_rect())
	for index in rects.size() - 1:
		_check(not rects[index].intersects(rects[index + 1]), "series buttons do not overlap (%s)" % language)


func _check_commerce_layout(map: Node, language: String) -> void:
	await process_frame
	var body: RichTextLabel = map.get("commerce_body")
	_check(body.get_content_height() <= body.size.y, "company text fits without scrolling (%s): %d/%d" % [language, body.get_content_height(), int(body.size.y)])
	var widths := {"commerce_recall_button": 150.0, "commerce_rest_button": 200.0, "commerce_close": 136.0}
	for key in widths:
		var button: Button = map.get(key)
		_check(_inside_screen(button) and button.get_combined_minimum_size().x <= float(widths[key]) + 0.5, "%s fits (%s)" % [key, language])
	for button in map.get("commerce_member_buttons"):
		if button.visible:
			_check(_inside_screen(button) and button.get_combined_minimum_size().x <= 163.5, "member button fits (%s): %s" % [language, button.text])


# The open company panel is modal: map selection, departure, mode switches, zoom, the other buttons,
# mouse input over the map and keyboard focus traversal are all blocked, and no time passes.
func _check_commerce_modal(map: Node) -> void:
	var overlay: Control = map.get("commerce_overlay")
	var mode := String(map.get("mode"))
	var scale := float(map.get("view").scale)
	var location := String(app.current_location_id)
	var minutes := int(app.calendar_minutes)
	var place_buttons: Dictionary = map.get("place_buttons")
	var other := ""
	for place_id in place_buttons:
		if String(place_id) != location:
			other = String(place_id)
			break
	map.select_place(other)
	place_buttons[other].pressed.emit()
	map.depart()
	_check(other != "" and not map.get("route_card").visible and String(map.get("selected_place_id")) == "", "map selection and departure are blocked while the company panel is open")
	for key in ["globe_button", "region_button", "zoom_in_button", "zoom_out_button"]:
		map.get(key).pressed.emit()
	map.enter_global()
	map.enter_region(String(map.get("active_region_id")))
	_check(String(map.get("mode")) == mode and is_equal_approx(float(map.get("view").scale), scale), "mode switches and zoom are blocked while the company panel is open")
	for key in ["field_button", "talk_button", "save_button", "growth_button", "back_button"]:
		map.get(key).pressed.emit()
	await _settle()
	_check(current_scene == map and overlay.visible and not map.get("field_overlay").visible, "field log, talk, save, growth and menu buttons do nothing while the company panel is open")
	# Real input through the viewport: a click on a place marker and a wheel step over the map never reach the map.
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.position = place_buttons[other].get_global_rect().get_center()
	click.pressed = true
	root.push_input(click, true)
	var release: InputEventMouseButton = click.duplicate()
	release.pressed = false
	root.push_input(release, true)
	var wheel := InputEventMouseButton.new()
	wheel.button_index = MOUSE_BUTTON_WHEEL_UP
	wheel.position = map.get("map_frame").get_global_rect().get_center()
	wheel.pressed = true
	root.push_input(wheel, true)
	await process_frame
	_check(not map.get("route_card").visible and is_equal_approx(float(map.get("view").scale), scale) and app.current_location_id == location and int(app.calendar_minutes) == minutes, "mouse clicks and wheel do not reach the map; no travel and no time passes")
	# Keyboard: Tab, Shift+Tab and arrow keys keep focus inside the panel; nothing underneath can take focus.
	var focus_inside := overlay.is_ancestor_of(root.gui_get_focus_owner())
	for action in ["ui_focus_next", "ui_focus_next", "ui_focus_next", "ui_focus_next", "ui_focus_next", "ui_focus_prev", "ui_focus_prev", "ui_focus_prev", "ui_up", "ui_left", "ui_down", "ui_right", "ui_up"]:
		var press := InputEventAction.new()
		press.action = action
		press.pressed = true
		root.push_input(press, true)
		var owner := root.gui_get_focus_owner()
		focus_inside = focus_inside and owner != null and overlay.is_ancestor_of(owner)
	_check(focus_inside and overlay.visible, "keyboard focus traversal stays inside the company panel")
	var unfocusable := true
	for key in ["save_button", "growth_button", "back_button", "field_button", "commerce_button", "zoom_in_button", "globe_button", "region_button", "depart_button"]:
		unfocusable = unfocusable and map.get(key).get_focus_mode_with_override() == Control.FOCUS_NONE
	for button in place_buttons.values():
		unfocusable = unfocusable and button.get_focus_mode_with_override() == Control.FOCUS_NONE
	_check(unfocusable, "no control under the company panel can take keyboard focus")


func _inside_screen(control: Control) -> bool:
	return Rect2(0, 0, 640, 360).encloses(control.get_global_rect())


func _science_city_id() -> String:
	for location_id in app.travel_location_ids("science"):
		if app.travel_location(location_id).get("type", "") == "city":
			return location_id
	return ""


func _company(city_id: String) -> Dictionary:
	return app.commerce_ledger_state()["companies"].get(city_id, {})


func _units() -> int:
	return int(app.commerce_ledger_state()["ledgerUnits"])


func _xp_until_level(member: Dictionary, target_level: int) -> int:
	var required := -int(member.get("xp", 0))
	for level in range(int(member["level"]), target_level):
		required += GrowthRules.xp_to_next(level)
	return required


func _interact(area: Node) -> void:
	var event := InputEventAction.new()
	event.action = "interact"
	event.pressed = true
	area._unhandled_input(event)


func _settle() -> void:
	await process_frame
	await process_frame


func _clear_saves() -> void:
	var directory := DirAccess.open(SAVE_ROOT)
	if directory == null:
		return
	for name in directory.get_files():
		directory.remove(name)


func _check(condition: bool, label: String) -> bool:
	checks += 1
	if not condition:
		failures += 1
		push_error("Merchant city commerce check failed: " + label)
	return condition
