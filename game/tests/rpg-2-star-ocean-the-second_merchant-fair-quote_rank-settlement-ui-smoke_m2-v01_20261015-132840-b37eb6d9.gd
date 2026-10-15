extends SceneTree

# Stage-2 Merchant passive Fair Quote (公平报价): JP rank, weekly settlement and UI protection.
# Liang Xu reaches Merchant and Contract Manager through the real growth screen buttons (XP is granted
# directly instead of fighting), upgrades Fair Quote with JP, runs the city company and rests week by
# week. Checks the formula (+5 % of base per rank, companion-rate weeks only), that Supply Pact stays a
# placeholder, that no Merchant skill appears or runs in battle, that a stationed manager's rank is
# frozen, and that save/load restores rank, JP and ledger together so nothing is settled twice or
# re-priced. The company panel (zh/en) labels the shown rate as the full-week rate and adds a this-week
# line in the opening week and the partial NPC-rate week after (re-)stationing. An old (da394c3-shaped)
# save with a stage-2 Merchant at rank 1 earns 105 at its next settlement. Ledger amounts are
# provisional non-currency units, not economic balance.

const SAVE_ROOT := "user://test-saves/merchant-fair-quote"
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
const GROWTH_SCENE := "res://scenes/growth_screen.tscn"
const BATTLE_SCENE := "res://scenes/battle_arena.tscn"
const FAIR := "merchant_fair_quote"
const SUPPLY := "merchant_supply_pact"
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
	_test_rules()
	if failures == 0:
		await _test_path()
	if failures == 0:
		_test_legacy_save()
	_clear_saves()
	if failures > 0:
		print("MERCHANT_FAIR_QUOTE_FAILED failures=%d checks=%d" % [failures, checks])
		quit(1)
		return
	print("MERCHANT_FAIR_QUOTE_OK checks=%d" % checks)
	quit(0)


func _test_rules() -> void:
	_check(CommerceLedger.FAIR_QUOTE_PERCENT_PER_RANK == 5 and CommerceLedger.FAIR_QUOTE_MAX_RANK == GrowthRules.SKILL_JP_BASE.size(), "Fair Quote is +5 % of base per rank, up to the JP rank cap")
	_check([0, 1, 2, 3].map(func(rank): return CommerceLedger.companion_rate_percent(rank)) == [100, 105, 110, 115], "companion rate by rank: 100/105/110/115 %")
	_check(CommerceLedger.companion_rate_percent(99) == 115 and CommerceLedger.companion_rate_percent(-4) == 100, "out-of-range ranks are clamped")
	_check(not GrowthRules.job_skills_have_effect("merchant") and GrowthRules.job_skills_have_effect("sword"), "Merchant job skills still have no battle effect")
	_check(GrowthRules.job_skill_upgradable("merchant", FAIR) and not GrowthRules.job_skill_upgradable("merchant", SUPPLY), "only Fair Quote is JP-upgradable; Supply Pact stays a placeholder")
	_check(GrowthRules.job_skill_upgradable("sword", "sword_slash") and not GrowthRules.job_skill_upgradable("sword", FAIR) and not GrowthRules.job_skill_upgradable("unknown", FAIR), "other series keep their skills; Fair Quote belongs to Merchant only")
	var ledger := CommerceLedger.new()
	ledger.reset(10)
	ledger.open_company("city", "m", 10)
	_check(ledger.week_income("city", 11, {"m": true}) == BASE and ledger.week_income("city", 11, {"m": true}, {"m": 2}) == BASE * 110 / 100, "the ledger pays the base without ranks and adds Fair Quote when given one")
	_check(ledger.week_income("city", 11, {}, {"m": 3}) == NPC, "a manager who no longer earns the companion rate gets no Fair Quote bonus")
	_check(GrowthRules.fair_quote_rank({"job_series": "merchant", "job_stage": 1, "job_records": {"merchant": {"skills": {FAIR: 3}}}}) == 0, "Fair Quote counts only at stage 2 (Contract Manager)")
	_check(GrowthRules.fair_quote_rank({"job_series": "tactics", "job_stage": 2, "job_records": {"merchant": {"skills": {FAIR: 3}}}}) == 0, "Fair Quote counts only while in the Merchant job")


func _test_path() -> void:
	app.begin_new_run()
	app.language = "zh"
	var city_id := String(app.current_location_id)
	_check(app.commerce_city_block_reason(city_id) == "", "the run starts in a discovered city that can host a company")
	_check(app.recruit_member("liang-xu"), "Liang Xu joins")
	var liang: Dictionary = app.member_state("liang-xu")
	app._grant_growth(app.hero_state, _xp_until_level(app.hero_state, 10), 0)
	app._grant_growth(liang, _xp_until_level(liang, 10), 0)

	# Level 10: the hero stays, Liang Xu switches to Merchant on the growth screen.
	change_scene_to_file(GROWTH_SCENE)
	await _settle()
	var growth: Node = current_scene
	growth.get("stay_button").pressed.emit()
	_check(growth.get("selected_id") == "liang-xu", "the growth screen moves on to Liang Xu")
	var series_buttons: Array = growth.get("series_buttons")
	series_buttons[growth.SERIES_IDS.find("merchant")].pressed.emit()
	liang = app.member_state("liang-xu")
	var upgrades: Array = growth.get("upgrade_buttons")
	_check(liang["job_series"] == "merchant" and int(liang["job_stage"]) == 1 and GrowthRules.fair_quote_rank(liang) == 0, "stage-1 Merchant has no Fair Quote")
	_check(not upgrades[1].visible and upgrades[0].disabled and String(upgrades[0].text) == app.text_for("growth_placeholder_skill") % app.text_for("job_skill_" + SUPPLY), "stage 1 shows only the Supply Pact placeholder")
	liang["jp"] = 500
	_check(not app.upgrade_job_skill("liang-xu", FAIR) and not app.upgrade_job_skill("liang-xu", SUPPLY) and int(liang["jp"]) == 500, "no JP is spent on Fair Quote before promotion or on Supply Pact")
	_check(String(growth.get("pending_label").text) == app.text_for("growth_merchant_note"), "stage 1 keeps the plain Merchant hint")

	# Level 20: promote to Contract Manager; Fair Quote starts at rank 1 for free.
	liang["jp"] = 0
	app._grant_growth(liang, _xp_until_level(liang, 20), 0)
	growth._refresh()
	growth.get("promote_button").pressed.emit()
	liang = app.member_state("liang-xu")
	_check(int(liang["job_stage"]) == 2 and GrowthRules.skill_rank(liang, FAIR) == 1 and GrowthRules.fair_quote_rank(liang) == 1 and int(liang["jp"]) == 0, "promotion to Contract Manager grants Fair Quote rank 1 with no JP")
	var cost_2 := GrowthRules.jp_cost(liang, "merchant", 2)
	var cost_3 := GrowthRules.jp_cost(liang, "merchant", 3)
	_check(cost_2 == 32 and cost_3 == 51, "JP costs follow the Adaptive aptitude path (Adaptive 67: rank 2 = 32, rank 3 = 51), got %d/%d" % [cost_2, cost_3])
	var fair_name: String = app.text_for("job_skill_" + FAIR)
	_check(upgrades[1].visible and upgrades[1].disabled and String(upgrades[1].text) == app.text_for("growth_upgrade") % [fair_name, cost_2], "the Fair Quote button shows its JP cost and is disabled without JP")
	_check(String(growth.get("pending_label").text) == app.text_for("growth_fair_quote_note") % [1, 5], "the growth screen states the rank-1 effect (+5 %)")
	_check(String(growth.get("skill_label").text).contains("暂无战斗效果"), "the skill line still says Merchant skills have no battle effect")
	liang["jp"] = 100
	growth._refresh()
	_check(not upgrades[1].disabled and upgrades[0].disabled, "with JP, Fair Quote can be upgraded and Supply Pact still cannot")
	upgrades[0].pressed.emit()
	_check(int(liang["jp"]) == 100 and GrowthRules.skill_rank(liang, SUPPLY) == 1, "pressing the Supply Pact placeholder spends nothing")
	upgrades[1].pressed.emit()
	_check(GrowthRules.skill_rank(liang, FAIR) == 2 and int(liang["jp"]) == 100 - cost_2, "upgrading Fair Quote spends exactly %d JP" % cost_2)
	_check(String(growth.get("pending_label").text) == app.text_for("growth_fair_quote_note") % [2, 10] and String(upgrades[1].text) == app.text_for("growth_upgrade") % [fair_name, cost_3], "the screen shows rank 2 (+10 %) and the next cost")
	var personal_rank := int(liang["personal_skill_rank"])
	liang["jp"] = 500
	growth.get("personal_upgrade_button").pressed.emit()
	_check(int(liang["personal_skill_rank"]) == personal_rank + 1 and int(liang["jp"]) < 500, "the personal skill stays upgradable")
	await _check_note_fits(growth, "zh")
	app.toggle_language()
	await process_frame
	_check(String(growth.get("pending_label").text) == "Fair Quote Lv2: +10% on fully stationed weeks. World map · Company.", "English rank note")
	await _check_note_fits(growth, "en")
	app.toggle_language()
	await process_frame

	await _check_battle_hides_merchant_skills()

	# Station Liang Xu: the rank is frozen while stationed.
	liang = app.member_state("liang-xu")
	liang["jp"] = 500
	_check(app.open_commerce_company(city_id, "liang-xu")["ok"] and not app.active_party_ids.has("liang-xu"), "Liang Xu opens the city company and leaves the party")
	_check(not app.upgrade_job_skill("liang-xu", FAIR) and GrowthRules.skill_rank(liang, FAIR) == 2 and int(liang["jp"]) == 500, "a stationed manager cannot upgrade Fair Quote")
	_check(app.commerce_companion_rate_percent("liang-xu") == 110, "the stationed rate at rank 2 is 110 %")
	_check(app.commerce_current_week_rate_percent(city_id) == 0, "the running opening week would settle at 0 %")
	await _check_company_panel(city_id, 110, "commerce_week_opening", [110], "opening week")
	_check(app.rest_one_week()["units"] == 0, "the opening week pays nothing")
	_check(app.rest_one_week()["units"] == 110 and _units() == 110, "a full stationed week at rank 2 pays 110")
	await _check_company_panel(city_id, 110, "", [], "full week at rank 2")

	# Save, buy rank 3 in a discarded timeline, load: rank, JP and ledger come back together.
	app.save_return_scene = MAP_SCENE
	var save_id: String = app.write_manual_save(1)
	_check(save_id != "" and app._valid_snapshot(app.make_snapshot("map", Vector2.ZERO, "manual_note")), "manual save with a stage-2 Merchant is valid")
	_check(app.rest_one_week()["units"] == 110, "one more week after saving")
	_check(app.recall_commerce_manager(city_id)["ok"] and app.upgrade_job_skill("liang-xu", FAIR) and GrowthRules.fair_quote_rank(app.member_state("liang-xu")) == 3, "after recall, Fair Quote can reach rank 3")
	_check(app.load_save(save_id), "load the save")
	liang = app.member_state("liang-xu")
	_check(GrowthRules.fair_quote_rank(liang) == 2 and int(liang["jp"]) == 500 and _units() == 110 and int(_company(city_id)["weeksSettled"]) == 1 and _company(city_id)["managerId"] == "liang-xu", "loading restores rank 2, the JP, the ledger and the post")
	_check(app.rest_one_week()["units"] == 110 and _units() == 220 and int(_company(city_id)["weeksSettled"]) == 2, "after loading, the next week settles once at rank 2; the discarded rank 3 never pays")

	# Recall: NPC weeks get no bonus. Upgrade in the party, station again: partial week NPC, then rank 3.
	_check(app.recall_commerce_manager(city_id)["ok"], "recall Liang Xu")
	_check(app.rest_one_week()["units"] == NPC, "an NPC-run week pays %d with no Fair Quote bonus" % NPC)
	_check(app.upgrade_job_skill("liang-xu", FAIR) and GrowthRules.fair_quote_rank(app.member_state("liang-xu")) == 3 and int(app.member_state("liang-xu")["jp"]) == 500 - cost_3, "back in the party, rank 3 costs %d JP" % cost_3)
	_check(app.upgrade_job_skill("liang-xu", FAIR) == false, "rank 3 is the maximum")
	_check(app.assign_commerce_manager(city_id, "liang-xu")["ok"], "station Liang Xu again")
	_check(app.commerce_companion_rate_percent("liang-xu") == 115 and app.commerce_current_week_rate_percent(city_id) == CommerceLedger.NPC_EFFICIENCY_PERCENT, "after re-stationing, the full-week rate is 115 % but the running week is at the NPC rate")
	await _check_company_panel(city_id, 115, "commerce_week_partial", [CommerceLedger.NPC_EFFICIENCY_PERCENT, 115], "re-stationed partial week")
	_check(app.rest_one_week()["units"] == NPC, "the partial week after stationing pays the NPC rate")
	_check(app.rest_one_week()["units"] == 115, "a full week at rank 3 pays 115")

	# Guards: a tampered rank is clamped; leaving Merchant or stage 2 drops the bonus.
	liang = app.member_state("liang-xu")
	liang["job_records"]["merchant"]["skills"][FAIR] = 99
	_check(app.rest_one_week()["units"] == 115, "a tampered rank 99 still pays only 115")
	liang["job_records"]["merchant"]["skills"][FAIR] = 3
	liang["job_stage"] = 1
	_check(app.rest_one_week()["units"] == BASE, "a stage-1 record pays the plain companion rate")
	liang["job_stage"] = 2
	liang["job_series"] = "tactics"
	_check(app.rest_one_week()["units"] == NPC, "a manager who left Merchant pays the NPC rate with no bonus")
	liang["job_series"] = "merchant"
	_check(app.rest_one_week()["units"] == 115, "back in Merchant, the full rate with Fair Quote returns")

	# The company panel shows the 115 % Fair Quote rate with no this-week caveat.
	await _check_company_panel(city_id, 115, "", [], "full week at rank 3")

	# Direct API: a stationed stage-1 Merchant with a pending choice can neither promote nor switch.
	liang = app.member_state("liang-xu")
	liang["job_stage"] = 1
	liang["job_records"]["merchant"]["stage"] = 1
	liang["pending_job_choices"] = 1
	var switch_target := ""
	for series_id in GrowthRules.SERIES:
		if series_id != "merchant" and GrowthRules.can_enter(liang, series_id):
			switch_target = series_id
	_check(switch_target != "", "Liang Xu has another series a switch could enter")
	_check(not app.choose_job("liang-xu", "promote") and not app.choose_job("liang-xu", "switch", switch_target), "a stationed manager cannot promote or switch through choose_job")
	_check(liang["job_series"] == "merchant" and int(liang["job_stage"]) == 1 and GrowthRules.skill_rank(liang, FAIR) == 3 and GrowthRules.fair_quote_rank(liang) == 0 and int(liang["pending_job_choices"]) == 1 and _company(city_id)["managerId"] == "liang-xu" and not app.active_party_ids.has("liang-xu"), "the refused choice keeps series, stage, rank, the pending choice and the post")
	_check(app.rest_one_week()["units"] == BASE, "that week still settles at the stage-1 companion rate")
	_check(app.recall_commerce_manager(city_id)["ok"] and app.choose_job("liang-xu", "promote") and int(liang["job_stage"]) == 2 and int(liang["pending_job_choices"]) == 0, "after recall the pending promotion goes through")


# Old save: before Fair Quote paid (da394c3), promotion already set the stage-2 skill to rank 1, so a
# save can hold a stationed Contract Manager with Fair Quote rank 1 whose weeks were paid the plain 100.
# The save format did not change. Loading keeps those weeks as paid; the next settlement pays 105.
func _test_legacy_save() -> void:
	app.begin_new_run()
	app.language = "zh"
	var city_id := String(app.current_location_id)
	_check(app.recruit_member("liang-xu"), "old save: Liang Xu joins")
	var liang: Dictionary = app.member_state("liang-xu")
	app._grant_growth(liang, _xp_until_level(liang, 10), 0)
	_check(app.choose_job("liang-xu", "switch", "merchant"), "old save: Liang Xu switches to Merchant")
	app._grant_growth(liang, _xp_until_level(liang, 20), 0)
	_check(app.choose_job("liang-xu", "promote"), "old save: Liang Xu is promoted to Contract Manager")
	_check(liang["job_records"]["merchant"] == {"stage": 2, "skills": {SUPPLY: 1, FAIR: 1}}, "old save: the Merchant record has the da394c3 shape, Fair Quote rank 1 from promotion: %s" % [liang["job_records"]["merchant"]])
	_check(app.open_commerce_company(city_id, "liang-xu")["ok"], "old save: Liang Xu opens the company")
	app.rest_one_week()
	app.rest_one_week()
	var snapshot: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
	var block: Dictionary = snapshot["commerce"]
	_check(block.keys() == ["version", "ledgerUnitKind", "settledWeekIndex", "ledgerUnits", "companies"] and int(block["version"]) == 1 and block["companies"][city_id].keys() == ["managerId", "managerSinceWeekIndex", "openedWeekIndex", "weeksSettled", "unitsEarned"], "old save: the commerce block keeps its version-1 shape (no Fair Quote field)")
	# da394c3 paid that one full week at the plain companion rate.
	block["ledgerUnits"] = BASE
	block["companies"][city_id]["unitsEarned"] = BASE
	var save_id := SaveStore.write_entry("manual", 2, snapshot)
	app.begin_new_run()
	_check(save_id != "" and app.load_save(save_id), "old save: the save loads")
	liang = app.member_state("liang-xu")
	_check(GrowthRules.fair_quote_rank(liang) == 1 and _company(city_id).get("managerId", "") == "liang-xu" and _units() == BASE and int(_company(city_id)["unitsEarned"]) == BASE and int(_company(city_id)["weeksSettled"]) == 1, "old save: rank 1, the post and the 100 already paid are restored as saved")
	_check(app.commerce_companion_rate_percent("liang-xu") == 105 and app.commerce_current_week_rate_percent(city_id) == 105, "old save: the running full week is at 105 %")
	var result: Dictionary = app.rest_one_week()
	_check(int(result["weeks_settled"]) == 1 and int(result["units"]) == 105 and _units() == BASE + 105 and int(_company(city_id)["unitsEarned"]) == BASE + 105 and int(_company(city_id)["weeksSettled"]) == 2, "old save: the next settlement pays 105 once; the earlier week stays at 100")


# Opens the company panel in zh and en. The companion line must show full_rate as the full-week rate;
# week_key names the this-week caveat line that must follow it ("" = no caveat in either form).
func _check_company_panel(city_id: String, full_rate: int, week_key: String, week_args: Array, label: String) -> void:
	change_scene_to_file(MAP_SCENE)
	await _settle()
	var map: Node = current_scene
	map.open_commerce()
	var body: RichTextLabel = map.get("commerce_body")
	var texts := {}
	for language in ["zh", "en"]:
		if app.language != language:
			app.toggle_language()
			map._refresh_commerce()
		await process_frame
		var company: Dictionary = _company(city_id)
		var text := String(body.text)
		texts[language] = text
		var line: String = app.text_for("commerce_company_companion") % [app.travel_location_name(city_id), app.member_name("liang-xu"), full_rate, int(company["weeksSettled"]), int(company["unitsEarned"])]
		var opening: String = app.text_for("commerce_week_opening") % full_rate
		var partial: String = app.text_for("commerce_week_partial") % [CommerceLedger.NPC_EFFICIENCY_PERCENT, full_rate]
		var week_ok := not text.contains(opening) and not text.contains(partial)
		if week_key != "":
			week_ok = text.contains(line + "\n" + app.text_for(week_key) % week_args)
		_check(map.get("commerce_overlay").visible and text.contains(line) and week_ok, "company panel, %s (%s): full-week %d %% and the right this-week line: %s" % [label, language, full_rate, text])
		_check(body.get_content_height() <= body.size.y, "company text fits, %s (%s): %d/%d" % [label, language, body.get_content_height(), int(body.size.y)])
	if week_key == "commerce_week_partial":
		_check(String(texts["zh"]).contains("满周收益 %d%%" % full_rate) and String(texts["zh"]).contains("本周：派驻未满一周，按普通 NPC 80%% 结算；下周起按满周 %d%%。" % full_rate), "Chinese full-week label and partial-week line")
		_check(String(texts["en"]).contains("full-week rate %d%%" % full_rate) and String(texts["en"]).contains("This week: not stationed for the full week, so it settles at the NPC rate (80%%); %d%% from next week." % full_rate), "English full-week label and partial-week line")
	if app.language != "zh":
		app.toggle_language()
	map.close_commerce()


func _check_battle_hides_merchant_skills() -> void:
	app.begin_battle("patrol", Vector2(330, 215))
	change_scene_to_file(BATTLE_SCENE)
	await _settle()
	var battle: Node = current_scene
	var fighters: Array = battle.get("fighters")
	var liang_index := -1
	for index in fighters.size():
		if fighters[index]["id"] == "liang-xu":
			liang_index = index
	_check(liang_index > 0, "the Contract Manager fights in the party")
	battle.set("enemy_windup", 0.0)
	battle._choose_control(liang_index)
	battle._toggle_pause()
	var job_buttons: Array = battle.get("pause_job_skill_buttons")
	_check(battle.get("paused") and not job_buttons[0].visible and not job_buttons[1].visible, "neither Merchant skill is shown in battle at stage 2")
	var energy := int(app.member_state("liang-xu")["energy"])
	_check(not battle._use_job_skill(liang_index, FAIR) and not battle._use_job_skill(liang_index, SUPPLY) and int(app.member_state("liang-xu")["energy"]) == energy, "Fair Quote and Supply Pact never run in battle")
	battle._toggle_pause()
	battle.set("enemy_hp", 1)
	fighters[0]["x"] = battle.get("enemy_x") - 40.0
	fighters[0]["attack_cooldown"] = 0.0
	battle._try_attack(0)
	_check(battle.get("battle_won"), "the check battle is won")
	battle._return_after_result()
	await _settle()


func _check_note_fits(growth: Node, language: String) -> void:
	await process_frame
	var label: Label = growth.get("pending_label")
	_check(label.position.x + label.get_combined_minimum_size().x <= 640.0 and label.get_global_rect().end.y <= growth.get("upgrade_buttons")[0].get_global_rect().position.y, "the Fair Quote note fits on screen (%s): %s" % [language, label.get_combined_minimum_size()])


func _company(city_id: String) -> Dictionary:
	return app.commerce_ledger_state()["companies"].get(city_id, {})


func _units() -> int:
	return int(app.commerce_ledger_state()["ledgerUnits"])


func _xp_until_level(member: Dictionary, target_level: int) -> int:
	var required := -int(member.get("xp", 0))
	for level in range(int(member["level"]), target_level):
		required += GrowthRules.xp_to_next(level)
	return required


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
		push_error("Merchant Fair Quote check failed: " + label)
	return condition
