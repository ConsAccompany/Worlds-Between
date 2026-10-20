extends SceneTree

# Normal host movement, unchanged collision and explicit initial placement. Not a human playtest.
var host: Node
var app: Node
var fps := 30
var out := ""
var tag := ""
var context := "city"
var trace := []
var failures := []
var checks := 0

func _initialize() -> void:
	call_deferred("run")

func ck(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures.append(label)
		print("SEA_DISTANCE_ROOT_FAIL ", label)

func tick(label: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	trace.append({"case": label, "position": [host.hero.position.x, host.hero.position.y], "state": host.sprite_pilot.state()})

func shot(label: String) -> void:
	var image := root.get_texture().get_image()
	ck(image.get_size() == Vector2i(1280, 720), "native capture " + label)
	ck(image.save_png(out.path_join("rpg-2-star-ocean-the-second_heroine-sea-distance_%s-%s_actual-input-v01_%s.png" % [context, label, tag])) == OK, "saved " + label)

func move_for(action: String, seconds: float, label: String) -> void:
	var start: Vector2 = host.hero.position
	Input.action_press(action)
	for n in int(round(seconds * fps)):
		await tick(label)
		if n == int(seconds * fps * 0.5):
			shot(label + "-mid")
	Input.action_release(action)
	ck(host.hero.position.distance_to(start) > 5.0, "actual displacement " + label)

func stop_for(seconds: float, label: String) -> void:
	# One frame lets the actual host observe the released input; subsequent positions must be fixed.
	await tick(label + "-release")
	var pin: Vector2 = host.hero.position
	for n in int(round(seconds * fps)):
		await tick(label)
		ck(host.hero.position == pin, "physical stop " + label + str(n))
		if n == 1:
			shot(label + "-settle")
	if seconds >= 0.16:
		ck(host.sprite_pilot.action == "idle", "settled exact idle " + label)
		shot(label + "-idle")

func run() -> void:
	var args := OS.get_cmdline_user_args()
	out = args[1]
	tag = args[2]
	context = args[3]
	fps = int(args[4])
	app = root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = "female"
	app.language = "en" if context == "city" else "zh"
	app.select_destination("scifi.city")
	app.current_annex_room = 2
	var loader = load("res://scripts/exploration_sprite_set_pilot.gd")
	var driver = load("res://scripts/hsea09/rpg-2-star-ocean-the-second_heroine-sea_distance-driver_opt-in-v01_20261020-214620-4be375a2.gd")
	loader.enabled_override = 0
	loader.registry_override = args[0]
	driver.enabled_override = 1
	var scene := "res://scenes/scifi_exploration_area.tscn" if context == "city" else "res://scenes/survey_annex.tscn"
	ck(change_scene_to_file(scene) == OK, "normal scene entry")
	for n in 3:
		await process_frame
	host = current_scene
	host.hero.position = Vector2(270, 235)
	ck(host.sprite_pilot != null, "new optional driver attached")
	if host.sprite_pilot == null:
		quit(1)
		return
	ck(host.hero.scale == Vector2(0.5, 0.5), "48logical scale")
	ck(host.hero.texture.get_size() == Vector2(80, 112), "80x112 source")
	await stop_for(0.20, "initial-rest")
	await move_for("move_right", 0.70, "east-start-run")
	await stop_for(0.0667, "short-stop")
	await move_for("move_right", 0.20, "same-facing-repress")
	await stop_for(0.24, "east-stop")
	await move_for("move_left", 0.65, "west-reversal")
	await stop_for(0.24, "west-stop")
	await move_for("move_up", 0.24, "north-turn")
	await stop_for(0.24, "north-stop")
	await move_for("move_down", 0.24, "south-reversal")
	await stop_for(0.24, "south-stop")
	var proof := {"checks": checks, "failures": failures, "trace": trace, "context": context, "fps": fps, "initialPlacement": [270,235], "normalHostInput": true, "artApproved": false, "fluidityCertified": false, "defaultAdopted": false, "scope": "Actual input and fixed-position settling; does not certify world-footlock, dark visibility or full motion quality."}
	var file := FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_heroine-sea-distance_%s-root-proof_v01_%s.json" % [context,tag]), FileAccess.WRITE)
	file.store_string(JSON.stringify(proof, " "))
	file.close()
	host.queue_free()
	await process_frame
	loader.clear_cache()
	if failures.is_empty():
		print("SEA_DISTANCE_ROOT_PASS checks=", checks)
		quit(0)
	else:
		quit(1)
