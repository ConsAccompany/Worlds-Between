extends RefCounted

# Ji Cheng (纪澄) companion path: creator-authorized MVP default; final art/motion UNAPPROVED.
# Ji stays a companion: recruited at the existing scifi.ruins recruit NPC through the normal dialogue only after the
# existing records console sets ji_records_checked, Tab-controlled in battle, never a follower or hero replacement.
#   exploration: the existing ruins recruit Sprite2D (field_npc) gets the jpath33 driver (lpath30 driver reused with jexplore31 paths);
#   battle: a separate member-scoped companion combat model with the jcombat32 index draws only the Ji slot.
# validate() checks the whole package read-only. configure() runs it first and mutates nothing on refusal; on success it
# prepares a fresh separate-save preview run at scifi.ruins (no forced recruit, no records bypass) and sets only this
# file's enabled_override. It never sets the host overrides (field_npc_presenter_override, companion_combat_member/
# index_override): the hosts pick this config by recruit/member id. rollback() restores exactly what configure() replaced.
# Hero, Zhao and Liang defaults, AI, damage, cooldowns, input, party order, saves, story, collisions and encounters are untouched.

const DEFAULT_ADOPTED := true
const ART_APPROVED := false
const MEMBER_ID := "ji-cheng"
const DESTINATION := "scifi.ruins"
const LANGUAGES := ["en", "zh"]
const APPEARANCES := ["male", "female"]
const DRIVER_PATH := "res://scripts/jpath33/rpg-2-star-ocean-the-second_ji-playable-path_npc-driver_opt-in-v01_20261021-222438-7d4b2e91.gd"
const CONFIG_PATH := "res://scripts/jpath33/rpg-2-star-ocean-the-second_ji-playable-path_config_opt-in-v01_20261021-222438-7d4b2e91.gd"
const COMBAT_INDEX_PATH := "res://data/jcombat32/rpg-2-star-ocean-the-second_ji-cheng-combat_runtime-index_unapproved-jcombat32-v01_20261021-220632-089ef67c.json"
const COMBAT_LOADER_PATH := "res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd"
const EXPLORATION_PATH := "res://scripts/scifi_exploration_area.gd"
const EXPLORATION_SCENE := "res://scenes/scifi_exploration_area.tscn"

static var enabled_override := -1
static var registry_path_override := ""
static var supplement_path_override := ""
static var combat_index_override := ""
static var _previous := {}


static func enabled() -> bool:
	if enabled_override >= 0:
		return enabled_override == 1
	return DEFAULT_ADOPTED


static func registry_path() -> String:
	return registry_path_override if registry_path_override != "" else load(DRIVER_PATH).JI_REGISTRY_PATH


static func supplement_path() -> String:
	return supplement_path_override if supplement_path_override != "" else load(DRIVER_PATH).JI_SUPPLEMENT_PATH


static func combat_index_path() -> String:
	return combat_index_override if combat_index_override != "" else COMBAT_INDEX_PATH


static func _fail(message: String) -> Dictionary:
	return {"ok": false, "error": message}


static func _app() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.root.get_node_or_null("AppState") if tree != null else null


# Read-only whole-package check: exploration (all four directions, idle/walk banks, every stop bridge) and an exact
# member-only combat index (sets == {ji-cheng}) whose set loads under the ji-cheng key.
static func validate(language: String, appearance: String) -> Dictionary:
	if not LANGUAGES.has(language):
		return _fail("language must be en or zh, got '%s'" % language)
	if not APPEARANCES.has(appearance):
		return _fail("appearance must be male or female, got '%s'" % appearance)
	var app := _app()
	if app == null:
		return _fail("AppState autoload missing")
	if not app.is_scene_destination(DESTINATION) or app.area_scene_path(DESTINATION) != EXPLORATION_SCENE:
		return _fail("scifi.ruins does not open the normal exploration scene")
	var area = load(EXPLORATION_PATH)
	if area == null or String(area.AREA_CONFIG.get(DESTINATION, {}).get("recruit", "")) != MEMBER_ID:
		return _fail("scifi.ruins recruit NPC is not ji-cheng")
	var explore: Dictionary = load(DRIVER_PATH).prepare_ji_package(registry_path(), supplement_path())
	if not explore["ok"]:
		return _fail("ji exploration package rejected: %s" % str(explore["errors"]))
	var combat = load(COMBAT_LOADER_PATH)
	var index_path := combat_index_path()
	if not FileAccess.file_exists(index_path):
		return _fail("ji combat index missing: " + index_path)
	var index: Dictionary = combat.load_index(index_path)
	var sets: Dictionary = index.get("sets", {})
	if String(index.get("status", "")) != "loaded" or sets.size() != 1 or not sets.has(MEMBER_ID):
		return _fail("ji combat index rejected (must list exactly ji-cheng): %s %s" % [str(index.get("status", "")), str(sets.keys())])
	var combat_set: Dictionary = combat.load_set(String(sets[MEMBER_ID]), MEMBER_ID)
	if String(combat_set.get("status", "")) != "loaded" or combat_set.get("key") != MEMBER_ID:
		return _fail("ji combat set rejected: %s" % str(combat_set.get("status", "")))
	return {"ok": true, "error": "", "registry": registry_path(), "supplement": supplement_path(), "combat_index": index_path,
		"combat_set_id": String(combat_set.get("set_id", "")), "explore_set_id": String(explore["set"].get("set_id", ""))}


static func configure(app: Node, language: String, appearance: String = "male") -> Dictionary:
	if app == null:
		return _fail("AppState autoload missing")
	var checked := validate(language, appearance)
	if not checked["ok"]:
		return checked
	if _previous.is_empty():
		_previous = {"enabled": enabled_override}
	app.begin_new_run()
	app.hero_appearance = appearance
	app.show_initial_guide = false
	if app.language != language:
		app.toggle_language()
	if not app.select_destination(DESTINATION):
		rollback()
		return _fail("scifi.ruins could not be selected")
	enabled_override = 1
	return {"ok": true, "error": "", "language": language, "appearance": appearance, "destination": DESTINATION,
		"scene": EXPLORATION_SCENE, "combat_index": checked["combat_index"]}


# Restores this file's knob exactly as configure() found it (configure sets nothing else).
static func rollback() -> void:
	if _previous.is_empty():
		return
	enabled_override = _previous["enabled"]
	_previous.clear()


static func clear_cache() -> void:
	load(DRIVER_PATH).clear_ji_cache()
	load("res://scripts/exploration_sprite_set_pilot.gd").clear_cache()
	load(COMBAT_LOADER_PATH).clear_cache()


# Host hook (exploration): returns the Ji driver for the recruit NPC, or null (off, other member, or refused whole).
static func attach_field_npc(target: Sprite2D, member_id: String) -> Node:
	if not enabled() or member_id != MEMBER_ID:
		return null
	var app := _app()
	if app == null or not validate(app.language, app.hero_appearance).get("ok", false):
		return null
	return load(DRIVER_PATH).attach_ji_npc(target, member_id, registry_path(), supplement_path())


# True only when the jpath33 driver draws the actual ji-cheng recruit NPC of `scene` (scifi.ruins keeps it in field_npc).
static func npc_attached(scene: Node) -> bool:
	if scene == null or not ("field_npc_driver" in scene) or not ("field_npc" in scene):
		return false
	var driver = scene.get("field_npc_driver")
	var npc = scene.get("field_npc")
	return driver != null and is_instance_valid(driver) and npc != null and is_instance_valid(npc) \
		and String(scene.get("recruit_id")) == MEMBER_ID and driver.get_parent() == npc \
		and driver.get_script() != null and driver.get_script().resource_path == DRIVER_PATH
