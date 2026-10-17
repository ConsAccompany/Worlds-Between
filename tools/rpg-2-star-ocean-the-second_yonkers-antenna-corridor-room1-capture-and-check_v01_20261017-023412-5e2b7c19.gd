extends SceneTree

# Native Godot captures plus clue/navigation checks for the Yonkers room 1 antenna fixture pilot.
# Usage: Godot --path game -s <this file> -- <output dir> <tag> <stamp-id>
const SCENE := "res://scenes/survey_annex.tscn"
const APPROVED_HERO_IDLE := preload("res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
const CLUES := [Vector2(163, 165), Vector2(320, 165), Vector2(477, 165)]

var app: Node
var host: Node2D
var hero: Sprite2D


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


func _use_reference_hero() -> void:
	hero.texture = APPROVED_HERO_IDLE
	hero.scale = Vector2(0.5, 0.5)
	hero.offset = Vector2(0, -40)


func _fail(message: String) -> void:
	push_error(message)
	print("YONKERS_ROOM1_FAIL " + message)
	quit(1)


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var folder: String = args[0]
	var tag: String = args[1]
	var stamp: String = args[2]
	Engine.max_fps = 60
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(640, 360)
	SaveStore.root_path = "user://test-saves/yonkers-room1-antenna-review"
	app = root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = "female"
	app.select_destination("scifi.outskirts")
	app.current_annex_room = 1
	host = (load(SCENE) as PackedScene).instantiate()
	root.add_child(host)
	current_scene = host
	await process_frame
	await process_frame
	host.set_process(false)
	hero = host.hero
	_use_reference_hero()
	DirAccess.make_dir_recursive_absolute(folder)
	if host.find_children("*", "Camera2D", true, false).size() != 0:
		_fail("unexpected Camera2D in survey annex")
		return
	var shots := [["zh", Vector2(87, 261), "start"], ["en", Vector2(87, 261), "start"], ["zh", Vector2(320, 238), "lane-b"]]
	for shot in shots:
		app.language = shot[0]
		hero.position = shot[1]
		host._refresh_text()
		var name := "rpg-2-star-ocean-the-second_yonkers-antenna-room1_%s-godot-%s-%s-640x360_v01_%s.png" % [tag, shot[0], shot[2], stamp]
		if not await _capture(folder.path_join(name)):
			_fail("capture failed " + name)
			return
		print("YONKERS_ROOM1_CAPTURE " + folder.path_join(name))
	app.language = "zh"
	host._refresh_text()
	var labels := []
	for label in host.clue_labels:
		labels.append(label.text)
	print("YONKERS_ROOM1_TEXT " + host.title_label.text + " | " + " / ".join(labels) + " | " + host.next_label.text + " | " + host.exit_label.text)
	# Clue interaction from the same clear side approach used by room 2, plus one from directly below each fixture.
	var interaction := InputEventAction.new()
	interaction.action = "interact"
	interaction.pressed = true
	for approach in [Vector2(39, 20), Vector2(0, 43)]:
		app.survey_clues.clear()
		for index in 3:
			host._close_overlay()
			hero.position = CLUES[index] + approach
			host._unhandled_input(interaction)
			var clue_key := "scifi.outskirts:%d" % index
			if not app.survey_clues.has(clue_key) or host.overlay_clue_index != index:
				_fail("room 1 clue did not register: %s from %s" % [clue_key, str(approach)])
				return
	host._close_overlay()
	print("YONKERS_ROOM1_INTERACTIONS_OK 3x2")
	# Real held input along the central lane: start marker to next-room marker, nothing blocks or snaps.
	hero.position = Vector2(87, 261)
	host.set_process(true)
	Input.action_press("move_right")
	var frames := 0
	var last_x := hero.position.x
	while hero.position.x < 578.0 and frames < 600:
		await process_frame
		frames += 1
		if hero.position.x < last_x or absf(hero.position.y - 261.0) > 0.01:
			Input.action_release("move_right")
			_fail("lane walk regressed at " + str(hero.position))
			return
		last_x = hero.position.x
	Input.action_release("move_right")
	if hero.position.x < 578.0:
		_fail("lane walk did not reach next marker: " + str(hero.position))
		return
	print("YONKERS_ROOM1_LANE_WALK_OK x=%.1f frames=%d" % [hero.position.x, frames])
	# Walk up through the antenna B fixture footprint: no collision was added, only the old clamp applies.
	hero.position = Vector2(320, 280)
	Input.action_press("move_up")
	frames = 0
	while hero.position.y > 78.5 and frames < 600:
		await process_frame
		frames += 1
	Input.action_release("move_up")
	if hero.position.y > 78.5 or absf(hero.position.x - 320.0) > 0.01:
		_fail("vertical walk through fixture footprint blocked: " + str(hero.position))
		return
	print("YONKERS_ROOM1_NO_NEW_COLLISION_OK y=%.1f" % hero.position.y)
	host.set_process(false)
	# Door logic: the next-room marker still opens room 2.
	hero.position = Vector2(580, 257)
	host._unhandled_input(interaction)
	await process_frame
	await process_frame
	if int(app.current_annex_room) != 2:
		_fail("next marker did not move to room 2")
		return
	print("YONKERS_ROOM1_NEXT_ROOM_OK")
	quit()
