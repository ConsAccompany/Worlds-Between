extends SceneTree

# One-candidate visual review harness. No production scene, art, or save is edited.
# Godot --path game --script res://tests/<this-file>.gd -- --candidate=res://...png --label=male --height=76 --anchor-x=48 --anchor-y=104
const OUTPUT_DIR := "res://../outputs"
const FOOT := Vector2(340, 253)
const ALPHA_THRESHOLD := 64

var options: Dictionary = {}


func _initialize() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("M8_CHARACTER_QUALITY_REVIEW: " + reason)
	quit(1)


func _read_options() -> bool:
	for argument: String in OS.get_cmdline_user_args():
		if not argument.begins_with("--") or not argument.contains("="):
			return false
		var parts := argument.substr(2).split("=", false, 1)
		options[parts[0]] = parts[1]
	return options.has("candidate") and options.has("label")


func _safe_label(label: String) -> bool:
	if label.is_empty():
		return false
	for index in label.length():
		var character := label.unicode_at(index)
		if not ((character >= 97 and character <= 122) or (character >= 48 and character <= 57) or character == 45):
			return false
	return true


func _alpha_metrics(image: Image) -> Dictionary:
	var width := image.get_width()
	var height := image.get_height()
	var bytes := image.get_data()
	var left := width
	var top := height
	var right := -1
	var bottom := -1
	var transparent := 0
	var partial := 0
	var solid := 0
	var low_alpha := 0
	var middle_alpha := 0
	var near_opaque := 0
	var border_content := 0
	for y in height:
		for x in width:
			var alpha: int = bytes[(y * width + x) * 4 + 3]
			if alpha == 0:
				transparent += 1
			else:
				if alpha < 255:
					partial += 1
				else:
					solid += 1
				if alpha < 64:
					low_alpha += 1
				elif alpha < 248:
					middle_alpha += 1
				else:
					near_opaque += 1
			if alpha >= ALPHA_THRESHOLD:
				left = mini(left, x)
				top = mini(top, y)
				right = maxi(right, x)
				bottom = maxi(bottom, y)
				if x == 0 or y == 0 or x == width - 1 or y == height - 1:
					border_content += 1
	return {
		"bounds": [left, top, right, bottom],
		"transparent_pixels": transparent,
		"partial_alpha_pixels": partial,
		"solid_pixels": solid,
		"low_alpha_1_to_63_pixels": low_alpha,
		"middle_alpha_64_to_247_pixels": middle_alpha,
		"near_opaque_248_to_255_pixels": near_opaque,
		"content_pixels_on_canvas_edge": border_content,
		"threshold": ALPHA_THRESHOLD,
	}


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
	if not _read_options():
		_fail("provide --candidate=<one PNG> and --label=<lowercase-hyphenated-name>")
		return
	var candidate: String = str(options["candidate"])
	var label: String = str(options["label"])
	if not _safe_label(label) or not candidate.to_lower().ends_with(".png"):
		_fail("label must use lowercase letters/digits/hyphens and candidate must be PNG")
		return
	var target_height := int(str(options.get("height", "76")))
	if target_height < 48 or target_height > 96:
		_fail("height must be 48..96 logical pixels; select the comparison target deliberately")
		return
	var render_mode: String = str(options.get("render-mode", "viewport"))
	var show_npc := str(options.get("show-npc", "false")) == "true"
	if render_mode != "viewport" and render_mode != "canvas-items":
		_fail("render-mode must be viewport or canvas-items")
		return
	# Explicit process-local mode makes paired captures independent of project.godot.
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS if render_mode == "canvas-items" else Window.CONTENT_SCALE_MODE_VIEWPORT
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(1280, 720)
	var image := Image.new()
	if image.load(candidate) != OK:
		_fail("cannot load candidate PNG: " + candidate)
		return
	image.convert(Image.FORMAT_RGBA8)
	var anchor_x := int(str(options.get("anchor-x", str(image.get_width() / 2))))
	var anchor_y := int(str(options.get("anchor-y", str(image.get_height() - 8))))
	if anchor_x < 0 or anchor_x >= image.get_width() or anchor_y < 0 or anchor_y >= image.get_height():
		_fail("foot anchor must be inside candidate image")
		return
	var metrics := _alpha_metrics(image)
	var bounds: Array = metrics["bounds"]
	if metrics["transparent_pixels"] == 0 or bounds[2] < 0:
		_fail("candidate needs a visible figure and real transparency")
		return
	var figure_height := anchor_y - int(bounds[1])
	if figure_height <= 0:
		_fail("foot anchor must be below the figure top")
		return
	var scale_factor := float(target_height) / float(figure_height)
	var warnings: Array[String] = []
	if int(metrics["content_pixels_on_canvas_edge"]) > 0:
		warnings.append("Figure touches PNG canvas edge; check clipping or alpha fringe.")
	if int(bounds[3]) > anchor_y + 2:
		warnings.append("Visible pixels extend below foot anchor; check built-in shadow or foot placement.")
	if float(anchor_y - int(bounds[3])) * scale_factor > 2.0:
		warnings.append("Figure ends over two logical pixels above foot anchor; check low-alpha fringe or foot placement.")
	if target_height > 80:
		warnings.append("Above current 48..80px diagnostic comparison band.")
	SaveStore.root_path = "user://test-saves/m8-character-quality-review"
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = "female" if label.contains("female") else "male"
	app.select_destination("scifi.city")
	change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
	await process_frame
	await process_frame
	var city: Node2D = current_scene
	city.set_process(false)
	city.get("hero").visible = false
	var native_liang: Sprite2D = city.get("city_npc")
	native_liang.visible = show_npc
	if show_npc:
		# Same foot plane, clear of the city's trace label on the left.
		native_liang.position = Vector2(390, FOOT.y)
		native_liang.z_index = int(FOOT.y)
	city.get("npc_label").visible = false
	city.get("city_hero_silhouette").visible = false
	var shadow := Sprite2D.new()
	shadow.texture = _shadow_texture()
	shadow.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	shadow.position = FOOT + Vector2(0, -2)
	shadow.z_index = int(FOOT.y) - 1
	city.add_child(shadow)
	var sprite := Sprite2D.new()
	sprite.texture = ImageTexture.create_from_image(image)
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.position = FOOT
	sprite.offset = Vector2(image.get_width() * 0.5 - anchor_x, image.get_height() * 0.5 - anchor_y)
	sprite.scale = Vector2.ONE * scale_factor
	sprite.z_index = int(FOOT.y)
	city.add_child(sprite)
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var capture := root.get_viewport().get_texture().get_image()
	var expected_size := Vector2i(1280, 720) if render_mode == "canvas-items" else Vector2i(640, 360)
	if capture == null or capture.get_size() != expected_size:
		_fail("unexpected city render size: expected " + str(expected_size) + ", got " + str(capture.get_size() if capture != null else Vector2i.ZERO))
		return
	var output_path := ProjectSettings.globalize_path(OUTPUT_DIR)
	if DirAccess.make_dir_recursive_absolute(output_path) != OK:
		_fail("cannot make output directory")
		return
	var stamp := Time.get_datetime_string_from_system(false).replace("-", "").replace(":", "").replace("T", "-")
	var unique_id := "%08x" % randi()
	var context := "-with-liang" if show_npc else ""
	var stem := "rpg-2-star-ocean-the-second_scifi-city_%s-character-quality-h%02d-%s%s_m8-v02_%s-%s" % [label, target_height, render_mode, context, stamp, unique_id]
	var capture_path := output_path.path_join(stem + ".png")
	if capture.save_png(capture_path) != OK:
		_fail("cannot save city capture")
		return
	var receipt := {
		"status": "technical review only; visual acceptance pending",
		"candidate": candidate,
		"candidate_size": [image.get_width(), image.get_height()],
		"visible_figure_height_source_pixels": figure_height,
		"requested_visible_height_logical_pixels": target_height,
		"scale": scale_factor,
		"foot_anchor_source_pixels": [anchor_x, anchor_y],
		"foot_anchor_city_pixels": [FOOT.x, FOOT.y],
		"alpha_metrics": metrics,
		"warnings": warnings,
		"shadow": "separate procedural soft ellipse 40x14",
		"texture_filter": "nearest (figure), linear (shadow and city)",
		"render_mode": render_mode,
		"show_native_liang_at_same_ground_y": show_npc,
		"logical_content_size": [640, 360],
		"capture_size": [capture.get_width(), capture.get_height()],
		"capture": capture_path,
	}
	var receipt_path := output_path.path_join(stem + ".json")
	var file := FileAccess.open(receipt_path, FileAccess.WRITE)
	if file == null:
		_fail("cannot save review receipt")
		return
	file.store_string(JSON.stringify(receipt, "\t"))
	file.close()
	print("CAPTURE " + capture_path)
	print("RECEIPT " + receipt_path)
	for warning in warnings:
		print("REVIEW_WARNING " + warning)
	quit(0)
