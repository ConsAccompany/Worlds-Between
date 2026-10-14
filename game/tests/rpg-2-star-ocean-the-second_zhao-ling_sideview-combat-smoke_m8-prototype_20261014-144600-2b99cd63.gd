extends SceneTree

var captures: Array[String] = []


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var app: Node = root.get_node("AppState")
	SaveStore.root_path = "user://test-saves/m8-zhao-combat-art"
	app.begin_new_run()
	if not _check(app.recruit_member("zhao-ling"), "Zhao recruited"):
		return
	app.begin_battle("patrol", Vector2(330, 215))
	change_scene_to_file("res://scenes/battle_arena.tscn")
	await process_frame
	await process_frame
	var battle: Node2D = current_scene
	if not _check(battle != null and battle.name == "BattleArena" and battle.fighters.size() == 2, "battle arena has Zhao"):
		return
	battle.paused = true
	var fighter: Dictionary = battle.fighters[1]
	var member: Dictionary = app.member_state("zhao-ling")
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
		member["hp"] = int(member["max_hp"])
		fighter["visual_action"] = ""
		fighter["visual_elapsed"] = 0.0
		fighter["visual_moving"] = false
		fighter["visual_loop_clock"] = 0.0
		fighter["dodge_time"] = 0.0
		fighter["guard"] = false
		match action:
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
				member["hp"] = 0
				fighter["visual_action"] = "down"
				fighter["visual_elapsed"] = 0.20
			"skill":
				fighter["visual_action"] = "skill"
				fighter["visual_elapsed"] = 0.35
		var texture: Texture2D = battle._zhao_combat_texture(fighter, 1)
		var expected := "zhao-ling_sideview-%s-right-phase-%02d_m8-prototype_20261014-144336-" % [action, phase]
		if not _check(texture != null and texture.get_size() == Vector2(80, 80) and texture.resource_path.contains(expected), action + " selects valid phase " + str(phase)):
			return
		if bool(entry["capture"]) and capture_enabled:
			battle.queue_redraw()
			await process_frame
			await process_frame
			if not _capture(action, phase, stamp):
				quit(1)
				return
	member["hp"] = int(member["max_hp"])
	member["energy"] = int(member["max_energy"])
	fighter["dodge_time"] = 0.0
	fighter["attack_cooldown"] = 0.0
	battle._try_attack(1)
	if not _check(fighter["visual_action"] == "attack", "attack call selects attack animation"):
		return
	if not _check(battle._use_skill(1) and fighter["visual_action"] == "skill", "personal skill selects skill animation"):
		return
	if not _check(battle._try_dodge(1) and fighter["dodge_time"] > 0.0, "dodge call selects dodge interval"):
		return
	fighter["dodge_time"] = 0.0
	fighter["x"] = battle.enemy_x - 45.0
	battle.enemy_target_index = 1
	battle._apply_enemy_hit()
	if not _check(fighter["visual_action"] == "hit", "enemy damage selects hit animation"):
		return
	if capture_enabled:
		var name := "rpg-2-star-ocean-the-second_zhao-ling_scifi-battle-native-capture-manifest_m8-prototype_%s-%08x.json" % [stamp, randi()]
		var file := FileAccess.open("res://../outputs/" + name, FileAccess.WRITE)
		if file != null:
			file.store_string(JSON.stringify({"canvas": [640, 360], "status": "unapproved_prototype", "captures": captures}, "\t") + "\n")
	print("M8_ZHAO_COMBAT_VISUAL_SMOKE_OK captures=%d" % captures.size())
	quit(0)


func _capture(action: String, phase: int, stamp: String) -> bool:
	var image := root.get_viewport().get_texture().get_image()
	if image == null or image.get_size() != Vector2i(640, 360):
		push_error("Capture viewport missing or wrong size")
		return false
	var name := "rpg-2-star-ocean-the-second_zhao-ling_scifi-battle-native-%s-phase-%02d_m8-prototype_%s-%08x.png" % [action, phase, stamp, randi()]
	var path := "res://../outputs/" + name
	if image.save_png(path) != OK:
		push_error("Capture failed: " + path)
		return false
	captures.append(name)
	print("CAPTURED " + ProjectSettings.globalize_path(path))
	return true


func _check(condition: bool, label: String) -> bool:
	if condition:
		return true
	push_error("M8 Zhao combat art smoke failed: " + label)
	quit(1)
	return false
