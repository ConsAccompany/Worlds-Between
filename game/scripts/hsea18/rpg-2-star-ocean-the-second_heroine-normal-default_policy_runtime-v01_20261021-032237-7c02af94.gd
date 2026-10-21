extends RefCounted

# Ordinary-game default for the female protagonist (creator default use authorized 2026-10-21; art and motion UNAPPROVED).
# Default use of this package is not art approval. With no explicit pilot flag or override, the exploration avatar
# "protagonist-female" uses the front17 Sea distance/phase driver and the battle hero (appearance female) uses the
# heroine-sea combat set with the heroine contact/recovery timing: the same files, driver and calls as the opt-in
# playable path (hsea16 config). Any explicit exploration or battle knob (flag, enabled/registry/index override, or an
# explicit contact enable) keeps the existing explicit semantics instead, so override 0 still disables and older
# technical profiles still mean what they did. Male and every other actor are never touched.
# The package is checked whole (exploration registry/set/52 PNGs/bridges/phase bridges and the combat index/manifest/
# sheet) once per session: if any piece is missing or differs from the pinned bytes, exploration keeps the legacy
# textures and battle keeps the legacy frames with the legacy immediate attack. Refusal only warns; never fatal.

const REGISTRY_PATH := "res://data/hsea-front17/rpg-2-star-ocean-the-second_hero-female_exploration-sprite-set-registry_runtime-v01_20261020-222654-e8633039.json"
const REGISTRY_SHA256 := "a0c6eeb745cc4116beb3ca402047c120cfd70922f0128f9b11c4cbee6b7805f6"
const COMBAT_INDEX_PATH := "res://data/hsc19/rpg-2-star-ocean-the-second_heroine-sea-combat_pose-revision_spritesheet-index_20261021-034640-07587a3c.json"
const COMBAT_PINNED := {
	COMBAT_INDEX_PATH: "59d07551ad128f096e679e7eb32567d320120a61f6b14fff905c515af4fd7938",
	"res://data/hsc19/rpg-2-star-ocean-the-second_heroine-sea-combat_pose-revision_spritesheet-manifest_20261021-034640-07587a3c.json": "e32403b3218ff35221d2a6ef1c2c186acef8d2de048f9fa3f5c50fde35e2ee62",
	"res://data/hsc19/rpg-2-star-ocean-the-second_heroine-sea-combat_pose-revision_spritesheet_20261021-034640-07587a3c.png": "6ec802cfb11bff6441c407307e65bfc528a9220129acc7d8ecd49ef4cfc43e7c",
}
const SPRITE_SET_PILOT_PATH := "res://scripts/exploration_sprite_set_pilot.gd"
const SEA_DRIVER_PATH := "res://scripts/hsea09/rpg-2-star-ocean-the-second_heroine-sea_distance-driver_opt-in-v01_20261020-214620-4be375a2.gd"
const FEMALE_COMPLETE_PATH := "res://scripts/fexp/rpg-2-star-ocean-the-second_female-complete-explore_driver_pilot-v01_20261019-184900-f2c0a7e1.gd"
const COMBAT_LOADER_PATH := "res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd"
const ACTOR_ID := "protagonist-female"
const COMBAT_KEY := "hero:female"
const ART_APPROVED := false
const CREATOR_DEFAULT_ADOPTED := true

# {} = not checked yet; otherwise {"ok": bool, "reason": String}. Failures are cached too.
static var _package := {}


static func clear_cache() -> void:
	_package = {}


static func _has_arg_prefix(prefix: String) -> bool:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with(prefix):
			return true
	return false


# True when no explicit exploration knob is set, so the prepared default may select the driver for `actor`.
static func exploration_default_applies(actor: String) -> bool:
	if actor != ACTOR_ID:
		return false
	var args := OS.get_cmdline_user_args()
	var sea = load(SEA_DRIVER_PATH)
	if sea.enabled_override >= 0 or args.has(sea.FLAG):
		return false
	var loader = load(SPRITE_SET_PILOT_PATH)
	if loader.enabled_override >= 0 or args.has(loader.FLAG) or loader.registry_override != "" or _has_arg_prefix(loader.REGISTRY_ARG):
		return false
	var complete = load(FEMALE_COMPLETE_PATH)
	if complete.enabled_override >= 0 or complete.enabled():
		return false
	return true


static func package_ok() -> bool:
	return bool(package_status()["ok"])


static func package_status() -> Dictionary:
	if _package.is_empty():
		_package = _check_package()
		if not _package["ok"]:
			push_warning("Heroine normal default refused (legacy heroine kept): " + String(_package["reason"]))
	return _package


static func _refuse(reason: String) -> Dictionary:
	return {"ok": false, "reason": reason}


static func _check_package() -> Dictionary:
	if not FileAccess.file_exists(REGISTRY_PATH) or FileAccess.get_sha256(REGISTRY_PATH) != REGISTRY_SHA256:
		return _refuse("exploration registry missing or not the pinned bytes")
	for path in COMBAT_PINNED:
		if not FileAccess.file_exists(path) or FileAccess.get_sha256(path) != COMBAT_PINNED[path]:
			return _refuse("combat file missing or not the pinned bytes: " + String(path).get_file())
	# Whole exploration package through the driver's own checks (set hash profile, 52 source PNGs, bridges, phase bridges).
	if load(SEA_DRIVER_PATH).prepare(ACTOR_ID, REGISTRY_PATH).is_empty():
		return _refuse("front17 exploration package rejected by the distance driver")
	var combat = load(COMBAT_LOADER_PATH)
	var index: Dictionary = combat.load_index(COMBAT_INDEX_PATH)
	if String(index.get("status", "")) != "loaded" or not index["sets"].has(COMBAT_KEY):
		return _refuse("combat index rejected or lists no " + COMBAT_KEY)
	var loaded: Dictionary = combat.load_set(String(index["sets"][COMBAT_KEY]), COMBAT_KEY)
	if String(loaded.get("status", "")) != "loaded":
		return _refuse("combat set rejected: " + String(loaded.get("status", "")))
	return {"ok": true, "reason": ""}
