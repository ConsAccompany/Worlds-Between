extends SceneTree
# Independent scope / rollback / malformed-input check for the Zhao Ling playable-path config.
# Scope: the frozen public API plus the two process-local host hooks that the integrated config replaces.
# Not normal-input gameplay, not art approval, not default adoption.
# Zhao is a companion: this test asserts the preview never replaces the male/female hero package, never
# touches the hero generic knobs, force-recruits nobody and creates no follower.
# PASS here is NOT creator authorization and NOT evidence that DEFAULT_ADOPTED should change.
#
# Run from the project root with APPDATA pointed inside the checkout, so user:// (logs and saves) is
# isolated from the existing player save. See the matching *_run-note_*.md in this directory.
# Expected marker: ZHAO_SCOPE_ALL_PASS. Missing policy prints ZHAO_SCOPE NOT_RUN and exits 2.

const CONFIG_PATH := "res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_config_opt-in-v01_20261021-223218-3246d731.gd"
const AREA_SCENE := "res://scenes/scifi_exploration_area.tscn"
const ARENA_PATH := "res://scripts/battle_arena.gd"
const EXPLORE_PATH := "res://scripts/exploration_sprite_set_pilot.gd"
const AREA_PATH := "res://scripts/scifi_exploration_area.gd"
const SAVE_STORE_PATH := "res://scripts/save_store.gd"

var Cfg
var Arena
var Explore
var Area
var SaveStore
var app: Node
var checks := 0
var failed := false
var initial_own: Dictionary = {}
var initial_scope: Dictionary = {}
var initial_knobs: Dictionary = {}
var original_save_root := ""
var isolated_save_root := ""


func _initialize() -> void:
	_run.call_deferred()


func ck(ok: bool, label: String) -> void:
	checks += 1
	failed = failed or not ok
	print("ZHAO_SCOPE ", "PASS " if ok else "FAIL ", label)


func _run() -> void:
	if not FileAccess.file_exists(CONFIG_PATH):
		print("ZHAO_SCOPE NOT_RUN config_missing ", CONFIG_PATH)
		quit(2)
		return
	Cfg = load(CONFIG_PATH)
	if Cfg == null or not (Cfg is GDScript):
		print("ZHAO_SCOPE NOT_RUN config_load_failed ", CONFIG_PATH)
		quit(2)
		return
	Arena = load(ARENA_PATH)
	Explore = load(EXPLORE_PATH)
	Area = load(AREA_PATH)
	SaveStore = load(SAVE_STORE_PATH)
	app = root.get_node_or_null("AppState")
	if app == null or Arena == null or Explore == null or Area == null or SaveStore == null:
		ck(false, "AppState, battle arena, exploration pilot, area host and save store load")
		_finish()
		return

	_isolate_saves()
	Cfg.clear_cache()
	initial_own = _own()
	initial_scope = _scope()
	initial_knobs = _knobs()

	# Fixture baseline: deliberately not the values configure() would install, so refusals are visible.
	app.begin_new_run()
	app.language = "zh"
	app.hero_appearance = "female"
	app.current_destination_id = "scifi.city"
	app.calendar_minutes = 12345

	# 1. Frozen public surface and no default-adoption claim.
	ck(Cfg.DEFAULT_ADOPTED == false, "DEFAULT_ADOPTED=false: no ordinary default adoption")
	ck(int(Cfg.enabled_override) == -1, "enabled_override defaults to -1")
	ck(String(Cfg.registry_path_override) == "" and String(Cfg.supplement_path_override) == "" and String(Cfg.combat_index_override) == "", "registry/supplement/combat overrides default empty")

	# 2. Whole-package validate is read-only, for both hero appearances.
	var app0 := _app()
	var own0 := _own()
	var knobs0 := _knobs()
	var validate_en: Dictionary = Cfg.validate("en", "male")
	var validate_zh: Dictionary = Cfg.validate("zh", "female")
	ck(bool(validate_en.get("ok", false)), "whole package validates en/male")
	ck(bool(validate_zh.get("ok", false)), "whole package validates zh/female")
	ck(_app() == app0, "valid validate leaves AppState untouched")
	ck(_own() == own0, "valid validate leaves own overrides untouched")
	ck(_knobs() == knobs0, "valid validate leaves hero knobs untouched")

	# 3. Malformed language/appearance/page refusals: no AppState, override, hero-knob or save write.
	_expect_refusal("invalid language validate", false, "fr", "male")
	_expect_refusal("invalid appearance validate", false, "en", "scifi.outskirts")
	_expect_refusal("empty language validate", false, "", "male")
	_expect_refusal("invalid language configure", true, "fr", "male")
	_expect_refusal("invalid appearance configure", true, "en", "scifi.outskirts")

	# 4. Missing registry / supplement / combat index: cache reset, refusal, then exact restore.
	_missing_package_case("registry", "registry_path_override")
	_missing_package_case("supplement", "supplement_path_override")
	_missing_package_case("combat", "combat_index_override")

	# clear_cache() itself must not mutate state.
	var cache_own := _own()
	var cache_app := _app()
	Cfg.clear_cache()
	ck(_own() == cache_own, "clear_cache leaves own overrides unchanged")
	ck(_app() == cache_app, "clear_cache leaves AppState unchanged")

	# 5. Configure is a preview fresh run for either hero appearance; hero paths stay exact.
	for pair in [["en", "male"], ["zh", "female"]]:
		Cfg.rollback()
		Cfg.clear_cache()
		var before_scope := _scope()
		var before_knobs := _knobs()
		var before_defaults := _hero_defaults()
		var configured: Dictionary = Cfg.configure(app, pair[0], pair[1])
		var ok := bool(configured.get("ok", false))
		ck(ok, "configure preview %s/%s succeeds" % [pair[0], pair[1]])
		if ok:
			ck(app.hero_appearance == pair[1], "preview selects %s hero appearance" % pair[1])
			ck(app.current_destination_id == "scifi.outskirts", "preview selects scifi.outskirts")
			ck(app.run_active, "preview starts a fresh run")
			ck(int(Cfg.enabled_override) == 1, "preview enables only its own Zhao knob")
		ck(_knobs() == before_knobs, "configure leaves hero generic knobs unchanged for %s" % pair[1])
		ck(_hero_defaults() == before_defaults, "configure leaves male/female hero package defaults unchanged for %s" % pair[1])
		ck(not app.recruited_members.has("zhao-ling"), "configure does not force-recruit Zhao (%s)" % pair[1])
		ck(app.active_party_ids.size() == 1 and app.active_party_ids[0] == "hero", "party stays hero-only after configure (%s)" % pair[1])
		Cfg.rollback()
		ck(_scope() == before_scope, "rollback restores all pre-configure own/host overrides exactly (%s)" % pair[1])
		ck(_knobs() == before_knobs, "rollback leaves hero knobs unchanged (%s)" % pair[1])

	# 6. Previous enabled_override 0/1/-1 must survive configure/rollback exactly.
	for sentinel in [0, 1, -1]:
		Cfg.rollback()
		Cfg.enabled_override = sentinel
		Cfg.registry_path_override = ""
		Cfg.supplement_path_override = ""
		Cfg.combat_index_override = ""
		Cfg.clear_cache()
		var enabled_scope := _scope()
		var enabled_knobs := _knobs()
		var enabled_configured: Dictionary = Cfg.configure(app, "en", "male")
		ck(bool(enabled_configured.get("ok", false)), "configure succeeds with prior enabled=%d" % sentinel)
		Cfg.rollback()
		ck(_scope() == enabled_scope, "rollback restores own/host overrides exactly for prior enabled=%d" % sentinel)
		ck(_knobs() == enabled_knobs, "rollback leaves hero knobs unchanged for prior enabled=%d" % sentinel)

	# 7. Nested configure keeps the first pre-configure snapshot; repeated rollback is harmless.
	Cfg.rollback()
	Cfg.enabled_override = 0
	Cfg.registry_path_override = ""
	Cfg.supplement_path_override = ""
	Cfg.combat_index_override = ""
	Cfg.clear_cache()
	var nested_scope := _scope()
	var first: Dictionary = Cfg.configure(app, "en", "male")
	var second: Dictionary = Cfg.configure(app, "zh", "female")
	ck(bool(first.get("ok", false)) and bool(second.get("ok", false)), "nested preview configure succeeds twice")
	Cfg.rollback()
	ck(_scope() == nested_scope, "one rollback after nested configure restores the original own/host overrides")
	Cfg.rollback()
	ck(_scope() == nested_scope, "repeated rollback is harmless")

	# 8. Actual outskirts scene: actual Zhao NPC attached, no forced recruit, no follower, static NPC.
	Cfg.rollback()
	Cfg.enabled_override = -1
	Cfg.registry_path_override = ""
	Cfg.supplement_path_override = ""
	Cfg.combat_index_override = ""
	Cfg.clear_cache()
	var scene_configured: Dictionary = Cfg.configure(app, "en", "male")
	if not bool(scene_configured.get("ok", false)):
		ck(false, "scene probe requires a successful preview configure")
	else:
		var change_error := change_scene_to_file(AREA_SCENE)
		ck(change_error == OK, "preview enters the normal exploration scene")
		for i in 5:
			await process_frame
		var scene := current_scene
		ck(scene != null, "exploration scene instance exists")
		if scene != null:
			ck(Cfg.npc_attached(scene), "actual Zhao field NPC is attached in scifi.outskirts")
			var npc = scene.get("field_npc")
			ck(npc != null and npc is Sprite2D, "scifi.outskirts has the ordinary field NPC")
			if npc != null:
				ck(npc.visible, "field NPC stays visible because Zhao is not recruited")
				var static_position: Vector2 = npc.position
				for i in 8:
					await process_frame
				ck(npc.position == static_position, "ordinary NPC stays static (scripted probe, not normal input)")
			ck(_find_named(scene, "follower").is_empty(), "no follower node created")
			ck(not app.recruited_members.has("zhao-ling"), "entering the preview does not recruit Zhao")
			ck(app.active_party_ids.size() == 1 and app.active_party_ids[0] == "hero", "no follower added to the active party")
	Cfg.rollback()
	ck(_scope() == initial_scope, "final rollback returns own/host overrides to the process default")

	_finish()


func _expect_refusal(label: String, is_configure: bool, language: String, appearance: String) -> void:
	var app0 := _app()
	var scope0 := _scope()
	var knobs0 := _knobs()
	var saves0 := _saves()
	var result: Dictionary
	if is_configure:
		result = Cfg.configure(app, language, appearance)
	else:
		result = Cfg.validate(language, appearance)
	ck(not bool(result.get("ok", true)), label + " is refused")
	ck(_app() == app0, label + " leaves AppState unchanged")
	ck(_scope() == scope0, label + " leaves own/host overrides unchanged")
	ck(_knobs() == knobs0, label + " leaves hero knobs unchanged")
	ck(_saves() == saves0, label + " writes no save")


func _missing_package_case(label: String, property: String) -> void:
	Cfg.rollback()
	var own0 := _own()
	var scope0 := _scope()
	var app0 := _app()
	var knobs0 := _knobs()
	var saves0 := _saves()
	Cfg.clear_cache()
	ck(_scope() == scope0 and _app() == app0, "clear_cache before missing-%s injection is inert" % label)
	_set_own(property, "user://zhao-scope-missing-%s-%s.json" % [label, _stamp()])
	ck(_own() != own0, "missing-%s fixture injected through the public override" % label)
	var validated: Dictionary = Cfg.validate("en", "male")
	ck(not bool(validated.get("ok", true)), "missing %s refuses validate" % label)
	var configured: Dictionary = Cfg.configure(app, "en", "male")
	ck(not bool(configured.get("ok", true)), "missing %s refuses configure" % label)
	ck(_app() == app0, "missing %s leaves AppState unchanged" % label)
	ck(_knobs() == knobs0, "missing %s leaves hero knobs unchanged" % label)
	ck(_saves() == saves0, "missing %s writes no save" % label)
	_set_own(property, own0[property])
	Cfg.clear_cache()
	ck(bool(Cfg.validate("en", "male").get("ok", false)), "restored %s plus cache reset validates again" % label)
	ck(_scope() == scope0, "restored %s leaves own/host overrides at the pre-test value" % label)
	ck(_app() == app0, "AppState is still unchanged after restoring %s" % label)


func _isolate_saves() -> void:
	original_save_root = String(SaveStore.root_path)
	isolated_save_root = "user://zhao-scope-check-%s" % _stamp()
	SaveStore.root_path = isolated_save_root
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(isolated_save_root))


func _stamp() -> String:
	return str(Time.get_ticks_usec())


func _set_own(property: String, value) -> void:
	match property:
		"enabled_override":
			Cfg.enabled_override = value
		"registry_path_override":
			Cfg.registry_path_override = value
		"supplement_path_override":
			Cfg.supplement_path_override = value
		"combat_index_override":
			Cfg.combat_index_override = value
		_:
			push_error("unknown own override: " + property)


func _own() -> Dictionary:
	return {
		"enabled_override": Cfg.enabled_override,
		"registry_path_override": Cfg.registry_path_override,
		"supplement_path_override": Cfg.supplement_path_override,
		"combat_index_override": Cfg.combat_index_override,
	}


# Everything configure() is allowed to replace: this config's four public knobs plus the two host
# hooks it installs. Hero generic knobs are deliberately NOT here; _knobs() asserts they never move.
func _scope() -> Dictionary:
	return {
		"config": _own(),
		"presenter": Area.field_npc_presenter_override,
		"combat_member": Arena.companion_combat_member_override,
		"combat_index": Arena.companion_combat_index_override,
	}


func _knobs() -> Dictionary:
	return {
		"explore_enabled": Explore.enabled_override,
		"explore_registry": Explore.registry_override,
		"combat_enabled": Arena.combat_sprite_set_override,
		"combat_index": Arena.combat_sprite_set_index_override,
		"male_index": Arena.male_playable_path_index_override,
		"heroine_contact": Arena.heroine_sea_contact_override,
	}


func _hero_defaults() -> Dictionary:
	return {
		"female": Arena.heroine_default_battle_applies(["hero"], "female"),
		"male": Arena.heroine_default_battle_applies(["hero"], "male"),
	}


func _app() -> Dictionary:
	return {
		"language": app.language,
		"hero_appearance": app.hero_appearance,
		"current_destination_id": app.current_destination_id,
		"run_active": app.run_active,
		"calendar_minutes": app.calendar_minutes,
		"hero_state": app.hero_state.duplicate(true),
		"member_states": app.member_states.duplicate(true),
		"active_party_ids": app.active_party_ids.duplicate(),
		"recruited_members": app.recruited_members.duplicate(true),
		"party_bonds": app.party_bonds.duplicate(true),
	}


func _saves() -> Array:
	var out: Array = []
	var directory := DirAccess.open(String(SaveStore.root_path))
	if directory == null:
		return out
	directory.list_dir_begin()
	var entry := directory.get_next()
	while entry != "":
		if entry != "." and entry != "..":
			var path := String(SaveStore.root_path).path_join(entry)
			if directory.current_is_dir():
				out.append("D:" + entry)
			else:
				out.append("F:%s:%d" % [entry, FileAccess.get_file_as_bytes(path).size()])
		entry = directory.get_next()
	directory.list_dir_end()
	out.sort()
	return out


func _find_named(node: Node, fragment: String) -> Array:
	var hits: Array = []
	if String(node.name).to_lower().contains(fragment.to_lower()):
		hits.append(node)
	for child in node.get_children():
		hits.append_array(_find_named(child, fragment))
	return hits


func _finish() -> void:
	if Cfg != null:
		Cfg.rollback()
		if not initial_scope.is_empty():
			for key in initial_scope["config"]:
				_set_own(key, initial_scope["config"][key])
			Area.field_npc_presenter_override = initial_scope["presenter"]
			Arena.companion_combat_member_override = initial_scope["combat_member"]
			Arena.companion_combat_index_override = initial_scope["combat_index"]
		else:
			for key in initial_own:
				_set_own(key, initial_own[key])
		Cfg.clear_cache()
	if Explore != null and Arena != null and not initial_knobs.is_empty():
		Explore.enabled_override = initial_knobs["explore_enabled"]
		Explore.registry_override = initial_knobs["explore_registry"]
		Arena.combat_sprite_set_override = initial_knobs["combat_enabled"]
		Arena.combat_sprite_set_index_override = initial_knobs["combat_index"]
		Arena.male_playable_path_index_override = initial_knobs["male_index"]
		Arena.heroine_sea_contact_override = initial_knobs["heroine_contact"]
	if current_scene != null and is_instance_valid(current_scene):
		var previous_scene := current_scene
		root.remove_child(previous_scene)
		previous_scene.free()
	if SaveStore != null and original_save_root != "":
		SaveStore.root_path = original_save_root
	# Keep the bounded isolated fixture directory for evidence; never recursively delete save paths.
	if failed:
		print("ZHAO_SCOPE_ALL_FAIL checks=", checks)
	else:
		print("ZHAO_SCOPE_ALL_PASS checks=", checks)
	quit(1 if failed else 0)
