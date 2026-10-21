extends RefCounted

# Opt-in Zhao Ling (赵铃) companion path (art/motion UNAPPROVED). Zhao stays a companion: recruited at the existing Yonkers
# (scifi.outskirts) field NPC through the normal dialogue, Tab-controlled in battle, never a follower or hero replacement.
#   exploration: the existing field NPC Sprite2D gets the zexplore25 driver (4-direction idle/walk + stop supplement);
#   battle: a separate member-scoped companion combat model with the zcombat26 index draws only the Zhao slot.
# validate() checks the whole package read-only. configure() runs it first and mutates nothing on refusal; on success it
# prepares a fresh separate-save preview run at scifi.outskirts (no forced recruit) and sets only this file's knobs and the
# two guarded host hooks. rollback() restores exactly what configure() replaced. Hero generic knobs, hero package
# defaults, AI, damage, cooldowns, input, party order, saves, story, collisions and encounters are untouched.
# DEFAULT_ADOPTED stays false until the creator authorizes ordinary Zhao use; no default credit is implied.

const DEFAULT_ADOPTED := false
const ART_APPROVED := false
const MEMBER_ID := "zhao-ling"
const DESTINATION := "scifi.outskirts"
const LANGUAGES := ["en", "zh"]
const APPEARANCES := ["male", "female"]
const DRIVER_PATH := "res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_npc-driver_opt-in-v01_20261021-223218-3246d731.gd"
const CONFIG_PATH := "res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_config_opt-in-v01_20261021-223218-3246d731.gd"
const COMBAT_INDEX_PATH := "res://data/zcombat26/rpg-2-star-ocean-the-second_zhao-ling-combat_runtime-index_unapproved-zcombat26-v01_20261021-180157-63cae05d.json"
const COMBAT_LOADER_PATH := "res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd"
const EXPLORATION_PATH := "res://scripts/scifi_exploration_area.gd"
const BATTLE_ARENA_PATH := "res://scripts/battle_arena.gd"
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
	return registry_path_override if registry_path_override != "" else load(DRIVER_PATH).REGISTRY_PATH


static func supplement_path() -> String:
	return supplement_path_override if supplement_path_override != "" else load(DRIVER_PATH).SUPPLEMENT_PATH


static func combat_index_path() -> String:
	return combat_index_override if combat_index_override != "" else COMBAT_INDEX_PATH


static func _fail(message: String) -> Dictionary:
	return {"ok": false, "error": message}


static func _app() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.root.get_node_or_null("AppState") if tree != null else null


# Read-only whole-package check: exploration (all four directions, idle/walk banks, every stop bridge) and combat.
static func validate(language: String, appearance: String) -> Dictionary:
	if not LANGUAGES.has(language):
		return _fail("language must be en or zh, got '%s'" % language)
	if not APPEARANCES.has(appearance):
		return _fail("appearance must be male or female, got '%s'" % appearance)
	var app := _app()
	if app == null:
		return _fail("AppState autoload missing")
	if not app.is_scene_destination(DESTINATION) or app.area_scene_path(DESTINATION) != EXPLORATION_SCENE:
		return _fail("scifi.outskirts does not open the normal exploration scene")
	var area = load(EXPLORATION_PATH)
	if area == null or String(area.AREA_CONFIG.get(DESTINATION, {}).get("recruit", "")) != MEMBER_ID:
		return _fail("scifi.outskirts field NPC is not zhao-ling")
	var explore: Dictionary = load(DRIVER_PATH).prepare_package(registry_path(), supplement_path())
	if not explore["ok"]:
		return _fail("zhao exploration package rejected: %s" % str(explore["errors"]))
	var combat = load(COMBAT_LOADER_PATH)
	var index_path := combat_index_path()
	if not FileAccess.file_exists(index_path):
		return _fail("zhao combat index missing: " + index_path)
	var index: Dictionary = combat.load_index(index_path)
	if String(index.get("status", "")) != "loaded" or not index.get("sets", {}).has(MEMBER_ID):
		return _fail("zhao combat index rejected: %s" % str(index.get("status", "")))
	var combat_set: Dictionary = combat.load_set(String(index["sets"][MEMBER_ID]), MEMBER_ID)
	if String(combat_set.get("status", "")) != "loaded" or combat_set.get("key") != MEMBER_ID:
		return _fail("zhao combat set rejected: %s" % str(combat_set.get("status", "")))
	return {"ok": true, "error": "", "registry": registry_path(), "supplement": supplement_path(), "combat_index": index_path,
		"combat_set_id": String(combat_set.get("set_id", "")), "explore_set_id": String(explore["set"].get("set_id", ""))}


static func configure(app: Node, language: String, appearance: String = "male") -> Dictionary:
	if app == null:
		return _fail("AppState autoload missing")
	var checked := validate(language, appearance)
	if not checked["ok"]:
		return checked
	var area = load(EXPLORATION_PATH)
	var arena = load(BATTLE_ARENA_PATH)
	if _previous.is_empty():
		_previous = {"enabled": enabled_override, "presenter": area.field_npc_presenter_override,
			"member": arena.companion_combat_member_override, "index": arena.companion_combat_index_override}
	app.begin_new_run()
	app.hero_appearance = appearance
	app.show_initial_guide = false
	if app.language != language:
		app.toggle_language()
	if not app.select_destination(DESTINATION):
		rollback()
		return _fail("scifi.outskirts could not be selected")
	enabled_override = 1
	area.field_npc_presenter_override = CONFIG_PATH
	arena.companion_combat_member_override = MEMBER_ID
	arena.companion_combat_index_override = checked["combat_index"]
	return {"ok": true, "error": "", "language": language, "appearance": appearance, "destination": DESTINATION,
		"scene": EXPLORATION_SCENE, "combat_index": checked["combat_index"]}


# Restores this file's knob and the two host hooks exactly as configure() found them.
static func rollback() -> void:
	if _previous.is_empty():
		return
	enabled_override = _previous["enabled"]
	load(EXPLORATION_PATH).field_npc_presenter_override = _previous["presenter"]
	var arena = load(BATTLE_ARENA_PATH)
	arena.companion_combat_member_override = _previous["member"]
	arena.companion_combat_index_override = _previous["index"]
	_previous.clear()


static func clear_cache() -> void:
	load(DRIVER_PATH).clear_zhao_cache()
	load("res://scripts/exploration_sprite_set_pilot.gd").clear_cache()
	load(COMBAT_LOADER_PATH).clear_cache()


# Host hook (exploration): returns the Zhao driver for the field NPC, or null (off, other member, or refused whole).
static func attach_field_npc(target: Sprite2D, member_id: String) -> Node:
	if not enabled() or member_id != MEMBER_ID:
		return null
	var app := _app()
	if app == null or not validate(app.language, app.hero_appearance).get("ok", false):
		return null
	return load(DRIVER_PATH).attach_npc(target, member_id, registry_path(), supplement_path())


# True only when the zpath27 driver draws the actual zhao-ling field NPC of `scene`.
static func npc_attached(scene: Node) -> bool:
	if scene == null or not ("field_npc_driver" in scene) or not ("field_npc" in scene):
		return false
	var driver = scene.get("field_npc_driver")
	var npc = scene.get("field_npc")
	return driver != null and is_instance_valid(driver) and npc != null and is_instance_valid(npc) \
		and String(scene.get("recruit_id")) == MEMBER_ID and driver.get_parent() == npc \
		and driver.get_script() != null and driver.get_script().resource_path == DRIVER_PATH
