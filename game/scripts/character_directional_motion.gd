extends RefCounted

# Generated from native-animation manifests. These are prototypes, not accepted art.
const TEXTURES := {
	"protagonist-male": {
		"walk": {
			"south": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-walk-south-phase-01_m8-v01_20261014-141005-436af298.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-walk-south-phase-02_m8-v01_20261014-141005-29374e56.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-walk-south-phase-03_m8-v01_20261014-141005-5f38a7ce.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-walk-south-phase-04_m8-v01_20261014-141005-d2ec04a4.png")],
			"west": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-walk-west-phase-01_m8-v01_20261014-141005-fd273214.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-walk-west-phase-02_m8-v01_20261014-141005-3cbdbc31.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-walk-west-phase-03_m8-v01_20261014-141005-270ede32.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-walk-west-phase-04_m8-v01_20261014-141005-be3105ee.png")],
			"north": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-walk-north-phase-01_m8-v01_20261014-141005-f5b76ad0.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-walk-north-phase-02_m8-v01_20261014-141005-4edb9a49.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-walk-north-phase-03_m8-v01_20261014-141005-646b582b.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-walk-north-phase-04_m8-v01_20261014-141005-5fca84e8.png")],
			"east": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-walk-east-phase-01_m8-v01_20261014-141005-13409b7d.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-walk-east-phase-02_m8-v01_20261014-141005-e22e471c.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-walk-east-phase-03_m8-v01_20261014-141005-07c86cc5.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-walk-east-phase-04_m8-v01_20261014-141005-35f342a6.png")],
		},
		"attack": {
			"south": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-attack-south-phase-01_m8-v01_20261014-141005-9308d8f8.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-attack-south-phase-02_m8-v01_20261014-141005-2c79502f.png")],
		},
		"hit": {
			"south": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-hit-south-phase-01_m8-v01_20261014-141005-415fb87e.png")],
		},
	},
	"protagonist-female": {
		"walk": {
			"south": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-walk-south-phase-01_m8-prototype_20261014-140955-44edae33.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-walk-south-phase-02_m8-prototype_20261014-140955-8a297561.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-walk-south-phase-03_m8-prototype_20261014-140955-ba73f592.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-walk-south-phase-04_m8-prototype_20261014-140955-70d3f0b5.png")],
			"west": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-walk-west-phase-01_m8-prototype_20261014-140955-2dcfd7d6.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-walk-west-phase-02_m8-prototype_20261014-140955-0414ee00.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-walk-west-phase-03_m8-prototype_20261014-140955-ced52cdf.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-walk-west-phase-04_m8-prototype_20261014-140955-2c076f46.png")],
			"north": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-walk-north-phase-01_m8-prototype_20261014-140955-58596add.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-walk-north-phase-02_m8-prototype_20261014-140955-ed6fede0.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-walk-north-phase-03_m8-prototype_20261014-140955-3fb442f6.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-walk-north-phase-04_m8-prototype_20261014-140955-b2d5f22d.png")],
			"east": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-walk-east-phase-01_m8-prototype_20261014-140955-6f7850bb.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-walk-east-phase-02_m8-prototype_20261014-140955-e7004da9.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-walk-east-phase-03_m8-prototype_20261014-140955-bc4dbcc0.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-walk-east-phase-04_m8-prototype_20261014-140955-eed6c024.png")],
		},
		"attack": {
			"south": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-attack-south-phase-01_m8-prototype_20261014-140955-2ee405ad.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-attack-south-phase-02_m8-prototype_20261014-140955-e9f1aefe.png")],
		},
		"hit": {
			"south": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-hit-south-phase-01_m8-prototype_20261014-140955-07862d1f.png")],
		},
	},
	"liang-xu": {
		"walk": {
			"south": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-walk-south-phase-01_m8-v01_20261014-181000-31d26e44.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-walk-south-phase-02_m8-v01_20261014-181000-36b8a744.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-walk-south-phase-03_m8-v01_20261014-181000-05539097.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-walk-south-phase-04_m8-v01_20261014-181000-a7ab13df.png")],
			"west": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-walk-west-phase-01_m8-v01_20261014-181000-568f3554.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-walk-west-phase-02_m8-v01_20261014-181000-8459de6f.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-walk-west-phase-03_m8-v01_20261014-181000-46c7cffd.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-walk-west-phase-04_m8-v01_20261014-181000-0e3deeeb.png")],
			"north": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-walk-north-phase-01_m8-v01_20261014-181000-e39392dc.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-walk-north-phase-02_m8-v01_20261014-181000-25bacda0.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-walk-north-phase-03_m8-v01_20261014-181000-59c36846.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-walk-north-phase-04_m8-v01_20261014-181000-5eb6ac1c.png")],
			"east": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-walk-east-phase-01_m8-v01_20261014-181000-63772afa.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-walk-east-phase-02_m8-v01_20261014-181000-f79d911a.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-walk-east-phase-03_m8-v01_20261014-181000-a139d35b.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-walk-east-phase-04_m8-v01_20261014-181000-0989e6e0.png")],
		},
		"attack": {
			"south": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-attack-south-phase-01_m8-v01_20261014-181000-eb922dfd.png"), preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-attack-south-phase-02_m8-v01_20261014-181000-2137cf8b.png")],
		},
		"hit": {
			"south": [preload("res://assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-hit-south-phase-01_m8-v01_20261014-181000-40dea4d0.png")],
		},
	},
}


static func texture_for(character_id: String, action: String, direction: String, phase: int = 1) -> Texture2D:
	var actions: Dictionary = TEXTURES.get(character_id, {})
	var directions: Dictionary = actions.get(action, {})
	var frames: Array = directions.get(direction, [])
	if phase < 1 or phase > frames.size():
		return null
	return frames[phase - 1] as Texture2D
