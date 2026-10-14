extends RefCounted

# Native 32x48 idle prototypes. These are four static facings, not walk cycles.
const TEXTURES := {
	"protagonist-male": {
		"south": preload("res://assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-male_native-idle-south_m8-v01_20261014-135316-4438515e.png"),
		"west": preload("res://assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-male_native-idle-west_m8-v01_20261014-135316-2d359882.png"),
		"north": preload("res://assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-male_native-idle-north_m8-v01_20261014-135316-2fa1bb39.png"),
		"east": preload("res://assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-male_native-idle-east_m8-v01_20261014-135316-a23d4672.png"),
	},
	"protagonist-female": {
		"south": preload("res://assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-female_native-idle-south_m8-prototype_20261014-135400-3bacea6e.png"),
		"west": preload("res://assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-female_native-idle-west_m8-prototype_20261014-135400-b023f47c.png"),
		"north": preload("res://assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-female_native-idle-north_m8-prototype_20261014-135400-daa6122c.png"),
		"east": preload("res://assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-female_native-idle-east_m8-prototype_20261014-135400-39d3f522.png"),
	},
	"liang-xu": {
		"south": preload("res://assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_liang-xu_native-idle-south_m8-v03_20261014-175132-e17b4c09.png"),
		"west": preload("res://assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_liang-xu_native-idle-west_m8-v03_20261014-175132-b52910e1.png"),
		"north": preload("res://assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_liang-xu_native-idle-north_m8-v03_20261014-175132-c742d602.png"),
		"east": preload("res://assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_liang-xu_native-idle-east_m8-v03_20261014-175132-d853a711.png"),
	},
}


static func texture_for(character_id: String, direction: String) -> Texture2D:
	return TEXTURES[character_id][direction]
