extends RefCounted

# Opt-in heroine playable path (motion and art UNAPPROVED). configure() prepares a fresh female run in
# the normal exploration scene and turns on the existing opt-in pilots through their static overrides:
#   exploration: sprite-set registry override = REGISTRY_PATH, Sea distance driver enabled_override = 1;
#   battle: combat sprite set override = 1 with index COMBAT_INDEX_PATH, heroine contact override = 1.
# HP, damage, AI, encounters and battle return are the unchanged normal rules. Nothing here edits the
# main menu, saved preferences or any default; the overrides live only in this process.
# Missing pinned files are refused: the caller must not fall back to the legacy heroine.

const REGISTRY_PATH := "res://data/hsea-front17/rpg-2-star-ocean-the-second_hero-female_exploration-sprite-set-registry_runtime-v01_20261020-222654-e8633039.json"
const COMBAT_INDEX_PATH := "res://data/heroine-sea-combat-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_spritesheet-index_v01_20261020-201338-38ecfcb0.json"
const SPRITE_SET_PILOT_PATH := "res://scripts/exploration_sprite_set_pilot.gd"
const SEA_DRIVER_PATH := "res://scripts/hsea09/rpg-2-star-ocean-the-second_heroine-sea_distance-driver_opt-in-v01_20261020-214620-4be375a2.gd"
const BATTLE_ARENA_PATH := "res://scripts/battle_arena.gd"
const EXPLORATION_SCENE := "res://scenes/scifi_exploration_area.tscn"
const ACTOR_ID := "protagonist-female"
const LANGUAGES := ["en", "zh"]
const DESTINATIONS := ["scifi.city", "scifi.outskirts", "scifi.ruins"]
const DEFAULT_DESTINATION := "scifi.outskirts"


static func _fail(message: String) -> Dictionary:
	return {"ok": false, "error": message}


# Read-only checks; nothing is changed when this fails.
static func validate(app: Node, language: String, destination: String) -> Dictionary:
	if app == null:
		return _fail("AppState autoload missing")
	if not LANGUAGES.has(language):
		return _fail("language must be en or zh, got '%s'" % language)
	if not DESTINATIONS.has(destination):
		return _fail("destination must be one of %s, got '%s'" % [", ".join(DESTINATIONS), destination])
	if not app.is_scene_destination(destination) or app.area_scene_path(destination) != EXPLORATION_SCENE:
		return _fail("destination '%s' does not open the normal exploration scene" % destination)
	for path in [REGISTRY_PATH, COMBAT_INDEX_PATH]:
		if not FileAccess.file_exists(path):
			return _fail("pinned file missing: " + path)
	var registry = JSON.parse_string(FileAccess.get_file_as_string(REGISTRY_PATH))
	if typeof(registry) != TYPE_DICTIONARY:
		return _fail("pinned registry is not a JSON object")
	var loader = load(SPRITE_SET_PILOT_PATH)
	var checked: Dictionary = loader.load_registry(REGISTRY_PATH)
	if not checked.get("ok", false) or String(checked.get("actors", {}).get(ACTOR_ID, "")) == "":
		return _fail("pinned registry rejected or lists no %s set" % ACTOR_ID)
	return {"ok": true, "error": ""}


static func configure(app: Node, language: String, destination: String, normal_defaults: bool = false) -> Dictionary:
	var checked := validate(app, language, destination)
	if not checked["ok"]:
		return checked
	app.begin_new_run()
	app.hero_appearance = "female"
	app.show_initial_guide = false
	if app.language != language:
		app.toggle_language()
	if not app.select_destination(destination):
		return _fail("destination '%s' could not be selected" % destination)
	if not normal_defaults:
		var loader = load(SPRITE_SET_PILOT_PATH)
		loader.registry_override = REGISTRY_PATH
		loader.clear_cache()
		load(SEA_DRIVER_PATH).enabled_override = 1
		var arena = load(BATTLE_ARENA_PATH)
		arena.combat_sprite_set_override = 1
		arena.combat_sprite_set_index_override = COMBAT_INDEX_PATH
		arena.heroine_sea_contact_override = 1
	return {"ok": true, "error": "", "language": language, "destination": destination, "scene": EXPLORATION_SCENE}


# True only when the Sea distance driver (not the legacy textures) draws the hero of `scene`.
static func driver_attached(scene: Node) -> bool:
	if scene == null or not ("sprite_pilot" in scene):
		return false
	var driver = scene.get("sprite_pilot")
	return driver != null and is_instance_valid(driver) and driver.get_script() != null \
		and driver.get_script().resource_path == SEA_DRIVER_PATH
