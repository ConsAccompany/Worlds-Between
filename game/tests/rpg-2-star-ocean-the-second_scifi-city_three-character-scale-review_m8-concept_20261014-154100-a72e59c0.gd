extends SceneTree

# Disjoint art-review capture. It never changes the production city scene.
const OUTPUT_DIR := "res://../outputs"
const TARGET_HEIGHT := 48.0
const GROUND_Y := 253.0
const ACTORS := [
	{
		"name": "protagonist-male",
		"path": "res://assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-male_south-exploration-premium-pixel_m8-v02_20261014-190703-746cf39d.png",
		"foot": Vector2(575, 1352), "top": 48, "city_x": 285.0,
	},
	{
		"name": "protagonist-female",
		"path": "res://assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-exploration-premium-pixel_m8-concept_20261014-145800-62c3a10f.png",
		"foot": Vector2(638, 1328), "top": 47, "city_x": 340.0,
	},
	{
		"name": "liang-xu",
		"path": "res://assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_liang-xu_south-exploration-premium-pixel_m8-concept_20261014-153531-4c6e2bcd.png",
		"foot": Vector2(560, 1486), "top": 83, "city_x": 395.0,
	},
]


func _initialize() -> void:
	call_deferred("_capture")


func _fail(reason: String) -> void:
	push_error("M8_THREE_CHARACTER_REVIEW: " + reason)
	quit(1)


func _shadow_texture() -> ImageTexture:
	var image := Image.create_empty(40, 14, false, Image.FORMAT_RGBA8)
	for y in 14:
		for x in 40:
			var nx := (float(x) + 0.5 - 20.0) / 20.0
			var ny := (float(y) + 0.5 - 7.0) / 7.0
			var weight := maxf(0.0, 1.0 - nx * nx - ny * ny)
			image.set_pixel(x, y, Color(0.06, 0.09, 0.10, weight * weight * 0.28))
	return ImageTexture.create_from_image(image)


func _capture() -> void:
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(1280, 720)
	SaveStore.root_path = "user://test-saves/m8-three-character-review"
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = "female"
	app.select_destination("scifi.city")
	change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
	await process_frame
	await process_frame
	var city: Node2D = current_scene
	city.set_process(false)
	city.get("hero").visible = false
	city.get("city_npc").visible = false
	city.get("npc_label").visible = false
	city.get("city_hero_silhouette").visible = false
	var shadow_texture := _shadow_texture()
	for actor: Dictionary in ACTORS:
		var image := Image.new()
		if image.load(actor["path"]) != OK:
			_fail("cannot load " + actor["path"])
			return
		var foot: Vector2 = actor["foot"]
		var scale_factor: float = TARGET_HEIGHT / (foot.y - float(actor["top"]))
		var position := Vector2(float(actor["city_x"]), GROUND_Y)
		var shadow := Sprite2D.new()
		shadow.texture = shadow_texture
		shadow.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		shadow.position = position + Vector2(0, -2)
		shadow.z_index = int(GROUND_Y) - 1
		city.add_child(shadow)
		var sprite := Sprite2D.new()
		sprite.texture = ImageTexture.create_from_image(image)
		sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		sprite.position = position
		sprite.offset = Vector2(image.get_width() * 0.5 - foot.x, image.get_height() * 0.5 - foot.y)
		sprite.scale = Vector2.ONE * scale_factor
		sprite.z_index = int(GROUND_Y)
		city.add_child(sprite)
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var capture := root.get_viewport().get_texture().get_image()
	if capture == null or capture.get_size() != Vector2i(1280, 720):
		_fail("expected actual 1280x720 screenshot")
		return
	var output_path := ProjectSettings.globalize_path(OUTPUT_DIR)
	if DirAccess.make_dir_recursive_absolute(output_path) != OK:
		_fail("cannot create output directory")
		return
	var stamp := Time.get_datetime_string_from_system(false).replace("-", "").replace(":", "").replace("T", "-")
	var unique_id := "%08x" % randi()
	var stem := "rpg-2-star-ocean-the-second_scifi-city_liang-xu-male-female-south-scale-review_m8-concept_%s-%s" % [stamp, unique_id]
	var capture_path := output_path.path_join(stem + ".png")
	if capture.save_png(capture_path) != OK:
		_fail("cannot save screenshot")
		return
	print("CAPTURE " + capture_path)
	quit(0)
