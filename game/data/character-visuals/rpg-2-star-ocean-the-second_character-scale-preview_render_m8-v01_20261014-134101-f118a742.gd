extends SceneTree

# Review renderer only. Each output is a separate, unaltered 640x360 Godot frame.
const CITY := "res://assets/environments/rpg-2-star-ocean-the-second_scifi-city_environment-background_m8-v02_20261013-232003-48d0ab67.png"
const CASES := [
	{
		"id": "protagonist-male",
		"source": "res://assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_protagonist-male_exploration-sprite-south_m8-draft_20261014-133644-a01be730.png",
		"region": Rect2(208, 136, 596, 1291),
		"output": "res://assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_protagonist-male_legibility-preview-40px-nearest_m8-v02_20261014-135136-a77c0a86.png",
		"linear_output": "res://assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_protagonist-male_legibility-preview-40px-linear_m8-v02_20261014-135136-a88d1b97.png",
	},
	{
		"id": "protagonist-female",
		"source": "res://assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_protagonist-female_exploration-sprite-south_m8-draft_20261014-133644-b02ce841.png",
		"region": Rect2(134, 122, 681, 1315),
		"output": "res://assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_protagonist-female_legibility-preview-40px-nearest_m8-v02_20261014-135136-b99e2ca8.png",
		"linear_output": "res://assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_protagonist-female_legibility-preview-40px-linear_m8-v02_20261014-135136-baae3db9.png",
	},
	{
		"id": "liang-xu",
		"source": "res://assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_liang-xu_exploration-sprite-south_m8-draft_20261014-133644-c03dfa52.png",
		"region": Rect2(222, 123, 566, 1323),
		"output": "res://assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_liang-xu_legibility-preview-40px-nearest_m8-v02_20261014-135136-cbbf4eca.png",
		"linear_output": "res://assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_liang-xu_legibility-preview-40px-linear_m8-v02_20261014-135136-cccf5fdb.png",
	},
]


func _initialize() -> void:
	call_deferred("_render_cases")


func _render_cases() -> void:
	for sample in CASES:
		var stage := Control.new()
		stage.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		root.add_child(stage)

		var background := Sprite2D.new()
		background.texture = load(CITY)
		background.position = Vector2(320, 180)
		background.scale = Vector2(640.0 / background.texture.get_width(), 360.0 / background.texture.get_height())
		background.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		stage.add_child(background)

		var source_texture: Texture2D = load(sample.source)
		if source_texture == null:
			push_error("Missing source: " + sample.source)
			quit(1)
			return
		var atlas := AtlasTexture.new()
		atlas.atlas = source_texture
		atlas.region = sample.region
		var sprite := Sprite2D.new()
		sprite.texture = atlas
		sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		var scale_factor: float = 40.0 / sample.region.size.y
		sprite.scale = Vector2(scale_factor, scale_factor)
		sprite.position = Vector2(320, 240 - 20)
		stage.add_child(sprite)

		for frame in range(8):
			await process_frame
		var capture := root.get_viewport().get_texture().get_image()
		if capture == null or (not FileAccess.file_exists(sample.output) and capture.save_png(sample.output) != OK):
			push_error("Capture failed: " + sample.output)
			quit(1)
			return
		print("CAPTURED ", sample.id, " ", ProjectSettings.globalize_path(sample.output))
		sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		for frame in range(8):
			await process_frame
		var linear_capture := root.get_viewport().get_texture().get_image()
		if linear_capture == null or (not FileAccess.file_exists(sample.linear_output) and linear_capture.save_png(sample.linear_output) != OK):
			push_error("Capture failed: " + sample.linear_output)
			quit(1)
			return
		print("CAPTURED linear ", sample.id, " ", ProjectSettings.globalize_path(sample.linear_output))
		stage.queue_free()
		await process_frame
	quit(0)
