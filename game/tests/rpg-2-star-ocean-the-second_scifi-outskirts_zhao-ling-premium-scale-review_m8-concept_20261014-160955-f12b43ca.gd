extends SceneTree

# Art-review screenshot only. Loads the real outskirts and repositions the native Zhao placeholder for scale comparison.
const CANDIDATE := "res://assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_zhao-ling_south-exploration-premium-pixel_m8-concept_20261014-160624-fe822f60.png"
const OUTPUT_DIR := "res://../outputs"
const TARGET_HEIGHT := 48.0
const SOURCE_FOOT := Vector2(570, 1484)
const SOURCE_TOP := 86.0
const CANDIDATE_FOOT := Vector2(315, 280)
const PLACEHOLDER_FOOT := Vector2(260, 280)


func _initialize() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("M8_ZHAO_PREMIUM_REVIEW: " + reason)
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


func _run() -> void:
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(1280, 720)
	var source := Image.new()
	if source.load(CANDIDATE) != OK:
		_fail("cannot load candidate")
		return
	SaveStore.root_path = "user://test-saves/m8-zhao-premium-scale-review"
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = "female"
	app.select_destination("scifi.outskirts")
	change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
	await process_frame
	await process_frame
	var area: Node2D = current_scene
	area.set_process(false)
	area.hero.visible = false
	area.field_npc.visible = true
	area.field_npc.position = PLACEHOLDER_FOOT
	area.field_npc.z_index = int(PLACEHOLDER_FOOT.y)
	area.npc_label.visible = false
	var shadow := Sprite2D.new()
	shadow.texture = _shadow_texture()
	shadow.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	shadow.position = CANDIDATE_FOOT + Vector2(0, -2)
	shadow.z_index = int(CANDIDATE_FOOT.y) - 1
	area.add_child(shadow)
	var sprite := Sprite2D.new()
	sprite.texture = ImageTexture.create_from_image(source)
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.position = CANDIDATE_FOOT
	sprite.offset = Vector2(source.get_width() * 0.5 - SOURCE_FOOT.x, source.get_height() * 0.5 - SOURCE_FOOT.y)
	sprite.scale = Vector2.ONE * (TARGET_HEIGHT / (SOURCE_FOOT.y - SOURCE_TOP))
	sprite.z_index = int(CANDIDATE_FOOT.y)
	area.add_child(sprite)
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var capture := root.get_viewport().get_texture().get_image()
	if capture == null or capture.get_size() != Vector2i(1280, 720):
		_fail("expected actual 1280x720 capture")
		return
	var output_path := ProjectSettings.globalize_path(OUTPUT_DIR)
	if DirAccess.make_dir_recursive_absolute(output_path) != OK:
		_fail("cannot make output directory")
		return
	var stamp := Time.get_datetime_string_from_system(false).replace("-", "").replace(":", "").replace("T", "-")
	var unique_id := "%08x" % randi()
	var stem := "rpg-2-star-ocean-the-second_scifi-outskirts_zhao-ling-premium-south-vs-native-h48_m8-concept_%s-%s" % [stamp, unique_id]
	var png_path := output_path.path_join(stem + ".png")
	if capture.save_png(png_path) != OK:
		_fail("cannot save screenshot")
		return
	var receipt := {
		"status": "technical and aesthetic review only; not approved",
		"candidate": CANDIDATE,
		"candidate_source_size": [source.get_width(), source.get_height()],
		"logical_canvas": [640, 360],
		"actual_capture_size": [capture.get_width(), capture.get_height()],
		"visible_height_logical_pixels": TARGET_HEIGHT,
		"candidate_source_foot": [SOURCE_FOOT.x, SOURCE_FOOT.y],
		"candidate_scene_foot": [CANDIDATE_FOOT.x, CANDIDATE_FOOT.y],
		"native_placeholder_scene_foot": [PLACEHOLDER_FOOT.x, PLACEHOLDER_FOOT.y],
		"shadow": "separate soft ellipse",
		"screenshot": png_path,
	}
	var json_path := output_path.path_join(stem + ".json")
	var file := FileAccess.open(json_path, FileAccess.WRITE)
	if file == null:
		_fail("cannot save receipt")
		return
	file.store_string(JSON.stringify(receipt, "\t"))
	file.close()
	print("CAPTURE " + png_path)
	print("RECEIPT " + json_path)
	quit(0)
