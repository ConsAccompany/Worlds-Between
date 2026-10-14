extends RefCounted

# Liang Xu side-view prototype. Source manifest uses only the valid 143736 batch.
# game/assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-combat-manifest_m8-prototype_20261014-143736-ddc3e7f9.json
const FRAMES := {
	"idle": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-idle-right-phase-01_m8-prototype_20261014-143736-36cefff5.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-idle-right-phase-02_m8-prototype_20261014-143736-27f4031b.png",
	],
	"move": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-move-right-phase-01_m8-prototype_20261014-143736-35626d95.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-move-right-phase-02_m8-prototype_20261014-143736-460a60e7.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-move-right-phase-03_m8-prototype_20261014-143736-e0def861.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-move-right-phase-04_m8-prototype_20261014-143736-a8ea1833.png",
	],
	"attack": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-attack-right-phase-01_m8-prototype_20261014-143736-7cf32f20.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-attack-right-phase-02_m8-prototype_20261014-143736-35146337.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-attack-right-phase-03_m8-prototype_20261014-143736-bca0b1cd.png",
	],
	"guard": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-guard-right-phase-01_m8-prototype_20261014-143736-4eeec6d5.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-guard-right-phase-02_m8-prototype_20261014-143736-c7c530ac.png",
	],
	"dodge": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-dodge-right-phase-01_m8-prototype_20261014-143736-4d51ac04.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-dodge-right-phase-02_m8-prototype_20261014-143736-4f965ab1.png",
	],
	"hit": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-hit-right-phase-01_m8-prototype_20261014-143736-6a13461e.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-hit-right-phase-02_m8-prototype_20261014-143736-037ee0a3.png",
	],
	"down": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-down-right-phase-01_m8-prototype_20261014-143736-94467fa2.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-down-right-phase-02_m8-prototype_20261014-143736-14a031e4.png",
	],
	"skill": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-skill-right-phase-01_m8-prototype_20261014-143736-e461c4fe.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-skill-right-phase-02_m8-prototype_20261014-143736-ef5d4617.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-skill-right-phase-03_m8-prototype_20261014-143736-ed2ce4ef.png",
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
