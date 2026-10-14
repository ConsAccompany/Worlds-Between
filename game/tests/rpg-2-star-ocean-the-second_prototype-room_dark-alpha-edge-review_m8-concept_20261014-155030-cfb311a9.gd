extends SceneTree

# Reversible art QA in the project's existing dark prototype room.
# Godot --path game --script res://tests/<this-file>.gd -- --candidate=res://...png --label=name --anchor-x=0 --anchor-y=0
const OUTPUT_DIR := "res://../outputs"
const FOOT := Vector2(320, 270)
const TARGET_HEIGHT := 48.0
const ALPHA_THRESHOLD := 64

var options: Dictionary = {}


func _initialize() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("M8_DARK_ALPHA_REVIEW: " + reason)
	quit(1)


func _read_options() -> bool:
	for argument: String in OS.get_cmdline_user_args():
		if not argument.begins_with("--") or not argument.contains("="):
			return false
		var parts := argument.substr(2).split("=", false, 1)
		options[parts[0]] = parts[1]
	return options.has("candidate") and options.has("label") and options.has("anchor-x") and options.has("anchor-y")


func _safe_label(label: String) -> bool:
	if label.is_empty():
		return false
	for index in label.length():
		var character := label.unicode_at(index)
		if not ((character >= 97 and character <= 122) or (character >= 48 and character <= 57) or character == 45):
			return false
	return true


func _shadow_texture() -> ImageTexture:
	var image := Image.create_empty(40, 14, false, Image.FORMAT_RGBA8)
	for y in 14:
		for x in 40:
			var nx := (float(x) + 0.5 - 20.0) / 20.0
			var ny := (float(y) + 0.5 - 7.0) / 7.0
			var weight := maxf(0.0, 1.0 - nx * nx - ny * ny)
			image.set_pixel(x, y, Color(0.03, 0.05, 0.06, weight * weight * 0.28))
	return ImageTexture.create_from_image(image)


func _run() -> void:
	if not _read_options():
		_fail("provide candidate, label, anchor-x, anchor-y")
		return
	var candidate: String = str(options["candidate"])
	var label: String = str(options["label"])
	if not _safe_label(label) or not candidate.to_lower().ends_with(".png"):
		_fail("unsafe label or candidate is not PNG")
		return
	var image := Image.new()
	if image.load(candidate) != OK:
		_fail("cannot load " + candidate)
		return
	image.convert(Image.FORMAT_RGBA8)
	var anchor := Vector2i(int(str(options["anchor-x"])), int(str(options["anchor-y"])))
	if anchor.x < 0 or anchor.x >= image.get_width() or anchor.y < 0 or anchor.y >= image.get_height():
		_fail("invalid foot anchor")
		return
	var top := image.get_height()
	var low_alpha := 0
	var detached_low_alpha := 0
	for y in image.get_height():
		for x in image.get_width():
			var a := image.get_pixel(x, y).a8
			if a >= ALPHA_THRESHOLD:
				top = mini(top, y)
			elif a > 0:
				low_alpha += 1
				if x < 100 or x > image.get_width() - 101 or y < 30 or y > image.get_height() - 31:
					detached_low_alpha += 1
	if top >= anchor.y:
		_fail("no visible subject above foot anchor")
		return
	var scale_factor := TARGET_HEIGHT / float(anchor.y - top)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(1280, 720)
	change_scene_to_file("res://scenes/prototype_room.tscn")
	await process_frame
	await process_frame
	var room: Node2D = current_scene
	room.set_process(false)
	room.hero.visible = false
	var shadow := Sprite2D.new()
	shadow.texture = _shadow_texture()
	shadow.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	shadow.position = FOOT + Vector2(0, -2)
	room.add_child(shadow)
	var sprite := Sprite2D.new()
	sprite.texture = ImageTexture.create_from_image(image)
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.position = FOOT
	sprite.offset = Vector2(image.get_width() * 0.5 - anchor.x, image.get_height() * 0.5 - anchor.y)
	sprite.scale = Vector2.ONE * scale_factor
	room.add_child(sprite)
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var capture := root.get_viewport().get_texture().get_image()
	if capture == null or capture.get_size() != Vector2i(1280, 720):
		_fail("capture must be actual 1280x720")
		return
	var output_path := ProjectSettings.globalize_path(OUTPUT_DIR)
	if DirAccess.make_dir_recursive_absolute(output_path) != OK:
		_fail("cannot create output directory")
		return
	var stamp := Time.get_datetime_string_from_system(false).replace("-", "").replace(":", "").replace("T", "-")
	var id := "%08x" % randi()
	var stem := "rpg-2-star-ocean-the-second_prototype-room_%s-dark-alpha-edge-h48_m8-concept_%s-%s" % [label, stamp, id]
	var png_path := output_path.path_join(stem + ".png")
	if capture.save_png(png_path) != OK:
		_fail("cannot write PNG")
		return
	var receipt := {
		"status": "technical art QA only; not approval",
		"candidate": candidate,
		"background_scene": "res://scenes/prototype_room.tscn",
		"background_note": "Existing dark teal underground prototype room; figure stands on #28434a floor and #33545c grid.",
		"logical_canvas": [640, 360],
		"actual_capture": [capture.get_width(), capture.get_height()],
		"target_visible_height_logical_pixels": TARGET_HEIGHT,
		"foot_anchor_source_pixels": [anchor.x, anchor.y],
		"foot_anchor_scene_pixels": [FOOT.x, FOOT.y],
		"scale": scale_factor,
		"low_alpha_1_to_63_source_pixels": low_alpha,
		"low_alpha_near_canvas_border_source_pixels": detached_low_alpha,
		"texture_filter": "nearest for character, linear for separate shadow",
		"png": png_path,
	}
	var json_path := output_path.path_join(stem + ".json")
	var file := FileAccess.open(json_path, FileAccess.WRITE)
	if file == null:
		_fail("cannot write JSON")
		return
	file.store_string(JSON.stringify(receipt, "\t"))
	file.close()
	print("CAPTURE " + png_path)
	print("RECEIPT " + json_path)
	quit(0)
