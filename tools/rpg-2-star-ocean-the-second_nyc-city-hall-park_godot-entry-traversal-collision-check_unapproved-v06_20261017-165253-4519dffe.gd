extends SceneTree

# NYC City Hall Park v06 (UNAPPROVED) -- native Godot entry/traversal/occlusion/interaction
# captures and focused collision, reveal, legacy-save and interaction checks in the real city scene.
# Run (windowed, so captures are real renders):
#   Godot --path game -s <this file> -- [--out=<abs dir>] [--chp6-dir=<abs dev dir>]
# The v06 candidate is switched on for this process only (enabled_override = 1).
# Entry captures show the approved female selout v8 SOUTH STATIC frame at 48 logical px;
# traversal captures use the runtime's own walking/idle frames moved by real input actions.
# Nothing here accepts the scene art.

const SCENE := "res://scenes/scifi_exploration_area.tscn"
const PARK_V06 := "res://scripts/city_hall_park_v06_scene.gd"
const PARK_V05 := "res://scripts/city_hall_park_scene.gd"
const APPROVED_HERO_IDLE := "res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png"
const TAG := "unapproved-v06_20261017-165253-4519dffe"
const HOTSPOTS := {
	"liang_xu": [Vector2(282, 180), 50.0], "trace_0": [Vector2(285, 267), 34.0],
	"trace_1": [Vector2(378, 181), 34.0], "assist": [Vector2(120, 187), 40.0],
	"survey": [Vector2(558, 166), 43.0], "report": [Vector2(470, 247), 50.0],
}

var out_dir := ""
var failures: Array[String] = []
var passes := 0
var off_mask_frames := 0
var moved_frames := 0
var app: Node
var host: Node2D
var park
var metrics := {}


func _initialize() -> void:
	call_deferred("_run")


func _check(ok: bool, message: String) -> void:
	if ok:
		passes += 1
		print("CHP6_PASS " + message)
	else:
		failures.append(message)
		push_error("CHP6_FAIL " + message)


func _frame_image() -> Image:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	return root.get_viewport().get_texture().get_image()


func _capture(name: String) -> void:
	var image := await _frame_image()
	_check(image.get_size() == Vector2i(640, 360), "native 640x360 capture " + name)
	if out_dir.is_empty():
		return
	var path := out_dir.path_join("rpg-2-star-ocean-the-second_nyc-city-hall-park_godot-%s_%s.png" % [name, TAG])
	_check(image.save_png(path) == OK, "saved " + name)
	print("CHP6_CAPTURE " + path)


func _open_city() -> void:
	if host != null and is_instance_valid(host):
		host.queue_free()
		await process_frame
	host = (load(SCENE) as PackedScene).instantiate()
	root.add_child(host)
	current_scene = host
	await process_frame
	await process_frame
	park = host.city_hall_park


func _release() -> void:
	for action in ["move_left", "move_right", "move_up", "move_down"]:
		Input.action_release(action)


func _walk_to(target: Vector2, max_frames := 900) -> bool:
	var hero: Sprite2D = host.hero
	var stuck := 0
	var last := hero.position
	for frame in max_frames:
		var delta := target - hero.position
		if delta.length() < 1.5:
			_release()
			return true
		_release()
		if delta.x > 1.0:
			Input.action_press("move_right")
		elif delta.x < -1.0:
			Input.action_press("move_left")
		if delta.y > 1.0:
			Input.action_press("move_down")
		elif delta.y < -1.0:
			Input.action_press("move_up")
		await process_frame
		moved_frames += 1
		if not park.walkable(hero.position):
			off_mask_frames += 1
		stuck = stuck + 1 if hero.position.distance_to(last) < 0.01 else 0
		last = hero.position
		if stuck > 30:
			break
	_release()
	return hero.position.distance_to(target) < 1.5


func _hold(action: String, frames: int) -> void:
	Input.action_press(action)
	for frame in frames:
		await process_frame
		moved_frames += 1
		if not park.walkable(host.hero.position):
			off_mask_frames += 1
	Input.action_release(action)
	await process_frame


func _route(points: Array) -> bool:
	for point in points:
		if not await _walk_to(point):
			push_error("route stalled before " + str(point) + " at " + str(host.hero.position))
			return false
	return true


func _set_language(lang: String) -> void:
	app.language = lang
	host._refresh_text()


func _interact() -> void:
	var event := InputEventAction.new()
	event.action = "interact"
	event.pressed = true
	host._unhandled_input(event)


func _settle_reveal(frames := 20) -> void:
	for frame in frames:
		await process_frame


func _hero_visible_fraction(at: Vector2) -> float:
	# Render with and without the hero at the same spot (reveal state unchanged) and count body pixels that differ.
	var hero: Sprite2D = host.hero
	host.set_process(false)
	hero.position = at
	hero.z_index = int(at.y)
	await _settle_reveal(4)
	var with_hero := await _frame_image()
	hero.visible = false
	var without_hero := await _frame_image()
	hero.visible = true
	var hero_image := hero.texture.get_image()
	var opaque := 0
	for y in hero_image.get_height():
		for x in hero_image.get_width():
			if hero_image.get_pixel(x, y).a > 0.5:
				opaque += 1
	var differ := 0
	for y in range(int(at.y) - 48, int(at.y) + 5):
		for x in range(int(at.x) - 17, int(at.x) + 17):
			if x >= 0 and y >= 0 and x < 640 and y < 360 and not with_hero.get_pixel(x, y).is_equal_approx(without_hero.get_pixel(x, y)):
				differ += 1
	host.set_process(true)
	return float(differ) / float(maxi(1, opaque))


func _run() -> void:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--out="):
			out_dir = argument.trim_prefix("--out=")
			DirAccess.make_dir_recursive_absolute(out_dir)
	Engine.max_fps = 60
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(640, 360)
	load("res://scripts/save_store.gd").root_path = "user://test-saves/chp6-check"
	app = root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = "female"
	app.select_destination("scifi.city")
	# v05 is a local-only baseline; when it is absent (clean clone) there is no v05 branch to switch off.
	if ResourceLoader.exists(PARK_V05):
		load(PARK_V05).enabled_override = 0

	# ---------------------------------------------------------------- same-viewport reference: CURRENT runtime city (switch off)
	load(PARK_V06).enabled_override = 0
	await _open_city()
	_check(park == null, "default runtime keeps the existing city plate")
	host.set_process(false)
	host.hero.texture = load(APPROVED_HERO_IDLE)
	host.hero.scale = Vector2(0.5, 0.5)
	host.hero.offset = Vector2(0, -40)
	_set_language("en")
	await _capture("en-current-runtime-city-reference-640x360")

	load(PARK_V06).enabled_override = 1
	_set_language("zh")
	await _open_city()
	_check(park != null and park.get_script().resource_path == PARK_V06, "City Hall Park v06 layers loaded in the real city scene")
	if park == null:
		_finish()
		return
	var hero: Sprite2D = host.hero
	_check(hero.position == Vector2(340, 253) and park.walkable(hero.position), "spawn unchanged (340,253) and walkable")
	_check(host.city_npc.visible and host.city_npc.position == Vector2(282, 180), "Liang Xu at the unchanged city position")
	_check(hero.texture.get_height() == 48 and hero.scale == Vector2.ONE, "runtime hero frame displays 48 logical px")
	var elm: Sprite2D = host.get_node("CityHallParkV06_tree_east_elm")
	_check(elm != null and elm.z_index == 305 and elm.texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST and elm.material is ShaderMaterial, "SE elm: pivot z 305, nearest filter, reveal shader")
	_check(host.get_node("CityHallParkV06_fountain_centre").z_index == 262, "fountain centre Y-sorted at its basin row")

	# ---------------------------------------------------------------- entry captures (approved v8 static at 48 px)
	host.set_process(false)
	var runtime_texture := hero.texture
	hero.texture = load(APPROVED_HERO_IDLE)
	hero.scale = Vector2(0.5, 0.5)
	hero.offset = Vector2(0, -40)
	_set_language("zh")
	await _capture("zh-entry-640x360")
	var zh_title: String = host.title_label.text
	_set_language("en")
	await _capture("en-entry-640x360")
	_check(host.title_label.text == "Lower Manhattan · City Hall Park", "English title unchanged")
	_check(zh_title != host.title_label.text and zh_title.contains("市政厅"), "Chinese title unchanged (" + zh_title + ")")
	hero.texture = runtime_texture
	hero.scale = Vector2.ONE
	hero.offset = Vector2(0, -20)
	host.set_process(true)

	# ---------------------------------------------------------------- traversal by real input
	_set_language("zh")
	var ok := await _route([Vector2(320, 253), Vector2(320, 214)])
	_check(ok, "walk up the central axis")
	await _capture("zh-traverse-axis-640x360")
	ok = await _route([Vector2(320, 192), Vector2(300, 192)])
	_check(ok, "reach the promenade in front of the City Hall gate beside Liang Xu")
	await _capture("zh-traverse-promenade-gate-640x360")
	ok = await _route([Vector2(170, 192), Vector2(170, 214), Vector2(110, 240), Vector2(104, 262), Vector2(120, 292),
		Vector2(171, 298), Vector2(228, 290), Vector2(244, 258), Vector2(196, 238)])
	_check(ok, "walk the lane all the way around the fountain basin")
	var centre: Sprite2D = host.get_node("CityHallParkV06_fountain_centre")
	_check(hero.z_index < centre.z_index, "fountain centrepiece drawn in front of the hero standing behind the basin")
	_set_language("en")
	await _capture("en-traverse-fountain-behind-640x360")
	ok = await _route([Vector2(240, 258), Vector2(285, 262), Vector2(320, 258), Vector2(400, 258), Vector2(470, 250)])
	_check(ok, "west link, axis and terrace walk to the report plaza")
	await _capture("en-traverse-report-plaza-640x360")
	ok = await _route([Vector2(470, 220), Vector2(470, 196), Vector2(566, 196), Vector2(594, 203)])
	_check(ok, "report link up to the promenade and east to the worst-covered foot under the SE elm (594,203)")
	metrics["se_elm_body_cover_at_594_203"] = snappedf(park.canopy_cover(hero.position), 0.001)
	await _settle_reveal(24)
	_check(park.reveal_strength() > 0.99, "SE elm reveal fully open while the hero is behind its crown (%.2f)" % park.reveal_strength())
	_check(not host.city_hero_silhouette.visible, "v06 needs no hide-and-silhouette cue under crowns")
	await _capture("en-occlusion-se-elm-reveal-640x360")
	_set_language("zh")
	await _capture("zh-occlusion-se-elm-reveal-640x360")
	ok = await _route([Vector2(558, 186), Vector2(558, 166)])
	_check(ok, "walk onto the survey kiosk apron (558,166)")
	await _settle_reveal(24)
	_check(park.reveal_strength() < 0.01, "reveal closes again once the hero leaves the crown")
	_set_language("en")
	await _capture("en-traverse-survey-kiosk-640x360")
	_check(off_mask_frames == 0, "hero never left the walk mask during %d moved frames" % moved_frames)

	# ---------------------------------------------------------------- crown reveal: measured hero visibility
	var spot := Vector2(594, 203)
	var revealed: float = await _hero_visible_fraction(spot)
	var material: ShaderMaterial = elm.material
	var max_hole = material.get_shader_parameter("max_hole")
	material.set_shader_parameter("max_hole", 0.0)
	var unrevealed: float = await _hero_visible_fraction(spot)
	material.set_shader_parameter("max_hole", max_hole)
	metrics["hero_visible_fraction_under_se_elm"] = {"reveal": snappedf(revealed, 0.001), "no_reveal": snappedf(unrevealed, 0.001)}
	_check(revealed > 0.8 and revealed > unrevealed + 0.1, "hero stays readable under the SE elm (%.2f visible with reveal vs %.2f without)" % [revealed, unrevealed])

	# ---------------------------------------------------------------- collision probes (real input)
	var probes := [
		["promenade north edge (City Hall fence/stair) stops the hero", Vector2(320, 192), "move_up", 50, "y", 179.4, 181.0],
		["lawn curb west of the axis is solid", Vector2(320, 230), "move_left", 50, "x", 297.4, 299.0],
		["fountain basin solid from the south", Vector2(171, 300), "move_up", 60, "y", 289.0, 301.0],
		["fountain basin solid from the north", Vector2(171, 226), "move_down", 60, "y", 225.0, 241.0],
		["plaza east lamp base is solid", Vector2(254, 250), "move_down", 40, "y", 250.0, 263.0],
		["footer row cannot be entered", Vector2(320, 290), "move_down", 60, "y", 290.0, 306.6],
		["kiosk stair mouth stops the hero on the apron", Vector2(558, 176), "move_up", 50, "y", 151.4, 153.0],
		["hedge beside the kiosk apron is solid", Vector2(520, 192), "move_up", 50, "y", 179.4, 181.0],
		["report terminal base is solid", Vector2(480, 258), "move_right", 40, "x", 480.0, 492.0],
		["assist (ledger) south edge blocks below y 204", Vector2(120, 187), "move_down", 60, "y", 202.0, 204.0],
	]
	for probe in probes:
		hero.position = probe[1]
		await _hold(probe[2], probe[3])
		var value: float = hero.position.y if probe[4] == "y" else hero.position.x
		_check(value >= probe[5] and value <= probe[6], "%s (%s=%.1f)" % [probe[0], probe[4], value])
	_check(not park.walkable(Vector2(82, 260)) and park.walkable(Vector2(82, 203.5)), "legacy spawn (82,260) is planting; landing (82,203.5) is west-apron paving")
	_check(off_mask_frames == 0, "no off-mask frame during collision probes")

	# ---------------------------------------------------------------- thin-post occlusion: promenade lamp
	host.set_process(false)
	hero.position = Vector2(212, 200)
	hero.z_index = int(hero.position.y)
	var lamps: Sprite2D = host.get_node("CityHallParkV06_lamps_promenade_s")
	_check(hero.z_index < lamps.z_index, "hero on the promenade is behind the south-edge lamp")
	var lamp_image := (lamps.texture as Texture2D).get_image()
	var shot := await _frame_image()
	var post_pixels := 0
	var post_matches := 0
	for y in range(170, 216):
		for x in range(209, 216):
			var c := lamp_image.get_pixel(x, y)
			if c.a > 0.5:
				post_pixels += 1
				if shot.get_pixel(x, y).is_equal_approx(c):
					post_matches += 1
	_check(post_pixels > 20 and post_matches == post_pixels, "lamp pixels drawn over the hero (%d/%d)" % [post_matches, post_pixels])
	host.set_process(true)

	# ---------------------------------------------------------------- swept reachability from spawn (as m8 navigation smoke)
	var reached := {Vector2i(340, 253): true}
	var pending: Array[Vector2i] = [Vector2i(340, 253)]
	var cursor := 0
	while cursor < pending.size():
		var cell := pending[cursor]
		cursor += 1
		for offset in [Vector2i(4, 0), Vector2i(-4, 0), Vector2i(0, 4), Vector2i(0, -4)]:
			var next: Vector2i = cell + offset
			if reached.has(next) or not park.walkable(Vector2(next)):
				continue
			if park.slide_position(Vector2(cell), Vector2(next)).is_equal_approx(Vector2(next)):
				reached[next] = true
				pending.append(next)
	for key in HOTSPOTS:
		var target: Vector2 = HOTSPOTS[key][0]
		var radius: float = HOTSPOTS[key][1]
		var best := INF
		for cell in reached:
			best = minf(best, Vector2(cell).distance_to(target))
		_check(park.walkable(target) and best < radius - 4.0, "hotspot %s standable and reachable (%.1f < %.0f)" % [key, best, radius])
	var stable := true
	for x in range(-20, 661, 20):
		for y in range(120, 341, 10):
			var repaired: Vector2 = park.safe_position(Vector2(x, y))
			if not park.walkable(repaired) or park.safe_position(repaired) != repaired:
				stable = false
	_check(stable, "save/resume recovery always lands on a stable walkable foot")

	# ---------------------------------------------------------------- interactions (actual interact action), with captures
	host.set_process(false)
	_set_language("zh")
	hero.position = HOTSPOTS["liang_xu"][0] + Vector2(0, 8)
	hero.z_index = int(hero.position.y)
	_interact()
	_check(host.dialogue_open and host.dialogue_mode == "recruit", "Liang Xu conversation opens")
	await _capture("zh-interact-liang-xu-640x360")
	host._close_dialogue()
	hero.position = HOTSPOTS["trace_0"][0]
	hero.z_index = int(hero.position.y)
	_interact()
	_check(app.field_traces.has("scifi.city:0"), "trace 1 (double-numbered sign) recorded")
	await _capture("zh-interact-trace-sign-640x360")
	host._close_dialogue()
	_set_language("en")
	hero.position = HOTSPOTS["trace_1"][0]
	hero.z_index = int(hero.position.y)
	_interact()
	_check(app.field_traces.has("scifi.city:1"), "trace 2 (gate-pier inspection sheet) recorded")
	await _capture("en-interact-trace-pier-640x360")
	host._close_dialogue()
	hero.position = HOTSPOTS["assist"][0]
	hero.z_index = int(hero.position.y)
	_interact()
	_check(host.dialogue_open and host.dialogue_mode == "assist", "allocation ledger assist opens")
	await _capture("en-interact-ledger-640x360")
	host._close_dialogue()
	hero.position = HOTSPOTS["report"][0]
	hero.z_index = int(hero.position.y)
	_interact()
	_check(host.feedback_key == "report_locked", "field report terminal answers (locked before the survey)")
	await _capture("en-interact-report-locked-640x360")
	host.set_process(true)
	var survey_foot: Vector2 = HOTSPOTS["survey"][0]
	hero.position = survey_foot
	_interact()
	await process_frame
	await process_frame
	_check(current_scene != null and current_scene.name == "SurveyAnnex", "survey entrance opens the public-works annex")
	if current_scene != null and current_scene.has_method("_back_room"):
		current_scene._back_room()
		await process_frame
		await process_frame
		host = current_scene
		park = host.get("city_hall_park")
		_check(park != null and park.get_script().resource_path == PARK_V06 and host.hero.position.distance_to(survey_foot) < 1.0 and park.walkable(host.hero.position), "return from the annex lands on the kiosk apron with the v06 layers")
		_set_language("zh")
		await _capture("zh-annex-return-kiosk-640x360")

	# ---------------------------------------------------------------- legacy save end to end (old saves are not rewritten)
	var legacy_save: String = app.write_auto_save("area", Vector2(82, 260), "manual_note")
	var saved_text := FileAccess.get_file_as_string(legacy_save) if FileAccess.file_exists(legacy_save) else ""
	_check(app.load_save(legacy_save), "legacy city save loads")
	change_scene_to_file(app.loaded_scene_path())
	await process_frame
	await process_frame
	await process_frame
	host = current_scene
	park = host.get("city_hall_park")
	_check(park != null and host.hero.position == Vector2(82, 203.5) and park.walkable(host.hero.position), "legacy (82,260) lands on the west apron (82,203.5), same spot as the old plate")
	_check(saved_text.is_empty() or FileAccess.get_file_as_string(legacy_save) == saved_text, "loading did not rewrite the legacy save file")
	_set_language("en")
	await _capture("en-legacy-save-landing-640x360")
	_finish()


func _finish() -> void:
	_release()
	print("CHP6_METRICS " + JSON.stringify(metrics))
	print("CHP6_SUMMARY passes=%d failures=%d moved_frames=%d off_mask_frames=%d" % [passes, failures.size(), moved_frames, off_mask_frames])
	if failures.is_empty():
		print("CHP6_GODOT_CHECK_OK")
	quit(0 if failures.is_empty() else 1)
