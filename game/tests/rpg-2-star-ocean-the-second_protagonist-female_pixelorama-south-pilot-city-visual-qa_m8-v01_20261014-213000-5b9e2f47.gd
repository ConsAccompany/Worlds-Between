extends Node

# Isolated visual QA: one unapproved Pixelorama south-idle pilot PNG beside the current
# 32x48 female gameplay placeholder in the science city. Review only — not art approval.
# No runtime script, scene, asset, or save is edited; saves are redirected to a test path.
# Run windowed (headless render capture can hang):
# Godot_v4.7.2-stable_win64_console.exe --path game res://tests/<this-scene>.tscn -- --pilot=downscale
# Pass --pilot=handpolish for the hand-polished pilot; each run writes one standalone capture.
# --pilot=boxquant / --pilot=lanczosquant select the 80x112 quantized-downscale experiments.
const PILOT_DIR := "res://assets/characters/pixelorama-pilots/"
const PILOT_PATHS := {
	"downscale": PILOT_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-downscale-pilot_m8-v01_20261014-210343-c45a80e2.png",
	"handpolish": PILOT_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-handpolish-pilot_m8-v01_20261014-210652-438e6fb3.png",
	"boxquant": PILOT_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-boxquant-pilot_m8-v01_20261014-212322-7c30d48c.png",
	"lanczosquant": PILOT_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-lanczosquant-pilot_m8-v01_20261014-212322-b9fd58f7.png",
}
const DEFAULT_VARIANT := "downscale"
const CITY_SCENE := "res://scenes/scifi_exploration_area.tscn"
const OUTPUT_DIR := "res://../outputs"
const TARGET_HEIGHT := 48
const PILOT_GAP := 36.0
const ALPHA_THRESHOLD := 128


func _ready() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("M8_PIXELORAMA_PILOT_CITY_QA: " + reason)
	get_tree().quit(1)


func _pilot_variant() -> String:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--pilot="):
			return arg.trim_prefix("--pilot=")
	return DEFAULT_VARIANT


func _alpha_bounds(image: Image) -> Rect2i:
	var left := image.get_width()
	var top := image.get_height()
	var right := -1
	var bottom := -1
	for y in image.get_height():
		for x in image.get_width():
			if image.get_pixel(x, y).a8 >= ALPHA_THRESHOLD:
				left = mini(left, x)
				top = mini(top, y)
				right = maxi(right, x)
				bottom = maxi(bottom, y)
	if right < 0:
		return Rect2i()
	return Rect2i(left, top, right - left + 1, bottom - top + 1)


func _run() -> void:
	var variant := _pilot_variant()
	if not PILOT_PATHS.has(variant):
		_fail("unknown --pilot=%s (expected one of %s)" % [variant, str(PILOT_PATHS.keys())])
		return
	var window := get_tree().root
	window.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	window.content_scale_size = Vector2i(640, 360)
	window.size = Vector2i(1280, 720)
	# Load from disk so the pilot does not need a Godot import entry.
	var pilot_image := Image.new()
	if pilot_image.load(ProjectSettings.globalize_path(PILOT_PATHS[variant])) != OK:
		_fail("cannot load pilot PNG")
		return
	pilot_image.convert(Image.FORMAT_RGBA8)
	var pilot_bounds := _alpha_bounds(pilot_image)
	if pilot_bounds.size.y <= 0:
		_fail("pilot has no visible pixels")
		return
	SaveStore.root_path = "user://test-saves/m8-pixelorama-pilot-city-qa"
	var app: Node = get_node("/root/AppState")
	app.begin_new_run()
	app.hero_appearance = "female"
	app.select_destination("scifi.city")
	var city: Node2D = (load(CITY_SCENE) as PackedScene).instantiate()
	add_child(city)
	await get_tree().process_frame
	await get_tree().process_frame
	city.set_process(false)
	var hero: Sprite2D = city.get("hero")
	var placeholder_image := hero.texture.get_image()
	placeholder_image.convert(Image.FORMAT_RGBA8)
	var placeholder_bounds := _alpha_bounds(placeholder_image)
	# Ground row of the placeholder's lowest opaque pixel, in city logical pixels.
	var texture_top := hero.position.y + hero.offset.y - placeholder_image.get_height() * 0.5
	var ground_y := texture_top + placeholder_bounds.end.y
	var scale_factor := float(TARGET_HEIGHT) / float(pilot_bounds.size.y)
	var pilot_foot_x := pilot_bounds.position.x + pilot_bounds.size.x * 0.5
	var pilot := Sprite2D.new()
	pilot.texture = ImageTexture.create_from_image(pilot_image)
	pilot.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	pilot.centered = false
	pilot.offset = Vector2(-pilot_foot_x, -pilot_bounds.end.y)
	pilot.scale = Vector2.ONE * scale_factor
	pilot.position = Vector2(hero.position.x + PILOT_GAP, ground_y)
	pilot.z_index = int(ground_y)
	city.add_child(pilot)
	await get_tree().process_frame
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var capture := window.get_viewport().get_texture().get_image()
	if capture == null or capture.get_size() != Vector2i(1280, 720):
		_fail("unexpected capture size: " + str(capture.get_size() if capture != null else Vector2i.ZERO))
		return
	var output_path := ProjectSettings.globalize_path(OUTPUT_DIR)
	if DirAccess.make_dir_recursive_absolute(output_path) != OK:
		_fail("cannot make output directory")
		return
	var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var unique_id := "%08x" % (randi() & 0xffffffff)
	var stem := "rpg-2-star-ocean-the-second_scifi-city_protagonist-female-pixelorama-south-%s-pilot-h48-beside-placeholder_m8-v01_%s-%s" % [variant, stamp, unique_id]
	var capture_path := output_path.path_join(stem + ".png")
	if capture.save_png(capture_path) != OK:
		_fail("cannot save capture")
		return
	var window_scale := float(capture.get_height()) / 360.0
	print("STATUS unapproved pilot; technical visual QA only")
	print("PILOT_VARIANT %s  SOURCE %s" % [variant, PILOT_PATHS[variant]])
	print("PILOT_SOURCE_SIZE %dx%d" % [pilot_image.get_width(), pilot_image.get_height()])
	print("PILOT_VISIBLE_BOUNDS_SOURCE %s" % str(pilot_bounds))
	print("PILOT_SCALE %.4f" % scale_factor)
	print("PILOT_VISIBLE_LOGICAL %.1fx%.1f" % [pilot_bounds.size.x * scale_factor, pilot_bounds.size.y * scale_factor])
	print("PILOT_VISIBLE_WINDOW %.1fx%.1f" % [pilot_bounds.size.x * scale_factor * window_scale, pilot_bounds.size.y * scale_factor * window_scale])
	print("PLACEHOLDER_TEXTURE %dx%d" % [placeholder_image.get_width(), placeholder_image.get_height()])
	print("PLACEHOLDER_VISIBLE_BOUNDS %s" % str(placeholder_bounds))
	print("PLACEHOLDER_VISIBLE_WINDOW %.1fx%.1f" % [placeholder_bounds.size.x * window_scale, placeholder_bounds.size.y * window_scale])
	print("GROUND_Y_LOGICAL %.1f  PLACEHOLDER_X %.1f  PILOT_X %.1f" % [ground_y, hero.position.x, pilot.position.x])
	print("CAPTURE " + capture_path)
	get_tree().quit(0)
