extends SceneTree

# Temporary visual-only harness. It never edits production scenes or saves.
const CITY_FOOT := Vector2(340, 253)
const TARGET_HEIGHT := 48.0
const OUTPUT_DIR := "res://../outputs"
const PHASES := [
	{
		"name": "idle-01",
		"path": "res://assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-exploration-premium-pixel_m8-concept_20261014-145800-62c3a10f.png",
		"anchor": Vector2i(638, 1328),
		"top": 47,
	},
	{
		"name": "left-stride",
		"path": "res://assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-walk-left-stride-premium-pixel_m8-concept_20261014-152600-3cf71b09.png",
		"anchor": Vector2i(644, 1331),
		"top": 37,
	},
	{
		"name": "idle-02",
		"path": "res://assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-exploration-premium-pixel_m8-concept_20261014-145800-62c3a10f.png",
		"anchor": Vector2i(638, 1328),
		"top": 47,
	},
	{
		"name": "right-stride",
		"path": "res://assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-walk-right-stride-corrected-premium-pixel_m8-concept-v02_20261014-154600-e783af92.png",
		"anchor": Vector2i(533, 1338),
		"top": 36,
	},
]


func _initialize() -> void:
	call_deferred("_run")


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
	SaveStore.root_path = "user://test-saves/m8-female-walk-visual-only"
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
	var shadow := Sprite2D.new()
	shadow.texture = _shadow_texture()
	shadow.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	shadow.position = CITY_FOOT + Vector2(0, -2)
	shadow.z_index = int(CITY_FOOT.y) - 1
	city.add_child(shadow)
	var sprite := Sprite2D.new()
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.position = CITY_FOOT
	sprite.z_index = int(CITY_FOOT.y)
	city.add_child(sprite)
	var output_dir := ProjectSettings.globalize_path(OUTPUT_DIR)
	if DirAccess.make_dir_recursive_absolute(output_dir) != OK:
		push_error("Could not create output directory")
		quit(1)
		return
	var stamp := Time.get_datetime_string_from_system(false).replace("-", "").replace(":", "").replace("T", "-")
	var batch_id := "%08x" % randi()
	var receipt: Array[Dictionary] = []
	for i in PHASES.size():
		var phase: Dictionary = PHASES[i]
		var source := Image.new()
		if source.load(str(phase["path"])) != OK:
			push_error("Could not load " + str(phase["path"]))
			quit(1)
			return
		var anchor: Vector2i = phase["anchor"]
		var figure_height: int = anchor.y - int(phase["top"])
		var scale_factor := TARGET_HEIGHT / float(figure_height)
		sprite.texture = ImageTexture.create_from_image(source)
		sprite.offset = Vector2(float(source.get_width()) * 0.5 - float(anchor.x), float(source.get_height()) * 0.5 - float(anchor.y))
		sprite.scale = Vector2.ONE * scale_factor
		await process_frame
		await RenderingServer.frame_post_draw
		var capture := root.get_viewport().get_texture().get_image()
		if capture.get_size() != Vector2i(1280, 720):
			push_error("Unexpected capture size: " + str(capture.get_size()))
			quit(1)
			return
		var stem := "rpg-2-star-ocean-the-second_protagonist-female_south-walk-phase-%02d-%s_city-visual_m8-concept_%s-%s" % [i + 1, phase["name"], stamp, batch_id]
		var capture_path := output_dir.path_join(stem + ".png")
		if capture.save_png(capture_path) != OK:
			push_error("Could not save " + capture_path)
			quit(1)
			return
		receipt.append({"phase": phase["name"], "source": phase["path"], "anchor": [anchor.x, anchor.y], "scale": scale_factor, "capture": capture_path})
		print("CAPTURE " + capture_path)
		await create_timer(0.16).timeout
	var receipt_path := output_dir.path_join("rpg-2-star-ocean-the-second_protagonist-female_south-walk-cycle_city-visual-manifest_m8-concept_%s-%s.json" % [stamp, batch_id])
	var receipt_file := FileAccess.open(receipt_path, FileAccess.WRITE)
	if receipt_file == null:
		push_error("Could not write visual manifest")
		quit(1)
		return
	receipt_file.store_string(JSON.stringify({"status": "visual feasibility only; no runtime animation", "logical_height": TARGET_HEIGHT, "render_mode": "canvas_items", "capture_size": [1280, 720], "city_foot": [CITY_FOOT.x, CITY_FOOT.y], "phase_hold_seconds": 0.16, "phases": receipt}, "\t"))
	receipt_file.close()
	print("MANIFEST " + receipt_path)
	quit(0)
