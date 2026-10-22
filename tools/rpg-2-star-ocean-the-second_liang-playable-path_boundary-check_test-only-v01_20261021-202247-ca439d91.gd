extends SceneTree
# LPATH30 independent boundary harness (test-only; no normal-input, motion, art or creator-approval claim).
# Liang is opt-in and NOT default-adopted. Recruit calls below are a DECLARED rendering fixture that only places
# Zhao/Liang in party slots so the separately validated companion combat models can bind; they are not recruitment,
# dialogue, story or save evidence. All malformed inputs are isolated files under user:// and are removed at the end.
const TAG := "20261021-202247-ca439d91"
const LIANG_CONFIG := "res://scripts/lpath30/rpg-2-star-ocean-the-second_liang-playable-path_config_opt-in-v01_20261021-202247-ca439d91.gd"
const LIANG_ENTRY := "res://scripts/lpath30/rpg-2-star-ocean-the-second_liang-playable-path_entry_opt-in-v01_20261021-202247-ca439d91.gd"
const ZHAO_CONFIG := "res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_config_opt-in-v01_20261021-223218-3246d731.gd"
const AREA_PATH := "res://scripts/scifi_exploration_area.gd"
const ARENA_PATH := "res://scripts/battle_arena.gd"
const FIXTURE_DIR := "user://lpath30-check-" + TAG
const DIRECTIONS := ["south", "west", "north", "east"]

var failed := false
var count := 0
var app: Node
var L
var Z
var area
var arena


func ck(ok: bool, label: String) -> void:
	count += 1
	failed = failed or not ok
	print("LPATH30_BOUNDARY ", "PASS " if ok else "FAIL ", label)


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
		"l_enabled": L.enabled_override,
		"l_registry": L.registry_path_override,
		"l_supplement": L.supplement_path_override,
		"l_index": L.combat_index_override,
		"z_enabled": Z.enabled_override,
		"presenter": area.field_npc_presenter_override,
		"member": arena.companion_combat_member_override,
		"index": arena.companion_combat_index_override,
		"language": app.language,
		"appearance": app.hero_appearance,
		"destination": app.current_destination_id,
		"party": app.active_party_ids,
		"recruited": app.recruited_members.keys(),
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


func ensure_fixture_party() -> void:
	if not app.recruited_members.has("zhao-ling"):
		app.recruit_member("zhao-ling")
	if not app.recruited_members.has("liang-xu"):
		app.recruit_member("liang-xu")


# Called only while the malformed Liang override is active: Liang must be absent whole, Zhao and hero must remain.
func assert_rejected_preserves_zhao(label: String) -> void:
	ensure_fixture_party()
	var battle := scene("battle_arena")
	var by_member = battle.get("companion_sets_by_member")
	var slots = battle.get("companion_slot_by_member")
	var zhao_model = by_member.get("zhao-ling") if by_member is Dictionary else null
	var zhao_slot: int = app.active_party_ids.find("zhao-ling")
	ck(by_member is Dictionary and by_member.has("zhao-ling") and not by_member.has("liang-xu"),
		label + ": battle keeps Zhao, rejects whole Liang")
	ck(slots is Dictionary and int(slots.get("zhao-ling", -1)) == zhao_slot,
		label + ": Zhao slot map kept")
	ck(zhao_model != null and zhao_model.loaded_count() == 1 and zhao_model.has_set(zhao_slot),
		label + ": Zhao model kept")
	ck(battle.get("companion_sprite_sets") == zhao_model and int(battle.get("companion_index")) == zhao_slot,
		label + ": legacy alias still Zhao")
	var hero_model = battle.get("combat_sprite_sets")
	ck(hero_model != null and hero_model.has_set(0) and hero_model.loaded_count() == 1,
		label + ": hero combat model kept")
	battle.free()
	app.select_destination("scifi.city")
	var city := scene("scifi_exploration_area")
	ck(not L.npc_attached(city), label + ": city hook refuses whole Liang")
	city.free()
	app.select_destination("scifi.outskirts")
	var outskirts := scene("scifi_exploration_area")
	ck(Z.npc_attached(outskirts), label + ": Zhao field NPC kept")
	outskirts.free()


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


func settle_idle(driver: Node) -> Dictionary:
	driver.walk()
	driver.advance(0.02)
	driver.idle()
	driver.advance(0.20)
	driver.idle()
	return driver.state()


func finish() -> void:
	if failed:
		print("LPATH30_BOUNDARY_FAILED checks=", count)
		quit(1)
	else:
		print("LPATH30_BOUNDARY_PASS checks=", count)
		quit(0)


func run() -> void:
	app = root.get_node_or_null("AppState")
	if app == null:
		ck(false, "AppState autoload present")
		finish()
		return
	ck(ResourceLoader.exists(LIANG_CONFIG), "Liang config exists")
	ck(ResourceLoader.exists(ZHAO_CONFIG), "Zhao config exists")
	ck(ResourceLoader.exists(LIANG_ENTRY), "Liang preview entry exists")
	if not ResourceLoader.exists(LIANG_CONFIG) or not ResourceLoader.exists(ZHAO_CONFIG):
		finish()
		return
	L = load(LIANG_CONFIG)
	Z = load(ZHAO_CONFIG)
	area = load(AREA_PATH)
	arena = load(ARENA_PATH)
	reset_overrides(L)
	reset_overrides(Z)
	L.clear_cache()

	# Defaults: Liang off, Zhao on, both art-unapproved, no override adopted.
	ck(not L.DEFAULT_ADOPTED and not L.ART_APPROVED, "Liang DEFAULT_ADOPTED/ART_APPROVED are false")
	ck(L.enabled_override == -1 and not L.enabled(), "Liang default off with no override")
	ck(String(L.MEMBER_ID) == "liang-xu" and String(L.DESTINATION) == "scifi.city",
		"Liang member/destination are liang-xu/scifi.city")
	ck(Z.DEFAULT_ADOPTED and not Z.ART_APPROVED and Z.enabled_override == -1 and Z.enabled(),
		"Zhao authorized default on and art-unapproved, unchanged")
	ck(load(LIANG_ENTRY) != null, "Liang preview entry parses/loads")

	# Valid opt-in configure. It may enable only its own knob and select the preview destination.
	var valid: Dictionary = L.configure(app, "en", "male")
	ck(valid.get("ok", false), "valid configure accepts whole package")
	ck(L.enabled_override == 1 and L.enabled(), "valid configure enables Liang own knob")
	ck(String(L.registry_path()).contains("lexplore28") and String(L.supplement_path()).contains("lexplore28")
		and String(L.combat_index_path()).contains("lcombat29"), "frozen lexplore28/lcombat29 paths used")
	ck(area.field_npc_presenter_override == "" and arena.companion_combat_member_override == ""
		and arena.companion_combat_index_override == "",
		"valid configure never hijacks Zhao/global host overrides")

	# Actual scifi.city host scene: the recruit NPC gets the driver; coordinates and party stay unchanged.
	app.select_destination("scifi.city")
	var city := scene("scifi_exploration_area")
	ck(L.npc_attached(city), "valid city NPC attaches")
	var npc := npc_of(city)
	var driver := driver_of(city)
	var city_pos: Vector2 = area.AREA_CONFIG["scifi.city"]["npc"]
	ck(npc != null and npc.position == city_pos, "city recruit NPC keeps field coordinates")
	ck(npc != null and driver != null and driver.get_parent() == npc and npc.get_parent() == city,
		"driver binds the existing NPC, not a follower")
	ck(app.active_party_ids.size() == 1 and app.active_party_ids[0] == "hero"
		and not app.recruited_members.has("liang-xu"), "configure leaves hero-only party; no forced recruit/follower")

	# Driver public APIs only: declared idle/walk banks and phase-aware stop cancellation. Not ordinary NPC walking.
	if driver != null and npc != null:
		var paths := {}
		for direction in DIRECTIONS:
			settle_idle(driver)
			driver.face(direction)
			var idle_state: Dictionary = driver.state()
			ck(String(idle_state.get("action", "")) == "idle" and String(idle_state.get("facing", "")) == direction
				and int(idle_state.get("frame", -1)) >= 0 and String(idle_state.get("path", "")).contains("lexplore28"),
				"declared idle bank " + direction)
			driver.walk()
			driver.advance(0.09)
			var walk_state: Dictionary = driver.state()
			ck(String(walk_state.get("action", "")) == "walk" and String(walk_state.get("facing", "")) == direction
				and int(walk_state.get("frame", -1)) >= 0 and String(walk_state.get("path", "")).contains("lexplore28"),
				"declared walk bank " + direction)
			paths[String(walk_state.get("path", ""))] = true
		ck(paths.size() == DIRECTIONS.size(), "four directions expose distinct walk paths")

		driver.face("south")
		driver.walk()
		driver.advance(0.09)
		driver.idle()
		var stop_state: Dictionary = driver.state()
		ck(String(stop_state.get("action", "")) == "stop" and int(stop_state.get("phase", -1)) >= 0,
			"phase-aware stop bridge entered from walk")
		driver.face("north")
		ck(String(driver.state().get("action", "")) == "idle", "facing change cancels stop bridge")
		driver.face("south")
		driver.walk()
		driver.advance(0.09)
		driver.idle()
		driver.walk()
		ck(String(driver.state().get("action", "")) == "walk", "walk cancels stop bridge")
		driver.idle()
		driver.advance(0.20)
		driver.idle()
		ck(String(driver.state().get("action", "")) == "idle", "stop bridge settles back to idle")
		ck(npc.position == city_pos, "driver calls never move the field NPC")
		ck(app.active_party_ids.size() == 1 and app.active_party_ids[0] == "hero",
			"driver calls never add a follower")
	city.free()

	# Zhao's own default field path remains intact.
	app.select_destination("scifi.outskirts")
	var outskirts := scene("scifi_exploration_area")
	ck(Z.npc_attached(outskirts), "Zhao default field NPC still attaches")
	var zhao_npc := npc_of(outskirts)
	ck(zhao_npc != null and zhao_npc.position == Vector2(area.AREA_CONFIG["scifi.outskirts"]["npc"]),
		"Zhao field coordinates unchanged")
	outskirts.free()

	# DECLARED rendering fixture: party slots only; not recruitment evidence.
	ensure_fixture_party()
	ck(app.active_party_ids.size() == 3 and app.active_party_ids.has("zhao-ling")
		and app.active_party_ids.has("liang-xu"), "declared fixture party holds hero/Zhao/Liang")
	var zhao_slot: int = app.active_party_ids.find("zhao-ling")
	var liang_slot: int = app.active_party_ids.find("liang-xu")
	var battle := scene("battle_arena")
	var by_member = battle.get("companion_sets_by_member")
	var slots = battle.get("companion_slot_by_member")
	var zhao_model = by_member.get("zhao-ling") if by_member is Dictionary else null
	var liang_model = by_member.get("liang-xu") if by_member is Dictionary else null
	ck(by_member is Dictionary and by_member.has("zhao-ling") and by_member.has("liang-xu"),
		"coexistence loads both models via companion_sets_by_member")
	ck(slots is Dictionary and int(slots.get("zhao-ling", -1)) == zhao_slot
		and int(slots.get("liang-xu", -1)) == liang_slot, "coexistence slots via companion_slot_by_member")
	ck(zhao_model != null and zhao_model.loaded_count() == 1 and zhao_model.has_set(zhao_slot)
		and not zhao_model.has_set(liang_slot), "Zhao model loads only Zhao slot")
	ck(liang_model != null and liang_model.loaded_count() == 1 and liang_model.has_set(liang_slot)
		and not liang_model.has_set(zhao_slot), "Liang model loads only Liang slot")
	ck(battle.get("companion_sprite_sets") == zhao_model and int(battle.get("companion_index")) == zhao_slot,
		"old companion_sprite_sets/companion_index alias stays Zhao")
	var hero_model = battle.get("combat_sprite_sets")
	ck(hero_model != null and hero_model.has_set(0) and hero_model.loaded_count() == 1,
		"hero combat model unchanged")
	ck(not zhao_model.has_set(0) and not liang_model.has_set(0), "companion models never own hero slot")
	battle.free()

	# Own disable removes Liang only; Zhao still binds both field and combat paths.
	L.enabled_override = 0
	L.clear_cache()
	battle = scene("battle_arena")
	by_member = battle.get("companion_sets_by_member")
	ck(by_member is Dictionary and by_member.has("zhao-ling") and not by_member.has("liang-xu"),
		"own disable removes Liang only from combat")
	ck(battle.get("companion_sprite_sets") == by_member.get("zhao-ling"),
		"own disable keeps Zhao alias")
	ck(battle.get("combat_sprite_sets") != null and battle.get("combat_sprite_sets").has_set(0),
		"own disable keeps hero model")
	battle.free()
	app.select_destination("scifi.city")
	city = scene("scifi_exploration_area")
	ck(not L.npc_attached(city), "own disable refuses existing city NPC hook")
	city.free()
	app.select_destination("scifi.outskirts")
	outskirts = scene("scifi_exploration_area")
	ck(Z.npc_attached(outskirts), "own disable keeps Zhao field NPC")
	outskirts.free()
	L.enabled_override = 1

	# Alias fallback: with Zhao disabled, the alias becomes the first loaded model (Liang), not a fake Zhao.
	Z.enabled_override = 0
	L.clear_cache()
	battle = scene("battle_arena")
	by_member = battle.get("companion_sets_by_member")
	var only_liang = by_member.get("liang-xu") if by_member is Dictionary else null
	ck(by_member is Dictionary and by_member.has("liang-xu") and not by_member.has("zhao-ling"),
		"Zhao disable loads only Liang")
	ck(battle.get("companion_sprite_sets") == only_liang and int(battle.get("companion_index")) == liang_slot,
		"alias falls back to the first loaded model")
	battle.free()
	Z.enabled_override = -1

	# Invalid language: configure must refuse atomically, leaving every knob and app field untouched.
	var before_bad := snapshot()
	var bad_language: Dictionary = L.configure(app, "fr", "male")
	ck(not bad_language.get("ok", true) and snapshot() == before_bad,
		"invalid language configure refuses atomically without state changes")

	# Isolated malformed fixtures. Only user:// files; source production files are never written or deleted.
	DirAccess.make_dir_recursive_absolute(FIXTURE_DIR)
	var valid_registry: String = L.registry_path()
	var valid_supplement: String = L.supplement_path()
	var valid_index: String = L.combat_index_path()
	var registry_data := read_json(valid_registry)
	var index_data := read_json(valid_index)
	var supplement_data := read_json(valid_supplement)
	var zhao_registry := read_json(Z.registry_path())
	var zhao_index := read_json(Z.combat_index_path())
	var zhao_set: String = Z.registry_path().get_base_dir().path_join(String(zhao_registry.get("actors", {}).get("zhao-ling", "")))
	var zhao_combat: String = Z.combat_index_path().get_base_dir().path_join(String(zhao_index.get("sets", {}).get("zhao-ling", "")))
	var liang_set: String = valid_index.get_base_dir().path_join(String(index_data.get("sets", {}).get("liang-xu", "")))
	var registry_wrong := write_json("registry-wrong-member-" + TAG + ".json",
		{"schema": String(registry_data.get("schema", "")), "actors": {"zhao-ling": zhao_set}})
	var supplement_wrong := write_json("supplement-wrong-actor-" + TAG + ".json",
		{"schema": String(supplement_data.get("schema", "")), "actor_id": "zhao-ling"})
	var index_wrong := write_json("index-wrong-member-" + TAG + ".json",
		{"schema": String(index_data.get("schema", "")), "sets": {"zhao-ling": zhao_combat}})
	var index_extra := write_json("index-extra-member-" + TAG + ".json",
		{"schema": String(index_data.get("schema", "")), "sets": {"liang-xu": liang_set, "zhao-ling": zhao_combat}})
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
		{"label": "extra-member combat index", "registry": valid_registry, "supplement": valid_supplement,
			"index": index_extra},
	]
	for item in cases:
		L.registry_path_override = String(item["registry"])
		L.supplement_path_override = String(item["supplement"])
		L.combat_index_override = String(item["index"])
		L.clear_cache()
		var before_case := snapshot()
		var rejected: Dictionary = L.validate("en", "male")
		ck(not rejected.get("ok", true), String(item["label"]) + " rejected by validate")
		var refused: Dictionary = L.configure(app, "en", "male")
		ck(not refused.get("ok", true) and snapshot() == before_case,
			String(item["label"]) + " configure refuses atomically")
		assert_rejected_preserves_zhao(String(item["label"]))

	L.registry_path_override = ""
	L.supplement_path_override = ""
	L.combat_index_override = ""
	L.clear_cache()

	# Explicit generic combat choice wins over both companion models.
	arena.combat_sprite_set_override = 0
	battle = scene("battle_arena")
	by_member = battle.get("companion_sets_by_member")
	ck(by_member is Dictionary and by_member.is_empty(), "explicit generic combat override suppresses companions")
	ck(battle.get("companion_sprite_sets") == null and int(battle.get("companion_index")) == -1,
		"explicit generic override clears companion aliases")
	battle.free()
	arena.combat_sprite_set_override = -1

	# Rollback restores only this config's knob; Zhao controls/defaults remain exactly as before.
	L.rollback()
	ck(L.enabled_override == -1 and not L.enabled(), "rollback restores Liang own knob")
	ck(area.field_npc_presenter_override == "" and arena.companion_combat_member_override == ""
		and arena.companion_combat_index_override == "" and Z.enabled_override == -1 and Z.enabled(),
		"rollback leaves Zhao controls/default untouched")
	battle = scene("battle_arena")
	by_member = battle.get("companion_sets_by_member")
	ck(by_member is Dictionary and by_member.has("zhao-ling") and not by_member.has("liang-xu"),
		"post-rollback defaults load Zhao only")
	ck(battle.get("companion_sprite_sets") == by_member.get("zhao-ling"),
		"post-rollback alias is Zhao")
	battle.free()
	app.select_destination("scifi.city")
	city = scene("scifi_exploration_area")
	ck(not L.npc_attached(city), "post-rollback Liang city NPC is off")
	city.free()
	app.select_destination("scifi.outskirts")
	outskirts = scene("scifi_exploration_area")
	ck(Z.npc_attached(outskirts), "post-rollback Zhao field NPC is on")
	outskirts.free()

	reset_overrides(L)
	reset_overrides(Z)
	L.clear_cache()
	remove_fixtures()
	finish()
