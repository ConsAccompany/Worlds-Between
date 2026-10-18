extends SceneTree

# Real Godot 640x360 captures plus behaviour checks for the Chicago Loop State/Lake v05 material-depth
# pass (UNAPPROVED, test-harness opt-in only). Started as a copy of the v04 check: every v04 check
# retargeted at v05, plus the v04, v03r1 and v03 opt-ins still reaching their untouched scenes through the
# v05 selector. The shared runtime Loop .tscn is NOT edited in this pass (another session may be using
# it): this tool hands the Loop scene path a test-only in-memory copy of that scene whose root script is
# the v05 selector (PackedScene.take_over_path, nothing written to disk), i.e. exactly what a one-line
# path= change would do, then flies in from the world map, saves, loads and leaves through that path.
# It also proves the real, unedited Loop .tscn stays v02 even with the v05 flag.
# Usage: Godot --path game -s <this file> -- <output dir> <stamp-id> <walkmask png> <reveal mask png> --chicago-state-lake-v05
# Writes PNGs and one JSON of visible-hero pixel counts into <output dir>; saves go to
# user://test-saves/chicago-loop-state-lake-v05.
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
const LOOP_SCENE := "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn"
const V05_SCENE := "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v05_20261017-234337-84862412.tscn"
const SELECTOR := "res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-scene-opt-in-selector_unapproved-v05_20261017-234337-84862412.gd"
const WIRED_SELECTOR := "rpg-2-star-ocean-the-second_chicago-loop_state-lake-scene-opt-in-selector_unapproved-v04_20261017-230650-c0d4b7f0.gd"
const V02_GROUND := "chicago-loop-state-lake-v02"
const CHICAGO := "earth.us.il.chicago"
const APPROVED_HERO_IDLE := preload("res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
# Feet spots whose visible hero pixels are recorded (reveal off and on) for the Python cross-check.
const SPOTS := {"open-plaza": Vector2(300, 220), "behind-west-column": Vector2(140, 182), "behind-east-column": Vector2(476, 182),
	"behind-kiosk": Vector2(432, 186), "behind-bench": Vector2(279, 180), "front-west-column": Vector2(128, 280),
	"behind-west-locust": Vector2(198, 272), "stair-foot": Vector2(566, 207), "behind-pylon": Vector2(240, 226)}

var app: Node
var host: Node
var folder := ""
var stamp := ""
var checks := 0
var counts := {}
var real_loop: PackedScene
var harness_loop: PackedScene


func _initialize() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	push_error(message)
	print("CHICAGO_V05_FAIL " + message)
	quit(1)


func _check(ok: bool, label: String) -> bool:
	if not ok:
		_fail(label)
		return false
	checks += 1
	print("CHICAGO_V05_CHECK_OK " + label)
	return true


func _frames(count: int) -> void:
	for i in count:
		await process_frame


func _image() -> Image:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	return root.get_viewport().get_texture().get_image()


func _capture(tag: String) -> bool:
	var image := await _image()
	if image.get_size() != Vector2i(640, 360):
		_fail("expected a 640x360 capture, got " + str(image.get_size()))
		return false
	var path := folder.path_join("rpg-2-star-ocean-the-second_chicago-loop_state-lake-godot-%s-640x360_v05_%s.png" % [tag, stamp])
	if image.save_png(path) != OK:
		_fail("could not save " + path)
		return false
	print("CHICAGO_V05_CAPTURE " + path)
	return true


func _set_language(code: String) -> void:
	app.language = code
	host._refresh_text()
	await _frames(2)


func _hold(action: String, frames: int) -> void:
	Input.action_press(action)
	await _frames(frames)
	Input.action_release(action)
	await process_frame


func _press(action: String) -> InputEventAction:
	var event := InputEventAction.new()
	event.action = action
	event.pressed = true
	return event


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	folder = args[0]
	stamp = args[1]
	Engine.max_fps = 60
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(640, 360)
	DirAccess.make_dir_recursive_absolute(folder)
	SaveStore.root_path = "user://test-saves/chicago-loop-state-lake-v05"
	app = root.get_node("AppState")
	app.begin_new_run()
	app.show_initial_guide = false
	app.hero_appearance = "female"
	app.language = "zh"
	var ok: bool = await _checks(args[2], args[3])
	if real_loop != null:
		real_loop.take_over_path(LOOP_SCENE)   # hand the Loop path back to the real scene resource
	if ok:
		var report := FileAccess.open(folder.path_join("rpg-2-star-ocean-the-second_chicago-loop_state-lake-godot-visible-hero-counts_v05_%s.json" % stamp), FileAccess.WRITE)
		report.store_string(JSON.stringify({"stamp": stamp, "spots": counts, "checks": checks}, "  ", true) + "\n")
		report.close()
		print("CHICAGO_LOOP_V05_OK checks=%d" % checks)
		quit()


# Visible hero pixels at a spot: the frame with the hero minus the frame without her, inside her box.
func _visible_hero(at: Vector2, reveal: bool) -> int:
	var hero: Sprite2D = host.hero
	hero.position = at
	_set_reveal_enabled(reveal)
	hero.visible = false
	var without := await _image()
	hero.visible = true
	var with_hero := await _image()
	var box := Rect2i(int(at.x) - 16, int(at.y) - 44, 32, 48).intersection(Rect2i(0, 0, 640, 360))
	var count := 0
	for y in range(box.position.y, box.end.y):
		for x in range(box.position.x, box.end.x):
			if not without.get_pixel(x, y).is_equal_approx(with_hero.get_pixel(x, y)):
				count += 1
	return count


func _set_reveal_enabled(on: bool) -> void:
	# Test hook: with the reveal off every prop keeps strength 0 (the raw y-sort occlusion).
	for sprite in host.prop_sprites:
		(sprite.material as ShaderMaterial).set_shader_parameter("strength", 0.0)
	if on:
		host.reveal_strength = 0.0
		host._update_reveal(10.0)


# Test-only wiring: an in-memory copy of the Loop scene (same root name and type) whose root script is the
# v05 selector takes over the Loop scene path in the resource cache, so every change_scene_to_file(LOOP_SCENE)
# below (map flight, save return, load, resume) goes through the v05 selector. Nothing is written to disk.
func _wire_harness_loop() -> bool:
	real_loop = load(LOOP_SCENE)
	var node := Node2D.new()
	node.name = "ChicagoLoopDistrict"
	node.set_script(load(SELECTOR))
	harness_loop = PackedScene.new()
	var err := harness_loop.pack(node)
	node.free()
	harness_loop.take_over_path(LOOP_SCENE)
	return err == OK and load(LOOP_SCENE) == harness_loop and harness_loop.resource_path == LOOP_SCENE


func _checks(mask_path: String, reveal_path: String) -> bool:
	var selector: GDScript = load(SELECTOR)
	# Opt-in switch: the CLI flag turns it on; the override can force either state.
	if not _check(selector.v05_enabled() and OS.get_cmdline_user_args().has(selector.V05_FLAG), "the --chicago-state-lake-v05 flag enables the candidate"):
		return false
	# The shared runtime Loop .tscn is not edited by this pass: it still names the v04 selector, so even
	# with the v05 flag the real Loop scene plays the unchanged v02 scene.
	var tscn := FileAccess.get_file_as_string(LOOP_SCENE)
	if not _check(tscn.contains(WIRED_SELECTOR) and not tscn.contains("unapproved-v05"), "the shared Loop .tscn still names the v04 selector (not edited by this pass)"):
		return false
	app.select_destination("scifi.loop")
	change_scene_to_file(LOOP_SCENE)
	await _frames(4)
	var ground: Sprite2D = current_scene.get_child(0) as Sprite2D
	if not _check(current_scene.scene_file_path == LOOP_SCENE and not ("prop_sprites" in current_scene) and ground != null and ground.texture.resource_path.contains(V02_GROUND)
			and current_scene.get_script().get_base_script().resource_path.contains("unapproved-v02"), "the real Loop .tscn runs the unchanged v02 scene even with the v05 flag"):
		return false
	app.language = "en"
	current_scene._refresh_text()
	if not await _capture("en-default-off-v02-entry"):
		return false
	app.language = "zh"
	if not _check(_wire_harness_loop(), "test-only harness: the Loop scene path now resolves to an in-memory Loop scene rooted in the v05 selector"):
		return false
	# Off by default through the v05 selector too.
	selector.v05_override = 0
	change_scene_to_file(LOOP_SCENE)
	await _frames(4)
	ground = current_scene.get_child(0) as Sprite2D
	if not _check(current_scene.scene_file_path == LOOP_SCENE and not ("prop_sprites" in current_scene) and ground != null and ground.texture.resource_path.contains(V02_GROUND)
			and current_scene.get_script().resource_path == SELECTOR and current_scene.get_script().get_base_script().resource_path.contains("unapproved-v02"),
			"without the opt-in the v05 selector plays the unchanged v02 scene"):
		return false
	# The earlier opt-ins still reach their untouched scenes through the v04 selector's rules.
	var v04_selector: GDScript = selector.V04Selector
	var v03r1_selector: GDScript = v04_selector.V03R1Selector
	var v03_selector: GDScript = v03r1_selector.V03Selector
	v04_selector.v04_override = 1
	change_scene_to_file(LOOP_SCENE)
	await _frames(6)
	if not _check(current_scene.scene_file_path == v04_selector.V04_SCENE, "the v04 opt-in still hands the Loop to the untouched v04 scene"):
		return false
	v04_selector.v04_override = 0
	v03r1_selector.v03r1_override = 1
	change_scene_to_file(LOOP_SCENE)
	await _frames(6)
	if not _check(current_scene.scene_file_path == v03r1_selector.V03R1_SCENE, "the v03r1 opt-in still hands the Loop to the untouched v03r1 scene"):
		return false
	v03r1_selector.v03r1_override = 0
	v03_selector.enabled_override = 1
	change_scene_to_file(LOOP_SCENE)
	await _frames(6)
	if not _check(current_scene.scene_file_path == v03_selector.V03_SCENE, "the v03 opt-in still hands the Loop to the untouched v03 scene"):
		return false
	v03_selector.enabled_override = -1
	v03r1_selector.v03r1_override = -1
	v04_selector.v04_override = -1
	if not _check(not v03_selector.v03_enabled() and not v03r1_selector.v03r1_enabled() and not v04_selector.v04_enabled(), "the v04, v03r1 and v03 opt-ins are off when only the v05 flag is given"):
		return false
	# Actual entry with the opt-in: fly from the world map to Chicago; the Loop hands over to v05.
	selector.v05_override = -1
	app.begin_new_run()
	app.show_initial_guide = false
	app.hero_appearance = "female"
	app.language = "zh"
	change_scene_to_file(MAP_SCENE)
	await _frames(4)
	var map: Node = current_scene
	map.select_place(CHICAGO)
	await _frames(4)
	var start_minutes: int = app.calendar_minutes
	map.depart_button.pressed.emit()
	await _frames(8)
	host = current_scene
	var script: GDScript = host.get_script()
	if not _check(host.scene_file_path == V05_SCENE and app.current_destination_id == "scifi.loop" and app.calendar_minutes > start_minutes, "departing for Chicago from the map lands in the v05 scene (flight charged once)"):
		return false
	var hero: Sprite2D = host.hero
	if not _check(hero.position == script.SPAWN and script.walkable(script.SPAWN), "arrival at the walkable Lake St plaza spawn"):
		return false
	if not _check(host.title_label.text == "芝加哥 · 卢普区" and host.badge_label.text == "技术占位 · 美术未验收", "zh title and art-unaccepted badge unchanged"):
		return false
	if not await _capture("zh-entry"):
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
	if not _check(painted, "street labels are painted under the hero and props"):
		return false
	if not await _capture("en-entry"):
		return false
	# Collision equals the authored walk mask; the reveal mask equals the authored occlusion data.
	var mask := Image.load_from_file(mask_path)
	var reveal := Image.load_from_file(reveal_path)
	var mismatches := 0
	var walkable_count := 0
	var reveal_mismatches := 0
	for y in 360:
		for x in 640:
			var authored := mask.get_pixel(x, y).r > 0.5
			walkable_count += 1 if authored else 0
			if authored != script.walkable(Vector2(x, y)):
				mismatches += 1
			if (reveal.get_pixel(x, y).r > 0.5) != host.needs_reveal(Vector2(x, y)):
				reveal_mismatches += 1
	if not _check(mismatches == 0 and walkable_count > 60000, "walkable() matches the authored walk mask (%d walkable px, %d mismatches)" % [walkable_count, mismatches]):
		return false
	if not _check(reveal_mismatches == 0, "runtime reveal mask equals the authored occlusion mask"):
		return false
	if not _check(script.walkable(Vector2(400, 180)) and not script.walkable(Vector2(440, 195)) and script.slide_position(Vector2(400, 180), Vector2(410, 190)) == Vector2(410, 180), "legacy smoke pins: plaza walkable under the L, kiosk solid, slide past the litter bin"):
		return false
	var solids := {"west L column plinth": Vector2(140, 256), "east L column plinth": Vector2(474, 256), "civic kiosk": Vector2(432, 195),
		"bench": Vector2(270, 184), "litter bin": Vector2(404, 186), "Chicago lamp": Vector2(88, 180), "stone planter": Vector2(230, 182),
		"wayfinding pylon": Vector2(240, 230), "granite seat": Vector2(380, 262), "honey locust grate": Vector2(198, 290),
		"bike-share dock": Vector2(360, 292), "station stair": Vector2(574, 195), "east terrace": Vector2(620, 220),
		"fountain": Vector2(600, 280), "bollard": Vector2(90, 224), "storefronts under the deck": Vector2(320, 168),
		"header": Vector2(320, 40), "footer": Vector2(320, 330)}
	for key in solids:
		if not _check(not script.walkable(solids[key]), "solid: " + key):
			return false
	if not _check(script.WALK_TOP - 44 >= script.DECK_BOTTOM, "walk top keeps the 44 px hero head clear of the deck girder"):
		return false
	# Held input: north from the arrival to the L, no calendar time.
	var minutes: int = app.calendar_minutes
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
	# West along the under-L lane from the stair foot, through both column lines and over State St.
	await _set_language("zh")
	hero.position = Vector2(565, 220)
	Input.action_press("move_left")
	frames = 0
	var last_x := hero.position.x
	var snapped := false
	while hero.position.x > 20.0 and frames < 600:
		await process_frame
		frames += 1
		if hero.position.x > last_x or absf(hero.position.y - 220.0) > 0.01:
			Input.action_release("move_left")
			return _check(false, "lane walk regressed at " + str(hero.position))
		last_x = hero.position.x
		if not snapped and hero.position.x < 300.0:
			snapped = true
			if not await _capture("zh-traverse-under-l-lane"):
				Input.action_release("move_left")
				return false
	Input.action_release("move_left")
	if not _check(hero.position.x <= 20.0 and app.calendar_minutes == minutes, "the under-L lane and State St crosswalk walk end to end (x=%.1f)" % hero.position.x):
		return false
	hero.position = Vector2(40, 240)
	await _set_language("en")
	if not await _capture("en-traverse-crosswalk"):
		return false
	await _set_language("zh")
	if not await _capture("zh-traverse-crosswalk"):
		return false
	hero.position = Vector2(300, 220)
	await _set_language("en")
	if not await _capture("en-traverse-under-l-lane"):
		return false
	# A column plinth blocks a straight walk south; the hero stops north of it.
	hero.position = Vector2(140, 236)
	await _hold("move_down", 30)
	if not _check(hero.position.y < 250.0 and hero.position.x == 140.0, "column plinth blocks a straight walk south (y=%.1f)" % hero.position.y):
		return false
	hero.position = Vector2(560, 222)
	host.set_process(false)
	await _set_language("zh")
	if not await _capture("zh-traverse-stair-foot"):
		return false
	# Occlusion: exact visible-hero counts with the reveal off and on (cross-checked offline), south idle.
	hero.texture = load("res://scripts/character_directional_idle.gd").texture_for("protagonist-female", "south")
	var full: int = 0
	for key in SPOTS:
		var raw := await _visible_hero(SPOTS[key], false)
		var revealed := await _visible_hero(SPOTS[key], true)
		counts[key] = {"at": [SPOTS[key].x, SPOTS[key].y], "raw": raw, "reveal": revealed, "needs_reveal": host.needs_reveal(SPOTS[key])}
		if key == "open-plaza":
			full = raw
	if not _check(full > 500, "open plaza shows the whole hero (%d px)" % full):
		return false
	for key in counts:
		var c: Dictionary = counts[key]
		if c["needs_reveal"] and not _check(c["raw"] < full / 2 and c["reveal"] >= int(full * 0.45), "%s: hidden (%d px) without the reveal, readable (%d px) with it" % [key, c["raw"], c["reveal"]]):
			return false
		if not c["needs_reveal"] and not _check(c["raw"] == c["reveal"], "%s: no reveal where she is mostly visible (%d px)" % [key, c["raw"]]):
			return false
	if not _check(counts["front-west-column"]["raw"] >= full - 2, "in front of a column the hero covers the plinth"):
		return false
	_set_reveal_enabled(false)
	host.hero.position = SPOTS["behind-west-column"]
	if not await _capture("zh-occlusion-column-raw"):
		return false
	_set_reveal_enabled(true)
	await _set_language("en")
	if not await _capture("en-occlusion-column-reveal"):
		return false
	host.hero.position = SPOTS["behind-west-locust"]
	host._update_reveal(10.0)
	await _set_language("zh")
	if not await _capture("zh-occlusion-honey-locust"):
		return false
	if not _check(script.YSORT_PROPS[script.YSORT_PROPS.size() - 1][2] > script.WALK.end.y, "the south parapet and fence always draw over the hero"):
		return false
	# The three sites: E near each opens its bilingual note; nothing in the game state changes.
	var interaction := _press("interact")
	var clues: int = app.survey_clues.size()
	var expect := {"kiosk": ["State/Lake", "Lake Street elevated"], "stair": ["站台", "platform"], "pylon": ["五条线", "Purple"]}
	for site in script.SITES:
		var id: String = site[0]
		hero.position = site[1]
		host._update_reveal(10.0)
		await _set_language("zh")
		host._unhandled_input(interaction)
		await _frames(2)
		if not _check(host.info_panel.visible and host.active_site == id and host.info_label.text.contains(expect[id][0]) and app.calendar_minutes == minutes and app.survey_clues.size() == clues, "%s opens its zh note, no time or clue change" % id):
			return false
		if not await _capture("zh-interact-" + id):
			return false
		await _set_language("en")
		if not _check(host.info_label.text.contains(expect[id][1]), "%s note switches to English" % id):
			return false
		if not await _capture("en-interact-" + id):
			return false
		host._unhandled_input(interaction)
		await _frames(2)
		if not _check(not host.info_panel.visible, "E again closes the %s note" % id):
			return false
	hero.position = script.SPAWN
	host._unhandled_input(interaction)
	await _frames(2)
	if not _check(not host.info_panel.visible, "E away from every site does nothing"):
		return false
	if not _check(not app.areas_visited.has("scifi.loop"), "the Loop is not counted toward the three-place goal"):
		return false
	# Reference captures with the approved 48 px heroine idle (same scale, offset and spot as v02's).
	var runtime_texture := hero.texture
	hero.texture = APPROVED_HERO_IDLE
	hero.scale = Vector2(0.5, 0.5)
	hero.offset = Vector2(0, -40)
	for code in ["zh", "en"]:
		await _set_language(code)
		hero.position = Vector2(296, 228)
		host._update_reveal(10.0)
		if not await _capture("%s-approved-heroine-ref" % code):
			return false
	hero.texture = runtime_texture
	hero.scale = Vector2.ONE
	hero.offset = Vector2(0, -20)
	# Resume safety: old placeholder, v01 and v02 save spots land on walkable ground.
	for old in [Vector2(80, 90), Vector2(400, 180), Vector2(560, 300), Vector2(115, 284), Vector2(320, 40), Vector2(440, 195), Vector2(523, 284), Vector2(620, 230), Vector2(330, 260), Vector2(162, 240)]:
		if not _check(script.walkable(script.safe_position(old)), "old save spot %s resumes on walkable ground" % str(old)):
			return false
	# Save from v05 returns through the Loop scene path; with the opt-in the Loop hands back to v05 at the spot.
	host.set_process(true)
	hero.position = Vector2(330, 260)
	host.save_button.pressed.emit()
	await _frames(3)
	if not _check(current_scene.scene_file_path.ends_with("save_screen.tscn") and app.save_return_scene == LOOP_SCENE and app.save_return_position == Vector2(330, 260), "save opens with the Loop return scene and spot"):
		return false
	var id: String = app.write_manual_save(1)
	if not _check(id != "" and SaveStore.read_entry(id)["snapshot"]["destination"] == "scifi.loop", "the v05 save is a Loop area save"):
		return false
	current_scene._back()
	await _frames(8)
	if not _check(current_scene.scene_file_path == V05_SCENE and current_scene.hero.position.is_equal_approx(Vector2(330, 260)), "back from save returns to v05 at the same spot"):
		return false
	if not _check(app.load_save(id) and app.loaded_scene_path() == LOOP_SCENE, "loading the save restores the Loop scene path"):
		return false
	change_scene_to_file(app.loaded_scene_path())
	await _frames(8)
	if not _check(current_scene.scene_file_path == V05_SCENE and current_scene.hero.position.is_equal_approx(Vector2(330, 260)), "the loaded save resumes in v05 at the saved spot"):
		return false
	current_scene.get_viewport().push_input(_press("ui_cancel"))
	await _frames(4)
	return _check(current_scene.scene_file_path == MAP_SCENE, "Esc in the Loop returns to the world map")
