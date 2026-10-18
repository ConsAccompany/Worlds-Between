extends SceneTree

# WDC annex room 1 v02 review gate: replays the three creator-accepted rooms (NYC room 1, NYC room 2,
# Yonkers room 2) exactly as their acceptance harnesses did, writing captures to a caller-given folder
# (never to outputs/), and re-runs their clue interactions. Pixel comparison is done by the caller.
# Usage: Godot --path game -s <this file> -- <output dir> <stamp-id>
const SCENE := "res://scenes/survey_annex.tscn"
const APPROVED_HERO_IDLE := preload("res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")

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
	print("ACCEPTED_REPLAY_FAIL " + message)
	quit(1)


func _capture(name: String) -> bool:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_viewport().get_texture().get_image()
	if image.get_size() != Vector2i(640, 360):
		push_error("Expected 640x360, got " + str(image.get_size()))
		return false
	var path := folder.path_join("rpg-2-star-ocean-the-second_%s_%s.png" % [name, stamp])
	if image.save_png(path) != OK:
		return false
	print("ACCEPTED_REPLAY_CAPTURE " + path)
	return true


func _open(destination: String, room: int) -> void:
	if host != null:
		host.queue_free()
		await process_frame
	# Each acceptance harness started from a fresh run, so every room starts from one here too.
	app.begin_new_run()
	app.hero_appearance = "female"
	app.select_destination(destination)
	app.current_annex_room = room
	host = (load(SCENE) as PackedScene).instantiate()
	root.add_child(host)
	current_scene = host
	await process_frame
	await process_frame
	host.set_process(false)
	hero = host.hero
	hero.texture = APPROVED_HERO_IDLE
	hero.scale = Vector2(0.5, 0.5)
	hero.offset = Vector2(0, -40)


func _both_languages(label: String) -> bool:
	for lang in ["zh", "en"]:
		app.language = lang
		host._refresh_text()
		if not await _capture(label % lang):
			return false
	return true


func _interact_at(at: Vector2, clue_key: String) -> bool:
	host._close_overlay()
	hero.position = at
	host._unhandled_input(interaction)
	return app.survey_clues.has(clue_key)


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	folder = args[0]
	stamp = args[1]
	interaction.action = "interact"
	interaction.pressed = true
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(640, 360)
	SaveStore.root_path = "user://test-saves/wdc-r1v02-gate-replay-%s" % stamp
	app = root.get_node("AppState")
	DirAccess.make_dir_recursive_absolute(folder)

	# NYC public facilities room 1 (accepted 2/12).
	await _open("scifi.city", 1)
	if not await _both_languages("nyc-public-facilities-room1_existing-scene-godot-%s-640x360-review-v01"):
		_fail("nyc room 1 capture")
		return
	app.language = "zh"
	host._refresh_text()
	for index in [0, 1, 2]:
		if not _interact_at(Vector2([163, 320, 477][index] + 39, 185), "scifi.city:%d" % index):
			_fail("nyc room 1 clue %d" % index)
			return
	print("ACCEPTED_REPLAY_NYC_ROOM1_INTERACTIONS_OK 3")

	# NYC public facilities room 2 (accepted 1/12): same order as its harness.
	await _open("scifi.city", 2)
	if not await _both_languages("nyc-public-facilities-room2_three-pixel-fixtures-godot-%s-640x360_unapproved-v01"):
		_fail("nyc room 2 capture")
		return
	hero.position = Vector2(202, 185)
	app.language = "zh"
	host._refresh_text()
	if not await _capture("nyc-public-facilities-room2_repair-manual-approach-godot-zh-640x360_unapproved-v01"):
		_fail("nyc room 2 approach capture")
		return
	host._unhandled_input(interaction)
	if not app.survey_clues.has("scifi.city:3"):
		_fail("nyc room 2 clue 3")
		return
	if not await _capture("nyc-public-facilities-room2_repair-manual-interaction-godot-zh-640x360_unapproved-v01"):
		_fail("nyc room 2 interaction capture")
		return
	for index in [1, 2]:
		if not _interact_at(Vector2([320, 477][index - 1] + 39, 185), "scifi.city:%d" % (3 + index)):
			_fail("nyc room 2 clue %d" % (3 + index))
			return
	print("ACCEPTED_REPLAY_NYC_ROOM2_INTERACTIONS_OK 3")

	# Yonkers signal maintenance room 2 (accepted 3/12).
	await _open("scifi.outskirts", 2)
	if not await _both_languages("yonkers-maintenance-room2_four-pixel-fixtures-godot-%s-640x360-review-v01"):
		_fail("yonkers room 2 capture")
		return
	app.language = "zh"
	host._refresh_text()
	for index in [0, 1, 2]:
		if not _interact_at(Vector2([163, 320, 477][index] + 39, 185), "scifi.outskirts:%d" % (index + 3)):
			_fail("yonkers room 2 clue %d" % (index + 3))
			return
	print("ACCEPTED_REPLAY_YONKERS_ROOM2_INTERACTIONS_OK 3")

	var dir_path := ProjectSettings.globalize_path(SaveStore.root_path)
	if DirAccess.dir_exists_absolute(dir_path):
		for file in DirAccess.get_files_at(dir_path):
			DirAccess.remove_absolute(dir_path.path_join(file))
		DirAccess.remove_absolute(dir_path)
	print("ACCEPTED_REPLAY_ALL_OK")
	quit()
