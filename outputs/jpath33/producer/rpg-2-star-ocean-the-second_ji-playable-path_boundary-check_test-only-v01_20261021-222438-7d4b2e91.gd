extends SceneTree
# JPATH33 independent boundary harness (test-only; no normal-input, motion, art or creator-approval claim).
# Checks: Ji default OFF while Zhao/Liang defaults stay on; configure() refusals (locale, appearance, registry, supplement,
# wrong-member and multi-member combat index) mutate nothing; rollback restores the knob; explicit generic and member-pair
# combat overrides keep exact semantics across Zhao/Liang/Ji. DECLARED RENDERING FIXTURE: ji_records_checked + recruit
# calls only place Zhao/Liang/Ji in party slots so the companion combat models can bind; they are not recruitment, dialogue,
# story or save evidence. Malformed inputs are isolated files under user:// and are removed at the end.
const TAG := "20261021-222438-7d4b2e91"
const JI_CONFIG := "res://scripts/jpath33/rpg-2-star-ocean-the-second_ji-playable-path_config_opt-in-v01_20261021-222438-7d4b2e91.gd"
const LIANG_CONFIG := "res://scripts/lpath30/rpg-2-star-ocean-the-second_liang-playable-path_config_opt-in-v01_20261021-202247-ca439d91.gd"
const ZHAO_CONFIG := "res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_config_opt-in-v01_20261021-223218-3246d731.gd"
const FIXTURE_DIR := "user://jpath33-check-" + TAG

var failed := false
var count := 0
var app: Node
var J
var L
var Z
var area
var arena


func ck(ok: bool, label: String) -> void:
	count += 1
	failed = failed or not ok
	print("JPATH33_BOUNDARY ", "PASS " if ok else "FAIL ", label)


func _initialize() -> void:
	call_deferred("run")


func scene(kind: String) -> Node:
	var host: Node = load("res://scenes/" + kind + ".tscn").instantiate()
	root.add_child(host)
	host.set_process(false)
	return host


func snapshot() -> String:
	return JSON.stringify({"j": [J.enabled_override, J.registry_path_override, J.supplement_path_override, J.combat_index_override],
		"l": L.enabled_override, "z": Z.enabled_override, "presenter": area.field_npc_presenter_override,
		"member": arena.companion_combat_member_override, "index": arena.companion_combat_index_override,
		"language": app.language, "appearance": app.hero_appearance, "destination": app.current_destination_id,
		"party": app.active_party_ids, "recruited": app.recruited_members.keys(), "records": app.ji_records_checked})


func write_json(name: String, data: Dictionary) -> String:
	var path := FIXTURE_DIR.path_join(name)
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		return ""
	file.store_string(JSON.stringify(data, "\n"))
	file.close()
	return path


func remove_fixtures() -> void:
	if DirAccess.dir_exists_absolute(FIXTURE_DIR):
		for name in DirAccess.get_files_at(FIXTURE_DIR):
			DirAccess.remove_absolute(FIXTURE_DIR.path_join(name))
		DirAccess.remove_absolute(FIXTURE_DIR)


func battle_members() -> Array:
	var battle := scene("battle_arena")
	var by_member = battle.get("companion_sets_by_member")
	var keys: Array = by_member.keys() if by_member is Dictionary else ["<none>"]
	var ji_slot: int = app.active_party_ids.find("ji-cheng")
	if by_member is Dictionary and by_member.has("ji-cheng"):
		var model = by_member["ji-cheng"]
		ck(model.loaded_count() == 1 and model.has_set(ji_slot) and int(battle.get("companion_slot_by_member")["ji-cheng"]) == ji_slot,
			"Ji model binds exactly the Ji slot %d" % ji_slot)
	battle.free()
	keys.sort()
	return keys


func refused(label: String, language: String, appearance: String) -> void:
	J.clear_cache()
	var before := snapshot()
	var result: Dictionary = J.configure(app, language, appearance)
	ck(not result.get("ok", true) and String(result.get("error", "")) != "", label + " refused: " + String(result.get("error", "")).left(90))
	ck(snapshot() == before, label + " refusal preserved state")


func run() -> void:
	app = root.get_node_or_null("AppState")
	J = load(JI_CONFIG)
	L = load(LIANG_CONFIG)
	Z = load(ZHAO_CONFIG)
	area = load("res://scripts/scifi_exploration_area.gd")
	arena = load("res://scripts/battle_arena.gd")
	DirAccess.make_dir_recursive_absolute(FIXTURE_DIR)
	# Defaults: Ji OFF, Zhao and Liang on; hosts register Ji by member id only.
	ck(not J.DEFAULT_ADOPTED and J.enabled_override == -1 and not J.enabled(), "Ji default OFF without override")
	ck(L.DEFAULT_ADOPTED and L.enabled() and Z.DEFAULT_ADOPTED and Z.enabled(), "Zhao and Liang defaults still on")
	ck(area.FIELD_NPC_PRESENTERS.get("ji-cheng", "") == JI_CONFIG and arena.COMPANION_COMBAT_POLICIES.has(JI_CONFIG)
		and arena.COMPANION_COMBAT_POLICIES[0] == ZHAO_CONFIG and arena.COMPANION_COMBAT_POLICIES[1] == LIANG_CONFIG, "host registrations: Ji appended, Zhao/Liang order kept")
	ck(area.field_npc_presenter_override == "" and arena.companion_combat_member_override == "" and arena.companion_combat_index_override == "", "no host overrides at start")
	ck(J.validate("en", "male").get("ok", false) and J.validate("zh", "female").get("ok", false), "package validates en/male and zh/female")
	# Default-off exploration: the ruins NPC keeps its static texture.
	app.begin_new_run()
	app.select_destination("scifi.ruins")
	var ruins := scene("scifi_exploration_area")
	ck(ruins.get("field_npc") != null and ruins.get("field_npc_driver") == null and not J.npc_attached(ruins), "default OFF: ruins NPC has no jpath33 driver")
	ruins.free()
	# Declared rendering fixture party: hero + Zhao + Liang + Ji.
	app.ji_records_checked = true
	for member in ["zhao-ling", "liang-xu", "ji-cheng"]:
		app.recruit_member(member)
	ck(app.active_party_ids == ["hero", "zhao-ling", "liang-xu", "ji-cheng"], "DECLARED FIXTURE party hero/Zhao/Liang/Ji")
	ck(battle_members() == ["liang-xu", "zhao-ling"], "default OFF battle: Zhao + Liang models only, Ji legacy")
	# Refusals mutate nothing.
	refused("bad language", "fr", "male")
	refused("bad appearance", "en", "robot")
	J.registry_path_override = FIXTURE_DIR.path_join("missing-registry.json")
	refused("missing registry", "en", "male")
	J.registry_path_override = write_json("wrong-actor-registry.json", {"schema": "worlds-between.exploration-sprite-set-registry.v1", "actors": {"liang-xu": "x.json"}})
	refused("registry without ji-cheng", "en", "male")
	J.registry_path_override = ""
	J.supplement_path_override = FIXTURE_DIR.path_join("missing-supplement.json")
	refused("missing supplement", "en", "male")
	J.supplement_path_override = write_json("bad-supplement.json", {"schema": "nope", "actor_id": "ji-cheng"})
	refused("malformed supplement", "en", "male")
	J.supplement_path_override = ""
	J.combat_index_override = L.COMBAT_INDEX_PATH
	refused("Liang-only combat index", "en", "male")
	var ji_index: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(J.COMBAT_INDEX_PATH))
	var two: Dictionary = ji_index.duplicate(true)
	two["sets"]["liang-xu"] = two["sets"]["ji-cheng"]
	J.combat_index_override = write_json("two-member-index.json", two)
	refused("two-member combat index", "en", "male")
	J.combat_index_override = FIXTURE_DIR.path_join("missing-index.json")
	refused("missing combat index", "en", "male")
	J.combat_index_override = ""
	J.clear_cache()
	# Success, then rollback restores exactly the knob.
	var before: int = J.enabled_override
	var ok: Dictionary = J.configure(app, "zh", "female")
	ck(ok.get("ok", false) and J.enabled() and app.current_destination_id == "scifi.ruins" and app.language == "zh"
		and app.active_party_ids == ["hero"] and not app.ji_records_checked, "configure: fresh ruins run, no forced recruit, records unchecked")
	ck(area.field_npc_presenter_override == "" and arena.companion_combat_member_override == "" and arena.companion_combat_index_override == "", "configure sets no host override")
	ruins = scene("scifi_exploration_area")
	ck(J.npc_attached(ruins), "enabled: jpath33 driver on the ruins Ji NPC")
	ruins.free()
	app.ji_records_checked = true
	for member in ["zhao-ling", "liang-xu", "ji-cheng"]:
		app.recruit_member(member)
	ck(battle_members() == ["ji-cheng", "liang-xu", "zhao-ling"], "enabled: Zhao + Liang + Ji member-scoped models")
	# Member pairs: a pair naming one member suppresses the others; a mismatched index loads nothing for that member.
	arena.companion_combat_member_override = "ji-cheng"
	arena.companion_combat_index_override = J.COMBAT_INDEX_PATH
	ck(battle_members() == ["ji-cheng"], "pair (ji-cheng, Ji index) -> Ji only")
	arena.companion_combat_member_override = "liang-xu"
	arena.companion_combat_index_override = L.COMBAT_INDEX_PATH
	ck(battle_members() == ["liang-xu"], "pair (liang-xu, Liang index) -> Liang only")
	arena.companion_combat_member_override = "zhao-ling"
	arena.companion_combat_index_override = Z.COMBAT_INDEX_PATH
	ck(battle_members() == ["zhao-ling"], "pair (zhao-ling, Zhao index) -> Zhao only")
	arena.companion_combat_member_override = "ji-cheng"
	arena.companion_combat_index_override = L.COMBAT_INDEX_PATH
	ck(battle_members() == [], "pair (ji-cheng, Liang index) -> nothing loaded")
	arena.companion_combat_member_override = ""
	arena.companion_combat_index_override = ""
	arena.combat_sprite_set_override = 0
	ck(battle_members() == [], "explicit generic combat override suppresses all companions")
	arena.combat_sprite_set_override = -1
	J.rollback()
	ck(J.enabled_override == before and not J.enabled(), "rollback restores the Ji knob (default OFF)")
	ck(L.enabled() and Z.enabled(), "Zhao/Liang still on after rollback")
	remove_fixtures()
	if failed:
		print("JPATH33_BOUNDARY_FAILED checks=", count)
		quit(1)
	else:
		print("JPATH33_BOUNDARY_PASS checks=", count)
		quit(0)
