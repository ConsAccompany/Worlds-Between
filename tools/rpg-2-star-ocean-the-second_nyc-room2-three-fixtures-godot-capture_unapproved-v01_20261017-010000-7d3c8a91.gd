extends SceneTree

# Captures the actual survey_annex scene at native 640x360 with the three
# unapproved pixel fixtures. This is evidence, not creator acceptance.
const SCENE := "res://scenes/survey_annex.tscn"
const OUTPUT_DIR := "res://../outputs/room2-fixtures-pilot"
const APPROVED_HERO_IDLE := preload("res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")


func _initialize() -> void:
	call_deferred("_run")


func _grab(path: String) -> bool:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_viewport().get_texture().get_image()
	if image.get_size() != Vector2i(640, 360):
		push_error("Unexpected capture size: " + str(image.get_size()))
		return false
	return image.save_png(path) == OK


func _run() -> void:
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(640, 360)
	SaveStore.root_path = "user://test-saves/room2-fixtures-pilot"
	var app := root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = "female"
	app.select_destination("scifi.city")
	app.current_annex_room = 2
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
	var pass_count := 0
	for lang in ["zh", "en"]:
		app.language = lang
		host._refresh_text()
		var name := "rpg-2-star-ocean-the-second_nyc-public-facilities-room2_three-pixel-fixtures-godot-%s-640x360_unapproved-v01_%s-%s.png" % [lang, stamp, uid]
		var path := folder.path_join(name)
		if await _grab(path):
			print("ROOM2_FIXTURE_CAPTURE " + path)
			pass_count += 1
		else:
			quit(1)
			return
	hero.position = Vector2(202, 185)
	app.language = "zh"
	host._refresh_text()
	var approach_name := "rpg-2-star-ocean-the-second_nyc-public-facilities-room2_repair-manual-approach-godot-zh-640x360_unapproved-v01_%s-%s.png" % [stamp, uid]
	if await _grab(folder.path_join(approach_name)):
		print("ROOM2_FIXTURE_CAPTURE " + folder.path_join(approach_name))
		pass_count += 1
	else:
		quit(1)
		return
	var interaction := InputEventAction.new()
	interaction.action = "interact"
	interaction.pressed = true
	host._unhandled_input(interaction)
	if not app.survey_clues.has("scifi.city:3"):
		push_error("Repair-manual interaction failed from the clear right-side approach")
		quit(1)
		return
	var name := "rpg-2-star-ocean-the-second_nyc-public-facilities-room2_repair-manual-interaction-godot-zh-640x360_unapproved-v01_%s-%s.png" % [stamp, uid]
	if await _grab(folder.path_join(name)):
		print("ROOM2_FIXTURE_CAPTURE " + folder.path_join(name))
		pass_count += 1
	else:
		quit(1)
		return
	for index in [1, 2]:
		host._close_overlay()
		hero.position = Vector2([320, 477][index - 1] + 39, 185)
		host._unhandled_input(interaction)
		var clue_key := "scifi.city:%d" % (3 + index)
		if not app.survey_clues.has(clue_key):
			push_error("Room 2 clue failed from the clear right-side approach: " + clue_key)
			quit(1)
			return
	print("ROOM2_FIXTURE_INTERACTIONS_OK 3")
	print("ROOM2_FIXTURE_CAPTURE_OK %d" % pass_count)
	quit()
