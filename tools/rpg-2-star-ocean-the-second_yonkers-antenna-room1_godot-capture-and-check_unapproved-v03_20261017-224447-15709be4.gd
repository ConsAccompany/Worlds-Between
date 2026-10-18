extends SceneTree

# Yonkers antenna corridor room 1 v03 (UNAPPROVED candidate; v03 art pass, same layout as v02): native Godot 640x360 zh/en captures (entry,
# approach + interact, traversal, occlusion) and focused checks: header fit, caption/marker clearance, all six
# clues by real `interact`, three transitions, collision with slide, y-sort depth (probe sprite), reachability.
# Usage: Godot --path game -s <this file> -- <output dir> <stamp-id>
const SCENE := "res://scenes/survey_annex.tscn"
const APPROVED_HERO_IDLE := preload("res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
const DEST := "scifi.outskirts"
const CLUES := [Vector2(163, 165), Vector2(320, 165), Vector2(477, 165)]
const MARKERS := [Vector2(163, 228), Vector2(320, 228), Vector2(477, 228)]
const SPAWN := Vector2(87, 261)
const EXIT := Vector2(57, 257)
const NEXT := Vector2(580, 257)
const RESUME := Vector2(555, 257)

var app: Node
var host: Node2D
var hero: Sprite2D
var folder := ""
var stamp := ""
var interaction := InputEventAction.new()
var probe: ImageTexture
var antenna_images: Array[Image] = []


func _initialize() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	push_error(message)
	print("YK1_V03_FAIL " + message)
	Input.action_release("move_left")
	Input.action_release("move_right")
	Input.action_release("move_up")
	Input.action_release("move_down")
	quit(1)


func _grab() -> Image:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	return root.get_viewport().get_texture().get_image()


func _dress_hero() -> void:
	hero = host.hero
	# Capture-only reference: the creator-approved female south idle at 48 logical px (as in every room review).
	hero.texture = APPROVED_HERO_IDLE
	hero.scale = Vector2(0.5, 0.5)
	hero.offset = Vector2(0, -40)


func _probe_hero() -> void:
	# Solid 12x40 magenta stand-in so depth can be measured by counting its visible pixels.
	hero.texture = probe
	hero.scale = Vector2.ONE
	hero.offset = Vector2(0, -20)


func _open(destination: String, room: int) -> void:
	if host != null and is_instance_valid(host):
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


func _shot(language: String, at: Vector2, label: String) -> bool:
	app.language = language
	_place(at)
	host._refresh_text()
	var image: Image = await _grab()
	if image.get_size() != Vector2i(640, 360):
		push_error("Expected 640x360, got " + str(image.get_size()))
		return false
	var path := folder.path_join("rpg-2-star-ocean-the-second_yonkers-antenna-room1_v03-godot-%s-%s-640x360_%s.png" % [language, label, stamp])
	if image.save_png(path) != OK:
		return false
	print("YK1_V03_CAPTURE %s at=%s" % [path, str(at)])
	return true


func _hold(actions: Array, done: Callable, limit := 900) -> int:
	host.set_process(true)
	for action in actions:
		Input.action_press(action)
	var frames := 0
	while not done.call() and frames < limit:
		await process_frame
		frames += 1
	for action in actions:
		Input.action_release(action)
	await process_frame
	host.set_process(false)
	return frames


func _walk_until_stopped(start: Vector2, action: String, limit := 300) -> Vector2:
	_place(start)
	var state := {"last": Vector2(-999, -999), "still": 0}
	var stop := func():
		if hero.position.distance_to(state["last"]) < 0.01:
			state["still"] += 1
		else:
			state["still"] = 0
		state["last"] = hero.position
		return state["still"] >= 6
	await _hold([action], stop, limit)
	return hero.position


func _blocked(at: Vector2) -> bool:
	return host._yonkers_blocked(at)


func _magenta(image: Image, at: Vector2) -> int:
	var count := 0
	for y in range(int(at.y) - 42, int(at.y) + 2):
		for x in range(int(at.x) - 8, int(at.x) + 8):
			if x < 0 or y < 0 or x >= 640 or y >= 360:
				continue
			var c := image.get_pixel(x, y)
			if c.r > 0.95 and c.g < 0.05 and c.b > 0.95:
				count += 1
	return count


func _antenna_alpha(index: int, at: Vector2i) -> float:
	# Screen pixel -> antenna sprite texel alpha (sprite top-left = (clue x - 64, 58)).
	var image: Image = antenna_images[index]
	var local := at - Vector2i(int(CLUES[index].x) - 64, 58)
	if local.x < 0 or local.y < 0 or local.x >= image.get_width() or local.y >= image.get_height():
		return 0.0
	return image.get_pixel(local.x, local.y).a


func _rect_clear_of_antennas(rect: Rect2) -> int:
	var hits := 0
	for y in range(int(rect.position.y), int(rect.end.y)):
		for x in range(int(rect.position.x), int(rect.end.x)):
			for index in 3:
				if _antenna_alpha(index, Vector2i(x, y)) > 0.0:
					hits += 1
	return hits


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	folder = args[0]
	stamp = args[1]
	interaction.action = "interact"
	interaction.pressed = true
	var probe_image := Image.create(12, 40, false, Image.FORMAT_RGBA8)
	probe_image.fill(Color(1, 0, 1, 1))
	probe = ImageTexture.create_from_image(probe_image)
	Engine.max_fps = 60
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(640, 360)
	SaveStore.root_path = "user://test-saves/yonkers-room1-v03-%s" % stamp
	app = root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = "female"
	DirAccess.make_dir_recursive_absolute(folder)
	await _open(DEST, 1)
	for texture in host.YONKERS_ROOM_ONE_ANTENNAS:
		antenna_images.append(texture.get_image())

	# --- structure: room-1 build only, three y-sorted antennas, nearest filtering, foreground above the heroine.
	var antennas := host.find_children("YonkersAntenna*", "Sprite2D", false, false)
	var fg := host.find_children("YonkersForeground", "Sprite2D", false, false)
	if not host.yonkers_room_one or antennas.size() != 3 or fg.size() != 1 or not host.y_sort_enabled \
			or host.texture_filter != CanvasItem.TEXTURE_FILTER_NEAREST or fg[0].z_index != 1:
		_fail("room 1 v03 structure missing")
		return
	print("YK1_V03_PLATE " + host.ROOM_ONE_BACKGROUND[DEST].resource_path + " " + str(host.ROOM_ONE_BACKGROUND[DEST].get_size()))
	for node in antennas:
		print("YK1_V03_ANTENNA %s pos=%s tex=%s size=%s" % [node.name, str(node.position), node.texture.resource_path, str(node.texture.get_size())])
	print("YK1_V03_FOREGROUND " + fg[0].texture.resource_path)
	for at in [SPAWN, EXIT, NEXT, RESUME]:
		if _blocked(at):
			_fail("door/spawn point inside a blocker " + str(at))
			return

	# --- HUD clearance (v03): no antenna texel above screen y 66; the 62 px header hides nothing of A, B or C.
	for index in 3:
		var image: Image = antenna_images[index]
		var top_row := -1
		for y in image.get_height():
			for x in image.get_width():
				if image.get_pixel(x, y).a > 0.0:
					top_row = y
					break
			if top_row >= 0:
				break
		var screen_top := 58 + top_row
		var under_header := 0
		for y in range(0, maxi(0, 62 - 58)):
			for x in image.get_width():
				if image.get_pixel(x, y).a > 0.0:
					under_header += 1
		print("YK1_V03_HUD_CLEAR antenna=%d top_screen_y=%d texels_under_header=%d" % [index, screen_top, under_header])
		if screen_top < 66 or under_header != 0:
			_fail("antenna %d reaches under the 62 px header (top y %d)" % [index, screen_top])
			return

	# --- header: English title, Save and the widened back button all fit inside 640 px.
	for language in ["zh", "en"]:
		app.language = language
		host._refresh_text()
		await process_frame
		var title_right: float = host.title_label.position.x + host.title_label.get_minimum_size().x
		var back: Button = host.back_button
		var save: Button = host.save_button
		var need: float = back.get_combined_minimum_size().x
		print("YK1_V03_HEADER_%s title_right=%.1f save=[%.0f..%.0f] back=[%.0f..%.0f] back_text_min=%.1f '%s'" % [language, title_right,
				save.position.x, save.position.x + save.size.x, back.position.x, back.position.x + back.size.x, need, back.text])
		if title_right >= save.position.x - 4.0 or need > back.size.x + 0.01 or back.position.x + back.size.x > 632.0 \
				or save.position.x + save.size.x > back.position.x - 4.0:
			_fail("header does not fit in " + language)
			return

	# --- captions and markers never cover an antenna (antenna texel alpha under each rect).
	for language in ["zh", "en"]:
		app.language = language
		host._refresh_text()
		await process_frame
		for index in 3:
			var label: Label = host.clue_labels[index]
			var r := Rect2(label.position, label.get_minimum_size())
			var marker := Rect2(MARKERS[index] - Vector2(16, 16), Vector2(32, 32))
			var hits := _rect_clear_of_antennas(r) + _rect_clear_of_antennas(marker)
			print("YK1_V03_CAPTION_%s %d '%s' rect=%s antenna_texels_under=%d" % [language, index, label.text, str(r), hits])
			if hits != 0 or r.end.x > 632.0:
				_fail("caption or marker %d covers an antenna in %s" % [index, language])
				return

	# --- captures (separate zh and en files).
	var shots := []
	for language in ["zh", "en"]:
		shots.append_array([
			[language, SPAWN, "entry"],
			[language, Vector2(163, 238), "approach-a"], [language, Vector2(320, 238), "approach-b"], [language, Vector2(477, 238), "approach-c"],
			[language, Vector2(262, 262), "b-dish-from-lane"],
			[language, Vector2(170, 180), "occlusion-behind-a"], [language, Vector2(482, 180), "occlusion-behind-c"],
			[language, Vector2(366, 192), "beside-b"], [language, Vector2(28, 270), "west-stair"],
		])
	for shot in shots:
		if _blocked(shot[1]):
			_fail("capture position is inside a blocker " + str(shot))
			return
		if not await _shot(shot[0], shot[1], shot[2]):
			_fail("capture failed " + str(shot))
			return
	# interact captures: the clue sheet opened by a real `interact` at the floor marker.
	for pair in [["zh", 0], ["zh", 1], ["zh", 2], ["en", 0], ["en", 1], ["en", 2]]:
		app.language = pair[0]
		host._close_overlay()
		_place(Vector2(MARKERS[pair[1]].x, 238))
		host._unhandled_input(interaction)
		if not host.overlay.visible or host.overlay_clue_index != pair[1]:
			_fail("interact did not open clue %d" % pair[1])
			return
		if not await _shot(pair[0], hero.position, "interact-%s" % ["a", "b", "c"][pair[1]]):
			_fail("interact capture failed")
			return
	host._close_overlay()
	app.survey_clues.clear()
	host._refresh_text()
	# traversal: a real held-input walk along the lane, captured mid-way after release (both languages).
	for pair in [["zh", Vector2(87, 261), 240.0], ["en", Vector2(250, 261), 420.0]]:
		app.language = pair[0]
		host._refresh_text()
		_place(pair[1])
		var target: float = pair[2]
		await _hold(["move_right"], func(): return hero.position.x >= target)
		_dress_hero()
		if not await _shot(pair[0], hero.position, "traversal"):
			_fail("traversal capture failed")
			return
	# entry with the actual runtime heroine sprite (not the review reference), both languages.
	for language in ["zh", "en"]:
		app.language = language
		host._refresh_text()
		_place(SPAWN)
		hero.texture = load("res://scripts/character_directional_idle.gd").texture_for("protagonist-female", "south")
		hero.scale = Vector2.ONE
		hero.offset = Vector2(0, -20)
		if not await _shot(language, SPAWN, "entry-runtime-heroine"):
			_fail("runtime heroine capture failed")
			return
	_dress_hero()

	# --- depth: a probe is hidden behind each antenna (feet above the 210 base line) and fully drawn in front.
	_probe_hero()
	app.language = "zh"
	host._refresh_text()
	for index in 3:
		var x: float = [168.0, 320.0, 477.0][index]
		var behind := Vector2(x, 182)
		var front := Vector2(x, 236)
		var hidden := -1
		if index == 1:
			# The strip behind the dish is a raised cable trough: the heroine can never stand fully hidden there.
			for y in range(166, 212):
				if not _blocked(Vector2(x, y)):
					_fail("strip behind the dish is walkable at y %d" % y)
					return
		else:
			_place(behind)
			var img_behind: Image = await _grab()
			hidden = 480 - _magenta(img_behind, behind)
		_place(front)
		var img_front: Image = await _grab()
		var shown := _magenta(img_front, front)
		print("YK1_V03_DEPTH antenna=%d behind_hidden_px=%d front_visible_px=%d/480" % [index, hidden, shown])
		if (index != 1 and (hidden < 40 or hidden > 400)) or shown != 480:
			_fail("depth order wrong at antenna %d" % index)
			return
	# The heroine is drawn over the plate everywhere else (lane spot), and under the foreground shrubs on the stair.
	_place(Vector2(400, 262))
	var lane_visible := _magenta(await _grab(), Vector2(400, 262))
	_place(Vector2(26, 279))
	var stair_visible := _magenta(await _grab(), Vector2(26, 279))
	print("YK1_V03_DEPTH lane_visible=%d/480 west_stair_shrub_visible=%d/480" % [lane_visible, stair_visible])
	if lane_visible != 480 or stair_visible >= 480:
		_fail("lane or foreground depth wrong")
		return
	_dress_hero()

	# --- interactions: from the floor marker, the old side approach and from behind; no false positives.
	var content: Dictionary = host.CONTENT.DATA[DEST]
	app.language = "zh"
	for approach in ["marker", "side", "behind"]:
		app.survey_clues.clear()
		for index in 3:
			host._close_overlay()
			var c: Vector2 = CLUES[index]
			var at: Vector2 = {"marker": Vector2(c.x, 240), "side": Vector2(c.x + 39, 185), "behind": Vector2(c.x, 172)}[approach]
			if approach == "side" and index == 2:
				at = Vector2(c.x - 39, 185)  # east side of C is its battery; approach from the west instead
			if approach == "side" and index == 1:
				at = Vector2(c.x - 34, 185)  # the trough fills the east side of the dish; approach from the west
			if approach == "behind" and index == 1:
				at = Vector2(c.x + 43, 172)  # behind the dish is the cable trough; use the wall strip at its east end
			if _blocked(at):
				_fail("approach point blocked %s %d %s" % [approach, index, str(at)])
				return
			_place(at)
			host._unhandled_input(interaction)
			var key := "%s:%d" % [DEST, index]
			if not app.survey_clues.has(key) or host.overlay_clue_index != index or host.overlay_title.text != String(content[app.language]["clues"][index]["name"]):
				_fail("clue did not register: %s from %s" % [key, approach])
				return
	host._close_overlay()
	app.survey_clues.clear()
	for at in [Vector2(241, 261), Vector2(398, 261), Vector2(241, 200), Vector2(398, 205), Vector2(530, 270)]:
		_place(at)
		host._unhandled_input(interaction)
		if host.overlay.visible or app.survey_clues.size() != 0:
			_fail("unexpected clue at " + str(at))
			return
		if current_scene != host:
			_fail("a door fired at " + str(at))
			return
	print("YK1_V03_ROOM1_INTERACTIONS_OK 3x3 (marker, side, behind) no_false_positive=5")

	# --- lane walk with held input: start to the next-room marker, no snap, no back-step.
	_place(SPAWN)
	var lane := {"ok": true, "last": SPAWN.x}
	var frames := await _hold(["move_right"], func():
		if hero.position.x < lane["last"] or absf(hero.position.y - 261.0) > 0.01:
			lane["ok"] = false
		lane["last"] = hero.position.x
		return hero.position.x >= 578.0 or not lane["ok"])
	if not lane["ok"] or hero.position.x < 578.0:
		_fail("lane walk regressed at " + str(hero.position))
		return
	print("YK1_V03_LANE_WALK_OK x=%.1f frames=%d" % [hero.position.x, frames])
	_dress_hero()

	# --- collision: held input stops at each obstacle; openings stay open.
	var cases := [
		["antenna-a-from-front", Vector2(163, 250), "move_up", func(p): return p.y >= 212.0 and p.y < 217.0],
		["antenna-b-from-front", Vector2(320, 250), "move_up", func(p): return p.y >= 212.0 and p.y < 217.0],
		["antenna-c-from-front", Vector2(477, 250), "move_up", func(p): return p.y >= 212.0 and p.y < 217.0],
		["antenna-a-from-west", Vector2(108, 200), "move_right", func(p): return p.x < 124.0 and p.x > 119.0],
		["antenna-b-from-east", Vector2(380, 200), "move_left", func(p): return p.x >= 362.0 and p.x < 367.0],
		["antenna-c-from-west", Vector2(410, 195), "move_right", func(p): return p.x < 443.0 and p.x > 438.0],
		["back-wall", Vector2(272, 176), "move_up", func(p): return p.y >= 166.0 and p.y < 171.0],
		["cable-drum", Vector2(240, 200), "move_up", func(p): return p.y >= 186.0 and p.y < 191.0],
		["planter", Vector2(70, 200), "move_up", func(p): return p.y >= 186.0 and p.y < 191.0],
		["west-pier", Vector2(70, 200), "move_left", func(p): return p.x >= 38.0 and p.x < 43.0],
		["east-wall", Vector2(560, 200), "move_right", func(p): return p.x < 602.0 and p.x > 597.0],
		["front-parapet", Vector2(320, 261), "move_down", func(p): return p.y < 281.0 and p.y > 276.0],
		["west-stair-open", Vector2(70, 260), "move_left", func(p): return is_equal_approx(p.x, 25.0)],
		["east-door-open", Vector2(560, 260), "move_right", func(p): return is_equal_approx(p.x, 615.0)],
	]
	for case in cases:
		if _blocked(case[1]):
			_fail("collision start inside blocker " + case[0])
			return
		var stopped: Vector2 = await _walk_until_stopped(case[1], case[2])
		if not case[3].call(stopped):
			_fail("collision case %s stopped at %s" % [case[0], str(stopped)])
			return
		print("YK1_V03_COLLISION %s -> %s" % [case[0], str(stopped)])
	# Diagonal input slides along the dish plinth's front instead of sticking.
	_place(Vector2(300, 216))
	await _hold(["move_up", "move_right"], func(): return false, 40)
	if hero.position.x < 330.0 or _blocked(hero.position):
		_fail("diagonal slide stuck at " + str(hero.position))
		return
	print("YK1_V03_SLIDE_OK -> " + str(hero.position))
	# An older save inside a new blocker (v01 had none) can walk out.
	_place(Vector2(320, 200))
	await _hold(["move_down"], func(): return not _blocked(hero.position), 120)
	if _blocked(hero.position):
		_fail("stuck inside antenna B plinth at " + str(hero.position))
		return
	print("YK1_V03_ESCAPE_OK -> " + str(hero.position))
	_dress_hero()

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
	var targets := {"exit": false, "next": false, "clue0": false, "clue1": false, "clue2": false, "resume": reach.has(Vector2i(RESUME)),
			"behind_a": reach.has(Vector2i(170, 180)), "beside_b": reach.has(Vector2i(366, 192)), "behind_c": reach.has(Vector2i(482, 180))}
	for key in reach.keys():
		var v := Vector2(key)
		if v.distance_to(EXIT) < 46.0:
			targets["exit"] = true
		if v.distance_to(NEXT) < 46.0:
			targets["next"] = true
		for index in 3:
			if v.distance_to(CLUES[index]) < 45.0 or v.distance_to(MARKERS[index]) < 42.0:
				targets["clue%d" % index] = true
	for key in targets.keys():
		if not targets[key]:
			_fail("not reachable: " + key)
			return
	print("YK1_V03_REACHABILITY_OK cells=%d targets=%s" % [reach.size(), str(targets)])

	# --- transitions: next -> room 2 (clues 3-5 by real interact), back -> room 1 east door, exit -> surface.
	# Room 1's clues 0-2 are collected first by real `interact` at the floor markers, so the run ends at 6/6.
	app.survey_clues.clear()
	for index in 3:
		host._close_overlay()
		_place(Vector2(MARKERS[index].x, 240))
		host._unhandled_input(interaction)
	host._close_overlay()
	_place(NEXT)
	host._unhandled_input(interaction)
	await process_frame
	await process_frame
	if int(app.current_annex_room) != 2 or current_scene == host:
		_fail("next marker did not open room 2")
		return
	host = current_scene
	host.set_process(false)
	_dress_hero()
	if host.yonkers_room_one or host.y_sort_enabled or host.find_children("YonkersAntenna*", "Sprite2D", false, false).size() != 0:
		_fail("room 2 picked up the room 1 build")
		return
	print("YK1_V03_TRANSITION_NEXT_OK room=2")
	for index in 3:
		host._close_overlay()
		_place(Vector2(CLUES[index].x + 39, 185))
		host._unhandled_input(interaction)
		if not app.survey_clues.has("%s:%d" % [DEST, index + 3]):
			_fail("room 2 clue %d did not register" % (index + 3))
			return
	host._close_overlay()
	var all_six := 0
	for index in 6:
		if app.survey_clues.has("%s:%d" % [DEST, index]):
			all_six += 1
	if all_six != 6 or host._clue_count() != 6:
		_fail("expected all six clues, got %d" % all_six)
		return
	print("YK1_V03_ALL_SIX_CLUES_OK 6/6")
	host._back_room()
	await process_frame
	await process_frame
	host = current_scene
	if int(app.current_annex_room) != 1 or host.hero.position != RESUME or not host.yonkers_room_one or host._yonkers_blocked(host.hero.position):
		_fail("room 2 back did not return to room 1 east door")
		return
	host.set_process(false)
	_dress_hero()
	for language in ["zh", "en"]:
		if not await _shot(language, RESUME, "returned-from-room2"):
			_fail("return capture failed")
			return
	print("YK1_V03_TRANSITION_BACK_OK at=%s" % str(host.hero.position))
	_place(EXIT)
	host._unhandled_input(interaction)
	await process_frame
	await process_frame
	if current_scene == host or current_scene == null or current_scene.scene_file_path != "res://scenes/scifi_exploration_area.tscn":
		_fail("exit marker did not return to the surface")
		return
	print("YK1_V03_TRANSITION_EXIT_OK " + current_scene.scene_file_path)
	current_scene.queue_free()
	await process_frame
	host = null

	# --- other survey rooms do not pick up the room 1 build.
	for other in [["scifi.city", 1], ["scifi.city", 2], ["scifi.ruins", 1], ["scifi.ruins", 2]]:
		app.begin_new_run()
		app.hero_appearance = "female"
		await _open(other[0], other[1])
		if host.yonkers_room_one or host.find_children("YonkersAntenna*", "Sprite2D", false, false).size() != 0 or host.y_sort_enabled:
			_fail("room 1 build leaked into " + str(other))
			return
	print("YK1_V03_ISOLATION_OK 4 other rooms")
	var dir_path := ProjectSettings.globalize_path(SaveStore.root_path)
	if DirAccess.dir_exists_absolute(dir_path):
		for file in DirAccess.get_files_at(dir_path):
			DirAccess.remove_absolute(dir_path.path_join(file))
		DirAccess.remove_absolute(dir_path)
	print("YK1_V03_ALL_OK")
	quit()
