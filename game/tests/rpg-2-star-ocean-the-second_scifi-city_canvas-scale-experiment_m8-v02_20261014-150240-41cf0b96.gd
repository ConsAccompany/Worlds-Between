extends SceneTree

# Standalone render-mode diagnostic. Each invocation captures the unmodified city
# with its current native sprites; no project setting or scene file is written.
const OUTPUT_DIR := "res://../outputs"


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 1 or not str(args[0]).begins_with("--mode="):
		push_error("Use -- --mode=viewport or --mode=canvas-items")
		quit(1)
		return
	var mode: String = str(args[0]).trim_prefix("--mode=")
	if mode != "viewport" and mode != "canvas-items":
		push_error("Unknown mode " + mode)
		quit(1)
		return
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS if mode == "canvas-items" else Window.CONTENT_SCALE_MODE_VIEWPORT
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(1280, 720)
	SaveStore.root_path = "user://test-saves/m8-canvas-scale-experiment"
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = "male"
	app.select_destination("scifi.city")
	change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
	await process_frame
	await process_frame
	var area: Node2D = current_scene
	area.set_process(false)
	await RenderingServer.frame_post_draw
	var image := root.get_viewport().get_texture().get_image()
	var expected := Vector2i(1280, 720) if mode == "canvas-items" else Vector2i(640, 360)
	if image == null or image.get_size() != expected:
		push_error("Unexpected render size " + str(image.get_size() if image != null else Vector2i.ZERO))
		quit(1)
		return
	var directory := ProjectSettings.globalize_path(OUTPUT_DIR)
	DirAccess.make_dir_recursive_absolute(directory)
	var stamp := Time.get_datetime_string_from_system(false).replace("-", "").replace(":", "").replace("T", "-")
	var unique_id := "%08x" % randi()
	var stem := "rpg-2-star-ocean-the-second_scifi-city_native-scene-%s-render_m8-v02_%s-%s" % [mode, stamp, unique_id]
	var capture_path := directory.path_join(stem + ".png")
	if image.save_png(capture_path) != OK:
		push_error("Cannot save " + capture_path)
		quit(1)
		return
	var hero: Sprite2D = area.get("hero")
	var receipt := {
		"scene": "res://scenes/scifi_exploration_area.tscn",
		"mode": mode,
		"temporary_runtime_setting_only": true,
		"logical_content_size": [640, 360],
		"window_size": [root.size.x, root.size.y],
		"rendered_texture_size": [image.get_width(), image.get_height()],
		"hero_texture_size": [hero.texture.get_width(), hero.texture.get_height()],
		"hero_texture_filter": "nearest",
		"capture": capture_path,
	}
	var receipt_path := directory.path_join(stem + ".json")
	var file := FileAccess.open(receipt_path, FileAccess.WRITE)
	if file == null:
		push_error("Cannot save receipt")
		quit(1)
		return
	file.store_string(JSON.stringify(receipt, "\t"))
	file.close()
	print("CAPTURE " + capture_path)
	print("RECEIPT " + receipt_path)
	quit(0)
