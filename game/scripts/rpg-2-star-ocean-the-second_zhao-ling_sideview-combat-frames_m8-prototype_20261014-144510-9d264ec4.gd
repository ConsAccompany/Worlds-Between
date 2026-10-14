extends RefCounted

# Zhao Ling side-view prototype; 20 frames from the 144336 manifest only.
# game/assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-combat-manifest_m8-prototype_20261014-144336-7d0dd6cc.json
const FRAMES := {
	"idle": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-idle-right-phase-01_m8-prototype_20261014-144336-399a8229.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-idle-right-phase-02_m8-prototype_20261014-144336-36c4c17c.png",
	],
	"move": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-move-right-phase-01_m8-prototype_20261014-144336-cc9b9b6e.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-move-right-phase-02_m8-prototype_20261014-144336-3b6b600a.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-move-right-phase-03_m8-prototype_20261014-144336-8a9282a7.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-move-right-phase-04_m8-prototype_20261014-144336-78cdb2aa.png",
	],
	"attack": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-attack-right-phase-01_m8-prototype_20261014-144336-4b138b9a.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-attack-right-phase-02_m8-prototype_20261014-144336-8792624d.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-attack-right-phase-03_m8-prototype_20261014-144336-cbfc1163.png",
	],
	"guard": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-guard-right-phase-01_m8-prototype_20261014-144336-2ab295c1.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-guard-right-phase-02_m8-prototype_20261014-144336-8a565a1e.png",
	],
	"dodge": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-dodge-right-phase-01_m8-prototype_20261014-144336-b5ca56e5.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-dodge-right-phase-02_m8-prototype_20261014-144336-3ba9f074.png",
	],
	"hit": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-hit-right-phase-01_m8-prototype_20261014-144336-6dceafdc.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-hit-right-phase-02_m8-prototype_20261014-144336-3ef41921.png",
	],
	"down": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-down-right-phase-01_m8-prototype_20261014-144336-83576614.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-down-right-phase-02_m8-prototype_20261014-144336-6c28fccc.png",
	],
	"skill": [
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-skill-right-phase-01_m8-prototype_20261014-144336-a1587b37.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-skill-right-phase-02_m8-prototype_20261014-144336-23f8f2c9.png",
		"res://assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-skill-right-phase-03_m8-prototype_20261014-144336-1cb36aac.png",
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
