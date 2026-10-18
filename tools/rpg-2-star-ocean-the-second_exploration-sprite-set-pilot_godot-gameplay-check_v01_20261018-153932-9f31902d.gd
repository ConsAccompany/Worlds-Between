extends SceneTree

# Exploration sprite set pilot: real-gameplay check. Run windowed (captures need a real renderer) with the
# pilot's own command-line flags, so the scenes read them exactly as a player's launch would:
#   Godot --path game --fixed-fps <fps> -s <this file> -- <out dir> <run tag> <640|1280> <none|bilingual|density|motion> <fps>
#     --exploration-sprite-set-pilot --exploration-sprite-set-registry=<TEST-ONLY diagnostic fixture registry>
# For each normal exploration scene type (area city/outskirts/ruins, survey annex rooms, Chicago Loop) it enters
# the scene the way the game does (AppState.select_destination + change_scene_to_file), walks a timed rectangle
# with the real move_* actions (east, idle, south, idle, west, idle, north, idle) and, after every rendered
# frame, reads the viewport back and checks that the diagnostic ID patch the runtime drew encodes the pilot's
# own (actor, action, facing, frame) and that the outline spans exactly 48 logical px with the soles on the
# legacy foot row. It writes a JSON timeline (compared across 30/60 fps by the Python check) and, per mode,
# a few separate evidence captures. The fixtures are diagnostic, not art; nothing here claims smooth motion.
# Saves go to user:// (run with an isolated APPDATA); nothing in the project is written.
const Pilot := preload("res://scripts/exploration_sprite_set_pilot.gd")
const ANNEX_SCENE := "res://scenes/survey_annex.tscn"
const DIRECTIONS := ["south", "west", "north", "east"]
const ID_G := {"protagonist-female": {"idle": 40, "walk": 200}, "protagonist-male": {"idle": 60, "walk": 220}}
const OUTLINE := {"protagonist-female": Color8(255, 0, 255), "protagonist-male": Color8(0, 255, 0)}
# Rectangle walk: east, idle, south, idle, west, idle, north, idle. Each scene sets its walk-leg length so the loop
# stays clear of the always-on-top world labels; idle legs of 0.9 s cover both idle frames of each set.
const MOVES := ["move_right", "move_down", "move_left", "move_up"]
const IDLE_S := 0.9
# key, destination, scene kind, annex room, hero appearance, rectangle start (top-left corner, feet), walk leg s.
const SCENES := [
	["city", "scifi.city", "area", 0, "female", Vector2(310, 212), 0.6],
	["outskirts", "scifi.outskirts", "area", 0, "male", Vector2(220, 115), 0.6],
	["ruins", "scifi.ruins", "area", 0, "female", Vector2(250, 120), 0.6],
	["annex-city-r1", "scifi.city", "annex", 1, "male", Vector2(200, 200), 0.7],
	["annex-ruins-r2", "scifi.ruins", "annex", 2, "female", Vector2(380, 215), 0.6],
	["chicago-loop", "scifi.loop", "loop", 0, "female", Vector2(240, 190), 0.5],
]
# Evidence moments: [scene key, leg index, seconds into the leg].
const BILINGUAL_SHOTS := [["city", 0, 0.30], ["outskirts", 2, 0.45], ["ruins", 4, 0.30], ["annex-city-r1", 6, 0.20],
	["annex-ruins-r2", 3, 0.60], ["chicago-loop", 1, 0.20]]
const DENSITY_SHOTS := [["city", 0, 0.30], ["city", 1, 0.60]]
# Motion mode: every rendered frame of the city loop's first walk leg and the start of the idle that follows.
const MOTION_SCENE := "city"
const MOTION_FRAMES := 30

var app: Node
var out_dir := ""
var tag := ""
var scale_px := 1
var mode := "none"
var fps := 60
var failed_frames := {}
var report := {"scenes": [], "failures": [], "captures": [], "seen": {}}


func _initialize() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	report["failures"].append(message)
	print("SSP_FAIL " + message)


# Keeps the first failing frame of each scene (diagnosis only; named as such).
func _fail_frame(key: String, image: Image, message: String) -> void:
	_fail(message)
	if not failed_frames.has(key):
		failed_frames[key] = true
		_save(image, "%s_first-failed-frame-diagnosis" % key)


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	out_dir = args[0]
	tag = args[1]
	scale_px = 2 if args[2] == "1280" else 1
	mode = args[3]
	fps = int(args[4])
	DirAccess.make_dir_recursive_absolute(out_dir)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(640, 360) * scale_px
	app = root.get_node("AppState")
	SaveStore.root_path = "user://test-saves/ssp-gameplay-%s" % tag
	report["fps"] = fps
	report["window"] = [640 * scale_px, 360 * scale_px]
	report["mode"] = mode
	report["pilot_enabled_by_cli"] = Pilot.enabled() and Pilot.enabled_override == -1
	report["registry"] = Pilot.registry_path()
	if not report["pilot_enabled_by_cli"]:
		_fail("pilot flag not on the command line")
	for scene in SCENES:
		if (mode == "density" or mode == "motion") and scene[0] != MOTION_SCENE:
			continue
		await _play(scene)
	report["texture_loads"] = Pilot.texture_loads
	report["manifest_reads"] = Pilot.manifest_reads
	var expected := {}
	for actor in ID_G:
		for action in ["idle", "walk"]:
			for direction in DIRECTIONS:
				for frame in (2 if action == "idle" else 4):
					expected["%s/%s/%s/%d" % [actor, action, direction, frame]] = true
	var missing := []
	if mode == "none" or mode == "bilingual":
		for key in expected:
			if not report["seen"].has(key):
				missing.append(key)
	report["verified_states"] = report["seen"].size()
	report["missing_states"] = missing
	if not missing.is_empty():
		_fail("states never verified on screen: %s" % str(missing))
	var file := FileAccess.open(out_dir.path_join("rpg-2-star-ocean-the-second_spriteset-pilot_gameplay-%s-report_%s.json" % [tag, _stamp()]), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, " ", false) + "\n")
	file.close()
	print("SSP_GAMEPLAY_DONE failures=%d verified_states=%d" % [report["failures"].size(), report["seen"].size()])
	quit(1 if not report["failures"].is_empty() else 0)


func _stamp() -> String:
	return "20261018-153932-9f31902d"


func _enter(scene: Array) -> Node:
	app.begin_new_run()
	app.hero_appearance = scene[4]
	if app.language != "zh":
		app.toggle_language()
	var path := ""
	match scene[2]:
		"annex":
			app.select_destination(scene[1])
			app.current_annex_room = scene[3]
			path = ANNEX_SCENE
		_:
			if not app.select_destination(scene[1]):
				_fail("%s: destination not selectable" % scene[0])
				return null
			path = app.area_scene_path(scene[1])
	change_scene_to_file(path)
	for i in 3:
		await process_frame
	return current_scene


func _play(scene: Array) -> void:
	var key: String = scene[0]
	var host := await _enter(scene)
	if host == null:
		return
	var hero: Sprite2D = host.get("hero")
	var pilot = host.get("sprite_pilot")
	if hero == null or pilot == null:
		_fail("%s: pilot not attached (hero=%s)" % [key, str(hero)])
		return
	hero.position = scene[5]
	if host.get("destination_id") == "scifi.city" and scene[2] == "area":
		hero.z_index = int(hero.position.y)
	var entry := {"scene": key, "script": host.get_script().resource_path, "actor": pilot.actor_id, "set_id": pilot.sprite_set["set_id"],
		"hero_scale": [hero.scale.x, hero.scale.y], "hero_offset": [hero.offset.x, hero.offset.y], "ticks": [], "verified": 0}
	report["scenes"].append(entry)
	var tick := 0
	for leg_index in 8:
		var action: String = MOVES[leg_index / 2] if leg_index % 2 == 0 else ""
		var frames := int(round((float(scene[6]) if leg_index % 2 == 0 else IDLE_S) * fps))
		for name in ["move_left", "move_right", "move_up", "move_down"]:
			if name == action:
				Input.action_press(name)
			else:
				Input.action_release(name)
		for n in frames:
			await RenderingServer.frame_post_draw
			tick += 1
			var state: Dictionary = pilot.state()
			entry["ticks"].append({"tick": tick, "leg": leg_index, "n": n, "input": action, "action": state["action"], "facing": state["facing"],
				"frame": state["frame"], "clock_us": state["clock_us"], "x": hero.position.x, "y": hero.position.y})
			if _verify(key, hero, pilot, state):
				entry["verified"] += 1
			if mode == "motion":
				if tick <= MOTION_FRAMES:
					_save(root.get_viewport().get_texture().get_image(), "%s_motion-frame-%02d-%dx%d" % [key, tick, 640 * scale_px, 360 * scale_px])
					report["captures"].append({"tick": tick, "state": state, "hero": [hero.position.x, hero.position.y]})
				else:
					break
				continue
			await _maybe_shoot(key, leg_index, n, hero, pilot)
		if failed_frames.has(key) and entry["ticks"].size() - entry["verified"] > 20:
			break
	for name in ["move_left", "move_right", "move_up", "move_down"]:
		Input.action_release(name)
	entry["end"] = [hero.position.x, hero.position.y]
	entry["start"] = [scene[5].x, scene[5].y]


func _expected_rgb(state: Dictionary, actor: String) -> Color:
	return Color8(50 + 50 * DIRECTIONS.find(state["facing"]), ID_G[actor][state["action"]], 30 + 40 * int(state["frame"]))


func _verify(key: String, hero: Sprite2D, pilot, state: Dictionary) -> bool:
	var image := root.get_viewport().get_texture().get_image()
	var at: Vector2 = hero.get_global_transform_with_canvas() * Vector2.ZERO
	var actor: String = pilot.actor_id
	var want := _expected_rgb(state, actor)
	var centre := Vector2i(((at + Vector2(0, -24)) * scale_px).floor())
	for dy in range(-2, 3):
		for dx in range(-2, 3):
			var p := centre + Vector2i(dx, dy)
			if image.get_pixelv(p) != want:
				_fail_frame(key, image, "%s tick state %s: ID patch at %s is %s, want %s" % [key, str(state), str(p), image.get_pixelv(p).to_html(false), want.to_html(false)])
				return false
	var outline: Color = OUTLINE[actor]
	var rows := []
	var x0 := int(floor((at.x - 19) * scale_px))
	var x1 := int(ceil((at.x + 19) * scale_px))
	for y in range(int((at.y - 60) * scale_px), int((at.y + 6) * scale_px)):
		for x in range(x0, x1):
			if image.get_pixel(x, y) == outline:
				rows.append(y)
				break
	var line := (at.y + Pilot.FLOOR_DROP_LOGICAL) * scale_px
	var bottom := int(ceil(line - 0.5)) - 1
	var top := bottom - Pilot.BODY_LOGICAL * scale_px + 1
	if rows.size() != Pilot.BODY_LOGICAL * scale_px or rows[0] != top or rows[-1] != bottom:
		_fail_frame(key, image, "%s state %s: outline rows %s..%s (%d), want %d..%d (%d)" % [key, str(state), str(rows[0] if rows.size() else -1), str(rows[-1] if rows.size() else -1), rows.size(), top, bottom, Pilot.BODY_LOGICAL * scale_px])
		return false
	report["seen"]["%s/%s/%s/%d" % [actor, state["action"], state["facing"], state["frame"]]] = true
	return true


func _maybe_shoot(key: String, leg_index: int, n: int, hero: Sprite2D, pilot) -> void:
	var shots: Array = BILINGUAL_SHOTS if mode == "bilingual" else (DENSITY_SHOTS if mode == "density" else [])
	for shot in shots:
		if shot[0] != key or shot[1] != leg_index or n != int(round(float(shot[2]) * fps)):
			continue
		for lang in ["zh", "en"]:
			if app.language != lang:
				app.toggle_language()
				await RenderingServer.frame_post_draw
			var state: Dictionary = pilot.state()
			var ok := _verify(key, hero, pilot, state)
			var label := "%s_%s-%s-%s-f%d_%s" % [key, pilot.actor_id.trim_prefix("protagonist-"), state["action"], state["facing"], int(state["frame"]) + 1, lang]
			if scale_px == 2:
				label += "-1280x720"
			var path := _save(root.get_viewport().get_texture().get_image(), label)
			report["captures"].append({"file": path.get_file(), "scene": key, "language": lang, "state": state, "hero": [hero.position.x, hero.position.y], "verified": ok})
			if mode == "density":
				break
		if app.language != "zh":
			app.toggle_language()


func _save(image: Image, label: String) -> String:
	var path := out_dir.path_join("rpg-2-star-ocean-the-second_spriteset-pilot_%s_test-only_%s.png" % [label, _stamp()])
	if image.get_size() != Vector2i(640, 360) * scale_px or image.save_png(path) != OK:
		_fail("capture failed: " + path)
	return path
