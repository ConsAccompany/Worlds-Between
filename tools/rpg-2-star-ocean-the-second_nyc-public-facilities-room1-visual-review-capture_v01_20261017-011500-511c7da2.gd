extends SceneTree

# Native Godot review of the existing Room 1 art; no scene acceptance is implied.
const SCENE := "res://scenes/survey_annex.tscn"
const OUTPUT_DIR := "res://../outputs/room1-visual-review"
const APPROVED_HERO_IDLE := preload("res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")

func _initialize() -> void:
	call_deferred("_run")

func _capture(path: String) -> bool:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_viewport().get_texture().get_image()
	if image.get_size() != Vector2i(640, 360):
		push_error("Expected 640x360, got " + str(image.get_size()))
		return false
	return image.save_png(path) == OK

func _run() -> void:
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(640, 360)
	SaveStore.root_path = "user://test-saves/room1-visual-review"
	var app := root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = "female"
	app.select_destination("scifi.city")
	app.current_annex_room = 1
	var host: Node2D = (load(SCENE) as PackedScene).instantiate()
	root.add_child(host)
	current_scene = host
	await process_frame
	await process_frame
	host.set_process(false)
	var hero: Sprite2D = host.hero
	hero.texture = APPROVED_HERO_IDLE
	hero.scale = Vector2(0.5, 0.5)
	hero.offset = Vector2(0, -40)
	var folder := ProjectSettings.globalize_path(OUTPUT_DIR)
	DirAccess.make_dir_recursive_absolute(folder)
	var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	var uid := "%08x" % (randi() & 0xffffffff)
	for lang in ["zh", "en"]:
		app.language = lang
		host._refresh_text()
		var name := "rpg-2-star-ocean-the-second_nyc-public-facilities-room1_existing-scene-godot-%s-640x360-review-v01_%s-%s.png" % [lang, stamp, uid]
		if not await _capture(folder.path_join(name)):
			quit(1)
			return
		print("ROOM1_REVIEW_CAPTURE " + folder.path_join(name))
	app.language = "zh"
	host._refresh_text()
	var interaction := InputEventAction.new()
	interaction.action = "interact"
	interaction.pressed = true
	for index in [0, 1, 2]:
		host._close_overlay()
		hero.position = Vector2([163, 320, 477][index] + 39, 185)
		host._unhandled_input(interaction)
		var clue_key := "scifi.city:%d" % index
		if not app.survey_clues.has(clue_key):
			push_error("Room 1 clue did not register: " + clue_key)
			quit(1)
			return
	print("ROOM1_REVIEW_INTERACTIONS_OK 3")
	quit()
