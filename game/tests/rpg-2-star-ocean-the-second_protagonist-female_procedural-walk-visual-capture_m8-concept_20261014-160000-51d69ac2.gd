extends SceneTree

# Temporary visual-only test of translating one static image. No production scene edit.
const SOURCE := "res://assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-exploration-premium-pixel_m8-concept_20261014-145800-62c3a10f.png"
const SOURCE_ANCHOR := Vector2i(638, 1328)
const SOURCE_TOP := 47
const HEIGHT := 48.0
const START_FOOT := Vector2(316, 253)
const TRAVEL_PER_FRAME := 6.0
const PHASE_HOLD := 0.09
const OUTPUT_DIR := "res://../outputs"


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
	SaveStore.root_path = "user://test-saves/m8-female-procedural-walk-visual-only"
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
	var image := Image.new()
	if image.load(SOURCE) != OK:
		push_error("Could not load source")
		quit(1)
		return
	var base_scale := HEIGHT / float(SOURCE_ANCHOR.y - SOURCE_TOP)
	var sprite := Sprite2D.new()
	sprite.texture = ImageTexture.create_from_image(image)
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.offset = Vector2(float(image.get_width()) * 0.5 - float(SOURCE_ANCHOR.x), float(image.get_height()) * 0.5 - float(SOURCE_ANCHOR.y))
	sprite.scale = Vector2.ONE * base_scale
	sprite.z_index = 253
	city.add_child(sprite)
	var shadow := Sprite2D.new()
	shadow.texture = _shadow_texture()
	shadow.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	shadow.z_index = 252
	city.add_child(shadow)
	var output_dir := ProjectSettings.globalize_path(OUTPUT_DIR)
	if DirAccess.make_dir_recursive_absolute(output_dir) != OK:
		push_error("Could not create output directory")
		quit(1)
		return
	var stamp := Time.get_datetime_string_from_system(false).replace("-", "").replace(":", "").replace("T", "-")
	var batch_id := "%08x" % randi()
	var receipt: Array[Dictionary] = []
	var bob := [0.0, -0.45, -0.9, -0.45, 0.0, -0.45, -0.9, -0.45]
	var tilt := [-0.7, 0.0, 0.7, 0.0, 0.7, 0.0, -0.7, 0.0]
	for i in 8:
		var foot := START_FOOT + Vector2(float(i) * TRAVEL_PER_FRAME, 0)
		sprite.position = foot + Vector2(0, float(bob[i]))
		sprite.rotation = deg_to_rad(float(tilt[i]))
		shadow.position = foot + Vector2(0, -2)
		shadow.scale = Vector2(1.0 - absf(float(bob[i])) * 0.06, 1.0 - absf(float(bob[i])) * 0.04)
		shadow.modulate.a = 1.0 - absf(float(bob[i])) * 0.18
		await process_frame
		await RenderingServer.frame_post_draw
		var capture := root.get_viewport().get_texture().get_image()
		if capture.get_size() != Vector2i(1280, 720):
			push_error("Unexpected capture size: " + str(capture.get_size()))
			quit(1)
			return
		var stem := "rpg-2-star-ocean-the-second_protagonist-female_procedural-walk-phase-%02d_city-visual_m8-concept_%s-%s" % [i + 1, stamp, batch_id]
		var path := output_dir.path_join(stem + ".png")
		if capture.save_png(path) != OK:
			push_error("Could not save " + path)
			quit(1)
			return
		receipt.append({"phase": i + 1, "city_foot": [foot.x, foot.y], "bob_y": float(bob[i]), "tilt_degrees": float(tilt[i]), "capture": path})
		print("CAPTURE " + path)
		await create_timer(PHASE_HOLD).timeout
	var manifest_path := output_dir.path_join("rpg-2-star-ocean-the-second_protagonist-female_procedural-walk_city-visual-manifest_m8-concept_%s-%s.json" % [stamp, batch_id])
	var manifest_file := FileAccess.open(manifest_path, FileAccess.WRITE)
	if manifest_file == null:
		push_error("Could not write manifest")
		quit(1)
		return
	manifest_file.store_string(JSON.stringify({"status": "visual feasibility only; static source without leg motion", "source": SOURCE, "logical_height": HEIGHT, "source_anchor": [SOURCE_ANCHOR.x, SOURCE_ANCHOR.y], "source_top": SOURCE_TOP, "base_scale": base_scale, "render_mode": "canvas_items", "capture_size": [1280, 720], "phase_hold_seconds": PHASE_HOLD, "travel_per_frame": TRAVEL_PER_FRAME, "phases": receipt}, "\t"))
	manifest_file.close()
	print("MANIFEST " + manifest_path)
	quit(0)
