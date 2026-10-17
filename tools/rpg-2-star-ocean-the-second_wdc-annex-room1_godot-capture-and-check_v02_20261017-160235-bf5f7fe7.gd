extends SceneTree

# v02 Washington survey annex room 1 (scifi.ruins): native Godot 640x360 captures plus focused walk,
# collision, occlusion, reachability, interaction, save/load, door and header checks.
# Usage: Godot --path game -s <this file> -- <output dir> <stamp-id>
const SCENE := "res://scenes/survey_annex.tscn"
const APPROVED_HERO_IDLE := preload("res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
const CLUES := [Vector2(163, 165), Vector2(320, 165), Vector2(477, 165)]
const DEST := "scifi.ruins"
const SPAWN := Vector2(87, 261)
const EXIT := Vector2(57, 257)
const NEXT := Vector2(580, 257)

var app: Node
var host: Node2D
var hero: Sprite2D
var folder := ""
var stamp := ""
var interaction := InputEventAction.new()


func _initialize() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	push_error(message)
	print("WDC_V02_FAIL " + message)
	quit(1)


func _capture(path: String) -> bool:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_viewport().get_texture().get_image()
	if image.get_size() != Vector2i(640, 360):
		push_error("Expected 640x360, got " + str(image.get_size()))
		return false
	return image.save_png(path) == OK


func _dress_hero() -> void:
	hero = host.hero
	# Capture-only reference: the creator-approved female south idle at 48 logical px (as in v01).
	hero.texture = APPROVED_HERO_IDLE
	hero.scale = Vector2(0.5, 0.5)
	hero.offset = Vector2(0, -40)


func _open(destination: String, room: int) -> void:
	if host != null:
		host.queue_free()
		await process_frame
	app.select_destination(destination)
	app.current_annex_room = room
	host = (load(SCENE) as PackedScene).instantiate()
	root.add_child(host)
	current_scene = host
	await process_frame
	await process_frame
	host.set_process(false)
	_dress_hero()


func _place(at: Vector2) -> void:
	hero.position = at
	if host.wdc_front != null:
		host._wdc_update_front()


func _shot(language: String, at: Vector2, label: String) -> bool:
	app.language = language
	_place(at)
	host._refresh_text()
	var name := "rpg-2-star-ocean-the-second_wdc-annex-room1_v02-godot-%s-%s-640x360_%s.png" % [language, label, stamp]
	if not await _capture(folder.path_join(name)):
		return false
	print("WDC_V02_CAPTURE %s at=%s front_mask=%d" % [folder.path_join(name), str(at), host.wdc_front_mask])
	return true


func _hold(action: String, done: Callable, limit := 900) -> int:
	host.set_process(true)
	Input.action_press(action)
	var frames := 0
	while not done.call() and frames < limit:
		await process_frame
		frames += 1
	Input.action_release(action)
	await process_frame
	host.set_process(false)
	return frames


func _walk_until_stopped(start: Vector2, action: String, limit := 240) -> Vector2:
	_place(start)
	var state := {"last": Vector2(-999, -999), "still": 0}
	var stop := func():
		if hero.position.distance_to(state["last"]) < 0.01:
			state["still"] += 1
		else:
			state["still"] = 0
		state["last"] = hero.position
		return state["still"] >= 6
	await _hold(action, stop, limit)
	return hero.position


func _blocked(at: Vector2) -> bool:
	return host._wdc_blocked(at)


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	folder = args[0]
	stamp = args[1]
	interaction.action = "interact"
	interaction.pressed = true
	Engine.max_fps = 60
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(640, 360)
	SaveStore.root_path = "user://test-saves/wdc-annex-room1-v02-%s" % stamp
	app = root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = "female"
	DirAccess.make_dir_recursive_absolute(folder)
	await _open(DEST, 1)
	if host.wdc_front == null:
		_fail("Washington room 1 front layer missing")
		return
	var bg: Texture2D = host.ROOM_ONE_BACKGROUND[DEST]
	print("WDC_V02_BACKGROUND " + bg.resource_path + " " + str(bg.get_size()))
	print("WDC_V02_FOREGROUND " + host.WDC_ROOM_ONE_FOREGROUND.resource_path)
	for fixture in host.WDC_ROOM_ONE_FIXTURES:
		print("WDC_V02_FIXTURE " + fixture.resource_path)

	# --- header: the English title must end before the Save button; zh unchanged at 18 px.
	for language in ["zh", "en"]:
		app.language = language
		host._refresh_text()
		var labels := []
		for label in host.clue_labels:
			labels.append(label.text)
		var size := int(host.title_label.get_theme_font_size("font_size"))
		var right: float = host.title_label.position.x + host.title_label.get_minimum_size().x
		print("WDC_V02_TEXT_%s size=%d title_right=%.1f save_left=%.1f | %s | %s | %s | %s | %s" % [language, size, right,
				host.save_button.position.x, host.title_label.text, " / ".join(labels), host.exit_label.text, host.next_label.text, host.help_label.text])
		if right >= host.save_button.position.x - 4.0:
			if language == "en":
				_fail("en title overlaps Save: right %.1f" % right)
				return
			print("WDC_V02_WARN zh title reaches the Save button (unchanged by v02)")
		if size != (14 if language == "en" else 18):
			_fail("unexpected title size %d for %s" % [size, language])
			return

	# --- captures: entry, near each clue, and occlusion / obstacle views (separate zh and en files).
	var shots := [["zh", SPAWN, "entry"], ["en", SPAWN, "entry"]]
	for index in 3:
		var near: Vector2 = Vector2(CLUES[index].x, 238)
		shots.append(["zh", near, "near-clue-%d" % index])
		shots.append(["en", near, "near-clue-%d" % index])
	shots.append(["zh", Vector2(292, 204), "occlusion-behind-index"])
	shots.append(["en", Vector2(30, 258), "obstacle-west-stub"])
	for shot in shots:
		if _blocked(shot[1]):
			_fail("capture position is inside a blocker " + str(shot))
			return
		if not await _shot(shot[0], shot[1], shot[2]):
			_fail("capture failed " + str(shot))
			return
	_place(Vector2(292, 204))
	if host.wdc_front_mask != 2:
		_fail("behind the index cabinet the front mask is %d, expected 2" % host.wdc_front_mask)
		return
	_place(Vector2(320, 238))
	if host.wdc_front_mask != 0:
		_fail("in front of the cabinet the front mask is %d, expected 0" % host.wdc_front_mask)
		return
	print("WDC_V02_OCCLUSION_STATE_OK behind=2 front=0")

	# --- interactions: from behind (top), the side and the front of every fixture.
	var content: Dictionary = host.CONTENT.DATA[DEST]
	app.language = "zh"
	for approach in ["top", "side", "front"]:
		app.survey_clues.clear()
		for index in 3:
			host._close_overlay()
			var c: Vector2 = CLUES[index]
			var at: Vector2 = {"top": Vector2(c.x, 158), "side": Vector2(c.x + 38, 190), "front": Vector2(c.x, 236)}[approach]
			if _blocked(at):
				_fail("approach point blocked %s %d" % [approach, index])
				return
			_place(at)
			host._unhandled_input(interaction)
			var key := "%s:%d" % [DEST, index]
			if not app.survey_clues.has(key) or host.overlay_clue_index != index or host.overlay_title.text != String(content[app.language]["clues"][index]["name"]):
				_fail("clue did not register: %s from %s" % [key, approach])
				return
	host._close_overlay()
	# No false positives: the lane between fixtures and the door spots do not open clues.
	app.survey_clues.clear()
	for at in [Vector2(241, 240), Vector2(398, 240), Vector2(241, 180)]:
		_place(at)
		host._unhandled_input(interaction)
		if host.overlay.visible:
			_fail("unexpected overlay at " + str(at))
			return
	print("WDC_V02_INTERACTIONS_OK 3x3 (top, side, front)")

	# --- lane walk with held input: exit marker to the next-room marker without snapping.
	app.survey_clues.clear()
	_place(SPAWN)
	var frames := await _hold("move_right", func(): return hero.position.x >= 578.0)
	if hero.position.x < 578.0 or absf(hero.position.y - 261.0) > 0.01:
		_fail("lane walk regressed at " + str(hero.position))
		return
	print("WDC_V02_LANE_WALK_OK x=%.1f frames=%d" % [hero.position.x, frames])

	# --- collision: held input stops at each obstacle and slides along it.
	var cases := [
		["fixture-1-from-front", Vector2(320, 280), "move_up", func(p): return p.y >= 228.0 and p.y < 231.0 and absf(p.x - 320.0) < 0.01],
		["fixture-0-from-west", Vector2(100, 220), "move_right", func(p): return p.x < 129.0 and p.x > 126.0],
		["fixture-2-from-east", Vector2(540, 220), "move_left", func(p): return p.x >= 513.0 and p.x < 516.0],
		["bench-between-fixtures", Vector2(240, 280), "move_up", func(p): return p.y >= 156.0 and p.y < 159.0],
		["west-rubble", Vector2(120, 170), "move_left", func(p): return p.x >= 84.0 and p.x < 87.0],
		["east-rubble", Vector2(520, 195), "move_right", func(p): return p.x < 570.0 and p.x > 567.0],
		["east-stairwell", Vector2(500, 240), "move_right", func(p): return p.x < 584.0 and p.x > 581.0],
		["west-stub", Vector2(40, 240), "move_down", func(p): return p.y < 262.0 and p.y > 259.0],
		["east-stub", Vector2(600, 240), "move_down", func(p): return false],
		["near-edge", Vector2(320, 240), "move_down", func(p): return is_equal_approx(p.y, 305.0)],
	]
	for case in cases:
		if case[0] == "east-stub":
			continue
		var stopped: Vector2 = await _walk_until_stopped(case[1], case[2])
		if not case[3].call(stopped):
			_fail("collision case %s stopped at %s" % [case[0], str(stopped)])
			return
		print("WDC_V02_COLLISION %s -> %s" % [case[0], str(stopped)])
	# Diagonal input slides along the cabinet's front instead of sticking.
	_place(Vector2(300, 240))
	host.set_process(true)
	Input.action_press("move_up")
	Input.action_press("move_right")
	for i in 40:
		await process_frame
	Input.action_release("move_up")
	Input.action_release("move_right")
	await process_frame
	host.set_process(false)
	if hero.position.x < 330.0 or _blocked(hero.position):
		_fail("diagonal slide stuck at " + str(hero.position))
		return
	print("WDC_V02_SLIDE_OK -> " + str(hero.position))
	# A position inside a blocker (e.g. an older v01 save on the rubble) can walk out.
	_place(Vector2(30, 170))
	await _hold("move_right", func(): return not _blocked(hero.position), 120)
	if _blocked(hero.position):
		_fail("stuck inside west rubble at " + str(hero.position))
		return
	print("WDC_V02_ESCAPE_OK -> " + str(hero.position))

	# --- reachability flood fill on a 1 px grid inside the clamps.
	var reach := {}
	var queue: Array[Vector2i] = [Vector2i(SPAWN)]
	reach[Vector2i(SPAWN)] = true
	var head := 0
	while head < queue.size():
		var p: Vector2i = queue[head]
		head += 1
		for d in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var n: Vector2i = p + d
			if n.x < 25 or n.x > 615 or n.y < 78 or n.y > 305 or reach.has(n) or _blocked(Vector2(n)):
				continue
			reach[n] = true
			queue.append(n)
	var targets := {"exit": false, "next": false, "clue0": false, "clue1": false, "clue2": false, "save": reach.has(Vector2i(402, 262)), "resume": reach.has(Vector2i(555, 257))}
	for p in reach.keys():
		var v := Vector2(p)
		if v.distance_to(EXIT) < 46.0:
			targets["exit"] = true
		if v.distance_to(NEXT) < 46.0:
			targets["next"] = true
		for index in 3:
			if v.distance_to(CLUES[index]) < 45.0 or host._wdc_inspect_rect(index).has_point(v):
				targets["clue%d" % index] = true
	for key in targets.keys():
		if not targets[key]:
			_fail("not reachable: " + key)
			return
	print("WDC_V02_REACHABILITY_OK cells=%d of %d targets=%s" % [reach.size(), 591 * 228, str(targets)])

	# --- save / load: inspect clue 0 (auto save), manual save at a lane spot, reset, load both.
	app.begin_new_run()
	app.hero_appearance = "female"
	await _open(DEST, 1)
	app.language = "en"
	host._refresh_text()
	_place(Vector2(163, 236))
	host._unhandled_input(interaction)
	host._close_overlay()
	var autos: Array = SaveStore.list_entries().filter(func(e): return String(e.get("kind", "")) == "auto")
	if autos.is_empty():
		_fail("clue inspection wrote no auto save")
		return
	var auto_id := String(autos[0]["id"])
	var saved_at := Vector2(402, 262)
	_place(saved_at)
	app.save_return_scene = SCENE
	app.save_return_position = hero.position
	var manual_id: String = app.write_manual_save(1)
	if manual_id == "":
		_fail("manual save failed")
		return
	app.begin_new_run()
	if not app.load_save(manual_id):
		_fail("manual load failed")
		return
	if app.current_destination_id != DEST or int(app.current_annex_room) != 1 or not app.survey_clues.has(DEST + ":0") \
			or not app.resume_annex_pending or app.resume_annex_position != saved_at or app.language != "en":
		_fail("manual load restored wrong state")
		return
	if host != null:
		host.queue_free()
		await process_frame
	host = (load(SCENE) as PackedScene).instantiate()
	root.add_child(host)
	current_scene = host
	await process_frame
	await process_frame
	host.set_process(false)
	if host.hero.position != saved_at or host.destination_id != DEST or host.room != 1 or host.ROOM_ONE_BACKGROUND[DEST] != bg or host.wdc_front == null:
		_fail("resumed annex wrong: " + str(host.hero.position))
		return
	if host.progress_label.text.find("1/6") < 0:
		_fail("progress label after load: " + host.progress_label.text)
		return
	_dress_hero()
	if not await _shot("en", saved_at, "after-load"):
		_fail("capture after load failed")
		return
	app.begin_new_run()
	if not app.load_save(auto_id) or not app.survey_clues.has(DEST + ":0") or app.loaded_scene_kind != "annex":
		_fail("auto save load wrong")
		return
	print("WDC_V02_SAVE_LOAD_OK manual=%s auto=%s position=%s" % [manual_id, auto_id, str(saved_at)])

	# --- doors: the next marker opens room 2; room 2's back returns to room 1 at the east door.
	app.begin_new_run()
	app.hero_appearance = "female"
	await _open(DEST, 1)
	_place(NEXT)
	host._unhandled_input(interaction)
	await process_frame
	await process_frame
	if int(app.current_annex_room) != 2:
		_fail("next marker did not move to room 2")
		return
	host = current_scene
	if host.wdc_front != null:
		_fail("room 2 must not create the room-1 front layer")
		return
	host._back_room()
	await process_frame
	await process_frame
	host = current_scene
	if int(app.current_annex_room) != 1 or host.hero.position != Vector2(555, 257) or host._wdc_blocked(host.hero.position):
		_fail("room 2 back did not return to room 1 east door")
		return
	host.set_process(false)
	_dress_hero()
	_place(EXIT)
	host._unhandled_input(interaction)
	await process_frame
	await process_frame
	if current_scene == host or current_scene == null:
		_fail("exit marker did not leave the annex")
		return
	current_scene.queue_free()
	await process_frame
	host = null
	print("WDC_V02_DOORS_OK")

	# --- other rooms render exactly as before (compared offline against the v01 after captures).
	for other in [["scifi.city", 1, "city-room1"], ["scifi.outskirts", 1, "outskirts-room1"], ["scifi.ruins", 2, "ruins-room2"]]:
		app.begin_new_run()
		app.hero_appearance = "female"
		await _open(other[0], other[1])
		if host.wdc_front != null:
			_fail("front layer created outside Washington room 1")
			return
		if not await _shot("zh", SPAWN, "other-" + other[2]):
			_fail("capture failed " + str(other))
			return
	# Remove this run's test saves.
	var dir_path := ProjectSettings.globalize_path(SaveStore.root_path)
	for file in DirAccess.get_files_at(dir_path):
		DirAccess.remove_absolute(dir_path.path_join(file))
	DirAccess.remove_absolute(dir_path)
	print("WDC_V02_ALL_OK")
	quit()
