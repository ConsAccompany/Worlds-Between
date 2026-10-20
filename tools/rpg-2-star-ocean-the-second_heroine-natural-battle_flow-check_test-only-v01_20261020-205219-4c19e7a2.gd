extends SceneTree
# Natural normal-entry heroine battle flow (test-only, scripted normal-game evidence; NOT a human playtest).
# exploration walk -> real encounter -> Input.action_press driven battle under the real engine loop
# (--fixed-fps, optional --write-movie) -> natural victory -> result mouse click -> exploration return -> save reload.
# No HP/damage/timer/cooldown/AI writes, no _finish_battle/_try_attack calls, no renderer subclass or pose swap.
# Declared setup: the exploration hero is placed ONCE 70 px left of the visible enemy, then walks in with move_right.
# Args after --: <out_dir> <package_index_res_path> <tag> <scenario patrol|sentry>
const EXPLORE_PATH := "res://scenes/scifi_exploration_area.tscn"
const ARENA_SCRIPT := "res://scripts/battle_arena.gd"
const SOURCES := ["res://scripts/battle_arena.gd", "res://scripts/scifi_exploration_area.gd", "res://scripts/app_state.gd", "res://scripts/save_store.gd", "res://scripts/battle_rules.gd", "res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd", "res://scenes/battle_arena.tscn", "res://scenes/scifi_exploration_area.tscn"]
var app: Node
var arena_script: GDScript
var save_store: GDScript
var out := ""
var index_path := ""
var tag := ""
var scenario := ""
var checks: Array = []
var failures: Array = []
var trace: Array = []
var inputs: Array = []
var captures: Array = []
var frame := 0


func _initialize() -> void:
	call_deferred("_run")
	create_timer(150.0).timeout.connect(func(): print("NATURAL_FLOW_WATCHDOG"); quit(2))


func ck(ok: bool, label: String, detail: Variant = null) -> void:
	checks.append({"check": label, "passed": ok, "detail": detail})
	print("NATURAL_FLOW ", "PASS " if ok else "FAIL ", label, "" if detail == null else " " + str(detail))
	if not ok:
		failures.append(label)


func tick() -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	frame += 1


func press(action: String) -> void:
	Input.action_press(action)
	inputs.append({"frame": frame, "action": action, "pressed": true})


func release(action: String) -> void:
	if Input.is_action_pressed(action):
		Input.action_release(action)
		inputs.append({"frame": frame, "action": action, "pressed": false})


func shot(label: String) -> void:
	var img: Image = root.get_texture().get_image()
	var file := "rpg-2-star-ocean-the-second_heroine-natural-battle_%s-%s_critical-capture_%s.png" % [scenario, label, tag]
	var err := img.save_png(out.path_join(file))
	ck(err == OK and img.get_size() == Vector2i(1280, 720) and DisplayServer.get_name() != "headless", "critical capture %s saved at 1280x720 from the live window" % label, {"size": [img.get_width(), img.get_height()], "display": DisplayServer.get_name()})
	captures.append({"label": label, "file": file, "frame": frame, "sha256": FileAccess.get_sha256(out.path_join(file))})


func after_notes() -> Array:
	return save_store.list_entries().filter(func(e): return String(e.get("snapshot", {}).get("note", "")) == "after_battle")


func growth() -> Dictionary:
	return {"xp": int(app.hero_state["xp"]), "jp": int(app.hero_state["jp"]), "level": int(app.hero_state["level"]), "hp": int(app.hero_state["hp"])}


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	out = args[0]; index_path = args[1]; tag = args[2]; scenario = args[3]
	app = root.get_node("AppState")
	arena_script = load(ARENA_SCRIPT)
	save_store = load("res://scripts/save_store.gd")
	var patrol := scenario == "patrol"
	var destination := "scifi.outskirts" if patrol else "scifi.ruins"
	var lang := "en" if patrol else "zh"
	var hashes := {}
	for p in SOURCES:
		hashes[p] = FileAccess.get_sha256(p)
	hashes[index_path] = FileAccess.get_sha256(index_path)
	# Normal party setup only: a fresh run has the solo heroine; no companions are faked.
	app.begin_new_run()
	app.hero_appearance = "female"
	app.select_destination(destination)
	app.language = lang
	app.language_changed.emit()
	arena_script.combat_sprite_set_override = 1
	arena_script.combat_sprite_set_index_override = index_path
	arena_script.heroine_sea_contact_override = 1
	arena_script.battle_backdrop_override = 1 if patrol else 0
	arena_script.sentry_v2_override = 0
	arena_script.patrol_animation_override = 0
	ck(change_scene_to_file(EXPLORE_PATH) == OK, "normal exploration scene entry %s %s" % [destination, lang])
	for i in 3:
		await tick()
	var explore: Node = current_scene
	ck(explore != null and explore.enemy_visible, "enemy is visible in exploration", explore.enemy_position if explore != null else null)
	var enemy_pos: Vector2 = explore.enemy_position
	explore.hero.position = enemy_pos + Vector2(-70, 0)
	trace.append({"frame": frame, "phase": "explore", "declaredPlacement": [explore.hero.position.x, explore.hero.position.y]})
	shot("explore-start")
	var before_saves: int = save_store.list_entries().size()
	press("move_right")
	var guard := 0
	while current_scene == explore and guard < 120:
		await tick()
		guard += 1
	release("move_right")
	var battle: Node = current_scene
	for i in 2:
		await tick()
	battle = current_scene
	ck(battle != null and battle.get_script() == arena_script and battle.enemy_id == scenario, "walking into the enemy opens the real %s battle" % scenario, {"frames": guard})
	ck(app.battle_return_position.distance_to(enemy_pos) > 43.0, "return position is the natural >43 px safe point", [app.battle_return_position.x, app.battle_return_position.y])
	ck(save_store.list_entries().size() == before_saves + 1, "exactly one pre-battle autosave written by the encounter")
	ck(battle.enemy_hp == int(arena_script.ENEMIES[scenario]["max_hp"]) and battle.fighters.size() == 1 and battle.fighters[0]["id"] == "hero", "normal enemy max HP and solo heroine party", {"hp": battle.enemy_hp, "party": app.active_party_ids})
	ck(battle.fighters[0].has("contact_event_id") and battle.combat_sprite_sets != null and battle.combat_sprite_sets.has_set(0), "contact timing mode and actual package are active on the heroine")
	var growth_before := growth()
	var after_before := after_notes().size()
	var fighter: Dictionary = battle.fighters[0]
	var reach := float(app.MEMBER_DEFS["hero"]["attack_range"])
	var last_log := 0
	var anticipation_done := false
	var contact_done := false
	var finishing_frame := -1
	var result_frame := -1
	guard = 0
	while guard < 900:
		# Inputs are applied at the start of a frame (process_frame fires before node _process), so the arena's
		# is_action_just_pressed sees the request in exactly this frame; the release at the next frame start clears it.
		await process_frame
		release("battle_attack")
		var dist := absf(battle.enemy_x - float(fighter["x"]))
		var wants_attack: bool = not battle.battle_finished and float(fighter["attack_cooldown"]) == 0.0 and dist <= reach - 4.0
		if not battle.battle_finished and dist > reach - 10.0:
			press("move_right")
		else:
			release("move_right")
		if wants_attack:
			press("battle_attack")
		await RenderingServer.frame_post_draw
		frame += 1
		guard += 1
		var row := {"frame": frame, "enemyHP": battle.enemy_hp, "heroHP": int(app.hero_state["hp"]), "energy": int(app.hero_state["energy"]), "heroX": snappedf(float(fighter["x"]), 0.01), "enemyX": snappedf(battle.enemy_x, 0.01), "attackCooldown": snappedf(float(fighter["attack_cooldown"]), 0.0001), "enemyCooldown": snappedf(battle.enemy_cooldown, 0.0001), "enemyWindup": snappedf(battle.enemy_windup, 0.0001), "event": fighter["contact_event_id"], "eventState": fighter["contact_event_state"], "eventClock": snappedf(float(fighter["contact_event_clock"]), 0.0001), "attacks": battle.player_attack_count, "enemyAttacks": battle.enemy_attack_count, "finished": battle.battle_finished, "overlay": battle.result_overlay.visible, "sprite": battle.combat_sprite_sets.current_frame(0)}
		trace.append(row)
		if not anticipation_done and String(fighter["contact_event_state"]) == "pending" and float(fighter["contact_event_clock"]) > 0.05:
			anticipation_done = true
			shot("anticipation")
		if battle.contact_event_log.size() > last_log:
			for e in battle.contact_event_log.slice(last_log):
				row["resolved"] = e
				if not contact_done and String(e["outcome"]) == "hit":
					contact_done = true
					shot("contact")
			last_log = battle.contact_event_log.size()
		if battle.battle_finished and finishing_frame < 0:
			finishing_frame = frame
			shot("finishing-contact")
		if battle.battle_finished and battle.result_overlay.visible and not battle.result_button.disabled:
			result_frame = frame
			break
	release("move_right")
	var elog: Array = battle.contact_event_log.duplicate(true)
	var hits := elog.filter(func(e): return e["outcome"] == "hit")
	ck(battle.battle_finished and battle.battle_won and battle.enemy_hp == 0, "natural victory from the real engine loop", {"frames": guard, "attacks": battle.player_attack_count})
	ck(hits.size() >= 1, "at least one committed heroine contact", hits.size())
	var dmg_ok := true
	for e in hits:
		if int(e["damage"]) != 19 or absf(float(e["clock"]) - 5.0 / 30.0) > 1.0 / 60.0 + 0.0001:
			dmg_ok = false
	ck(dmg_ok, "every hit is real 19 damage committed at the 5/30 s contact (within one frame)", hits)
	var sum := 0
	for e in hits:
		sum += int(e["damage"])
	ck(sum >= int(arena_script.ENEMIES[scenario]["max_hp"]) and int(hits[hits.size() - 1]["enemy_hp"]) == 0, "enemy HP was removed only by logged heroine contacts", {"sum": sum})
	ck(int(app.hero_state["hp"]) > 0 and battle.enemy_attack_count >= 0, "heroine survived normal enemy AI", {"heroHP": growth_before["hp"], "enemyAttacks": battle.enemy_attack_count})
	ck(finishing_frame >= 0 and result_frame > finishing_frame, "result waited for the finishing contact recovery", {"finishing": finishing_frame, "result": result_frame, "waitFrames": result_frame - finishing_frame})
	var xp_reward: int = battle.result_reward_xp
	var jp_reward: int = battle.result_reward_jp
	var g_after := growth()
	ck(xp_reward == (26 if patrol else 44) and jp_reward == (12 if patrol else 20), "normal reward XP/JP", [xp_reward, jp_reward])
	ck(after_notes().size() == after_before + 1, "exactly one after-battle autosave")
	shot("result")
	# Result click: a real mouse press/release on the visible button through the window input path.
	var center: Vector2 = root.get_final_transform() * battle.result_button.get_global_rect().get_center()
	var pending_choice: bool = app.has_pending_job_choice()
	for pressed in [true, false]:
		var ev := InputEventMouseButton.new()
		ev.button_index = MOUSE_BUTTON_LEFT
		ev.pressed = pressed
		ev.position = center
		ev.global_position = center
		Input.parse_input_event(ev)
		inputs.append({"frame": frame, "action": "mouse_left", "pressed": pressed, "pos": [center.x, center.y]})
		await tick()
	for i in 3:
		await tick()
	var dest: Node = current_scene
	var expected_dest := "res://scenes/growth_screen.tscn" if pending_choice else EXPLORE_PATH
	ck(dest != null and dest != battle and dest.scene_file_path == expected_dest, "result click returns to the correct destination", {"scene": dest.scene_file_path if dest != null else "", "pendingJobChoice": pending_choice})
	if dest != null and dest.scene_file_path == EXPLORE_PATH:
		ck(not dest.enemy_visible and app.battle_enemy_id == "" and not app.returning_from_battle and app.enemy_cleared_for_return, "return flags: encounter cleared, battle id empty, return consumed")
		ck(dest.hero.position == app.battle_return_position, "hero returns at the pre-battle safe point")
		shot("return")
	ck(growth()["xp"] == g_after["xp"] and growth()["jp"] == g_after["jp"], "no reward on result/return", [growth_before, g_after, growth()])
	# Reload the after-battle autosave through the normal load path: no new damage, reward or save.
	var entries := after_notes()
	var saves_before_reload: int = save_store.list_entries().size()
	var loaded: bool = entries.size() > 0 and app.load_save(String(entries[0]["id"]))
	ck(loaded, "after-battle autosave loads")
	ck(change_scene_to_file(EXPLORE_PATH) == OK, "reloaded exploration scene entry")
	for i in 4:
		await tick()
	var reloaded: Node = current_scene
	ck(reloaded != null and not reloaded.enemy_visible and app.battle_enemy_id == "", "reloaded save keeps the encounter cleared")
	ck(growth()["xp"] == g_after["xp"] and growth()["jp"] == g_after["jp"] and growth()["hp"] == g_after["hp"], "reload grants no reward and applies no damage", [g_after, growth()])
	ck(save_store.list_entries().size() == saves_before_reload, "reload writes no new save")
	var report := {"scenario": scenario, "destination": destination, "language": lang, "fixedFps": Engine.physics_ticks_per_second, "engineMaxFps": Engine.max_fps, "party": app.active_party_ids, "declaredSetup": "exploration hero placed once 70 px left of the visible enemy; walk-in with move_right; no battle placement", "checks": checks, "failures": failures, "contactLog": elog, "inputs": inputs, "trace": trace, "captures": captures, "growthBefore": growth_before, "growthAfterVictory": g_after, "rewardXP": xp_reward, "rewardJP": jp_reward, "sourceSha256Raw": hashes, "humanPlaytest": false, "artApproved": false, "defaultAdoption": false}
	var f := FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_heroine-natural-battle_%s-flow-report_test-only-v01_%s.json" % [scenario, tag]), FileAccess.WRITE)
	f.store_string(JSON.stringify(report, " "))
	f.close()
	if failures.is_empty():
		print("NATURAL_FLOW_ALL_PASS scenario=%s checks=%d" % [scenario, checks.size()])
		quit(0)
	else:
		print("NATURAL_FLOW_FAILED scenario=%s failures=%s" % [scenario, failures])
		quit(1)
