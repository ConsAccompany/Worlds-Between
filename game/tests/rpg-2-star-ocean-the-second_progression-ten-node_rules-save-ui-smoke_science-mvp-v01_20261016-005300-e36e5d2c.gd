extends SceneTree

# SCIENCE-MVP ten-node progression slice (creator rules 2026-10-15). Checks:
# - the catalog against canon: the 20 approved series (ids, names, five stage names) and the 51 Game Bible
#   identities, 10 career nodes per series (2 per stage) and 10 personal nodes per identity by level 100;
#   only nodes the runtime already executes carry an effect, and no node design is claimed as authored;
# - rules: both nodes of a stage open at rank 1 on entry with no JP; JP only raises ranks 2-5; rank cap 5
#   for career and personal skills; stages 1-4 by level choice and stage 5 only after the series final
#   quest; switching series keeps every record; the signature is open on joining and personal nodes open
#   by level gates up to 100; skeleton nodes take no JP;
# - recruit seeding (provisional): stage 1 + level / 10, held at 4 until the home series final quest, with
#   only rank-1 stage nodes; old saves keep their seeded stage;
# - additive save migration of older records, round trip of the final-quest flag, clamping and rejection;
# - the growth screen's node overlay (zh/en) upgrades real nodes and stays on screen; a stationed Contract
#   Manager's Fair Quote buttons are disabled with the localized reason until recall.
# Optional: -- --capture=<absolute dir> writes zh/en PNGs of the overlay (windowed runs only).

const SAVE_ROOT := "user://test-saves/progression-ten-node"
const GROWTH_SCENE := "res://scenes/growth_screen.tscn"
const ROSTER := "outputs/rpg-2-star-ocean-the-second_all-jobs_five-tier-proposal_v01_20261013-224236-6f2b9c11.json"
const BIBLE := "outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json"
const APTITUDE_ZH := {"武艺": "martial", "应变": "adaptive", "研学": "scholarly", "灵觉": "spiritual"}

var app: Node
var checks := 0
var failures := 0
var capture_dir := ""


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	app = root.get_node("AppState")
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--capture="):
			capture_dir = argument.trim_prefix("--capture=")
	SaveStore.root_path = SAVE_ROOT
	_clear_saves()
	_test_catalog()
	_test_career_rules()
	_test_personal_rules()
	_test_recruits()
	_test_save_migration()
	await _test_ui()
	await _test_stationed_fair_quote_ui()
	_clear_saves()
	if failures > 0:
		print("PROGRESSION_TEN_NODE_FAILED failures=%d checks=%d" % [failures, checks])
		quit(1)
		return
	print("PROGRESSION_TEN_NODE_OK checks=%d" % checks)
	quit(0)


func _test_catalog() -> void:
	var catalog: Dictionary = GrowthRules.catalog()
	var rules: Dictionary = catalog.get("rules", {})
	_check(int(rules.get("careerStages", 0)) == 5 and int(rules.get("careerNodesPerStage", 0)) == 2 and int(rules.get("skillRankCap", 0)) == GrowthRules.SKILL_RANK_CAP and GrowthRules.SKILL_RANK_CAP == 5, "catalog rules: 5 stages x 2 nodes, rank cap 5")
	_check(rules.get("jpUnlocksNodes") == false and rules.get("changingSeriesPreservesRecords") == true and int(rules.get("personalLevelCeiling", 0)) == 100, "catalog rules: JP never unlocks, records persist, personal ceiling Lv100")
	var gates: Array = rules.get("personalUnlockLevels", [])
	_check(gates.size() == 10 and int(gates[0]) == 1 and int(gates[9]) == 100, "catalog rules: personal gates run from Lv1 to the creator's final gate Lv100: %s" % [gates])
	var roster: Array = _read_repo_json(ROSTER).get("series", [])
	var series: Array = catalog.get("series", [])
	_check(roster.size() == 20 and series.size() == 20, "20 approved series in roster and catalog")
	var node_ids := {}
	var career_effects := 0
	for index in mini(roster.size(), series.size()):
		var canon: Dictionary = roster[index]
		var entry: Dictionary = series[index]
		var id := String(canon["id"])
		_check(entry["id"] == id and entry["nameZh"] == canon["name"] and entry["nameEn"] == canon["en"] and entry["stageNamesZh"] == canon["stages"] and entry["aptitude"] == APTITUDE_ZH[canon["aptitude"]], "series identity matches the approved roster: " + id)
		var per_stage := {}
		for node in entry["nodes"]:
			per_stage[int(node["stage"])] = int(per_stage.get(int(node["stage"]), 0)) + 1
			_check(not node_ids.has(node["id"]), "career node id is unique: " + String(node["id"]))
			node_ids[node["id"]] = true
			career_effects += 1 if node["effect"] != "none" else 0
		_check(entry["nodes"].size() == 10 and per_stage == {1: 2, 2: 2, 3: 2, 4: 2, 5: 2}, "10 nodes, 2 per stage: " + id)
		_check(bool(entry["runtimeEnterable"]) == GrowthRules.SERIES.has(id), "runtime-enterable flag matches GrowthRules.SERIES: " + id)
		if GrowthRules.SERIES.has(id):
			_check(GrowthRules.SERIES[id]["aptitude"] == entry["aptitude"] and GrowthRules.SERIES[id]["skills"] == [GrowthRules.stage_node_ids(id, 1)[0], GrowthRules.stage_node_ids(id, 2)[0]], "battle action list is the stage-1/2 'a' nodes: " + id)
	_check(node_ids.size() == 200 and career_effects == 9, "200 career nodes; 9 carry an existing runtime effect (8 battle + Fair Quote)")
	var characters: Array = _read_repo_json(BIBLE).get("characters", [])
	var identities: Array = catalog.get("identities", [])
	_check(characters.size() == 51 and identities.size() == 51, "51 identities in Game Bible and catalog")
	var personal_effects := 0
	var personal_ids := {}
	for index in mini(characters.size(), identities.size()):
		var canon: Dictionary = characters[index]
		var identity: Dictionary = identities[index]
		_check(identity["id"] == canon["id"] and identity["nameZh"] == canon["cn"] and identity["nameEn"] == canon["en"], "identity matches the Game Bible: " + String(canon["id"]))
		var nodes: Array = identity["nodes"]
		var gates_ok := gates.size() == 10 and nodes.size() == 10 and int(nodes[0]["unlockLevel"]) == 1 and bool(nodes[0].get("signature", false)) and bool(nodes[0].get("availableOnJoin", false))
		for order in nodes.size():
			gates_ok = gates_ok and int(nodes[order]["order"]) == order + 1 and int(nodes[order]["unlockLevel"]) == int(gates[order]) and (order == 0 or int(nodes[order]["unlockLevel"]) > int(nodes[order - 1]["unlockLevel"]))
			personal_effects += 1 if nodes[order]["effect"] != "none" else 0
			personal_ids[nodes[order]["id"]] = true
		gates_ok = gates_ok and int(nodes[9]["unlockLevel"]) == 100
		_check(gates_ok, "10 personal nodes, signature on joining, shared ascending gates, node 10 at Lv100: " + String(canon["id"]))
	_check(personal_ids.size() == 510 and personal_effects == 4, "510 personal nodes; only the 4 runtime signatures carry an effect")
	for member_id in app.MEMBER_DEFS:
		var identity := GrowthRules.identity_for_member(member_id)
		_check(not identity.is_empty() and identity["nodes"][0].get("nameKey", "") == app.MEMBER_DEFS[member_id]["skill_key"], "runtime member maps to its identity and signature skill: " + member_id)
	var counts: Dictionary = catalog.get("counts", {})
	_check(int(counts.get("approvedNodeDesignsAuthored", -1)) == 0 and int(counts.get("careerNodes", 0)) == 200 and int(counts.get("personalNodes", 0)) == 510, "catalog does not claim any of the 710 node designs as authored")


func _test_career_rules() -> void:
	app.begin_new_run()
	var hero: Dictionary = app.hero_state
	_check(hero["job_records"] == {"sword": {"stage": 1, "skills": {"sword_slash": 1, "sword_s1b": 1}}}, "new run: both stage-1 sword nodes open at rank 1, nothing else: %s" % [hero["job_records"]])
	_check(GrowthRules.jp_cost(hero, "sword", 1) == -1 and GrowthRules.jp_cost(hero, "sword", 2) == 35 and GrowthRules.jp_cost(hero, "sword", 5) == 110 and GrowthRules.jp_cost(hero, "sword", 6) == -1, "JP prices ranks 2-5 only")
	hero["jp"] = 2000
	_check(not app.upgrade_job_skill("hero", "sword_s1b") and int(hero["jp"]) == 2000, "a skeleton node takes no JP")
	_check(not app.upgrade_job_skill("hero", "sword_arc") and int(hero["jp"]) == 2000, "JP cannot open a node of an unentered stage")
	for rank in [2, 3, 4, 5]:
		_check(app.upgrade_job_skill("hero", "sword_slash") and GrowthRules.skill_rank(hero, "sword_slash") == rank, "JP raises sword_slash to rank %d" % rank)
	_check(not app.upgrade_job_skill("hero", "sword_slash") and int(hero["jp"]) == 2000 - 280, "rank 5 is the cap; ranks 2-5 cost 35+55+80+110")
	_reach(hero, 10)
	_check(app.choose_job("hero", "promote") and int(hero["job_stage"]) == 2 and GrowthRules.skill_rank(hero, "sword_arc") == 1 and GrowthRules.skill_rank(hero, "sword_s2b") == 1 and int(hero["jp"]) == 1720, "promotion opens both stage-2 nodes with no JP")
	_reach(hero, 20)
	_check(app.choose_job("hero", "promote") and int(hero["job_stage"]) == 3 and GrowthRules.skill_rank(hero, "sword_s3a") == 1 and GrowthRules.skill_rank(hero, "sword_s3b") == 1, "stage 3 by level choice")
	_reach(hero, 30)
	_check(app.choose_job("hero", "promote") and int(hero["job_stage"]) == 4 and hero["job_records"]["sword"]["skills"].size() == 8, "stage 4 by level choice; 8 of 10 nodes open")
	_reach(hero, 40)
	_check(not GrowthRules.can_promote(hero, app.cleared_final_quests) and not app.choose_job("hero", "promote") and int(hero["job_stage"]) == 4, "stage 5 is refused before the series final quest")
	_check(app.choose_job("hero", "switch", "firearms") and hero["job_series"] == "firearms" and hero["job_records"]["firearms"] == {"stage": 1, "skills": {"firearms_shot": 1, "firearms_s1b": 1}}, "switching opens the new series at stage 1 with its two nodes")
	_check(hero["job_records"]["sword"]["stage"] == 4 and GrowthRules.career_nodes("sword").size() == 10 and int(hero["job_records"]["sword"]["skills"]["sword_slash"]) == 5, "the sword record is kept while away")
	_reach(hero, 50)
	_check(app.choose_job("hero", "switch", "sword") and int(hero["job_stage"]) == 4 and GrowthRules.skill_rank(hero, "sword_slash") == 5 and hero["job_records"].has("firearms"), "switching back restores stage 4 and rank 5")
	_check(app.clear_series_final_quest("sword") and not app.clear_series_final_quest("sword") and not app.clear_series_final_quest("no-such-series"), "a series final quest clears once, for known series only")
	_reach(hero, 60)
	_check(app.choose_job("hero", "promote") and int(hero["job_stage"]) == 5 and GrowthRules.skill_rank(hero, "sword_s5a") == 1 and GrowthRules.skill_rank(hero, "sword_s5b") == 1 and hero["job_records"]["sword"]["skills"].size() == 10, "after the final quest, stage 5 opens its 2 nodes; all 10 open")
	_check(GrowthRules.current_skill_id(hero) == "sword_arc" and GrowthRules.job_skills_have_effect("sword"), "the battle keeps its last action skill at stages 3-5")
	_reach(hero, 70)
	_check(not app.choose_job("hero", "promote") and app.choose_job("hero", "stay") and int(hero["job_stage"]) == 5, "stage 5 is the last stage")
	_check(GrowthRules.stage_name("sword", 5, "zh") == "界线剑圣" and GrowthRules.stage_name("sword", 1, "zh") == "剑客" and GrowthRules.stage_name("tactics", 3, "en") == "Tactics · Stage 3", "canonical stage names; English falls back where none is approved")


func _test_personal_rules() -> void:
	app.begin_new_run()
	var hero: Dictionary = app.hero_state
	var signature := GrowthRules.signature_node_id("hero")
	_check(signature == "hero.p01" and GrowthRules.personal_node_rank(hero, "hero", signature) == 1 and hero["personal_node_ranks"].is_empty(), "level 1: only the signature skill is open")
	hero["jp"] = 2000
	for rank in [2, 3, 4, 5]:
		_check(app.upgrade_personal_node("hero", signature) and int(hero["personal_skill_rank"]) == rank, "JP raises the signature to rank %d" % rank)
	_check(not app.upgrade_personal_skill("hero") and int(hero["jp"]) == 2000 - 280, "personal rank cap is 5")
	_reach(hero, 10)
	_check(hero["personal_node_ranks"] == {"hero.p02": 1}, "level 10 opens the Lv6 node only: %s" % [hero["personal_node_ranks"]])
	_check(not app.upgrade_personal_node("hero", "hero.p02") and not app.upgrade_personal_node("hero", "hero.p03") and int(hero["jp"]) == 1720, "skeleton and unopened personal nodes take no JP")
	app.choose_job("hero", "stay")
	while int(hero["level"]) < 90:
		_reach(hero, int(hero["level"]) + 10 - int(hero["level"]) % 10)
		app.choose_job("hero", "stay")
	_check(hero["personal_node_ranks"].size() == 8 and not hero["personal_node_ranks"].has("hero.p10"), "level 90: nodes 2-9 open, the Lv100 node is not")
	_reach(hero, 99)
	_check(hero["personal_node_ranks"].size() == 8 and not hero["personal_node_ranks"].has("hero.p10"), "level 99: the final personal node is still closed")
	_reach(hero, 100)
	_check(hero["personal_node_ranks"].size() == 9 and int(hero["personal_node_ranks"]["hero.p10"]) == 1 and int(hero["personal_skill_rank"]) == 5, "level 100 opens the final node: all 10 personal nodes are open")
	app.choose_job("hero", "stay")


func _test_recruits() -> void:
	app.begin_new_run()
	_check(app.recruit_member("zhao-ling"), "level-1 recruit joins")
	var zhao: Dictionary = app.member_state("zhao-ling")
	_check(GrowthRules.personal_node_rank(zhao, "zhao-ling", "character-31.p01") == 1 and zhao["personal_node_ranks"].is_empty(), "the unique signature skill is available on recruitment")
	_check(zhao["job_records"] == {"firearms": {"stage": 1, "skills": {"firearms_shot": 1, "firearms_s1b": 1}}}, "recruit's stage-1 nodes are open")
	app.begin_new_run()
	app.hero_state["level"] = 23
	_check(app.recruit_member("liang-xu"), "level-23 recruit joins")
	var liang: Dictionary = app.member_state("liang-xu")
	_check(int(liang["job_stage"]) == 3 and liang["job_records"]["tactics"] == {"stage": 3, "skills": {"tactics_mark": 1, "tactics_s1b": 1, "tactics_rally": 1, "tactics_s2b": 1, "tactics_s3a": 1, "tactics_s3b": 1}}, "level-23 recruit passed the Lv10 and Lv20 choices: stage 3 with its six nodes at rank 1")
	_check(liang["personal_node_ranks"] == {"character-01.p02": 1, "character-01.p03": 1, "character-01.p04": 1}, "a later recruit opens every personal node at or below the synced level")
	# Provisional seeding: stage = 1 + level / 10, held at stage 4 until the home series final quest.
	for case in [[1, 1], [9, 1], [10, 2], [19, 2], [20, 3], [30, 4], [39, 4], [40, 4], [99, 4]]:
		_check(GrowthRules.recruit_stage(case[0], "relics", {}) == case[1], "recruit stage at level %d is %d" % case)
	_check(GrowthRules.recruit_stage(40, "relics", {"relics": true}) == 5 and GrowthRules.recruit_stage(39, "relics", {"relics": true}) == 4 and GrowthRules.recruit_stage(99, "relics", {"sword": true}) == 4, "stage 5 needs level 40 and that series' own final quest")
	app.begin_new_run()
	app.hero_state["level"] = 45
	app.ji_records_checked = true
	_check(app.recruit_member("ji-cheng") and app.recruit_member("zhao-ling"), "level-45 recruits join")
	var ji: Dictionary = app.member_state("ji-cheng")
	_check(int(ji["job_stage"]) == 4 and int(ji["job_records"]["relics"]["stage"]) == 4 and ji["job_records"]["relics"]["skills"].size() == 8 and not ji["job_records"]["relics"]["skills"].has("relics_s5a"), "without the final quest a level-45 recruit is held at stage 4 with 8 nodes")
	var ranks_one := true
	for member in [ji, app.member_state("zhao-ling")]:
		for rank in member["job_records"][member["job_series"]]["skills"].values():
			ranks_one = ranks_one and int(rank) == 1
	_check(ranks_one and int(ji["jp"]) == 0 and int(ji["pending_job_choices"]) == 0, "seeded nodes are all rank 1; no JP-paid rank, no JP and no pending choice")
	_check(ji["job_series"] == "relics" and ji["job_records"].size() == 1 and ji["aptitudes"] == app.MEMBER_DEFS["ji-cheng"]["aptitudes"] and app.member_state("zhao-ling")["job_series"] == "firearms", "recruits keep their own home series and aptitudes")
	_check(int(ji["personal_skill_rank"]) == 3 and ji["learned_skill_ids"] == ["basic", "advanced"], "the existing signature catch-up still stops at rank 3")
	app.begin_new_run()
	app.hero_state["level"] = 45
	app.ji_records_checked = true
	_check(app.clear_series_final_quest("sword") and app.recruit_member("ji-cheng") and int(app.member_state("ji-cheng")["job_stage"]) == 4, "another series' final quest does not open stage 5")
	app.begin_new_run()
	app.hero_state["level"] = 45
	app.ji_records_checked = true
	_check(app.clear_series_final_quest("relics") and app.recruit_member("ji-cheng"), "a level-45 recruit joins after the relics final quest")
	ji = app.member_state("ji-cheng")
	_check(int(ji["job_stage"]) == 5 and ji["job_records"]["relics"]["skills"].size() == 10 and int(ji["job_records"]["relics"]["skills"]["relics_s5b"]) == 1, "after the party clears its series final quest, the recruit enters stage 5 with all 10 nodes")
	# The hero's level was set directly, so open its personal nodes first; otherwise loading migrates them.
	GrowthRules.unlock_personal_nodes(app.hero_state, "hero")
	var save_id := SaveStore.write_entry("manual", 2, app.make_snapshot("map", Vector2.ZERO, "manual_note"))
	app.begin_new_run()
	_check(save_id != "" and app.load_save(save_id) and not app.growth_state_migrated and int(app.member_state("ji-cheng")["job_stage"]) == 5, "a stage-5 recruit round-trips with no migration")
	# Old saves keep the recruit stage they were written with: loading never re-seeds a stage.
	app.begin_new_run()
	app.hero_state["level"] = 23
	app.recruit_member("liang-xu")
	var legacy: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
	legacy["members"]["liang-xu"]["job_stage"] = 2
	legacy["members"]["liang-xu"]["job_records"] = {"tactics": {"stage": 2, "skills": {"tactics_mark": 1, "tactics_rally": 1}}}
	var legacy_id := SaveStore.write_entry("manual", 3, legacy)
	app.begin_new_run()
	_check(legacy_id != "" and app.load_save(legacy_id) and int(app.member_state("liang-xu")["job_stage"]) == 2 and app.member_state("liang-xu")["job_records"]["tactics"]["skills"].size() == 4, "an old stage-2 recruit save loads at stage 2 (only its stage-2 nodes are added)")


func _test_save_migration() -> void:
	app.begin_new_run()
	var legacy: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
	legacy.erase("growthFinalQuests")
	var hero: Dictionary = legacy["hero"]
	hero.erase("personal_node_ranks")
	hero["level"] = 15
	hero["job_stage"] = 2
	hero["personal_skill_rank"] = 3
	hero["job_records"] = {"sword": {"stage": 2, "skills": {"sword_slash": 1, "sword_arc": 3}}, "firearms": {"stage": 1, "skills": {"firearms_shot": 2}}}
	var legacy_id := SaveStore.write_entry("manual", 1, legacy)
	app.begin_new_run()
	_check(legacy_id != "" and app.load_save(legacy_id) and app.growth_state_migrated, "a pre-ten-node save loads and reports migration")
	hero = app.hero_state
	_check(hero["job_records"]["sword"]["skills"] == {"sword_slash": 1, "sword_arc": 3, "sword_s1b": 1, "sword_s2b": 1} and hero["job_records"]["firearms"]["skills"] == {"firearms_shot": 2, "firearms_s1b": 1}, "migration only adds the nodes each saved stage earns and keeps every rank: %s" % [hero["job_records"]])
	_check(int(hero["personal_skill_rank"]) == 3 and hero["personal_node_ranks"] == {"hero.p02": 1, "hero.p03": 1} and app.cleared_final_quests.is_empty(), "migration opens personal nodes up to the saved level and keeps the signature rank")
	_check(app.clear_series_final_quest("sword"), "clear the sword final quest")
	var current_id := SaveStore.write_entry("manual", 2, app.make_snapshot("map", Vector2.ZERO, "manual_note"))
	app.begin_new_run()
	_check(app.load_save(current_id) and not app.growth_state_migrated and app.cleared_final_quests == {"sword": true} and int(app.hero_state["job_records"]["sword"]["skills"]["sword_arc"]) == 3, "a current save round-trips the final quest flag with no migration")
	var tampered: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
	tampered["hero"]["job_records"]["sword"]["skills"]["sword_arc"] = 99
	tampered["hero"]["personal_node_ranks"]["hero.p02"] = 42
	tampered["hero"]["personal_skill_rank"] = 0
	var tampered_id := SaveStore.write_entry("manual", 3, tampered)
	_check(app.load_save(tampered_id) and app.growth_state_migrated and int(app.hero_state["job_records"]["sword"]["skills"]["sword_arc"]) == 5 and int(app.hero_state["personal_node_ranks"]["hero.p02"]) == 5 and int(app.hero_state["personal_skill_rank"]) == 1, "out-of-range ranks are clamped to 1..5 on load")
	for case in [["stage 7", "job_stage", 7], ["node ranks not a dictionary", "personal_node_ranks", []]]:
		var bad: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
		bad["hero"][case[1]] = case[2]
		var bad_id := SaveStore.write_entry("manual", 3, bad)
		_check(bad_id != "" and not app.load_save(bad_id), "an invalid growth save is written and rejected on load: " + String(case[0]))
	var bad_quest: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
	bad_quest["growthFinalQuests"] = {"no-such-series": true}
	_check(not app._valid_snapshot(bad_quest), "an unknown series final quest is rejected")


func _test_ui() -> void:
	app.begin_new_run()
	app.language = "zh"
	var hero: Dictionary = app.hero_state
	_reach(hero, 10)
	app.choose_job("hero", "promote")
	hero["jp"] = 1000
	app.growth_return_scene = "res://scenes/scifi_world_map.tscn"
	change_scene_to_file(GROWTH_SCENE)
	await _settle()
	var growth: Control = current_scene
	_check(not growth.get("node_panel").visible and growth.get("nodes_button").visible and _inside_screen(growth.get("nodes_button")) and growth.get("nodes_button").get_global_rect().position.x >= growth.get("personal_upgrade_button").get_global_rect().end.x, "the node overlay starts hidden; its button fits beside the personal button")
	growth.get("nodes_button").pressed.emit()
	await _settle()
	_check(growth.get("node_panel").visible and growth.get("career_node_ids") == _ids(GrowthRules.career_nodes("sword")) and growth.get("personal_node_ids") == _ids(GrowthRules.personal_nodes("hero")), "the overlay lists the 10 sword nodes and the 10 hero nodes")
	var career: Array = growth.get("career_node_buttons")
	var personal: Array = growth.get("personal_node_buttons")
	_check(not career[2].disabled and String(career[2].text).contains("回旋剑势") and String(career[2].text).contains("35 JP"), "the stage-2 action node is upgradable for 35 JP")
	_check(career[1].disabled and String(career[1].text).contains("待设计") and career[4].disabled and String(career[4].text).contains("第 3 阶开放"), "skeleton and unopened career nodes are shown but disabled")
	_check(not personal[0].disabled and personal[1].disabled and String(personal[1].text).contains("待设计") and personal[2].disabled and String(personal[2].text).contains("Lv14 开放"), "signature upgradable; Lv6 skeleton open but disabled; Lv14 node locked")
	_check(String(growth.get("node_summary_label").text).contains("职业 2/10 · 个人 1/10"), "the overlay states how few nodes have an effect")
	career[2].pressed.emit()
	personal[0].pressed.emit()
	_check(GrowthRules.skill_rank(hero, "sword_arc") == 2 and int(hero["personal_skill_rank"]) == 2 and int(hero["jp"]) == 1000 - 70, "overlay buttons spend JP on the real nodes")
	for language in ["zh", "en"]:
		if app.language != language:
			app.toggle_language()
		await _settle()
		var fits := true
		for control in career + personal + [growth.get("node_close_button")]:
			fits = fits and _inside_screen(control)
		for label in [growth.get("node_title_label"), growth.get("node_career_label"), growth.get("node_personal_label")]:
			fits = fits and label.position.x + label.get_combined_minimum_size().x <= 640.0
		var summary: Label = growth.get("node_summary_label")
		fits = fits and summary.get_global_rect().end.y <= 360.0 and summary.get_line_count() * 16 <= int(summary.size.y)
		_check(fits, "overlay fits on screen (%s)" % language)
		_capture("overlay-" + language)
	growth.get("node_close_button").pressed.emit()
	_check(not growth.get("node_panel").visible, "the overlay closes")
	app.language = "zh"
	hero["job_stage"] = 4
	hero["job_records"]["sword"]["stage"] = 4
	hero["pending_job_choices"] = 1
	growth._refresh()
	_check(growth.get("promote_button").disabled and growth.get("promote_button").text == app.text_for("growth_promote_final_quest"), "stage-4 promotion names the final quest and stays disabled")
	app.clear_series_final_quest("sword")
	growth._refresh()
	_check(not growth.get("promote_button").disabled and growth.get("promote_button").text == app.text_for("growth_promote"), "after the final quest, promotion to stage 5 is offered")
	growth.get("promote_button").pressed.emit()
	_check(int(hero["job_stage"]) == 5 and GrowthRules.skill_rank(hero, "sword_s5b") == 1, "the screen promotes to stage 5")


# A stationed Contract Manager's Fair Quote is frozen: both growth-screen buttons must be disabled with
# the localized reason, matching the refused press, and come back after recall.
func _test_stationed_fair_quote_ui() -> void:
	app.begin_new_run()
	app.language = "zh"
	var city_id := String(app.current_location_id)
	_check(app.recruit_member("liang-xu"), "Liang Xu joins for the stationed check")
	var liang: Dictionary = app.member_state("liang-xu")
	_reach(liang, 10)
	_check(app.choose_job("liang-xu", "switch", "merchant"), "Liang Xu switches to Merchant")
	_reach(liang, 20)
	_check(app.choose_job("liang-xu", "promote") and GrowthRules.fair_quote_rank(liang) == 1, "Liang Xu is a rank-1 Contract Manager")
	liang["jp"] = 500
	_check(app.open_commerce_company(city_id, "liang-xu")["ok"] and app.fair_quote_frozen("liang-xu") and not app.fair_quote_frozen("liang-xu", "merchant_supply_pact"), "stationed: Fair Quote alone is frozen")
	change_scene_to_file(GROWTH_SCENE)
	await _settle()
	var growth: Control = current_scene
	growth.set("selected_id", "liang-xu")
	growth.get("nodes_button").pressed.emit()
	await _settle()
	for language in ["zh", "en"]:
		if app.language != language:
			app.toggle_language()
		await _settle()
		var fair_name: String = app.text_for("job_skill_merchant_fair_quote")
		var upgrade: Button = growth.get("upgrade_buttons")[1]
		var node_index: int = growth.get("career_node_ids").find("merchant_fair_quote")
		var node: Button = growth.get("career_node_buttons")[node_index]
		var reason: String = app.text_for("growth_fair_quote_frozen")
		_check(upgrade.disabled and upgrade.text == app.text_for("growth_fair_quote_frozen_button") % fair_name and String(growth.get("pending_label").text) == reason, "main Fair Quote button is disabled and the reason is shown (%s)" % language)
		_check(node_index == 2 and node.disabled and String(node.text).ends_with(app.text_for("growth_node_frozen") % 1) and String(growth.get("node_summary_label").text).ends_with(reason), "overlay Fair Quote node is disabled with the reason (%s)" % language)
		var summary: Label = growth.get("node_summary_label")
		var pending: Label = growth.get("pending_label")
		_check(_inside_screen(upgrade) and _inside_screen(node) and summary.get_global_rect().end.y <= 360.0 and summary.get_line_count() * 16 <= int(summary.size.y) and pending.position.x + pending.get_combined_minimum_size().x <= 640.0, "stationed texts fit on screen (%s)" % language)
		_capture("stationed-" + language)
	growth.get("career_node_buttons")[2].pressed.emit()
	growth.get("upgrade_buttons")[1].pressed.emit()
	_check(GrowthRules.skill_rank(liang, "merchant_fair_quote") == 1 and int(liang["jp"]) == 500, "pressing the frozen buttons spends nothing")
	_check(app.recall_commerce_manager(city_id)["ok"], "recall Liang Xu")
	growth._refresh()
	_check(not growth.get("upgrade_buttons")[1].disabled and not growth.get("career_node_buttons")[2].disabled and not String(growth.get("node_summary_label").text).contains(app.text_for("growth_fair_quote_frozen")), "after recall Fair Quote is upgradable again")
	growth.get("career_node_buttons")[2].pressed.emit()
	_check(GrowthRules.skill_rank(liang, "merchant_fair_quote") == 2 and int(liang["jp"]) < 500, "and the press now spends JP")
	app.language = "zh"


func _reach(member: Dictionary, level: int) -> void:
	var required := -int(member.get("xp", 0))
	for current in range(int(member["level"]), level):
		required += GrowthRules.xp_to_next(current)
	app._grant_growth(member, required, 0)
	_check(int(member["level"]) == level, "reached level %d" % level)


func _ids(nodes: Array) -> Array[String]:
	var ids: Array[String] = []
	for node in nodes:
		ids.append(String(node["id"]))
	return ids


func _read_repo_json(relative: String) -> Dictionary:
	var path := ProjectSettings.globalize_path("res://").path_join("..").path_join(relative).simplify_path()
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		_check(false, "canon source readable: " + path)
		return {}
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	return parsed if typeof(parsed) == TYPE_DICTIONARY else {}


func _capture(label: String) -> void:
	if capture_dir == "" or DisplayServer.get_name() == "headless":
		return
	var image := root.get_texture().get_image()
	var path := capture_dir.path_join("progression-ten-node_%s.png" % label)
	_check(image != null and image.save_png(path) == OK, "capture written: " + path)


func _inside_screen(control: Control) -> bool:
	return Rect2(0, 0, 640, 360).encloses(control.get_global_rect())


func _settle() -> void:
	for frame in 3:
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
		push_error("Progression ten-node check failed: " + label)
	return condition
