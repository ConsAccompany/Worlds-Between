extends SceneTree


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var app: Node = root.get_node("AppState")
	SaveStore.root_path = "user://test-saves/m8-female-combat-art"
	app.begin_new_run()
	app.hero_appearance = "female"
	app.begin_battle("patrol", Vector2(330, 215))
	change_scene_to_file("res://scenes/battle_arena.tscn")
	await process_frame
	await process_frame
	var battle: Node2D = current_scene
	if not _check(battle != null and battle.name == "BattleArena", "battle arena exists"):
		return
	# Freeze only the visual evidence setup; the regular M3 smoke exercises live combat.
	battle.paused = true
	var fighter: Dictionary = battle.fighters[0]
	var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	var capture_enabled := not OS.get_cmdline_user_args().has("--no-capture")
	var cases := [
		{"action": "idle", "phase": 1, "capture": true},
		{"action": "move", "phase": 2, "capture": false},
		{"action": "attack", "phase": 2, "capture": true},
		{"action": "guard", "phase": 1, "capture": false},
		{"action": "dodge", "phase": 2, "capture": false},
		{"action": "hit", "phase": 1, "capture": false},
		{"action": "down", "phase": 2, "capture": false},
		{"action": "skill", "phase": 3, "capture": true},
	]
	for entry in cases:
		var action: String = entry["action"]
		var phase: int = entry["phase"]
		app.hero_state["hp"] = 100
		fighter["visual_action"] = ""
		fighter["visual_elapsed"] = 0.0
		fighter["visual_moving"] = false
		fighter["visual_loop_clock"] = 0.0
		fighter["dodge_time"] = 0.0
		fighter["guard"] = false
		match action:
			"idle":
				pass
			"move":
				fighter["visual_moving"] = true
				fighter["visual_loop_clock"] = 0.11
			"attack":
				fighter["visual_action"] = "attack"
				fighter["visual_elapsed"] = 0.15
			"guard":
				fighter["guard"] = true
			"dodge":
				fighter["dodge_time"] = 0.1
			"hit":
				fighter["visual_action"] = "hit"
			"down":
				app.hero_state["hp"] = 0
				fighter["visual_action"] = "down"
				fighter["visual_elapsed"] = 0.20
			"skill":
				fighter["visual_action"] = "skill"
				fighter["visual_elapsed"] = 0.35
		var texture: Texture2D = battle._female_combat_texture(fighter, 0)
		if not _check(texture != null and texture.get_size() == Vector2(80, 80) and texture.resource_path.contains("protagonist-female_sideview-" + action + "-right-phase-%02d" % phase), action + " selects phase " + str(phase)):
			return
		if bool(entry["capture"]) and capture_enabled:
			battle.queue_redraw()
			await process_frame
			await process_frame
			if not _capture(action, phase, stamp):
				quit(1)
				return
	# The actual combat entry points set the same visual states; their gameplay
	# behavior remains covered by the existing M3 and M5 smoke tests.
	app.hero_state["hp"] = 100
	fighter["dodge_time"] = 0.0
	fighter["attack_cooldown"] = 0.0
	battle._try_attack(0)
	if not _check(fighter["visual_action"] == "attack", "attack call selects attack animation"):
		return
	if not _check(battle._use_skill(0) and fighter["visual_action"] == "skill", "personal skill call selects skill animation"):
		return
	if not _check(battle._try_dodge(0) and fighter["dodge_time"] > 0.0, "dodge call selects dodge interval"):
		return
	fighter["dodge_time"] = 0.0
	fighter["x"] = battle.enemy_x - 45.0
	battle._apply_enemy_hit()
	if not _check(fighter["visual_action"] == "hit", "enemy damage selects hit animation"):
		return
	print("M8_FEMALE_COMBAT_VISUAL_SMOKE_OK")
	quit(0)


func _capture(action: String, phase: int, stamp: String) -> bool:
	var image := root.get_viewport().get_texture().get_image()
	if image == null or image.get_size() != Vector2i(640, 360):
		push_error("Capture viewport missing or wrong size")
		return false
	var name := "rpg-2-star-ocean-the-second_protagonist-female_scifi-battle-native-%s-phase-%02d_m8-prototype_%s-%08x.png" % [action, phase, stamp, randi()]
	var path := "res://../outputs/" + name
	if image.save_png(path) != OK:
		push_error("Capture failed: " + path)
		return false
	print("CAPTURED " + ProjectSettings.globalize_path(path))
	return true


func _check(condition: bool, label: String) -> bool:
	if condition:
		return true
	push_error("M8 female combat art smoke failed: " + label)
	quit(1)
	return false
