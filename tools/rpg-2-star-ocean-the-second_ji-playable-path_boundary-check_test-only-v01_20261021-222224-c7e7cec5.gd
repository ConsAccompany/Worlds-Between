extends SceneTree
# JPATH33 Ji Cheng independent boundary harness (test-only; no normal-input, motion, art, full-gameplay or
# creator-approval claim). Adapted from the Liang LPATH30 120-case harness ca439d91, not a new framework.
# The console -> dialogue -> invite sequence below is exercised through the real ruins UI handler; the party
# additions for Zhao/Liang are a DECLARED rendering fixture for companion-model binding only. All malformed inputs
# are isolated user:// files and are removed at the end. Ji must stay DEFAULT_ADOPTED=false until creator authorization.
const TAG := "20261021-222224-c7e7cec5"
const JI_CONFIG := "res://scripts/jpath33/rpg-2-star-ocean-the-second_ji-playable-path_config_opt-in-v01_20261021-222438-7d4b2e91.gd"
const JI_ENTRY := "res://scripts/jpath33/rpg-2-star-ocean-the-second_ji-playable-path_entry_opt-in-v01_20261021-222438-7d4b2e91.gd"
const LIANG_CONFIG := "res://scripts/lpath30/rpg-2-star-ocean-the-second_liang-playable-path_config_opt-in-v01_20261021-202247-ca439d91.gd"
const ZHAO_CONFIG := "res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_config_opt-in-v01_20261021-223218-3246d731.gd"
const AREA_PATH := "res://scripts/scifi_exploration_area.gd"
const ARENA_PATH := "res://scripts/battle_arena.gd"
const FIXTURE_DIR := "user://jpath33-check-" + TAG
const DIRECTIONS := ["south", "west", "north", "east"]

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


func reset_overrides(cfg) -> void:
	cfg.enabled_override = -1
	cfg.registry_path_override = ""
	cfg.supplement_path_override = ""
	cfg.combat_index_override = ""


func snapshot() -> String:
	return JSON.stringify({
		"j_enabled": J.enabled_override,
		"j_registry": J.registry_path_override,
		"j_supplement": J.supplement_path_override,
		"j_index": J.combat_index_override,
		"l_enabled": L.enabled_override,
		"z_enabled": Z.enabled_override,
		"presenter": area.field_npc_presenter_override,
		"member": arena.companion_combat_member_override,
		"index": arena.companion_combat_index_override,
		"language": app.language,
		"appearance": app.hero_appearance,
		"destination": app.current_destination_id,
		"party": app.active_party_ids,
		"recruited": app.recruited_members.keys(),
		"records": app.ji_records_checked,
	})


func driver_of(host: Node) -> Node:
	if host != null and "field_npc_driver" in host:
		var driver = host.get("field_npc_driver")
		if driver != null and is_instance_valid(driver):
			return driver
	return null


func npc_of(host: Node) -> Sprite2D:
	if host == null:
		return null
	if "city_npc" in host and host.get("city_npc") != null:
		return host.get("city_npc")
	if "field_npc" in host and host.get("field_npc") != null:
		return host.get("field_npc")
	return null


func press_interact(host: Node) -> void:
	var event := InputEventAction.new()
	event.action = "interact"
	event.pressed = true
	host._unhandled_input(event)


func ensure_fixture_roster() -> void:
	if not app.recruited_members.has("zhao-ling"):
		app.recruit_member("zhao-ling")
	if not app.recruited_members.has("liang-xu"):
		app.recruit_member("liang-xu")


func read_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
	return parsed if parsed is Dictionary else {}


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


# Called only while a malformed Ji override is active: Ji must be absent whole; Zhao/Liang defaults and hero stay.
func assert_rejected_preserves_others(label: String) -> void:
	ensure_fixture_roster()
	var battle := scene("battle_arena")
	var by_member = battle.get("companion_sets_by_member")
	var slots = battle.get("companion_slot_by_member")
	var zhao_slot: int = app.active_party_ids.find("zhao-ling")
	var liang_slot: int = app.active_party_ids.find("liang-xu")
	var zhao_model = by_member.get("zhao-ling") if by_member is Dictionary else null
	var liang_model = by_member.get("liang-xu") if by_member is Dictionary else null
	ck(by_member is Dictionary and by_member.has("zhao-ling") and by_member.has("liang-xu")
		and not by_member.has("ji-cheng"), label + ": battle keeps Zhao/Liang, rejects whole Ji")
	ck(slots is Dictionary and int(slots.get("zhao-ling", -1)) == zhao_slot
		and int(slots.get("liang-xu", -1)) == liang_slot, label + ": Zhao/Liang slot map kept")
	ck(zhao_model != null and zhao_model.loaded_count() == 1 and zhao_model.has_set(zhao_slot)
		and liang_model != null and liang_model.loaded_count() == 1 and liang_model.has_set(liang_slot),
		label + ": Zhao/Liang models kept")
	ck(battle.get("companion_sprite_sets") == zhao_model and int(battle.get("companion_index")) == zhao_slot,
		label + ": legacy alias still Zhao")
	var hero_model = battle.get("combat_sprite_sets")
	ck(hero_model != null and hero_model.has_set(0) and hero_model.loaded_count() == 1,
		label + ": hero combat model kept")
	battle.free()
	app.select_destination("scifi.city")
	var city := scene("scifi_exploration_area")
	ck(not J.npc_attached(city) and L.npc_attached(city), label + ": Ji hook rejected whole; Liang city hook kept")
	city.free()
	app.select_destination("scifi.outskirts")
	var outskirts := scene("scifi_exploration_area")
	ck(Z.npc_attached(outskirts), label + ": Zhao field NPC kept")
	outskirts.free()
	app.select_destination("scifi.ruins")
	var ruins := scene("scifi_exploration_area")
	ck(not J.npc_attached(ruins), label + ": Ji ruins hook rejected whole")
	ruins.free()


func settle_idle(driver: Node) -> Dictionary:
	driver.walk()
	driver.advance(0.02)
	driver.idle()
	driver.advance(0.20)
	driver.idle()
	return driver.state()


func finish() -> void:
	if failed:
		print("JPATH33_BOUNDARY_FAILED checks=", count)
		quit(1)
	else:
		print("JPATH33_BOUNDARY_PASS checks=", count)
		quit(0)


func run() -> void:
	app = root.get_node_or_null("AppState")
	if app == null:
		ck(false, "AppState autoload present")
		finish()
		return
	ck(ResourceLoader.exists(JI_CONFIG), "Ji config exists")
	ck(ResourceLoader.exists(LIANG_CONFIG), "Liang config exists")
	ck(ResourceLoader.exists(ZHAO_CONFIG), "Zhao config exists")
	ck(ResourceLoader.exists(JI_ENTRY), "Ji preview entry exists")
	if not ResourceLoader.exists(JI_CONFIG) or not ResourceLoader.exists(LIANG_CONFIG) or not ResourceLoader.exists(ZHAO_CONFIG):
		finish()
		return
	J = load(JI_CONFIG)
	L = load(LIANG_CONFIG)
	Z = load(ZHAO_CONFIG)
	area = load(AREA_PATH)
	arena = load(ARENA_PATH)
	reset_overrides(J)
	reset_overrides(L)
	reset_overrides(Z)
	J.clear_cache()

	# Defaults: Ji stays off until separate creator authorization; Zhao/Liang authorized defaults stay on, art unapproved.
	ck(J.DEFAULT_ADOPTED == false and not J.ART_APPROVED, "Ji default false, art unapproved (no creator authorization)")
	ck(J.enabled_override == -1 and J.enabled() == false, "Ji no-override enable is false")
	ck(String(J.MEMBER_ID) == "ji-cheng" and String(J.DESTINATION) == "scifi.ruins",
		"Ji member/destination are ji-cheng/scifi.ruins")
	ck(Z.DEFAULT_ADOPTED and not Z.ART_APPROVED and Z.enabled_override == -1 and Z.enabled(),
		"Zhao authorized default on and art-unapproved, unchanged")
	ck(L.DEFAULT_ADOPTED and not L.ART_APPROVED and L.enabled_override == -1 and L.enabled(),
		"Liang authorized default on and art-unapproved, unchanged")
	ck(load(JI_ENTRY) != null, "Ji preview entry parses/loads")

	# Current female/male/default regressions before any Ji configure: normal app start initializes hero_state, then the
	# battle host must still give the hero model slot 0. (Direct battle instantiation before a run is not a normal path.)
	app.begin_new_run()
	for appearance in ["female", "male"]:
		app.hero_appearance = String(appearance)
		var hero_battle := scene("battle_arena")
		var hero_model = hero_battle.get("combat_sprite_sets")
		ck(hero_model != null and hero_model.has_set(0) and hero_model.loaded_count() == 1,
			"hero " + String(appearance) + " default combat model keeps slot 0")
		hero_battle.free()
	app.hero_appearance = "female"

	# Valid package: both declared appearances/languages validate read-only; index is exactly ji-cheng.
	ck(J.validate("en", "male").get("ok", false), "valid en/male package accepted")
	ck(J.validate("zh", "female").get("ok", false), "valid zh/female package accepted")
	var index_data := read_json(J.combat_index_path())
	ck(String(J.registry_path()).contains("jexplore31") and String(J.supplement_path()).contains("jexplore31"),
		"frozen jexplore31 exploration paths used")
	ck(String(J.combat_index_path()).contains("jcombat32") and index_data.get("sets", {}) is Dictionary
		and index_data.get("sets", {}).size() == 1 and index_data.get("sets", {}).has("ji-cheng"),
		"jcombat32 index is member-only ji-cheng")

	# Valid opt-in configure. It may enable only its own knob and select the preview destination.
	var valid: Dictionary = J.configure(app, "en", "male")
	ck(valid.get("ok", false), "valid configure accepts whole package")
	ck(J.enabled_override == 1 and J.enabled(), "valid configure enables Ji own knob")
	ck(app.hero_appearance == "male" and app.language == "en" and app.current_destination_id == "scifi.ruins",
		"valid configure selects male/en/scifi.ruins")
	ck(area.field_npc_presenter_override == "" and arena.companion_combat_member_override == ""
		and arena.companion_combat_index_override == "",
		"valid configure never hijacks global host overrides")

	# Actual ruins host scene: the existing recruit NPC gets the driver; coordinates/party stay unchanged.
	app.select_destination("scifi.ruins")
	var ruins := scene("scifi_exploration_area")
	ck(J.npc_attached(ruins), "valid ruins NPC attaches")
	var npc := npc_of(ruins)
	var driver := driver_of(ruins)
	var ruins_pos: Vector2 = area.AREA_CONFIG["scifi.ruins"]["npc"]
	ck(npc != null and npc == ruins.get("field_npc") and npc.position == ruins_pos,
		"ruins recruit NPC is field_npc at declared coordinates")
	ck(npc != null and driver != null and driver.get_parent() == npc and npc.get_parent() == ruins,
		"driver binds the existing ruins NPC, not a follower")
	ck(app.active_party_ids.size() == 1 and app.active_party_ids[0] == "hero"
		and not app.recruited_members.has("ji-cheng"), "configure leaves hero-only party; no forced Ji recruit/follower")

	# Driver public APIs only: declared idle/walk banks and phase-aware stop cancellation. Not ordinary NPC walking.
	if driver != null and npc != null:
		var paths := {}
		for direction in DIRECTIONS:
			settle_idle(driver)
			driver.face(direction)
			var idle_state: Dictionary = driver.state()
			ck(String(idle_state.get("action", "")) == "idle" and String(idle_state.get("facing", "")) == direction
				and int(idle_state.get("frame", -1)) >= 0 and String(idle_state.get("path", "")).contains("jexplore31"),
				"declared Ji idle bank " + direction)
			driver.walk()
			driver.advance(0.09)
			var walk_state: Dictionary = driver.state()
			ck(String(walk_state.get("action", "")) == "walk" and String(walk_state.get("facing", "")) == direction
				and int(walk_state.get("frame", -1)) >= 0 and String(walk_state.get("path", "")).contains("jexplore31"),
				"declared Ji walk bank " + direction)
			paths[String(walk_state.get("path", ""))] = true
		ck(paths.size() == DIRECTIONS.size(), "four Ji directions expose distinct walk paths")
		driver.face("south")
		driver.walk()
		driver.advance(0.09)
		driver.idle()
		var stop_state: Dictionary = driver.state()
		ck(String(stop_state.get("action", "")) == "stop" and int(stop_state.get("phase", -1)) >= 0,
			"Ji phase-aware stop bridge entered from walk")
		driver.face("north")
		ck(String(driver.state().get("action", "")) == "idle", "Ji facing change cancels stop bridge")
		driver.face("south")
		driver.walk()
		driver.advance(0.09)
		driver.idle()
		driver.walk()
		ck(String(driver.state().get("action", "")) == "walk", "Ji walk cancels stop bridge")
		driver.idle()
		driver.advance(0.20)
		driver.idle()
		ck(String(driver.state().get("action", "")) == "idle", "Ji stop bridge settles back to idle")
		ck(npc.position == ruins_pos, "Ji driver calls never move the ruins NPC")
		ck(app.active_party_ids.size() == 1 and app.active_party_ids[0] == "hero",
			"Ji driver calls never add a follower")

	# Actor prerequisite: actual records-console interaction must unlock the real dialogue invite; no bypass.
	ck(not app.ji_records_checked, "fresh run starts with Ji records unchecked")
	var before_guard: int = app.active_party_ids.size()
	ck(not app.recruit_member("ji-cheng") and app.active_party_ids.size() == before_guard
		and not app.recruited_members.has("ji-cheng"), "direct Ji recruit refused before records console")
	ruins.hero.position = ruins.npc_position
	press_interact(ruins)
	ck(ruins.dialogue_open and ruins.invite_button.disabled and not app.recruited_members.has("ji-cheng"),
		"Ji invite disabled and locked dialogue before records console")
	ck(String(ruins.dialogue_text.text) == String(app.text_for("recruit_ji_locked")),
		"locked Ji dialogue uses existing recruit_ji_locked text")
	ruins._close_dialogue()
	ruins.hero.position = area.RECORDS_POSITION
	press_interact(ruins)
	ck(app.ji_records_checked, "records console interaction sets ji_records_checked")
	ruins.hero.position = ruins.npc_position
	press_interact(ruins)
	ck(ruins.dialogue_open and not ruins.invite_button.disabled, "Ji invite enabled after records console")
	ck(String(ruins.dialogue_text.text) == String(app.text_for("recruit_ji")),
		"unlocked Ji dialogue uses existing recruit_ji text")
	ruins._dialogue_primary()
	ck(app.recruited_members.has("ji-cheng") and app.active_party_ids.has("ji-cheng")
		and not ruins.dialogue_open, "actual invite handler recruits Ji through normal dialogue")
	ck(J.npc_attached(ruins) and npc.position == ruins_pos, "Ji field driver stays installed after invite")
	ruins.free()

	# Zhao/Liang own default field paths remain intact.
	app.select_destination("scifi.city")
	var city := scene("scifi_exploration_area")
	ck(L.npc_attached(city), "Liang default city field NPC still attaches")
	var city_npc := npc_of(city)
	ck(city_npc != null and city_npc.position == Vector2(area.AREA_CONFIG["scifi.city"]["npc"]),
		"Liang city field coordinates unchanged")
	city.free()
	app.select_destination("scifi.outskirts")
	var outskirts := scene("scifi_exploration_area")
	ck(Z.npc_attached(outskirts), "Zhao default field NPC still attaches")
	var zhao_npc := npc_of(outskirts)
	ck(zhao_npc != null and zhao_npc.position == Vector2(area.AREA_CONFIG["scifi.outskirts"]["npc"]),
		"Zhao field coordinates unchanged")
	outskirts.free()

	# DECLARED rendering fixture: add Zhao/Liang slots; Ji was recruited through the real dialogue above.
	ensure_fixture_roster()
	app.select_destination("scifi.ruins")
	ck(app.active_party_ids.size() == 4 and app.active_party_ids.has("zhao-ling")
		and app.active_party_ids.has("liang-xu") and app.active_party_ids.has("ji-cheng"),
		"fixture party holds hero/Zhao/Liang/Ji")
	var zhao_slot: int = app.active_party_ids.find("zhao-ling")
	var liang_slot: int = app.active_party_ids.find("liang-xu")
	var ji_slot: int = app.active_party_ids.find("ji-cheng")
	var battle := scene("battle_arena")
	var by_member = battle.get("companion_sets_by_member")
	var slots = battle.get("companion_slot_by_member")
	var zhao_model = by_member.get("zhao-ling") if by_member is Dictionary else null
	var liang_model = by_member.get("liang-xu") if by_member is Dictionary else null
	var ji_model = by_member.get("ji-cheng") if by_member is Dictionary else null
	ck(by_member is Dictionary and by_member.has("zhao-ling") and by_member.has("liang-xu")
		and by_member.has("ji-cheng"), "three companions coexist via companion_sets_by_member")
	ck(slots is Dictionary and int(slots.get("zhao-ling", -1)) == zhao_slot
		and int(slots.get("liang-xu", -1)) == liang_slot and int(slots.get("ji-cheng", -1)) == ji_slot,
		"three companion slots via companion_slot_by_member")
	ck(zhao_model != null and zhao_model.loaded_count() == 1 and zhao_model.has_set(zhao_slot)
		and not zhao_model.has_set(liang_slot) and not zhao_model.has_set(ji_slot), "Zhao model loads only Zhao slot")
	ck(liang_model != null and liang_model.loaded_count() == 1 and liang_model.has_set(liang_slot)
		and not liang_model.has_set(zhao_slot) and not liang_model.has_set(ji_slot), "Liang model loads only Liang slot")
	ck(ji_model != null and ji_model.loaded_count() == 1 and ji_model.has_set(ji_slot)
		and not ji_model.has_set(zhao_slot) and not ji_model.has_set(liang_slot), "Ji model loads only Ji slot")
	ck(battle.get("companion_sprite_sets") == zhao_model and int(battle.get("companion_index")) == zhao_slot,
		"old companion_sprite_sets/companion_index alias stays Zhao")
	var hero_model = battle.get("combat_sprite_sets")
	ck(hero_model != null and hero_model.has_set(0) and hero_model.loaded_count() == 1,
		"hero combat model unchanged with three companions")
	ck(not zhao_model.has_set(0) and not liang_model.has_set(0) and not ji_model.has_set(0),
		"companion models never own hero slot")
	battle.free()

	# Own disable removes Ji only; Zhao/Liang still bind both field and combat paths.
	J.enabled_override = 0
	J.clear_cache()
	battle = scene("battle_arena")
	by_member = battle.get("companion_sets_by_member")
	ck(by_member is Dictionary and by_member.has("zhao-ling") and by_member.has("liang-xu")
		and not by_member.has("ji-cheng"), "own disable removes Ji only from combat")
	ck(battle.get("companion_sprite_sets") == by_member.get("zhao-ling"),
		"own disable keeps Zhao alias")
	ck(battle.get("combat_sprite_sets") != null and battle.get("combat_sprite_sets").has_set(0),
		"own disable keeps hero model")
	battle.free()
	app.select_destination("scifi.ruins")
	ruins = scene("scifi_exploration_area")
	ck(not J.npc_attached(ruins), "own disable refuses existing Ji ruins NPC hook")
	ruins.free()
	app.select_destination("scifi.city")
	city = scene("scifi_exploration_area")
	ck(L.npc_attached(city), "own Ji disable keeps Liang city field NPC")
	city.free()
	app.select_destination("scifi.outskirts")
	outskirts = scene("scifi_exploration_area")
	ck(Z.npc_attached(outskirts), "own Ji disable keeps Zhao field NPC")
	outskirts.free()
	J.enabled_override = 1

	# Alias fallback: with Zhao disabled, the alias becomes the first loaded model (Liang), not a fake Zhao.
	Z.enabled_override = 0
	J.clear_cache()
	battle = scene("battle_arena")
	by_member = battle.get("companion_sets_by_member")
	var only_liang = by_member.get("liang-xu") if by_member is Dictionary else null
	ck(by_member is Dictionary and by_member.has("liang-xu") and by_member.has("ji-cheng")
		and not by_member.has("zhao-ling"), "Zhao disable loads Liang and Ji")
	ck(battle.get("companion_sprite_sets") == only_liang and int(battle.get("companion_index")) == liang_slot,
		"alias falls back to the first loaded model (Liang), not fake Zhao")
	battle.free()
	Z.enabled_override = -1

	# Invalid language/appearance: configure must refuse atomically, leaving every knob and app field untouched.
	var before_bad := snapshot()
	var bad_language: Dictionary = J.configure(app, "fr", "male")
	ck(not bad_language.get("ok", true) and snapshot() == before_bad,
		"invalid language configure refuses atomically without state changes")
	before_bad = snapshot()
	var bad_appearance: Dictionary = J.configure(app, "en", "other")
	ck(not bad_appearance.get("ok", true) and snapshot() == before_bad,
		"invalid appearance configure refuses atomically without state changes")

	# Isolated malformed fixtures. Only user:// files; source production files are never written or deleted.
	DirAccess.make_dir_recursive_absolute(FIXTURE_DIR)
	var valid_registry: String = J.registry_path()
	var valid_supplement: String = J.supplement_path()
	var valid_index: String = J.combat_index_path()
	var registry_data := read_json(valid_registry)
	var index_data2 := read_json(valid_index)
	var supplement_data := read_json(valid_supplement)
	var zhao_registry := read_json(Z.registry_path())
	var zhao_index := read_json(Z.combat_index_path())
	var zhao_set: String = Z.registry_path().get_base_dir().path_join(String(zhao_registry.get("actors", {}).get("zhao-ling", "")))
	var zhao_combat: String = Z.combat_index_path().get_base_dir().path_join(String(zhao_index.get("sets", {}).get("zhao-ling", "")))
	var ji_set: String = valid_index.get_base_dir().path_join(String(index_data2.get("sets", {}).get("ji-cheng", "")))
	var registry_wrong := write_json("registry-wrong-member-" + TAG + ".json",
		{"schema": String(registry_data.get("schema", "")), "actors": {"zhao-ling": zhao_set}})
	var supplement_wrong := write_json("supplement-wrong-actor-" + TAG + ".json",
		{"schema": String(supplement_data.get("schema", "")), "actor_id": "zhao-ling"})
	var index_wrong := write_json("index-wrong-member-" + TAG + ".json",
		{"schema": String(index_data2.get("schema", "")), "sets": {"zhao-ling": zhao_combat}})
	var index_extra := write_json("index-extra-member-" + TAG + ".json",
		{"schema": String(index_data2.get("schema", "")), "sets": {"ji-cheng": ji_set, "zhao-ling": zhao_combat}})
	var cases: Array = [
		{"label": "missing registry", "registry": FIXTURE_DIR.path_join("missing-registry-" + TAG + ".json"),
			"supplement": valid_supplement, "index": valid_index},
		{"label": "wrong-member registry", "registry": registry_wrong,
			"supplement": valid_supplement, "index": valid_index},
		{"label": "missing supplement", "registry": valid_registry,
			"supplement": FIXTURE_DIR.path_join("missing-supplement-" + TAG + ".json"), "index": valid_index},
		{"label": "wrong-actor supplement", "registry": valid_registry,
			"supplement": supplement_wrong, "index": valid_index},
		{"label": "missing combat index", "registry": valid_registry, "supplement": valid_supplement,
			"index": FIXTURE_DIR.path_join("missing-index-" + TAG + ".json")},
		{"label": "wrong-member combat index", "registry": valid_registry, "supplement": valid_supplement,
			"index": index_wrong},
		{"label": "surplus-member combat index", "registry": valid_registry, "supplement": valid_supplement,
			"index": index_extra},
	]
	for item in cases:
		J.registry_path_override = String(item["registry"])
		J.supplement_path_override = String(item["supplement"])
		J.combat_index_override = String(item["index"])
		J.clear_cache()
		var before_case := snapshot()
		var rejected: Dictionary = J.validate("en", "male")
		ck(not rejected.get("ok", true), String(item["label"]) + " rejected by validate")
		var refused: Dictionary = J.configure(app, "en", "male")
		ck(not refused.get("ok", true) and snapshot() == before_case,
			String(item["label"]) + " configure refuses atomically")
		assert_rejected_preserves_others(String(item["label"]))

	J.registry_path_override = ""
	J.supplement_path_override = ""
	J.combat_index_override = ""
	J.clear_cache()

	# Explicit generic combat choice wins over all companion models.
	arena.combat_sprite_set_override = 0
	battle = scene("battle_arena")
	by_member = battle.get("companion_sets_by_member")
	ck(by_member is Dictionary and by_member.is_empty(), "explicit generic combat override suppresses companions")
	ck(battle.get("companion_sprite_sets") == null and int(battle.get("companion_index")) == -1,
		"explicit generic override clears companion aliases")
	battle.free()
	arena.combat_sprite_set_override = -1

	# Rollback restores only this config's knob; Zhao/Liang controls/defaults remain exactly as before.
	J.rollback()
	ck(J.enabled_override == -1 and J.enabled() == false, "rollback restores Ji unauthorized default off")
	ck(area.field_npc_presenter_override == "" and arena.companion_combat_member_override == ""
		and arena.companion_combat_index_override == "" and L.enabled_override == -1 and L.enabled()
		and Z.enabled_override == -1 and Z.enabled(),
		"rollback leaves Zhao/Liang controls/defaults untouched")
	battle = scene("battle_arena")
	by_member = battle.get("companion_sets_by_member")
	ck(by_member is Dictionary and by_member.has("zhao-ling") and by_member.has("liang-xu")
		and not by_member.has("ji-cheng"), "post-rollback companions are Zhao/Liang only, Ji off")
	ck(battle.get("companion_sprite_sets") == by_member.get("zhao-ling"),
		"post-rollback alias is Zhao")
	battle.free()
	app.select_destination("scifi.ruins")
	ruins = scene("scifi_exploration_area")
	ck(not J.npc_attached(ruins), "post-rollback Ji ruins NPC is off")
	ruins.free()
	app.select_destination("scifi.city")
	city = scene("scifi_exploration_area")
	ck(L.npc_attached(city), "post-rollback Liang city NPC is on")
	city.free()
	app.select_destination("scifi.outskirts")
	outskirts = scene("scifi_exploration_area")
	ck(Z.npc_attached(outskirts), "post-rollback Zhao field NPC is on")
	outskirts.free()

	reset_overrides(J)
	reset_overrides(L)
	reset_overrides(Z)
	J.clear_cache()
	remove_fixtures()
	finish()
