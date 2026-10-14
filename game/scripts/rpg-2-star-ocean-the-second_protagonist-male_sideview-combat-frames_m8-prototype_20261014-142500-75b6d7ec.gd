extends RefCounted

# Side-view combat prototype. Each action is an independent native-pixel frame sequence.
# Source: game/assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-combat-manifest_m8-prototype_20261014-142325-8655f25a.json
const FRAMES := {
	"idle": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-idle-right-phase-01_m8-prototype_20261014-142325-60931269.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-idle-right-phase-02_m8-prototype_20261014-142325-234c5900.png",
	],
	"move": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-move-right-phase-01_m8-prototype_20261014-142325-c31e5cb3.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-move-right-phase-02_m8-prototype_20261014-142325-877c850f.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-move-right-phase-03_m8-prototype_20261014-142325-57e52db9.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-move-right-phase-04_m8-prototype_20261014-142325-b76eee78.png",
	],
	"attack": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-attack-right-phase-01_m8-prototype_20261014-142325-8ce01011.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-attack-right-phase-02_m8-prototype_20261014-142325-fde1b074.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-attack-right-phase-03_m8-prototype_20261014-142325-ba7ac6b2.png",
	],
	"guard": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-guard-right-phase-01_m8-prototype_20261014-142325-b15c09fd.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-guard-right-phase-02_m8-prototype_20261014-142325-20f4cba3.png",
	],
	"dodge": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-dodge-right-phase-01_m8-prototype_20261014-142325-dbcfa7ae.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-dodge-right-phase-02_m8-prototype_20261014-142325-17dd7368.png",
	],
	"hit": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-hit-right-phase-01_m8-prototype_20261014-142325-206158cd.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-hit-right-phase-02_m8-prototype_20261014-142325-c63abe8c.png",
	],
	"down": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-down-right-phase-01_m8-prototype_20261014-142325-82a5eb4c.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-down-right-phase-02_m8-prototype_20261014-142325-815ad811.png",
	],
	"skill": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-skill-right-phase-01_m8-prototype_20261014-142325-cfc25c60.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-skill-right-phase-02_m8-prototype_20261014-142325-3ccb71ee.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-skill-right-phase-03_m8-prototype_20261014-142325-93cfb6f1.png",
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
