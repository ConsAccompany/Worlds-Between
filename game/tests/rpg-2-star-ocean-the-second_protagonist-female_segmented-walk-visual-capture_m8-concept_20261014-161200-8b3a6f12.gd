extends SceneTree

# Temporary one-character rig experiment. It derives masks in memory from one
# source PNG. It does not write edited artwork or change production scenes.
const SOURCE := "res://assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-exploration-premium-pixel_m8-concept_20261014-145800-62c3a10f.png"
const SOURCE_ANCHOR := Vector2i(638, 1328)
const SOURCE_TOP := 47
const SOURCE_HEIGHT := 48.0
const LEFT_HIP := Vector2i(525, 805)
const RIGHT_HIP := Vector2i(675, 805)
const START_FOOT := Vector2(340, 213)
const TRAVEL_PER_FRAME := 5.0
const PHASE_HOLD := 0.10
const OUTPUT_DIR := "res://../outputs"

# Viewer-left leg carries the knee guard. The polygons crop the original
# artwork; pixel colors are unchanged. Torso keeps coat, scarf and backpack.
var LEFT_POLY := PackedVector2Array([
	Vector2(464, 763), Vector2(600, 765), Vector2(634, 850),
	Vector2(623, 940), Vector2(608, 1065), Vector2(595, 1200),
	Vector2(594, 1340), Vector2(401, 1340), Vector2(406, 1220),
	Vector2(422, 1070), Vector2(433, 915),
])
var RIGHT_POLY := PackedVector2Array([
	Vector2(592, 763), Vector2(719, 766), Vector2(723, 860),
	Vector2(747, 960), Vector2(792, 1100), Vector2(849, 1340),
	Vector2(649, 1340), Vector2(630, 1190), Vector2(622, 1050),
	Vector2(605, 890),
])


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


func _segment(source: Image) -> Dictionary:
	var torso: Image = source.duplicate()
	var left := Image.create_empty(source.get_width(), source.get_height(), false, Image.FORMAT_RGBA8)
	var right := Image.create_empty(source.get_width(), source.get_height(), false, Image.FORMAT_RGBA8)
	var left_count := 0
	var right_count := 0
	for y in range(763, source.get_height()):
		for x in range(390, 870):
			var color := source.get_pixel(x, y)
			if color.a < 0.01:
				continue
			var sample := Vector2(float(x) + 0.5, float(y) + 0.5)
			if Geometry2D.is_point_in_polygon(sample, LEFT_POLY):
				left.set_pixel(x, y, color)
				torso.set_pixel(x, y, Color.TRANSPARENT)
				left_count += 1
			elif Geometry2D.is_point_in_polygon(sample, RIGHT_POLY):
				right.set_pixel(x, y, color)
				torso.set_pixel(x, y, Color.TRANSPARENT)
				right_count += 1
	return {"torso": torso, "left": left, "right": right, "left_pixels": left_count, "right_pixels": right_count}


func _part(image: Image, pivot: Vector2i, z: int, city: Node2D, scale_factor: float) -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.texture = ImageTexture.create_from_image(image)
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.offset = Vector2(float(image.get_width()) * 0.5 - float(pivot.x), float(image.get_height()) * 0.5 - float(pivot.y))
	sprite.scale = Vector2.ONE * scale_factor
	sprite.z_index = z
	city.add_child(sprite)
	return sprite


func _run() -> void:
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(1280, 720)
	SaveStore.root_path = "user://test-saves/m8-female-segmented-walk-visual-only"
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
	var source := Image.new()
	if source.load(SOURCE) != OK:
		push_error("Could not load source")
		quit(1)
		return
	source.convert(Image.FORMAT_RGBA8)
	var pieces := _segment(source)
	var base_scale := SOURCE_HEIGHT / float(SOURCE_ANCHOR.y - SOURCE_TOP)
	var shadow := Sprite2D.new()
	shadow.texture = _shadow_texture()
	shadow.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	city.add_child(shadow)
	var right_leg := _part(pieces["right"], RIGHT_HIP, 251, city, base_scale)
	var left_leg := _part(pieces["left"], LEFT_HIP, 252, city, base_scale)
	var torso := _part(pieces["torso"], SOURCE_ANCHOR, 253, city, base_scale)
	var output_dir := ProjectSettings.globalize_path(OUTPUT_DIR)
	if DirAccess.make_dir_recursive_absolute(output_dir) != OK:
		push_error("Could not create output directory")
		quit(1)
		return
	var stamp := Time.get_datetime_string_from_system(false).replace("-", "").replace(":", "").replace("T", "-")
	var batch_id := "%08x" % randi()
	var receipts: Array[Dictionary] = []
	var left_angle := [-4.0, -2.0, 0.0, 2.0, 4.0, 2.0, 0.0, -2.0]
	var right_angle := [4.0, 2.0, 0.0, -2.0, -4.0, -2.0, 0.0, 2.0]
	var left_step := [0.9, 0.4, 0.0, -0.5, -0.9, -0.5, 0.0, 0.4]
	var right_step := [-0.9, -0.5, 0.0, 0.4, 0.9, 0.4, 0.0, -0.5]
	var bob := [0.0, -0.3, -0.6, -0.3, 0.0, -0.3, -0.6, -0.3]
	for i in 8:
		var foot := START_FOOT + Vector2(0, float(i) * TRAVEL_PER_FRAME)
		var torso_y: float = float(bob[i])
		torso.position = foot + Vector2(0, torso_y)
		torso.rotation = deg_to_rad(0.35 * sin(float(i) * PI / 2.0))
		left_leg.position = foot + Vector2(LEFT_HIP - SOURCE_ANCHOR) * base_scale + Vector2(0, float(left_step[i]))
		right_leg.position = foot + Vector2(RIGHT_HIP - SOURCE_ANCHOR) * base_scale + Vector2(0, float(right_step[i]))
		left_leg.rotation = deg_to_rad(float(left_angle[i]))
		right_leg.rotation = deg_to_rad(float(right_angle[i]))
		shadow.position = foot + Vector2(0, -2)
		shadow.scale = Vector2.ONE * (1.0 - absf(torso_y) * 0.04)
		shadow.z_index = int(foot.y) - 1
		right_leg.z_index = int(foot.y)
		left_leg.z_index = int(foot.y) + 1
		torso.z_index = int(foot.y) + 2
		await process_frame
		await RenderingServer.frame_post_draw
		var capture := root.get_viewport().get_texture().get_image()
		if capture.get_size() != Vector2i(1280, 720):
			push_error("Unexpected capture size")
			quit(1)
			return
		var stem := "rpg-2-star-ocean-the-second_protagonist-female_segmented-walk-phase-%02d_city-visual_m8-concept_%s-%s" % [i + 1, stamp, batch_id]
		var path := output_dir.path_join(stem + ".png")
		if capture.save_png(path) != OK:
			push_error("Could not save " + path)
			quit(1)
			return
		receipts.append({"phase": i + 1, "city_foot": [foot.x, foot.y], "left_angle": float(left_angle[i]), "right_angle": float(right_angle[i]), "left_step_y": float(left_step[i]), "right_step_y": float(right_step[i]), "capture": path})
		print("CAPTURE " + path)
		await create_timer(PHASE_HOLD).timeout
	var manifest_path := output_dir.path_join("rpg-2-star-ocean-the-second_protagonist-female_segmented-walk_city-visual-manifest_m8-concept_%s-%s.json" % [stamp, batch_id])
	var file := FileAccess.open(manifest_path, FileAccess.WRITE)
	if file == null:
		push_error("Could not write manifest")
		quit(1)
		return
	file.store_string(JSON.stringify({"status": "temporary same-source rig experiment; no production runtime", "source": SOURCE, "logical_height": SOURCE_HEIGHT, "render_mode": "canvas_items", "capture_size": [1280, 720], "phase_hold_seconds": PHASE_HOLD, "segmentation_pixels": {"viewer_left_leg": pieces["left_pixels"], "viewer_right_leg": pieces["right_pixels"]}, "phases": receipts}, "\t"))
	file.close()
	print("MANIFEST " + manifest_path)
	quit(0)
