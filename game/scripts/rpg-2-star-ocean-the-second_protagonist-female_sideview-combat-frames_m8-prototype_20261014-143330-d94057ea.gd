extends RefCounted

# Female protagonist side-view prototype. Independent native-pixel PNG per action frame.
# Source: game/assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-combat-manifest_m8-prototype_20261014-143059-e2500154.json
const FRAMES := {
	"idle": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-phase-01_m8-prototype_20261014-143059-fda7d2c5.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-phase-02_m8-prototype_20261014-143059-d81b907a.png",
	],
	"move": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-move-right-phase-01_m8-prototype_20261014-143059-d9ea5adf.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-move-right-phase-02_m8-prototype_20261014-143059-656d11e6.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-move-right-phase-03_m8-prototype_20261014-143059-324d5ed6.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-move-right-phase-04_m8-prototype_20261014-143059-73395247.png",
	],
	"attack": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-attack-right-phase-01_m8-prototype_20261014-143059-8a09aa35.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-attack-right-phase-02_m8-prototype_20261014-143059-3ab565ca.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-attack-right-phase-03_m8-prototype_20261014-143059-6516ccc0.png",
	],
	"guard": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-guard-right-phase-01_m8-prototype_20261014-143059-f0fd8009.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-guard-right-phase-02_m8-prototype_20261014-143059-e1d36655.png",
	],
	"dodge": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-dodge-right-phase-01_m8-prototype_20261014-143059-8f6e3043.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-dodge-right-phase-02_m8-prototype_20261014-143059-45ea2f90.png",
	],
	"hit": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-hit-right-phase-01_m8-prototype_20261014-143059-6df4fe59.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-hit-right-phase-02_m8-prototype_20261014-143059-ff1bbf12.png",
	],
	"down": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-down-right-phase-01_m8-prototype_20261014-143059-9a7aa81c.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-down-right-phase-02_m8-prototype_20261014-143059-7f6df8a7.png",
	],
	"skill": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-skill-right-phase-01_m8-prototype_20261014-143059-909db3b0.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-skill-right-phase-02_m8-prototype_20261014-143059-3b5bdd90.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-skill-right-phase-03_m8-prototype_20261014-143059-a663df7f.png",
	],
}
static var _texture_cache: Dictionary = {}

static func frame(action: String, phase: int) -> Texture2D:
	var sequence: Array = FRAMES.get(action, [])
	if sequence.is_empty():
		return null
	var path: String = sequence[clampi(phase - 1, 0, sequence.size() - 1)]
	if not _texture_cache.has(path):
		_texture_cache[path] = load(path)
	return _texture_cache[path] as Texture2D

static func count(action: String) -> int:
	return (FRAMES.get(action, []) as Array).size()
