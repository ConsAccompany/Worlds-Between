extends SceneTree

# TEST-ONLY, NONRUNTIME capture harness for the Chicago Loop State/Lake v06 materials/depth candidate
# (UNAPPROVED). It edits no game file: the shared Loop .tscn, the v05 scene, its script, its selector and
# its art are untouched on disk. In memory only, it
#   1. hands the Loop scene path a copy of the Loop scene rooted in the existing v05 opt-in selector
#      (PackedScene.take_over_path, the same harness the v05 check used) with the v05 override on;
#   2. replaces the six v05 art textures in the resource cache with ImageTextures built from the v06
#      runtime-candidate PNGs in outputs/ (Texture2D.take_over_path on the v05 res:// paths), so the
#      unchanged v05 scene script draws v06 pixels through the real Godot renderer, y-sort and reveal shader.
# The v05 reveal mask is not replaced (v06 must produce the identical mask; checked below).
# Two controls run first: (A) the real v05 assets, (B) the v05 PNGs injected the same way; both must equal
# the committed v05 en-entry capture pixel for pixel, which proves the override path renders exactly what
# the imported textures render.
# The deliverable captures show the approved 48-logical-px heroine reference (the same texture, scale and
# offset the v05 check used for its reference captures), labelled "heroine-ref48" in every file name. It is
# a scale reference only, not a new character approval.
# Usage: Godot --path game -s <this file> -- <out dir> <capture stamp> <v06 dir> <v05 committed en-entry png>
#        <v05 art dir> <v06 walkmask png> <v06 reveal mask png>
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
const LOOP_SCENE := "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn"
const V05_SCENE := "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v05_20261017-234337-84862412.tscn"
const SELECTOR := "res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-scene-opt-in-selector_unapproved-v05_20261017-234337-84862412.gd"
const WIRED_SELECTOR := "rpg-2-star-ocean-the-second_chicago-loop_state-lake-scene-opt-in-selector_unapproved-v04_20261017-230650-c0d4b7f0.gd"
const V05_ART := "res://assets/environments/chicago-loop-state-lake-v05/rpg-2-star-ocean-the-second_chicago-loop_state-lake_%s_unapproved-v05_20261017-234337-84862412.png"
const V05_FILE := "rpg-2-star-ocean-the-second_chicago-loop_state-lake_%s_unapproved-v05_20261017-234337-84862412.png"
const V06_FILE := "rpg-2-star-ocean-the-second_chicago-loop_state-lake_%s_unapproved-v06_20261018-155129-19790a70.png"
const LAYERS := ["ground-far", "ysort-underdeck-props", "ysort-l-columns", "ysort-station-stair-east", "ysort-plaza-props", "ysort-foreground"]
const CHICAGO := "earth.us.il.chicago"
const APPROVED_HERO_IDLE := preload("res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
const SPAWN := Vector2(320, 286)
const SITES := {"kiosk": Vector2(432, 214), "stair": Vector2(574, 214), "pylon": Vector2(240, 240)}
const LANE_SPOT_X := 300.0
const COLUMN_SPOT := Vector2(140, 182)

var app: Node
var host: Node
var folder := ""
var stamp := ""
var checks := 0
var log_lines: Array[String] = []
var real_loop: PackedScene
var harness_loop: PackedScene
var injected: Array[Texture2D] = []    # strong refs: the resource cache only holds weak ones
var diffs := {}


func _initialize() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	push_error(message)
	print("CHICAGO_V06_FAIL " + message)
	log_lines.append("FAIL " + message)
	_write_report(false)
	quit(1)


func _check(ok: bool, label: String) -> bool:
	if not ok:
		_fail(label)
		return false
	checks += 1
	print("CHICAGO_V06_CHECK_OK " + label)
	log_lines.append("OK " + label)
	return true


func _frames(count: int) -> void:
	for i in count:
		await process_frame


func _image() -> Image:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	return root.get_viewport().get_texture().get_image()


func _capture(tag: String) -> Image:
	var image := await _image()
	if image.get_size() != Vector2i(640, 360):
		_fail("expected a 640x360 capture, got " + str(image.get_size()))
		return null
	var path := folder.path_join("rpg-2-star-ocean-the-second_chicago-loop_state-lake-godot-%s-640x360_v06_%s.png" % [tag, stamp])
	if image.save_png(path) != OK:
		_fail("could not save " + path)
		return null
	print("CHICAGO_V06_CAPTURE " + path)
	return image


func _diff_px(a: Image, b: Image) -> int:
	if a == null or b == null or a.get_size() != b.get_size():
		return -1
	a.convert(Image.FORMAT_RGB8)
	b.convert(Image.FORMAT_RGB8)
	var n := 0
	for y in a.get_height():
		for x in a.get_width():
			if a.get_pixel(x, y) != b.get_pixel(x, y):
				n += 1
	return n


func _set_language(code: String) -> void:
	app.language = code
	host._refresh_text()
	await _frames(2)


func _wire_harness_loop() -> bool:
	real_loop = load(LOOP_SCENE)
	var node := Node2D.new()
	node.name = "ChicagoLoopDistrict"
	node.set_script(load(SELECTOR))
	harness_loop = PackedScene.new()
	var err := harness_loop.pack(node)
	node.free()
	harness_loop.take_over_path(LOOP_SCENE)
	return err == OK and load(LOOP_SCENE) == harness_loop


func _inject(dir: String, file_format: String) -> bool:
	injected.clear()
	for layer in LAYERS:
		var image := Image.load_from_file(dir.path_join(file_format % layer))
		if image == null or image.get_size() != Vector2i(640, 360):
			return false
		var texture := ImageTexture.create_from_image(image)
		texture.take_over_path(V05_ART % layer)
		injected.append(texture)
	for i in LAYERS.size():
		if load(V05_ART % LAYERS[i]) != injected[i]:
			return false
	return true


func _enter_from_map() -> bool:
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
	return host.scene_file_path == V05_SCENE and app.current_destination_id == "scifi.loop" and app.calendar_minutes > start_minutes and host.hero.position == SPAWN


func _use_reference_heroine() -> void:
	host.set_process(false)   # keeps the reference texture (no walk animation swaps it back)
	host.hero.texture = APPROVED_HERO_IDLE
	host.hero.scale = Vector2(0.5, 0.5)
	host.hero.offset = Vector2(0, -40)


func _scene_uses_injected() -> bool:
	var ground: Sprite2D = host.get_child(0) as Sprite2D
	if ground == null or ground.texture != injected[0]:
		return false
	for sprite in host.prop_sprites:
		if not injected.has(sprite.texture):
			return false
	return true


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	folder = args[0]
	stamp = args[1]
	Engine.max_fps = 60
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(640, 360)
	DirAccess.make_dir_recursive_absolute(folder)
	app = root.get_node("AppState")
	var ok: bool = await _checks(args[2], args[3], args[4], args[5], args[6])
	if real_loop != null:
		real_loop.take_over_path(LOOP_SCENE)
	if ok:
		_write_report(true)
		print("CHICAGO_LOOP_V06_HARNESS_OK checks=%d" % checks)
		quit()


func _write_report(ok: bool) -> void:
	var f := FileAccess.open(folder.path_join("rpg-2-star-ocean-the-second_chicago-loop_state-lake-godot-harness-report_v06_%s.json" % stamp), FileAccess.WRITE)
	if f == null:
		return
	f.store_string(JSON.stringify({"stamp": stamp, "ok": ok, "checks": checks, "diffs": diffs, "log": log_lines,
		"godot": Engine.get_version_info()["string"], "nonruntime": true, "game_files_written": 0}, "  ", true) + "\n")
	f.close()


func _checks(v06_dir: String, v05_entry_path: String, v05_art_dir: String, mask_path: String, reveal_path: String) -> bool:
	var selector: GDScript = load(SELECTOR)
	var tscn := FileAccess.get_file_as_string(LOOP_SCENE)
	if not _check(tscn.contains(WIRED_SELECTOR) and not tscn.contains("unapproved-v05") and not tscn.contains("v06"), "the shared Loop .tscn on disk still names the v04 selector (not edited)"):
		return false
	if not _check(_wire_harness_loop(), "test-only: the Loop scene path resolves to an in-memory Loop rooted in the existing v05 selector"):
		return false
	selector.v05_override = 1
	# Control A: real imported v05 art, runtime hero at the spawn, English, against the committed v05 capture.
	if not _check(await _enter_from_map(), "control A: map flight to Chicago lands in the unchanged v05 scene at the spawn (flight charged)"):
		return false
	await _set_language("en")
	var committed := Image.load_from_file(v05_entry_path)
	diffs["control_a_real_v05_assets_vs_committed_v05_en_entry"] = _diff_px(await _image(), committed.duplicate())
	if not _check(diffs["control_a_real_v05_assets_vs_committed_v05_en_entry"] == 0, "control A: harness render of real v05 assets equals the committed v05 en-entry capture (0 px)"):
		return false
	# Control B: the v05 PNGs injected as ImageTextures over their own paths.
	if not _check(_inject(v05_art_dir, V05_FILE), "control B: v05 PNGs injected as ImageTextures over the v05 res:// paths"):
		return false
	if not _check(await _enter_from_map() and _scene_uses_injected(), "control B: the v05 scene draws the injected textures"):
		return false
	await _set_language("en")
	diffs["control_b_injected_v05_pngs_vs_committed_v05_en_entry"] = _diff_px(await _image(), committed.duplicate())
	if not _check(diffs["control_b_injected_v05_pngs_vs_committed_v05_en_entry"] == 0, "control B: injected v05 PNGs render exactly like the imported v05 textures (0 px)"):
		return false
	# Same-spot v05 reference capture for the before/after pair (heroine reference at the spawn).
	_use_reference_heroine()
	await _set_language("en")
	if await _capture("v05-control-en-entry-heroine-ref48") == null:
		return false
	# v06: inject the runtime-candidate PNGs and fly in again.
	if not _check(_inject(v06_dir, V06_FILE), "v06 runtime-candidate PNGs injected over the v05 res:// paths (outputs/ only, no game file)"):
		return false
	if not _check(await _enter_from_map() and _scene_uses_injected(), "v06: map flight lands in the v05 scene at the spawn and it draws the v06 textures"):
		return false
	var script: GDScript = host.get_script()
	var mask := Image.load_from_file(mask_path)
	var reveal := Image.load_from_file(reveal_path)
	var mismatches := 0
	var reveal_mismatches := 0
	var walkable_count := 0
	for y in 360:
		for x in 640:
			var authored := mask.get_pixel(x, y).r > 0.5
			walkable_count += 1 if authored else 0
			if authored != script.walkable(Vector2(x, y)):
				mismatches += 1
			if (reveal.get_pixel(x, y).r > 0.5) != host.needs_reveal(Vector2(x, y)):
				reveal_mismatches += 1
	if not _check(mismatches == 0 and walkable_count > 60000, "v06 walk-mask guide equals the scene's walkable() (%d walkable px, %d mismatches)" % [walkable_count, mismatches]):
		return false
	if not _check(reveal_mismatches == 0, "v06 occlusion reveal mask equals the scene's needs_reveal() everywhere"):
		return false
	var sites_ok: bool = script.SPAWN == SPAWN and script.SITES.size() == SITES.size()
	for site in script.SITES:
		sites_ok = sites_ok and SITES.get(site[0], Vector2(-1, -1)) == site[1]
	if not _check(sites_ok, "spawn and the three interaction anchors are the v05 ones"):
		return false
	if not _check(host.title_label.text == "芝加哥 · 卢普区" and host.badge_label.text == "技术占位 · 美术未验收", "zh title and art-not-accepted badge unchanged"):
		return false
	_use_reference_heroine()
	await _set_language("zh")
	if await _capture("zh-entry-heroine-ref48") == null:
		return false
	await _set_language("en")
	if not _check(host.title_label.text == "Chicago · The Loop" and host.badge_label.text == "Technical placeholder · Art not accepted", "en title and badge unchanged"):
		return false
	if await _capture("en-entry-heroine-ref48") == null:
		return false
	# Street walk: held move_left along the under-L lane from the stair foot, through the east column line,
	# stopping on the lane west of the plate; no calendar time.
	host.set_process(true)
	host.hero.texture = load("res://scripts/character_directional_idle.gd").texture_for("protagonist-female", "south")
	host.hero.scale = Vector2.ONE
	host.hero.offset = Vector2(0, -20)
	var minutes: int = app.calendar_minutes
	host.hero.position = Vector2(565, 220)
	Input.action_press("move_left")
	var frames := 0
	while host.hero.position.x > LANE_SPOT_X and frames < 600:
		await process_frame
		frames += 1
		if not script.walkable(host.hero.position) or absf(host.hero.position.y - 220.0) > 0.01:
			Input.action_release("move_left")
			return _check(false, "lane walk left the walkable lane at " + str(host.hero.position))
	Input.action_release("move_left")
	await process_frame
	if not _check(host.hero.position.x <= LANE_SPOT_X and host.hero.position.x > LANE_SPOT_X - 6.0 and app.calendar_minutes == minutes, "held move_left walks the under-L lane past the east column, no time charged (x=%.1f)" % host.hero.position.x):
		return false
	host.hero.position = Vector2(LANE_SPOT_X, 220)
	_use_reference_heroine()
	host._update_reveal(10.0)
	await _set_language("zh")
	if await _capture("zh-walk-under-l-lane-heroine-ref48") == null:
		return false
	await _set_language("en")
	if await _capture("en-walk-under-l-lane-heroine-ref48") == null:
		return false
	# Occlusion: behind the west L column, the y-sorted column draws over her and the dithered reveal opens.
	host.hero.position = COLUMN_SPOT
	if not _check(host.needs_reveal(COLUMN_SPOT), "behind the west column is a reveal spot (unchanged mask)"):
		return false
	host.reveal_strength = 0.0
	host._update_reveal(10.0)
	await _set_language("zh")
	if await _capture("zh-occlusion-west-column-reveal-heroine-ref48") == null:
		return false
	await _set_language("en")
	if await _capture("en-occlusion-west-column-reveal-heroine-ref48") == null:
		return false
	return _check(not app.areas_visited.has("scifi.loop"), "the Loop is still not counted toward the three-place goal")
