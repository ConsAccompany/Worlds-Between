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
	"zhao-ling": {
		"south": preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_zhao-ling_native-exploration-idle-south_m8-v01_20261014-142000-a9c9de72.png"),
		"west": preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_zhao-ling_native-exploration-idle-west_m8-v01_20261014-142000-e3e2513c.png"),
		"north": preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_zhao-ling_native-exploration-idle-north_m8-v01_20261014-142000-08ee8688.png"),
		"east": preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_zhao-ling_native-exploration-idle-east_m8-v01_20261014-142000-e9ef7e6e.png"),
	},
	"ji-cheng": {
		"south": preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_ji-cheng_native-idle-south-phase-00_m8-prototype_20261014-142157-13372e64.png"),
		"west": preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_ji-cheng_native-idle-west-phase-00_m8-prototype_20261014-142157-27adab1c.png"),
		"north": preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_ji-cheng_native-idle-north-phase-00_m8-prototype_20261014-142157-b0723fef.png"),
		"east": preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_ji-cheng_native-idle-east-phase-00_m8-prototype_20261014-142157-2ee5fd5c.png"),
	},
}


static func texture_for(character_id: String, direction: String) -> Texture2D:
	return TEXTURES[character_id][direction]
