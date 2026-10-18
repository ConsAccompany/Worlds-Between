extends SceneTree

# UNAPPROVED layout/collision fix check for the Washington survey annex (scifi.ruins) rooms 1 and 2, default and
# opt-in. Real Godot 640x360 zh/en captures of the working-tree script and of a given HEAD copy of
# survey_annex.gd (loaded in memory onto the same scene) as before/after evidence; real held-key walking into the
# room-2 plate walls and rubble; header title/button bounds; a 1 px reachability flood fill; real E/Esc clue,
# terminal and exit interactions (default mode). Run with APPDATA pointed at a temp dir (isolated user://).
# Default:  Godot --path game -s <this file> -- <capture dir> <probe dir> <stamp-id> <HEAD survey_annex.gd copy>
# Opt-in:   ... same args ... --wdc-records-chamber-v01
const SCENE := "res://scenes/survey_annex.tscn"
const CLUES := [Vector2(163, 165), Vector2(320, 165), Vector2(477, 165)]
const DEST := "scifi.ruins"
const SPAWN := Vector2(87, 261)
const EXIT := Vector2(57, 257)
const TERMINAL := Vector2(320, 263)
const FLAG := "--wdc-records-chamber-v01"
const TAG := "WDC_ROOMS_FIX"
# Held-key walks into the room-2 plate: [label, start, keys, step direction that must then be blocked].
const WALL_CASES := [
	["west-wall", Vector2(70, 220), [KEY_A], Vector2(-3, 0)],
	["east-wall", Vector2(570, 220), [KEY_D], Vector2(3, 0)],
	["back-wall", Vector2(240, 200), [KEY_W], Vector2(0, -3)],
	["west-back-corner", Vector2(110, 200), [KEY_W, KEY_A], Vector2(-3, -3)],
	["east-back-corner", Vector2(530, 200), [KEY_W, KEY_D], Vector2(3, -3)],
	["west-rubble", Vector2(80, 295), [KEY_A], Vector2(-3, 0)],
	["east-rubble", Vector2(560, 295), [KEY_D], Vector2(3, 0)],
]

var app: Node
var host: Node2D
var hero: Sprite2D
var folder := ""
var probe := ""
var stamp := ""
var mode := "default"
var head_script: GDScript
var walls: Array = []
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
	var file := FileAccess.open(probe.path_join("godot-check-results-%s.json" % mode), FileAccess.WRITE)
	if file != null:
		file.store_string(JSON.stringify(results, "  "))


func _name(which: String, language: String, label: String) -> String:
	return "rpg-2-star-ocean-the-second_wdc-annex-rooms_fix-%s-%s-godot-%s-%s-640x360_%s.png" % [mode, which, language, label, stamp]


func _frame() -> Image:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_viewport().get_texture().get_image()
	image.convert(Image.FORMAT_RGBA8)
	return image


func _save(image: Image, path: String) -> bool:
	if image.get_size() != Vector2i(640, 360) or image.save_png(path) != OK:
		_fail("capture " + path)
		return false
	print("%s_CAPTURE %s at=%s" % [TAG, path, str(hero.position)])
	return true


# which = "after" (working tree) or "before" (HEAD copy on the same scene).
func _open(which: String, room: int, language: String) -> void:
	if host != null:
		host.queue_free()
		await process_frame
	app.language = language
	app.select_destination(DEST)
	app.current_annex_room = room
	app.resume_annex_pending = false
	host = (load(SCENE) as PackedScene).instantiate()
	if which == "before":
		host.set_script(head_script)
	root.add_child(host)
	current_scene = host
	await process_frame
	await process_frame
	host.set_process(false)
	hero = host.hero


func _adopt_current_scene() -> void:
	await process_frame
	await process_frame
	host = current_scene
	host.set_process(false)
	hero = host.hero


# --- real input: key events go through Input, the InputMap and the viewport like a keyboard would.
func _key(keycode: Key, pressed: bool) -> void:
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


func _walk_until_stopped(start: Vector2, keys: Array, limit := 400) -> Vector2:
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


func _in_wall(at: Vector2) -> bool:
	for rect in walls:
		if rect.has_point(at):
			return true
	return false


# Header bounds: title end against Save, both buttons at their 98x38 boxes with their text fitting inside.
func _header() -> Dictionary:
	var title_right: float = host.title_label.position.x + host.title_label.get_minimum_size().x
	var info := {"title": host.title_label.text, "title_size": int(host.title_label.get_theme_font_size("font_size")),
			"title_right": title_right, "save_rect": str(host.save_button.get_rect()), "back_rect": str(host.back_button.get_rect()),
			"back_text": host.back_button.text, "back_font_size": int(host.back_button.get_theme_font_size("font_size")),
			"back_text_min_width": host.back_button.get_minimum_size().x, "save_text_min_width": host.save_button.get_minimum_size().x}
	var problems := []
	if title_right > host.save_button.position.x - 4.0:
		problems.append("title ends at %.0f, under Save at %.0f" % [title_right, host.save_button.position.x])
	for pair in [["Save", host.save_button], ["Back", host.back_button]]:
		var button: Button = pair[1]
		if button.size != Vector2(98, 38) or button.get_minimum_size().x > button.size.x or button.get_rect().end.x > 640.0:
			problems.append("%s '%s' overflows: rect %s, text needs %.0f" % [pair[0], button.text, str(button.get_rect()), button.get_minimum_size().x])
	if host.save_button.get_rect().intersects(host.back_button.get_rect()):
		problems.append("Save and Back overlap")
	info["problems"] = problems
	return info


func _diff(a: Image, b: Image) -> Dictionary:
	var da := a.get_data()
	var db := b.get_data()
	var count := 0
	var lo := Vector2i(640, 360)
	var hi := Vector2i(-1, -1)
	for i in range(0, da.size(), 4):
		if da[i] != db[i] or da[i + 1] != db[i + 1] or da[i + 2] != db[i + 2] or da[i + 3] != db[i + 3]:
			count += 1
			var p := Vector2i((i / 4) % 640, (i / 4) / 640)
			lo = Vector2i(mini(lo.x, p.x), mini(lo.y, p.y))
			hi = Vector2i(maxi(hi.x, p.x), maxi(hi.y, p.y))
	return {"pixels": count, "bbox": [lo.x, lo.y, hi.x, hi.y] if count > 0 else []}


func _remove_tree(path: String) -> void:
	if not DirAccess.dir_exists_absolute(path):
		return
	for sub in DirAccess.get_directories_at(path):
		_remove_tree(path.path_join(sub))
	for file in DirAccess.get_files_at(path):
		DirAccess.remove_absolute(path.path_join(file))
	DirAccess.remove_absolute(path)


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	folder = args[0]
	probe = args[1]
	stamp = args[2]
	mode = "optin" if args.has(FLAG) else "default"
	Engine.max_fps = 60
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(640, 360)
	DirAccess.make_dir_recursive_absolute(folder)
	DirAccess.make_dir_recursive_absolute(probe)
	head_script = GDScript.new()
	head_script.source_code = FileAccess.get_file_as_string(args[3])
	# Pinned "before" baseline (r1): survey_annex.gd blob eecdcca (7370739 = 7553581). After the fix is committed, HEAD is
	# not that baseline; pass `git show 7370739:game/scripts/survey_annex.gd`. Any other file fails.
	if head_script.source_code.replace("\r\n", "\n").sha256_text() != "bedc4adbff32ae08104674d2cabffdb466d848e0a419905c2d0b487cf3cea5c9":
		_fail("baseline copy is not the pinned pre-fix survey_annex.gd (create it with `git show 7370739:game/scripts/survey_annex.gd`): " + args[3])
		return
	if head_script.source_code.length() < 1000 or head_script.reload() != OK or head_script.source_code.contains(FLAG):
		_fail("HEAD script copy missing, failed to compile, or already has the room-2 branch: " + args[3])
		return
	SaveStore.root_path = "user://test-saves/wdc-annex-rooms-fix-%s-%s" % [mode, stamp]
	app = root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = "female"
	results["mode"] = mode
	results["user_data_dir"] = OS.get_user_data_dir()

	# --- header bounds and before/after frames for rooms 1 and 2 in zh and en.
	var header := {}
	var parity := {}
	for room in [1, 2]:
		for language in ["zh", "en"]:
			var key := "room%d_%s" % [room, language]
			await _open("after", room, language)
			if room == 2:
				if host.wdc_room_two != (mode == "optin") or not host.wdc_room_two_walls:
					_fail("room 2 branch flags wrong for mode " + mode)
					return
				if mode == "default" and (host.y_sort_enabled or host.wdc_room_two_markers.size() != 0):
					_fail("default room 2 built records-chamber nodes")
					return
				walls = []
				for index in host.WDC_ROOM_TWO_BLOCKERS.size():
					if not host.WDC_ROOM_TWO_FIXTURE_BLOCKERS.has(index):
						walls.append(host.WDC_ROOM_TWO_BLOCKERS[index])
			var after_info: Dictionary = _header()
			var after: Image = await _frame()
			if not _save(after, folder.path_join(_name("after", language, "room%d-entry" % room))):
				return
			# HEAD has no records-chamber branch, so room 2 is only comparable without the flag.
			var compare: bool = room == 1 or mode == "default"
			var before_info := {}
			if compare:
				await _open("before", room, language)
				before_info = _header()
				var before: Image = await _frame()
				if not _save(before, folder.path_join(_name("before", language, "room%d-entry" % room))):
					return
				parity[key] = _diff(after, before)
			header[key] = {"after": after_info, "before": before_info}
			print("%s_HEADER %s %s" % [TAG, key, JSON.stringify(header[key])])
			if not after_info["problems"].is_empty():
				_fail("%s header: %s" % [key, str(after_info["problems"])])
				return
	results["header"] = header
	results["parity_vs_head"] = parity
	print("%s_PARITY %s" % [TAG, JSON.stringify(parity)])
	# Allowed changes relative to HEAD: zh frames identical; en frames change only in the header (room 1: the
	# Back button; room 2: the title and the Back button).
	for key in parity.keys():
		var d: Dictionary = parity[key]
		if key.ends_with("_zh") and d["pixels"] != 0:
			_fail("%s differs from HEAD in %d px" % [key, d["pixels"]])
			return
		if key.ends_with("_en") and d["pixels"] > 0:
			var bbox: Array = d["bbox"]
			var limit := Rect2i(520, 0, 120, 62) if key.begins_with("room1") else Rect2i(0, 0, 640, 62)
			if not limit.encloses(Rect2i(bbox[0], bbox[1], bbox[2] - bbox[0] + 1, bbox[3] - bbox[1] + 1)):
				_fail("%s changes outside the header element: %s" % [key, str(bbox)])
				return
	if mode == "default":
		for key in ["room1_en", "room2_en"]:
			if header[key]["before"]["problems"].is_empty():
				_fail("HEAD %s header bug did not reproduce" % key)
				return

	# --- room 2: real held-key walks into the plate walls and rubble (working tree, and HEAD for before-evidence).
	var collision := {}
	for which in (["after", "before"] if mode == "default" else ["after"]):
		await _open(which, 2, "en")
		for case in WALL_CASES:
			var stopped: Vector2 = await _walk_until_stopped(case[1], case[2])
			var entry := {"start": str(case[1]), "stopped": str(stopped), "in_wall": _in_wall(stopped)}
			if which == "after":
				var travelled: float = stopped.distance_to(case[1])
				if _in_wall(stopped) or host._wdc_room_two_blocked(stopped) or not host._wdc_room_two_blocked(stopped + case[3]) or travelled < 4.0:
					_fail("%s: wall did not stop her cleanly (stopped %s, travelled %.1f)" % [case[0], str(stopped), travelled])
					return
			collision["%s_%s" % [which, case[0]]] = entry
			if case[0] in ["west-wall", "east-rubble"]:
				for language in ["zh", "en"]:
					app.language = language
					host._refresh_text()
					if not _save(await _frame(), folder.path_join(_name(which, language, "room2-" + case[0]))):
						return
				app.language = "en"
		print("%s_COLLISION_%s %s" % [TAG, which.to_upper(), JSON.stringify(collision)])
	if mode == "default":
		var reproduced := 0
		for case in WALL_CASES:
			if collision["before_" + case[0]]["in_wall"]:
				reproduced += 1
		results["head_cases_inside_walls"] = reproduced
		if reproduced < 4:
			_fail("HEAD wall walk-through reproduced in only %d cases" % reproduced)
			return
	results["collision"] = collision

	# --- reachability: 1 px flood fill from the spawn inside the room clamps (working tree).
	await _open("after", 2, "en")
	var reach := {}
	var queue: Array[Vector2i] = [Vector2i(SPAWN)]
	reach[Vector2i(SPAWN)] = true
	var head := 0
	while head < queue.size():
		var p: Vector2i = queue[head]
		head += 1
		for d in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var n: Vector2i = p + d
			if n.x < 25 or n.x > 615 or n.y < 78 or n.y > 305 or reach.has(n) or host._wdc_room_two_blocked(Vector2(n)):
				continue
			reach[n] = true
			queue.append(n)
	var targets := {"exit": false, "terminal": false, "room1_return_spot_free": not host._wdc_room_two_blocked(Vector2(555, 257))}
	for index in 3:
		targets["clue%d" % (index + 3)] = false
	for cell in reach.keys():
		var v := Vector2(cell)
		if v.distance_to(EXIT) < 46.0:
			targets["exit"] = true
		var in_clue := false
		for index in 3:
			if v.distance_to(CLUES[index]) < 45.0 or (host.wdc_room_two and host._wdc_room_two_inspect_rect(index).has_point(v)):
				in_clue = true
				targets["clue%d" % (index + 3)] = true
		if not in_clue and v.distance_to(TERMINAL) < 46.0:
			targets["terminal"] = true
	for key in targets.keys():
		if not targets[key]:
			_fail("not reachable: " + key)
			return
	results["reachability"] = {"cells": reach.size(), "targets": targets}
	print("%s_REACHABILITY_OK cells=%d targets=%s" % [TAG, reach.size(), str(targets)])

	# --- default room 2: real-key clue, terminal and exit interactions with the exact survey_content text.
	# (The opt-in interactions are covered by the records-chamber v01 check, rerun separately.)
	if mode == "default":
		var content: Dictionary = host.CONTENT.DATA[DEST]
		app.survey_clues.clear()
		for index in 3:
			hero.position = Vector2(CLUES[index].x, 250)
			await _hold([KEY_W], func(): return hero.position.distance_to(CLUES[index]) < 40.0)
			await _tap(KEY_E)
			var clue_key := "%s:%d" % [DEST, index + 3]
			if not host.overlay.visible or host.overlay_clue_index != index + 3 or not app.survey_clues.has(clue_key):
				_fail("E near clue %d did not open it (at %s)" % [index + 3, str(hero.position)])
				return
			for language in ["zh", "en"]:
				app.language = language
				host._refresh_text()
				var clue: Dictionary = content[language]["clues"][index + 3]
				if host.overlay_title.text != String(clue["name"]) or host.overlay_body.text != String(clue["text"]):
					_fail("overlay text differs from survey_content for clue %d %s" % [index + 3, language])
					return
				if not _save(await _frame(), folder.path_join(_name("after", language, "room2-interaction-clue-%d" % (index + 3)))):
					return
			app.language = "en"
			await _tap(KEY_ESCAPE)
			if host.overlay.visible:
				_fail("Esc did not close clue %d" % (index + 3))
				return
			results["clue_%d_opened_at" % (index + 3)] = str(hero.position)
		hero.position = Vector2(320, 225)
		await _hold([KEY_S], func(): return hero.position.distance_to(TERMINAL) < 30.0)
		await _tap(KEY_E)
		if not host.overlay.visible or host.overlay_mode != "message" or host.overlay_body.text != app.text_for("survey_locked"):
			_fail("terminal did not open the locked message at " + str(hero.position))
			return
		await _tap(KEY_ESCAPE)
		hero.position = Vector2(140, 257)
		await _hold([KEY_A], func(): return hero.position.distance_to(EXIT) < 30.0)
		await _tap(KEY_E)
		await _adopt_current_scene()
		if int(app.current_annex_room) != 1 or host.room != 1 or hero.position != Vector2(555, 257):
			_fail("room 2 exit marker did not return to room 1")
			return
		if not _save(await _frame(), folder.path_join(_name("after", "en", "room1-after-exit"))):
			return
		print(TAG + "_INTERACTIONS_OK")
		results["interactions"] = "clues 3/4/5 (zh+en exact text), terminal locked, exit -> room 1 (555,257)"

	var dir_path := ProjectSettings.globalize_path(SaveStore.root_path)
	_remove_tree(dir_path)
	results["test_saves_removed"] = not DirAccess.dir_exists_absolute(dir_path)
	results["ok"] = true
	_write_results()
	print("%s_%s_ALL_OK" % [TAG, mode.to_upper()])
	quit()
