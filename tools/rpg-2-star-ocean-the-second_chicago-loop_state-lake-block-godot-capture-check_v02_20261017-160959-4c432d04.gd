extends SceneTree

# Real Godot 640x360 captures plus behaviour checks for the Chicago Loop arrival scene
# (State St x Lake St block candidate v02, UNAPPROVED).
# Usage: Godot --path game -s <this file> -- <output dir> <stamp-id> <scene res path> <walkmask png>
#   <scene res path> is the v02 test scene (nonruntime) or the runtime Loop scene once v02 is wired.
# Writes PNGs only into <output dir>; saves go to user://test-saves/chicago-loop-state-lake-v02.
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
const APPROVED_HERO_IDLE := preload("res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")

var loop_scene := ""
var app: Node
var host: Node
var folder := ""
var stamp := ""
var checks := 0


func _initialize() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	push_error(message)
	print("CHICAGO_LOOP_FAIL " + message)
	quit(1)


func _check(ok: bool, label: String) -> bool:
	if not ok:
		_fail(label)
		return false
	checks += 1
	print("CHICAGO_LOOP_CHECK_OK " + label)
	return true


func _frames(count: int) -> void:
	for i in count:
		await process_frame


func _image() -> Image:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	return root.get_viewport().get_texture().get_image()


func _capture(name: String) -> bool:
	var image := await _image()
	if image.get_size() != Vector2i(640, 360):
		_fail("expected a 640x360 capture, got " + str(image.get_size()))
		return false
	var path := folder.path_join(name)
	if image.save_png(path) != OK:
		_fail("could not save " + path)
		return false
	print("CHICAGO_LOOP_CAPTURE " + path)
	return true


func _shot_name(tag: String) -> String:
	return "rpg-2-star-ocean-the-second_chicago-loop_%s-640x360_v02_%s.png" % [tag, stamp]


func _load_loop() -> void:
	app.select_destination("scifi.loop")
	host = (load(loop_scene) as PackedScene).instantiate()
	root.add_child(host)
	current_scene = host
	await _frames(3)


func _set_language(code: String) -> void:
	app.language = code
	host._refresh_text()
	await _frames(2)


func _hold(action: String, frames: int) -> void:
	Input.action_press(action)
	await _frames(frames)
	Input.action_release(action)
	await process_frame


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	folder = args[0]
	stamp = args[1]
	loop_scene = args[2]
	Engine.max_fps = 60
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(640, 360)
	DirAccess.make_dir_recursive_absolute(folder)
	SaveStore.root_path = "user://test-saves/chicago-loop-state-lake-v02"
	app = root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = "female"
	await _load_loop()
	host.set_process(false)
	if await _checks(args[3]):
		print("CHICAGO_LOOP_V02_OK checks=%d scene=%s runtime_scene=%s" % [checks, loop_scene, str(loop_scene == app.area_scene_path("scifi.loop"))])
		quit()


func _occluded(at: Vector2, box: Rect2i) -> int:
	var hero: Sprite2D = host.hero
	hero.position = at
	hero.visible = false
	var without := await _image()
	hero.visible = true
	var with_hero := await _image()
	return _diff(without, with_hero, box)


func _checks(mask_path: String) -> bool:
	var script: GDScript = host.get_script()
	var hero: Sprite2D = host.hero
	# Arrival and labels.
	if not _check(host.scene_file_path == loop_scene and hero.position == script.SPAWN and script.walkable(script.SPAWN), "arrival at the walkable Lake St plaza spawn"):
		return false
	await _set_language("zh")
	if not _check(host.title_label.text == "芝加哥 · 卢普区" and host.badge_label.text == "技术占位 · 美术未验收", "zh title and art-unaccepted badge unchanged"):
		return false
	if not await _capture(_shot_name("state-lake-godot-zh-arrival")):
		return false
	await _set_language("en")
	if not _check(host.title_label.text == "Chicago · The Loop" and host.badge_label.text == "Technical placeholder · Art not accepted" and host.help_label.text.contains("no calendar time"), "en labels unchanged"):
		return false
	var streets: Array[String] = []
	for label in host.street_labels:
		streets.append(label.text)
	if not _check(streets.has("E Lake St · 200 N") and streets.has("N State St · 0 E/W") and streets.has("State/Lake"), "real street and station names stay English: " + ", ".join(streets)):
		return false
	var sorted_index: int = hero.get_parent().get_index()
	var painted := true
	for label in host.street_labels:
		painted = painted and label.get_index() < sorted_index
	if not _check(painted, "street labels are painted under the hero and props (drawn before the y-sort node)"):
		return false
	if not await _capture(_shot_name("state-lake-godot-en-arrival")):
		return false
	# Walk mask parity: the runtime collision equals the authored guide mask pixel for pixel.
	var mask := Image.load_from_file(mask_path)
	var mismatches := 0
	var walkable_count := 0
	for y in 360:
		for x in 640:
			var authored := mask.get_pixel(x, y).r > 0.5
			walkable_count += 1 if authored else 0
			if authored != script.walkable(Vector2(x, y)):
				mismatches += 1
	if not _check(mismatches == 0 and walkable_count > 55000, "walkable() matches the authored walk mask (%d walkable px, %d mismatches)" % [walkable_count, mismatches]):
		return false
	# Legacy pins from the US migration smoke stay true (kiosk and bench replace v01's mid-lane car).
	if not _check(script.walkable(Vector2(400, 180)) and not script.walkable(Vector2(440, 195)) and script.slide_position(Vector2(400, 180), Vector2(410, 190)) == Vector2(410, 180), "legacy smoke pins: plaza walkable under the L, kiosk solid, slide past the bench"):
		return false
	var solids := {"west L column plinth": Vector2(160, 254), "east L column plinth": Vector2(478, 254), "info kiosk": Vector2(432, 195), "bench": Vector2(405, 193),
		"west planter": Vector2(131, 256), "east planter": Vector2(507, 256), "curb lamp": Vector2(85, 180), "raised terrace": Vector2(560, 185),
		"fountain court": Vector2(600, 250), "foreground tree": Vector2(105, 285), "forecourt lamp": Vector2(530, 292), "facade bases under the deck": Vector2(320, 168),
		"header": Vector2(320, 40), "footer": Vector2(320, 330)}
	for key in solids:
		if not _check(not script.walkable(solids[key]), "solid: " + key):
			return false
	if not _check(script.WALK_TOP - 44 >= script.DECK_BOTTOM, "walk top keeps the 44 px hero head clear of the deck girder"):
		return false
	# Real held input: north from the arrival point to the L, no calendar time.
	var minutes: int = app.calendar_minutes
	host.set_process(true)
	hero.position = script.SPAWN
	var frames := 0
	Input.action_press("move_up")
	while frames < 240:
		await process_frame
		frames += 1
		if not script.walkable(hero.position):
			Input.action_release("move_up")
			return _check(false, "walk north left the walkable ground at " + str(hero.position))
	Input.action_release("move_up")
	await process_frame
	if not _check(hero.position.y < script.WALK_TOP + 2.0 and absf(hero.position.x - script.SPAWN.x) < 0.01 and app.calendar_minutes == minutes, "held move_up walks the plaza to the L with no time charged (y=%.1f)" % hero.position.y):
		return false
	# West across the whole plaza under the L, between the column rows, then over State St.
	hero.position = Vector2(565, 230)
	Input.action_press("move_left")
	frames = 0
	var last_x := hero.position.x
	while hero.position.x > 20.0 and frames < 600:
		await process_frame
		frames += 1
		if hero.position.x > last_x or absf(hero.position.y - 230.0) > 0.01:
			Input.action_release("move_left")
			return _check(false, "plaza walk regressed at " + str(hero.position))
		last_x = hero.position.x
	Input.action_release("move_left")
	if not _check(hero.position.x <= 20.0, "the plaza and State St crosswalk walk end to end (x=%.1f)" % hero.position.x):
		return false
	# A column plinth blocks a straight walk south; the hero stops north of it.
	hero.position = Vector2(162, 236)
	await _hold("move_down", 30)
	if not _check(hero.position.y < 246.0 and hero.position.x == 162.0, "column plinth blocks a straight walk south (y=%.1f)" % hero.position.y):
		return false
	host.set_process(false)
	# Occlusion: behind a column the shaft covers the hero; in front the hero covers the plinth.
	var behind_column := await _occluded(Vector2(162, 240), Rect2i(154, 200, 16, 36))
	await _set_language("zh")
	if not await _capture(_shot_name("state-lake-godot-zh-behind-l-column")):
		return false
	var front_column := await _occluded(Vector2(162, 282), Rect2i(150, 244, 24, 18))
	if not _check(behind_column == 0 and front_column > 60, "column hides the hero behind it (%d px changed) and the hero covers the plinth in front (%d px)" % [behind_column, front_column]):
		return false
	# Kiosk and bench under the deck edge: behind them they cover the hero, in front she covers them.
	var behind_kiosk := await _occluded(Vector2(432, 187), Rect2i(422, 150, 20, 36))
	var front_kiosk := await _occluded(Vector2(432, 214), Rect2i(424, 186, 16, 14))
	var bench_legs := await _occluded(Vector2(405, 187), Rect2i(398, 183, 14, 4))
	var bench_head := await _occluded(Vector2(405, 187), Rect2i(398, 145, 14, 20))
	if not _check(behind_kiosk == 0 and front_kiosk > 30 and bench_legs == 0 and bench_head > 30, "kiosk hides the hero behind it (%d), hero covers its base in front (%d); bench hides her feet (%d), head stays visible (%d)" % [behind_kiosk, front_kiosk, bench_legs, bench_head]):
		return false
	# The forecourt and foreground-tree layers pivot below the walk area, so they always draw over the hero.
	if not _check(script.YSORT_LAYERS[4][1] > script.WALK.end.y and script.YSORT_LAYERS[5][1] > script.WALK.end.y, "forecourt and foreground tree always draw over the hero"):
		return false
	# Info kiosk: E near it opens a bilingual board; nothing in the game state changes.
	var interaction := InputEventAction.new()
	interaction.action = "interact"
	interaction.pressed = true
	hero.position = script.KIOSK
	var clues: int = app.survey_clues.size()
	host._unhandled_input(interaction)
	await _frames(2)
	if not _check(host.info_panel.visible and host.info_label.text.contains("State/Lake") and app.calendar_minutes == minutes and app.survey_clues.size() == clues, "kiosk opens the zh board, no time or clue change"):
		return false
	if not await _capture(_shot_name("state-lake-godot-zh-kiosk-board")):
		return false
	await _set_language("en")
	if not _check(host.info_label.text.contains("Lake Street elevated") and host.info_label.text.contains("0 E/W"), "kiosk board switches to English"):
		return false
	if not await _capture(_shot_name("state-lake-godot-en-kiosk-board")):
		return false
	host._unhandled_input(interaction)
	await _frames(2)
	if not _check(not host.info_panel.visible, "E again closes the board"):
		return false
	hero.position = script.SPAWN
	host._unhandled_input(interaction)
	await _frames(2)
	if not _check(not host.info_panel.visible, "E away from the kiosk does nothing"):
		return false
	# Reference captures with the approved 48 px heroine idle (same scale, offset and spot as v01's reference).
	var runtime_texture := hero.texture
	var runtime_scale := hero.scale
	var runtime_offset := hero.offset
	hero.texture = APPROVED_HERO_IDLE
	hero.scale = Vector2(0.5, 0.5)
	hero.offset = Vector2(0, -40)
	for code in ["zh", "en"]:
		await _set_language(code)
		hero.position = Vector2(296, 228)
		if not await _capture(_shot_name("state-lake-godot-%s-approved-heroine-ref" % code)):
			return false
	hero.position = Vector2(300, 196)
	if not await _capture(_shot_name("state-lake-godot-en-approved-heroine-under-l")):
		return false
	hero.texture = runtime_texture
	hero.scale = runtime_scale
	hero.offset = runtime_offset
	# Resume safety: old placeholder and v01 save spots land on walkable ground of the v02 block.
	for old in [Vector2(80, 90), Vector2(400, 180), Vector2(560, 300), Vector2(115, 284), Vector2(320, 40), Vector2(440, 195), Vector2(523, 284), Vector2(620, 230)]:
		if not _check(script.walkable(script.safe_position(old)), "old save spot %s resumes on walkable ground" % str(old)):
			return false
	# Save opens from the Loop at the hero spot; Esc returns to the world map.
	hero.position = Vector2(330, 260)
	host.save_button.pressed.emit()
	await _frames(3)
	if not _check(current_scene.scene_file_path.ends_with("save_screen.tscn") and app.save_return_scene == app.area_scene_path("scifi.loop") and app.save_return_position == Vector2(330, 260), "save opens with the Loop return scene and spot"):
		return false
	change_scene_to_file(loop_scene)
	await _frames(3)
	current_scene.get_viewport().push_input(_cancel())
	await _frames(3)
	return _check(current_scene.scene_file_path == MAP_SCENE, "Esc in the Loop returns to the world map")


func _cancel() -> InputEventAction:
	var event := InputEventAction.new()
	event.action = "ui_cancel"
	event.pressed = true
	return event


func _diff(a: Image, b: Image, box: Rect2i) -> int:
	var count := 0
	for y in range(box.position.y, box.end.y):
		for x in range(box.position.x, box.end.x):
			if not a.get_pixel(x, y).is_equal_approx(b.get_pixel(x, y)):
				count += 1
	return count
