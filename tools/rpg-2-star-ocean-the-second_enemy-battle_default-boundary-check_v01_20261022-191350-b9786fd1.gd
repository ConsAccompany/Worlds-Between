extends SceneTree

# Source-equivalence and simulation fixtures, separate from actual normal-speed motion captures.
var app: Node
var original: GDScript
var candidate: Script
var output := ""
var tag := ""
var assertions := 0
var results := {}

func _initialize() -> void:
	call_deferred("_run")

func _check(condition: bool, message: String) -> bool:
	assertions += 1
	if condition:
		return true
	results["failed"] = message
	push_error(message)
	_write()
	quit(1)
	return false

func _write() -> void:
	results["assertions"] = assertions
	var f := FileAccess.open(output.path_join("rpg-2-star-ocean-the-second_enemy-battle_default-boundary-proof_v01_%s.json" % tag),FileAccess.WRITE)
	if f: f.store_string(JSON.stringify(results,"  "))

func _state(battle: Node) -> Dictionary:
	var fighters := []
	for f in battle.fighters:
		# Deliberately excludes cosmetic pose/playback and result presentation clocks.
		fighters.append({"id":f.get("id"), "hp":f.get("hp"), "stamina":f.get("stamina"),
			"x":f.get("x"), "attack_cooldown":f.get("attack_cooldown"), "skill_cooldown":f.get("skill_cooldown")})
	return {"fighters":fighters, "enemy_hp":battle.enemy_hp,"enemy_x":battle.enemy_x,
		"enemy_cooldown":battle.enemy_cooldown,"enemy_windup":battle.enemy_windup,
		"enemy_attacks":battle.enemy_attack_count,"finished":battle.battle_finished,"won":battle.battle_won}

func _simulate(script: Script, enemy: String, enabled: int) -> Array:
	app.begin_new_run()
	app.hero_appearance = "female"
	app.select_destination("scifi.ruins" if enemy == "sentry" else "scifi.outskirts")
	app.begin_battle(enemy,Vector2(330,215))
	script.set("sentry_v2_override", enabled)
	script.set("patrol_animation_override", enabled)
	var scene: Node = load("res://scenes/battle_arena.tscn").instantiate()
	scene.set_script(script)
	root.add_child(scene)
	current_scene = scene
	scene.set_process(false)
	scene.auto_mode = true
	var trace := []
	for i in 720:
		scene._process(1.0/60.0)
		trace.append(_state(scene))
	scene.queue_free()
	current_scene = null
	await process_frame
	return trace

func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 3:
		push_error("Need output folder, original snapshot, unique tag")
		quit(1)
		return
	output = args[0]
	tag = args[2]
	DirAccess.make_dir_recursive_absolute(output)
	SaveStore.root_path = "user://test-saves/enemy49-boundary"
	app = root.get_node("AppState")
	candidate = load("res://scripts/battle_arena.gd")
	original = GDScript.new()
	original.source_code = FileAccess.get_file_as_string(args[1])
	if not _check(original.reload() == OK,"baseline compile"):
		return
	results["source_hashes"] = {"original_text_sha256":original.source_code.sha256_text(),
		"candidate_raw_sha256":FileAccess.get_sha256("res://scripts/battle_arena.gd")}
	if not _check(not candidate.SENTRY_MVP_DEFAULT and not candidate.PATROL_MVP_DEFAULT,"prepared defaults must remain false"):
		return
	for s in [original,candidate]:
		for value in [-1,0,1]:
			s.set("sentry_v2_override",value)
			s.set("patrol_animation_override",value)
			var sentry_expected: bool = value == 1 if value >= 0 else OS.get_cmdline_user_args().has("--sentry-v2-pilot")
			var patrol_expected: bool = value == 1 if value >= 0 else OS.get_cmdline_user_args().has("--patrol-battle-animation-pilot")
			if not _check(s.sentry_v2_enabled() == sentry_expected,"sentry override priority"):
				return
			if not _check(s.patrol_animation_enabled() == patrol_expected,"patrol override priority"):
				return
	var summary := {}
	for enemy in ["sentry","patrol"]:
		var baseline_off: Array = await _simulate(original,enemy,0)
		var prepared_off: Array = await _simulate(candidate,enemy,0)
		var prepared_on: Array = await _simulate(candidate,enemy,1)
		var baseline_on: Array = await _simulate(original,enemy,1)
		for i in baseline_off.size():
			if not _check(baseline_off[i] == prepared_off[i],enemy+" noflag source parity step "+str(i)):
				return
			if not _check(baseline_on[i] == prepared_on[i],enemy+" opt-in source parity step "+str(i)):
				return
			if not _check(prepared_off[i] == prepared_on[i],enemy+" animation simulation parity step "+str(i)):
				return
		summary[enemy] = {"steps_per_case":720,"cases":4,"all_simulation_states_equal":true}
	# Broken optional package degrades to the existing placeholder; no missing resource is loaded.
	candidate.set("patrol_animation_override",1)
	candidate.set("patrol_animation_package_override","res://assets/enemies/absent-enemy49-package.json")
	app.begin_new_run()
	app.begin_battle("patrol",Vector2(330,215))
	var broken: Node = load("res://scenes/battle_arena.tscn").instantiate()
	root.add_child(broken)
	broken.set_process(false)
	if not _check(broken.enemy_animation_texture == null and broken.enemy_texture == null,"invalid optional package fallback"):
		return
	broken.queue_free()
	candidate.set("patrol_animation_package_override","")
	candidate.set("patrol_animation_override",-1)
	candidate.set("sentry_v2_override",-1)
	results["simulation"] = summary
	results["passed"] = true
	results["scope"] = "Direct simulation fixtures, not normal gameplay or art acceptance; cosmetic result gate clocks excluded."
	_write()
	print("ENEMY49_BOUNDARY_ALL_OK assertions=",assertions)
	quit()
