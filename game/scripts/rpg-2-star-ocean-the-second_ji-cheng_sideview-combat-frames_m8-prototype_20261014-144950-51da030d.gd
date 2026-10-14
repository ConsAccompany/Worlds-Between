extends RefCounted

# Ji Cheng side-view prototype. Source: valid 144815 manifest only.
# game/assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-combat-manifest_m8-prototype_20261014-144815-54f4a48b.json
const FRAMES := {
	"idle": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-idle-right-phase-01_m8-prototype_20261014-144815-e729aa41.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-idle-right-phase-02_m8-prototype_20261014-144815-c9e0e9ef.png",
	],
	"move": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-move-right-phase-01_m8-prototype_20261014-144815-6d7e5296.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-move-right-phase-02_m8-prototype_20261014-144815-a519ec60.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-move-right-phase-03_m8-prototype_20261014-144815-29368d7f.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-move-right-phase-04_m8-prototype_20261014-144815-82f4e1f3.png",
	],
	"attack": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-attack-right-phase-01_m8-prototype_20261014-144815-439e1b11.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-attack-right-phase-02_m8-prototype_20261014-144815-ea31ec50.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-attack-right-phase-03_m8-prototype_20261014-144815-5e6714a3.png",
	],
	"guard": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-guard-right-phase-01_m8-prototype_20261014-144815-c4bf88a7.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-guard-right-phase-02_m8-prototype_20261014-144815-1e6dd992.png",
	],
	"dodge": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-dodge-right-phase-01_m8-prototype_20261014-144815-d90cd61e.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-dodge-right-phase-02_m8-prototype_20261014-144815-a53f25a8.png",
	],
	"hit": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-hit-right-phase-01_m8-prototype_20261014-144815-d9efb762.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-hit-right-phase-02_m8-prototype_20261014-144815-a2f6d8c1.png",
	],
	"down": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-down-right-phase-01_m8-prototype_20261014-144815-aaa9ddec.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-down-right-phase-02_m8-prototype_20261014-144815-abb0f187.png",
	],
	"skill": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-skill-right-phase-01_m8-prototype_20261014-144815-263507d2.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-skill-right-phase-02_m8-prototype_20261014-144815-abd6d26b.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-skill-right-phase-03_m8-prototype_20261014-144815-7ab67c1f.png",
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
