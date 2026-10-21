extends RefCounted

# Opt-in male playable path (motion and art UNAPPROVED). configure() validates the whole male package first and only
# then prepares a fresh male run in the normal exploration scene with:
#   exploration: mpath24 male driver (mexplore23 idle/walk + authored phase-aware stop supplement), male only;
#   battle: male-only battle index override with the mcombat22 index (all 8 states; visuals only).
# Mechanics are the unchanged normal rules: the male hero keeps the legacy immediate attack (no contact retiming),
# and HP, damage, AI, cooldowns, encounters, rewards and battle return are untouched. Overrides live only in this
# process; nothing edits the main menu, preferences or any default. rollback() restores every override it set.
# The generic sprite-set knobs (enabled/registry override) and the heroine default policy are not touched, so the
# female default and every other actor keep their exact current behaviour.

const DRIVER_PATH := "res://scripts/mpath24/rpg-2-star-ocean-the-second_male-playable-path_explore-driver_opt-in-v01_20261021-170200-5e1c24a7.gd"
const COMBAT_INDEX_PATH := "res://data/mcombat22/rpg-2-star-ocean-the-second_protagonist-male-combat_runtime-index_unapproved-v01_20261021-154716-8dee0dda.json"
const COMBAT_LOADER_PATH := "res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd"
const BATTLE_ARENA_PATH := "res://scripts/battle_arena.gd"
const EXPLORATION_SCENE := "res://scenes/scifi_exploration_area.tscn"
const ACTOR_ID := "protagonist-male"
const COMBAT_KEY := "hero:male"
const LANGUAGES := ["en", "zh"]
const DESTINATIONS := ["scifi.city", "scifi.outskirts", "scifi.ruins"]
const DEFAULT_DESTINATION := "scifi.outskirts"
const ART_APPROVED := false
static var _previous_overrides := {}


static func _fail(message: String) -> Dictionary:
	return {"ok": false, "error": message}


# Read-only whole-package checks; nothing in AppState or any override changes when this fails.
static func validate(app: Node, language: String, destination: String, registry: String = "", supplement: String = "", combat_index: String = "") -> Dictionary:
	if app == null:
		return _fail("AppState autoload missing")
	if not LANGUAGES.has(language):
		return _fail("language must be en or zh, got '%s'" % language)
	if not DESTINATIONS.has(destination):
		return _fail("destination must be one of %s, got '%s'" % [", ".join(DESTINATIONS), destination])
	if not app.is_scene_destination(destination) or app.area_scene_path(destination) != EXPLORATION_SCENE:
		return _fail("destination '%s' does not open the normal exploration scene" % destination)
	var driver = load(DRIVER_PATH)
	var registry_path: String = registry if registry != "" else driver.REGISTRY_PATH
	var supplement_path: String = supplement if supplement != "" else driver.SUPPLEMENT_PATH
	var index_path: String = combat_index if combat_index != "" else COMBAT_INDEX_PATH
	for path in [registry_path, supplement_path, index_path]:
		if not FileAccess.file_exists(path):
			return _fail("package file missing: " + path)
	var explore: Dictionary = driver.prepare_package(registry_path, supplement_path)
	if not explore["ok"]:
		return _fail("male exploration package rejected: %s" % str(explore["errors"]))
	var combat = load(COMBAT_LOADER_PATH)
	var index: Dictionary = combat.load_index(index_path)
	if String(index.get("status", "")) != "loaded" or not index["sets"].has(COMBAT_KEY):
		return _fail("male combat index rejected: %s" % str(index.get("status", "")))
	var combat_set: Dictionary = combat.load_set(String(index["sets"][COMBAT_KEY]), COMBAT_KEY)
	if String(combat_set.get("status", "")) != "loaded":
		return _fail("male combat set rejected: %s" % str(combat_set.get("status", "")))
	return {"ok": true, "error": "", "registry": registry_path, "supplement": supplement_path, "combat_index": index_path}


static func configure(app: Node, language: String, destination: String, registry: String = "", supplement: String = "", combat_index: String = "", normal_defaults: bool = false) -> Dictionary:
	var checked := validate(app, language, destination, registry, supplement, combat_index)
	if not checked["ok"]:
		return checked
	var driver = load(DRIVER_PATH)
	var arena = load(BATTLE_ARENA_PATH)
	if not normal_defaults and _previous_overrides.is_empty():
		_previous_overrides = {"enabled": driver.male_enabled_override, "registry": driver.registry_path_override, "supplement": driver.supplement_path_override, "combat": arena.male_playable_path_index_override}
	app.begin_new_run()
	app.hero_appearance = "male"
	app.show_initial_guide = false
	if app.language != language:
		app.toggle_language()
	if not app.select_destination(destination):
		return _fail("destination '%s' could not be selected" % destination)
	if not normal_defaults:
		driver.registry_path_override = checked["registry"] if checked["registry"] != driver.REGISTRY_PATH else ""
		driver.supplement_path_override = checked["supplement"] if checked["supplement"] != driver.SUPPLEMENT_PATH else ""
		driver.male_enabled_override = 1
		arena.male_playable_path_index_override = checked["combat_index"]
	return {"ok": true, "error": "", "language": language, "destination": destination, "scene": EXPLORATION_SCENE}


# Restores the process-local overrides configure() set; ordinary defaults were never changed.
static func rollback() -> void:
	if _previous_overrides.is_empty():
		return
	var driver = load(DRIVER_PATH)
	driver.male_enabled_override = _previous_overrides["enabled"]
	driver.registry_path_override = _previous_overrides["registry"]
	driver.supplement_path_override = _previous_overrides["supplement"]
	driver.clear_male_cache()
	load(BATTLE_ARENA_PATH).male_playable_path_index_override = _previous_overrides["combat"]
	_previous_overrides.clear()


# True only when the mpath24 male driver (not the legacy textures) draws the hero of `scene`.
static func driver_attached(scene: Node) -> bool:
	if scene == null or not ("sprite_pilot" in scene):
		return false
	var pilot = scene.get("sprite_pilot")
	return pilot != null and is_instance_valid(pilot) and pilot.get_script() != null \
		and pilot.get_script().resource_path == DRIVER_PATH
