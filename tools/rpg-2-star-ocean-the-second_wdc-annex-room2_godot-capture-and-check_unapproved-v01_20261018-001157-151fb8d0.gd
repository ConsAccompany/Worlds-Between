extends SceneTree

# UNAPPROVED v01 Washington survey annex room 2 (scifi.ruins, 记录内室 / Records Chamber) records-chamber
# fixtures: real Godot 640x360 captures (zh and en) plus real-key-input walk, interaction, collision,
# occlusion, reachability, door/return transitions and save/load through the real Save screen and title-menu
# Load (mouse clicks), in isolated user data (run with APPDATA pointed at a temp dir).
# Usage: Godot --path game -s <this file> -- <capture dir> <probe dir> <stamp-id> --wdc-records-chamber-v01
# Captures for review go to <capture dir>; hero-hidden probe frames used by the pixel check go to <probe dir>.
# Default-off proof (no flag): ... -- <capture dir> <probe dir> <stamp-id> <HEAD survey_annex.gd copy> --default-off-parity
const SCENE := "res://scenes/survey_annex.tscn"
const APPROVED_HERO_IDLE := preload("res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
const CLUES := [Vector2(163, 165), Vector2(320, 165), Vector2(477, 165)]
const DEST := "scifi.ruins"
const SPAWN := Vector2(87, 261)
const EXIT := Vector2(57, 257)
const TERMINAL := Vector2(320, 263)
const FLAG := "--wdc-records-chamber-v01"
const TAG := "WDC_R2_V01"
# Default-off parity (r1, 2026-10-18): the c3ff819c default layout fix changes the Washington English header on
# purpose, so default-off English may differ from HEAD only above this row; Chinese must stay 0 px.
const HEADER_ROWS := 62
# The default-off baseline is pinned (r1): survey_annex.gd before the records-chamber branch, git blob eecdcca at
# 7370739 and 7553581. Once the candidate is committed, HEAD is no longer that baseline, so the copy must come from
# `git show 7370739:game/scripts/survey_annex.gd`; any other file fails.
const BASELINE_SURVEY_ANNEX_SHA256_TEXT_LF := "bedc4adbff32ae08104674d2cabffdb466d848e0a419905c2d0b487cf3cea5c9"

var app: Node
var host: Node2D
var hero: Sprite2D
var folder := ""
var probe := ""
var stamp := ""
var dressed := true
var results := {}


func _initialize() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	push_error(message)
	print(TAG + "_FAIL " + message)
	results["failed"] = message
	_write_results()
	quit(1)


func _write_results() -> void:
	var file := FileAccess.open(probe.path_join("godot-check-results.json"), FileAccess.WRITE)
	if file != null:
		file.store_string(JSON.stringify(results, "  "))


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
	if not dressed:
		return
	# Capture-only reference: the creator-approved female south idle at 48 logical px (as in room 1 v02).
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


func _adopt_current_scene() -> void:
	# After a real door or load transition: take the scene the game itself switched to.
	await process_frame
	await process_frame
	host = current_scene
	host.set_process(false)
	_dress_hero()


func _adopt_screen(scene_file: String) -> bool:
	await process_frame
	await process_frame
	if current_scene == null or not current_scene.scene_file_path.ends_with(scene_file):
		_fail("expected %s, got %s" % [scene_file, current_scene.scene_file_path if current_scene != null else "<none>"])
		return false
	return true


# A left click at the control's centre, delivered through Input and the viewport like a mouse.
func _click(control: Control) -> void:
	var at := control.get_global_rect().get_center()
	for pressed in [true, false]:
		var event := InputEventMouseButton.new()
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = pressed
		event.position = at
		event.global_position = at
		Input.parse_input_event(event)
		await process_frame
	await process_frame


# Capture the scene as the game left it (no repositioning), in the given language.
func _capture_as(language: String, label: String) -> bool:
	app.language = language
	host._refresh_text()
	var path := folder.path_join(_name(language, label))
	if not await _capture(path):
		_fail("capture " + label)
		return false
	print("%s_CAPTURE %s at=%s" % [TAG, path, str(hero.position)])
	return true


func _name(language: String, label: String) -> String:
	return "rpg-2-star-ocean-the-second_wdc-annex-room2_v01-godot-%s-%s-640x360_%s.png" % [language, label, stamp]


func _shot(language: String, at: Vector2, label: String, with_probe := false) -> bool:
	app.language = language
	hero.position = at
	host._refresh_text()
	var path := folder.path_join(_name(language, label))
	if not await _capture(path):
		return false
	print("%s_CAPTURE %s at=%s" % [TAG, path, str(at)])
	if with_probe:
		hero.visible = false
		var ok := await _capture(probe.path_join("probe-hidden-hero_%s_%s.png" % [language, label]))
		hero.visible = true
		if not ok:
			return false
	return true


# --- real input: key events go through Input, the InputMap and the viewport like a keyboard would.
func _key(keycode: Key, pressed: bool) -> void:
	# A real key press carries both codes: the game's actions bind physical keys, ui_cancel binds keycode.
	var event := InputEventKey.new()
	event.keycode = keycode
	event.physical_keycode = keycode
	event.pressed = pressed
	Input.parse_input_event(event)


func _tap(keycode: Key) -> void:
	_key(keycode, true)
	await process_frame
	_key(keycode, false)
	await process_frame
	await process_frame


func _hold(keys: Array, done: Callable, limit := 900) -> int:
	host.set_process(true)
	for k in keys:
		_key(k, true)
	var frames := 0
	while not done.call() and frames < limit:
		await process_frame
		frames += 1
	for k in keys:
		_key(k, false)
	await process_frame
	host.set_process(false)
	return frames


func _walk_until_stopped(start: Vector2, keys: Array, limit := 300) -> Vector2:
	hero.position = start
	var state := {"last": Vector2(-999, -999), "still": 0}
	var stop := func():
		if hero.position.distance_to(state["last"]) < 0.01:
			state["still"] += 1
		else:
			state["still"] = 0
		state["last"] = hero.position
		return state["still"] >= 6
	await _hold(keys, stop, limit)
	return hero.position


func _blocked(at: Vector2) -> bool:
	return host._wdc_room_two_blocked(at)


# Default-off proof (run WITHOUT the opt-in flag): Washington rooms 1 and 2 drawn by the working-tree script and
# by a given copy of the tracked HEAD script (loaded in memory onto the same scene) must be pixel-identical in zh
# and identical below the 62-row header in en (r1: intentional c3ff819c header fix), and room 2 must build none of
# the records-chamber nodes.
# Usage: Godot --path game -s <this file> -- <capture dir> <probe dir> <stamp-id> <HEAD survey_annex.gd copy> --default-off-parity
func _default_off_parity(head_path: String) -> void:
	if OS.get_cmdline_user_args().has(FLAG):
		_fail("the default-off parity run must not pass " + FLAG)
		return
	var head := GDScript.new()
	head.source_code = FileAccess.get_file_as_string(head_path)
	if head.source_code.replace("\r\n", "\n").sha256_text() != BASELINE_SURVEY_ANNEX_SHA256_TEXT_LF:
		_fail("baseline copy is not the pinned pre-candidate survey_annex.gd (create it with `git show 7370739:game/scripts/survey_annex.gd`): " + head_path)
		return
	if head.source_code.length() < 1000 or head.reload() != OK or head.source_code.contains(FLAG):
		_fail("HEAD script copy missing, failed to compile, or already contains the opt-in branch: " + head_path)
		return
	SaveStore.root_path = "user://test-saves/wdc-annex-room2-v01-parity-%s" % stamp
	app = root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = "female"
	var parity := {}
	for room in [1, 2]:
		for language in ["zh", "en"]:
			var images := {}
			for which in ["working-tree", "head"]:
				if host != null:
					host.queue_free()
					await process_frame
				app.language = language
				app.select_destination(DEST)
				app.current_annex_room = room
				host = (load(SCENE) as PackedScene).instantiate()
				if which == "head":
					host.set_script(head)
				root.add_child(host)
				current_scene = host
				await process_frame
				await process_frame
				host.set_process(false)
				if which == "working-tree":
					for node in host.get_children():
						if String(node.name).begins_with("WdcRecords"):
							_fail("default room %d built %s without the flag" % [room, node.name])
							return
					if host.wdc_room_two or (room == 2 and host.y_sort_enabled):
						_fail("default room 2 switched on the records-chamber branch")
						return
				await process_frame
				await RenderingServer.frame_post_draw
				images[which] = root.get_viewport().get_texture().get_image()
				images[which].convert(Image.FORMAT_RGBA8)
				var path := folder.path_join("rpg-2-star-ocean-the-second_wdc-annex-room2_v01-default-off-%s-room%d-%s-640x360_%s.png" % [which, room, language, stamp])
				images[which].save_png(path)
				print("%s_CAPTURE %s" % [TAG, path])
			var a: PackedByteArray = images["working-tree"].get_data()
			var b: PackedByteArray = images["head"].get_data()
			var differing := 0
			var below_header := 0
			for i in range(0, a.size(), 4):
				if a[i] != b[i] or a[i + 1] != b[i + 1] or a[i + 2] != b[i + 2] or a[i + 3] != b[i + 3]:
					differing += 1
					if i / 4 / 640 >= HEADER_ROWS:
						below_header += 1
			parity["room%d_%s" % [room, language]] = differing
			if a.size() != 640 * 360 * 4 or below_header != 0 or (language == "zh" and differing != 0):
				_fail("default room %d %s differs from HEAD in %d px (%d below the header)" % [room, language, differing, below_header])
				return
	results["default_off_parity_differing_pixels"] = parity
	results["ok"] = true
	_write_results()
	print("%s_DEFAULT_OFF_PARITY_OK %s" % [TAG, JSON.stringify(parity)])
	quit()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	folder = args[0]
	probe = args[1]
	stamp = args[2]
	Engine.max_fps = 60
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(640, 360)
	DirAccess.make_dir_recursive_absolute(folder)
	DirAccess.make_dir_recursive_absolute(probe)
	if args.has("--default-off-parity"):
		await _default_off_parity(args[3])
		return
	if not args.has(FLAG):
		_fail("run with " + FLAG)
		return
	SaveStore.root_path = "user://test-saves/wdc-annex-room2-v01-%s" % stamp
	app = root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = "female"
	results["save_root"] = ProjectSettings.globalize_path(SaveStore.root_path)
	results["user_data_dir"] = OS.get_user_data_dir()

	# --- integration: opt-in builds three fixtures and the terminal table in room 2 only.
	await _open(DEST, 1)
	if host.wdc_room_two or host.y_sort_enabled:
		_fail("room 1 must not build the room-2 fixtures")
		return
	await _open(DEST, 2)
	if not host.wdc_room_two or not host.y_sort_enabled or host.wdc_room_two_markers.size() != 4:
		_fail("room 2 fixtures missing under the opt-in flag")
		return
	var textures := []
	for node in host.get_children():
		if node is Sprite2D and String(node.name).begins_with("WdcRecords"):
			textures.append("%s %s pos=%s offset=%s filter=%d" % [node.name, node.texture.resource_path, str(node.position), str(node.offset), node.texture_filter])
	if textures.size() != 4:
		_fail("expected 4 fixture sprites, got %d" % textures.size())
		return
	for line in textures:
		print(TAG + "_SPRITE " + line)
	results["sprites"] = textures
	var bg: Texture2D = host.ROOM_TWO_BACKGROUND[DEST]
	print(TAG + "_BACKGROUND " + bg.resource_path)

	# --- header and labels (unchanged text); report the title edge against Save.
	for language in ["zh", "en"]:
		app.language = language
		host._refresh_text()
		var labels := []
		for label in host.clue_labels:
			labels.append(label.text)
		var right: float = host.title_label.position.x + host.title_label.get_minimum_size().x
		results["text_" + language] = {"title": host.title_label.text, "title_size": int(host.title_label.get_theme_font_size("font_size")),
				"title_right": right, "save_left": host.save_button.position.x, "clues": labels, "terminal": host.terminal_label.text,
				"exit": host.exit_label.text, "help": host.help_label.text}
		print("%s_TEXT_%s %s" % [TAG, language, JSON.stringify(results["text_" + language])])
		if right > host.save_button.position.x - 4.0:
			_fail("%s title (right edge %.0f) runs under Save (%.0f)" % [language, right, host.save_button.position.x])
			return

	# --- layout: clue names, lifted discs, terminal label and fixtures must not overlap (both languages).
	var avoid := []
	for node in host.get_children():
		if node is Sprite2D and String(node.name).begins_with("WdcRecords"):
			avoid.append(Rect2(node.position + node.offset, node.texture.get_size()))
	for index in 3:
		avoid.append(Rect2(CLUES[index] + host.WDC_ROOM_TWO_MARKER_LIFT - Vector2(16, 16), Vector2(32, 32)))
	avoid.append(Rect2(TERMINAL - Vector2(16, 16), Vector2(32, 32)))
	var layout := {}
	for language in ["zh", "en"]:
		app.language = language
		host._refresh_text()
		var rects := []
		for label in host.clue_labels + [host.terminal_label]:
			var text_size: Vector2 = label.get_minimum_size()
			var x: float = label.position.x + ((label.size.x - text_size.x) / 2.0 if label.horizontal_alignment == HORIZONTAL_ALIGNMENT_CENTER else 0.0)
			var text_rect := Rect2(Vector2(x, label.position.y), text_size)
			for other in avoid + rects:
				if text_rect.intersects(other):
					_fail("%s label '%s' %s overlaps %s" % [language, label.text, str(text_rect), str(other)])
					return
			if text_rect.position.x < 0 or text_rect.end.x > 640 or text_rect.position.y < 62:
				_fail("%s label '%s' leaves the room view %s" % [language, label.text, str(text_rect)])
				return
			rects.append(text_rect)
		layout[language] = rects.map(func(r): return str(r))
	results["label_layout"] = layout
	print("%s_LAYOUT_OK %s" % [TAG, JSON.stringify(layout)])

	# --- captures: entry, in front of each fixture, behind each fixture (occlusion: head above the top,
	# body hidden, beside the lifted disc), terminal approach.
	var shots := [["zh", SPAWN, "entry", true], ["en", SPAWN, "entry", true]]
	for index in 3:
		var front: Vector2 = Vector2(CLUES[index].x, 230)
		shots.append(["zh", front, "front-clue-%d" % (index + 3), true])
		shots.append(["en", front, "front-clue-%d" % (index + 3), true])
		shots.append(["zh", Vector2(CLUES[index].x - 28, 196), "occlusion-behind-clue-%d" % (index + 3), true])
		shots.append(["en", Vector2(CLUES[index].x - 28, 196), "occlusion-behind-clue-%d" % (index + 3), true])
	shots.append(["zh", Vector2(320, 268), "terminal-approach", true])
	shots.append(["en", Vector2(320, 268), "terminal-approach", true])
	for shot in shots:
		if _blocked(shot[1]):
			_fail("capture position is inside a blocker " + str(shot))
			return
		if not await _shot(shot[0], shot[1], shot[2], shot[3]):
			_fail("capture failed " + str(shot))
			return

	# --- real-key interactions: walk with WASD from the spawn to each fixture and press E; Esc closes.
	var content: Dictionary = host.CONTENT.DATA[DEST]
	app.survey_clues.clear()
	host._refresh_text()
	hero.position = SPAWN
	for index in 3:
		var target_x: float = CLUES[index].x
		# along the lane, then up until the fixture base stops her
		await _hold([KEY_D] if hero.position.x < target_x else [KEY_A], func(): return absf(hero.position.x - target_x) < 2.5)
		if hero.position.y < 240.0:
			await _hold([KEY_S], func(): return hero.position.y >= 245.0)
			await _hold([KEY_D] if hero.position.x < target_x else [KEY_A], func(): return absf(hero.position.x - target_x) < 2.5)
		var stopped: Vector2 = await _walk_until_stopped(hero.position, [KEY_W])
		if stopped.y < 226.0 or stopped.y > 228.5:
			_fail("fixture %d front did not stop her: %s" % [index + 3, str(stopped)])
			return
		await _tap(KEY_E)
		var key := "%s:%d" % [DEST, index + 3]
		if not host.overlay.visible or host.overlay_clue_index != index + 3 or not app.survey_clues.has(key):
			_fail("E at fixture %d did not open clue %s (at %s)" % [index + 3, key, str(hero.position)])
			return
		for language in ["zh", "en"]:
			app.language = language
			host._refresh_text()
			if host.overlay_title.text != String(content[language]["clues"][index + 3]["name"]) or host.overlay_body.text != String(content[language]["clues"][index + 3]["text"]):
				_fail("overlay text differs from survey_content for clue %d %s" % [index + 3, language])
				return
			var path := folder.path_join(_name(language, "interaction-clue-%d" % (index + 3)))
			if not await _capture(path):
				_fail("interaction capture")
				return
			print("%s_CAPTURE %s" % [TAG, path])
		app.language = "zh"
		await _tap(KEY_ESCAPE)
		if host.overlay.visible:
			_fail("Esc did not close the clue overlay")
			return
		results["walk_to_clue_%d" % (index + 3)] = str(stopped)
		print("%s_REAL_INPUT_CLUE_%d_OK stopped=%s" % [TAG, index + 3, str(stopped)])
		await _hold([KEY_S], func(): return hero.position.y >= 245.0)
	# terminal: from the lane walk down to the table and press E (locked until six clues).
	await _hold([KEY_A] if hero.position.x > 320.0 else [KEY_D], func(): return absf(hero.position.x - 320.0) < 2.5)
	var at_table: Vector2 = await _walk_until_stopped(hero.position, [KEY_S])
	if at_table.y >= 272.0 or at_table.y < 270.0:
		_fail("terminal table did not stop her: " + str(at_table))
		return
	await _tap(KEY_E)
	if not host.overlay.visible or host.overlay_mode != "message" or host.overlay_body.text != app.text_for("survey_locked"):
		_fail("E at the terminal did not open the locked message at " + str(at_table))
		return
	for language in ["zh", "en"]:
		app.language = language
		host._refresh_text()
		var path := folder.path_join(_name(language, "interaction-terminal-locked"))
		if not await _capture(path):
			_fail("terminal capture")
			return
		print("%s_CAPTURE %s" % [TAG, path])
	app.language = "zh"
	await _tap(KEY_ESCAPE)
	results["walk_to_terminal"] = str(at_table)
	print("%s_REAL_INPUT_TERMINAL_OK stopped=%s" % [TAG, str(at_table)])
	# all six clues: the terminal moves to linking, and a solved survey recolours its marker.
	for index in 6:
		app.survey_clues["%s:%d" % [DEST, index]] = true
	await _tap(KEY_E)
	if host.overlay_mode != "link":
		_fail("terminal with six clues did not open linking: " + host.overlay_mode)
		return
	await _tap(KEY_ESCAPE)
	app.survey_solved[DEST] = true
	host._refresh_text()
	if not await _shot("zh", Vector2(410, 262), "terminal-solved-marker"):
		_fail("solved capture")
		return
	app.survey_solved.erase(DEST)
	app.survey_clues.clear()
	host._refresh_text()
	# no false positives on the lane between fixtures or beside them (the spawn is inside the exit radius, so not here)
	for at in [Vector2(241, 240), Vector2(398, 240), Vector2(241, 180), Vector2(398, 180), Vector2(87, 200), Vector2(560, 262)]:
		hero.position = at
		await _tap(KEY_E)
		if host.overlay.visible:
			_fail("unexpected overlay at " + str(at))
			return
	# every fixture also opens from behind and from both sides
	for index in 3:
		var c: Vector2 = CLUES[index]
		for at in [Vector2(c.x, 190), Vector2(c.x - 50, 205), Vector2(c.x + 50, 205), Vector2(c.x, 236)]:
			app.survey_clues.clear()
			if _blocked(at):
				_fail("approach point blocked %s" % str(at))
				return
			hero.position = at
			await _tap(KEY_E)
			if not host.overlay.visible or host.overlay_clue_index != index + 3:
				_fail("clue %d did not open from %s" % [index + 3, str(at)])
				return
			await _tap(KEY_ESCAPE)
	app.survey_clues.clear()
	host._refresh_text()
	print(TAG + "_INTERACTIONS_OK real keys: walk+E for 3 clues and the terminal; behind/sides/front 3x4; no lane false positives")

	# --- lane walk with a held key: exit marker east to the far side at constant y.
	hero.position = SPAWN
	var frames := await _hold([KEY_D], func(): return hero.position.x >= 600.0)
	if hero.position.x < 600.0 or absf(hero.position.y - SPAWN.y) > 0.01:
		_fail("lane walk regressed at " + str(hero.position))
		return
	results["lane_walk"] = {"to": str(hero.position), "frames": frames}
	print("%s_LANE_WALK_OK %s frames=%d" % [TAG, str(hero.position), frames])

	# --- collision with held keys: each obstacle stops her and she slides along it.
	var cases := [
		["clue-3-from-front", Vector2(163, 260), [KEY_W], func(p): return p.y >= 226.0 and p.y < 228.5],
		["clue-4-from-front", Vector2(320, 250), [KEY_W], func(p): return p.y >= 226.0 and p.y < 228.5],
		["clue-5-from-front", Vector2(477, 250), [KEY_W], func(p): return p.y >= 226.0 and p.y < 228.5],
		["clue-4-from-behind", Vector2(320, 150), [KEY_S], func(p): return p.y < 212.0 and p.y > 209.0],
		["clue-3-from-west", Vector2(90, 218), [KEY_D], func(p): return p.x < 116.0 and p.x > 113.0],
		["clue-3-from-east", Vector2(240, 218), [KEY_A], func(p): return p.x >= 215.0 and p.x < 218.0],
		["clue-5-from-east", Vector2(560, 218), [KEY_A], func(p): return p.x >= 528.0 and p.x < 531.0],
		["back-wall", Vector2(240, 160), [KEY_W], func(p): return p.y >= 114.0 and p.y < 117.0],
		["terminal-from-north", Vector2(300, 250), [KEY_S], func(p): return p.y < 272.0 and p.y > 269.0],
		["terminal-from-west", Vector2(220, 290), [KEY_D], func(p): return p.x < 258.0 and p.x > 255.0],
		["terminal-from-east", Vector2(420, 290), [KEY_A], func(p): return p.x >= 371.0 and p.x < 374.0],
		["near-edge-clamp", Vector2(200, 270), [KEY_S], func(p): return is_equal_approx(p.y, 305.0)],
		["west-wall", Vector2(120, 150), [KEY_A], func(p): return p.x >= 56.0 and p.x < 59.0],
		["west-back-corner", Vector2(50, 175), [KEY_W], func(p): return p.y >= 162.0 and p.y < 165.0],
		["east-wall", Vector2(540, 200), [KEY_D], func(p): return p.x < 600.0 and p.x > 597.0],
		["east-back-corner", Vector2(560, 170), [KEY_W], func(p): return p.y >= 144.0 and p.y < 147.0],
		["west-near-rubble", Vector2(90, 290), [KEY_A], func(p): return p.x >= 48.0 and p.x < 51.0],
		["east-near-rubble", Vector2(560, 290), [KEY_D], func(p): return p.x < 604.0 and p.x > 601.0],
	]
	var collision := {}
	for case in cases:
		var stopped: Vector2 = await _walk_until_stopped(case[1], case[2])
		if not case[3].call(stopped):
			_fail("collision case %s stopped at %s" % [case[0], str(stopped)])
			return
		collision[case[0]] = str(stopped)
		print("%s_COLLISION %s -> %s" % [TAG, case[0], str(stopped)])
	results["collision"] = collision
	# diagonal input slides along a fixture front instead of sticking
	hero.position = Vector2(300, 240)
	await _hold([KEY_W, KEY_D], func(): return false, 40)
	if hero.position.x < 330.0 or _blocked(hero.position):
		_fail("diagonal slide stuck at " + str(hero.position))
		return
	results["slide"] = str(hero.position)
	# a position inside a blocker (e.g. an older save from before the opt-in) can walk out
	hero.position = Vector2(320, 219)
	await _hold([KEY_S], func(): return not _blocked(hero.position), 120)
	if _blocked(hero.position):
		_fail("stuck inside the stele base at " + str(hero.position))
		return
	results["escape"] = str(hero.position)
	print("%s_SLIDE_ESCAPE_OK slide=%s escape=%s" % [TAG, results["slide"], results["escape"]])

	# --- reachability flood fill on a 1 px grid inside the room clamps.
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
	var targets := {"exit": false, "terminal": false, "save": reach.has(Vector2i(410, 262))}
	for index in 3:
		targets["clue%d_front" % (index + 3)] = false
		targets["clue%d_behind" % (index + 3)] = false
	for p in reach.keys():
		var v := Vector2(p)
		if v.distance_to(EXIT) < 46.0:
			targets["exit"] = true
		var in_clue := false
		for index in 3:
			if v.distance_to(CLUES[index]) < 45.0 or host._wdc_room_two_inspect_rect(index).has_point(v):
				in_clue = true
				targets["clue%d_%s" % [index + 3, "front" if v.y > 218.0 else "behind"]] = true
		if not in_clue and v.distance_to(TERMINAL) < 46.0:
			targets["terminal"] = true
	for key in targets.keys():
		if not targets[key]:
			_fail("not reachable: " + key)
			return
	results["reachability"] = {"cells": reach.size(), "targets": targets}
	print("%s_REACHABILITY_OK cells=%d targets=%s" % [TAG, reach.size(), str(targets)])

	# --- save / load: a clue inspection autosaves; a manual save in en at a lane spot; reload both.
	app.begin_new_run()
	app.hero_appearance = "female"
	await _open(DEST, 2)
	app.language = "en"
	host._refresh_text()
	hero.position = Vector2(163, 232)
	await _tap(KEY_E)
	await _tap(KEY_ESCAPE)
	var autos: Array = SaveStore.list_entries().filter(func(e): return String(e.get("kind", "")) == "auto")
	if autos.is_empty() or not app.survey_clues.has(DEST + ":3"):
		_fail("clue inspection wrote no auto save")
		return
	var auto_id := String(autos[0]["id"])
	# Real UI: click the room's Save button, slot 1 "Save", then "Back" into the room.
	var saved_at := Vector2(410, 262)
	hero.position = saved_at
	await _click(host.save_button)
	if not await _adopt_screen("save_screen.tscn"):
		return
	await _click(current_scene.manual_save_buttons[0])
	var manuals: Array = SaveStore.list_entries().filter(func(e): return String(e.get("kind", "")) == "manual" and int(e.get("slot", 0)) == 1)
	if manuals.is_empty() or current_scene.feedback_label.text == "":
		_fail("Save screen slot 1 wrote no manual save")
		return
	var manual_id := String(manuals[0]["id"])
	var save_path := folder.path_join(_name("en", "save-screen-slot1"))
	if not await _capture(save_path):
		_fail("save screen capture")
		return
	print("%s_CAPTURE %s" % [TAG, save_path])
	await _click(current_scene.back_button)
	await _adopt_current_scene()
	if host.room != 2 or not host.wdc_room_two or host.hero.position != saved_at:
		_fail("Back from the Save screen did not resume room 2 at %s: %s" % [str(saved_at), str(host.hero.position)])
		return
	# A fresh run, then the title menu's Load -> slot 1 Load, as a player would.
	app.begin_new_run()
	app.language = "zh"
	change_scene_to_file("res://scenes/main_menu.tscn")
	if not await _adopt_screen("main_menu.tscn"):
		return
	await _click(current_scene.load_button)
	if not await _adopt_screen("save_screen.tscn"):
		return
	await _click(current_scene.manual_load_buttons[0])
	await _adopt_current_scene()
	if app.current_destination_id != DEST or host.room != 2 or not host.wdc_room_two or host.hero.position != saved_at \
			or not app.survey_clues.has(DEST + ":3") or app.language != "en" or host.progress_label.text.find("1/6") < 0:
		_fail("manual load resumed wrong: %s %s %s" % [str(host.hero.position), app.language, host.progress_label.text])
		return
	if not await _shot("en", saved_at, "after-load"):
		_fail("capture after load failed")
		return
	if not await _shot("zh", saved_at, "after-load"):
		_fail("capture after load failed")
		return
	# The auto save from the clue inspection loads the same way (newest auto row).
	app.begin_new_run()
	change_scene_to_file("res://scenes/main_menu.tscn")
	if not await _adopt_screen("main_menu.tscn"):
		return
	await _click(current_scene.load_button)
	if not await _adopt_screen("save_screen.tscn"):
		return
	await _click(current_scene.auto_load_buttons[0])
	await _adopt_current_scene()
	if host.room != 2 or not host.wdc_room_two or host.hero.position.distance_to(Vector2(163, 232)) > 0.01 or not app.survey_clues.has(DEST + ":3"):
		_fail("auto save load resumed wrong: %s" % str(host.hero.position))
		return
	results["save_load"] = {"manual": manual_id, "auto": auto_id, "position": str(saved_at),
			"path": "room Save button -> slot 1 Save -> Back; main menu Load -> slot 1 Load; main menu Load -> auto row 1 Load (mouse clicks)"}
	print("%s_SAVE_LOAD_OK manual=%s auto=%s position=%s" % [TAG, manual_id, auto_id, str(saved_at)])

	# --- transitions with real keys: room 1 'Go deeper' -> room 2 (fixtures built), Esc back to room 1,
	# deeper again, then room 2's exit marker (E) back to room 1.
	app.begin_new_run()
	app.hero_appearance = "female"
	await _open(DEST, 1)
	hero.position = Vector2(580, 257)
	await _tap(KEY_E)
	await _adopt_current_scene()
	if int(app.current_annex_room) != 2 or not host.wdc_room_two or host.hero.position != SPAWN:
		_fail("Go deeper did not open room 2 with fixtures")
		return
	if not await _capture_as("zh", "door-entry-from-room1"):
		return
	await _tap(KEY_ESCAPE)
	await _adopt_current_scene()
	if int(app.current_annex_room) != 1 or host.wdc_room_two or host.hero.position != Vector2(555, 257) or host._wdc_blocked(host.hero.position):
		_fail("Esc in room 2 did not return to room 1's east door")
		return
	if not await _capture_as("zh", "return-room1-via-esc"):
		return
	app.language = "en"
	hero.position = Vector2(580, 257)
	await _tap(KEY_E)
	await _adopt_current_scene()
	if not host.wdc_room_two or not await _capture_as("en", "door-entry-from-room1"):
		_fail("en door entry")
		return
	hero.position = EXIT
	await _tap(KEY_E)
	await _adopt_current_scene()
	if int(app.current_annex_room) != 1 or host.room != 1 or host.hero.position != Vector2(555, 257):
		_fail("room 2 exit marker did not return to room 1")
		return
	if not await _capture_as("en", "return-room1-via-exit-marker"):
		return
	app.language = "zh"
	print(TAG + "_TRANSITIONS_OK")
	results["transitions"] = "deeper->room2 (fixtures), Esc->room1 (555,257), deeper, exit marker E->room1"

	# --- the same scene with the actual runtime heroine sprite (not the capture-only reference).
	app.begin_new_run()
	app.hero_appearance = "female"
	dressed = false
	await _open(DEST, 2)
	if not await _shot("zh", Vector2(320, 230), "front-clue-4-runtime-hero"):
		_fail("runtime hero capture")
		return
	dressed = true

	var dir_path := ProjectSettings.globalize_path(SaveStore.root_path)
	for file in DirAccess.get_files_at(dir_path):
		DirAccess.remove_absolute(dir_path.path_join(file))
	DirAccess.remove_absolute(dir_path)
	results["test_saves_removed"] = not DirAccess.dir_exists_absolute(dir_path)
	results["ok"] = true
	_write_results()
	print(TAG + "_ALL_OK")
	quit()
