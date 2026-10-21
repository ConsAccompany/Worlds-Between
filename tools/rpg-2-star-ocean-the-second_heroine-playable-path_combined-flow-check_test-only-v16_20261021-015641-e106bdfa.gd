extends SceneTree
# Combined heroine playable path v16 (TEST-ONLY evidence; scripted normal input, NOT a human playtest or art approval).
# Reuses the actual normal-entry flow: exploration -> four-direction normal Input -> walk-in encounter -> real battle under
# the engine loop -> natural victory -> result mouse click -> exploration return -> save reload.
# Setup is the shared Claude config module: load(config).configure(app, language, destination). This harness does not
# begin runs, select destinations, set appearance, or override battle/package/contact values itself.
# No HP/damage/timer/cooldown/AI writes and no _try_attack/_finish_battle calls.
# Args: <out_dir> <config_res> <package_index_res> <language en|zh> <tag> <profile_path>
const EXPLORE_PATH := "res://scenes/scifi_exploration_area.tscn"
const ARENA_SCRIPT := "res://scripts/battle_arena.gd"
const SOURCES := ["res://scripts/hsea09/rpg-2-star-ocean-the-second_heroine-sea_distance-driver_opt-in-v01_20261020-214620-4be375a2.gd", "res://scripts/rpg-2-star-ocean-the-second_hsea09_locomotion-phase_model_v01_20261020-174416-39e12f18.gd", "res://scripts/battle_arena.gd", "res://scripts/scifi_exploration_area.gd", "res://scripts/app_state.gd", "res://scripts/save_store.gd", "res://scripts/battle_rules.gd", "res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd", "res://scenes/battle_arena.tscn", "res://scenes/scifi_exploration_area.tscn"]
var app: Node
var arena_script: GDScript
var save_store: GDScript
var out := ""
var config_path := ""
var index_path := ""
var language := ""
var tag := ""
var profile_path := ""
var checks: Array = []
var failures: Array = []
var trace: Array = []
var inputs: Array = []
var captures: Array = []
var frame := 0
var explore: Node
var scenario := "victory"


func _initialize() -> void:
	call_deferred("_run")
	create_timer(150.0).timeout.connect(func(): print("PATH16_WATCHDOG"); quit(2))


func ck(ok: bool, label: String, detail: Variant = null) -> void:
	checks.append({"check": label, "passed": ok, "detail": detail})
	print("PATH16 ", "PASS " if ok else "FAIL ", label, "" if detail == null else " " + str(detail))
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
	var file := "rpg-2-star-ocean-the-second_heroine-playable-path_%s-%s_critical-capture_v16_%s.png" % [language, label, tag]
	var size_ok := img.get_size() == Vector2i(1280, 720)
	var display := DisplayServer.get_name()
	var err := img.save_png(out.path_join(file))
	ck(err == OK and size_ok and display != "headless", "critical capture %s saved at 1280x720 from the live window" % label, {"size": [img.get_width(), img.get_height()], "display": display})
	captures.append({"label": label, "file": file, "frame": frame, "sha256": FileAccess.get_sha256(out.path_join(file))})


func after_notes() -> Array:
	return save_store.list_entries().filter(func(e): return String(e.get("snapshot", {}).get("note", "")) == "after_battle")


func growth() -> Dictionary:
	return {"xp": int(app.hero_state["xp"]), "jp": int(app.hero_state["jp"]), "level": int(app.hero_state["level"]), "hp": int(app.hero_state["hp"])}


func driver_check(host: Node, phase: String) -> void:
	ck(host != null, "exploration host present " + phase)
	if host == null:
		return
	var pilot: Node = host.sprite_pilot
	ck(pilot != null, "source-bound exploration driver active " + phase)
	if pilot == null:
		return
	var driver_path := ""
	if pilot.get_script() != null:
		driver_path = pilot.get_script().resource_path
	ck(driver_path != "" and (driver_path.contains("heroine") or driver_path.contains("hsea")), "source-bound exploration driver script " + phase, driver_path)
	var actor: Variant = pilot.get("actor_id")
	ck(String(actor) == "protagonist-female", "driver binds the heroine source actor " + phase, actor)
	if pilot.has_method("state"):
		var state: Variant = pilot.state()
		ck(state is Dictionary and state.has("frame") and state.has("facing"), "driver reports live source state " + phase, state)
	else:
		ck(false, "driver reports live source state " + phase, "missing state()")
	ck(host.hero.texture != null and host.hero.texture.get_size() == Vector2(80, 112), "heroine exploration source cell is 80x112 " + phase, host.hero.texture.get_size() if host.hero.texture != null else null)
	ck(host.hero.scale == Vector2(0.5, 0.5), "heroine exploration display scale is 0.5 " + phase, host.hero.scale)


func probe_direction(dir_name: String, action: String, opposite: String, expected: Vector2, start: Vector2) -> void:
	explore.hero.position = start
	await tick()
	var p0: Vector2 = explore.hero.position
	press(action)
	for i in 10:
		await tick()
	if dir_name == "east":
		shot("explore-move")
	release(action)
	await tick()
	var p1: Vector2 = explore.hero.position
	var moved := p1 - p0
	ck(moved.dot(expected) > 6.0, "normal Input %s moves the heroine" % dir_name, [moved.x, moved.y])
	var stopped := p1
	for i in 6:
		await tick()
		ck(explore.hero.position == stopped, "physical stop unchanged %s frame %d" % [dir_name, i], [explore.hero.position.x, explore.hero.position.y])
	press(action)
	for i in 6:
		await tick()
	release(action)
	await tick()
	var p2: Vector2 = explore.hero.position
	ck((p2 - stopped).dot(expected) > 3.0, "same-direction re-press resumes %s" % dir_name, [p2.x - stopped.x, p2.y - stopped.y])
	var p3: Vector2 = p2
	press(opposite)
	for i in 6:
		await tick()
	release(opposite)
	await tick()
	var p4: Vector2 = explore.hero.position
	ck((p4 - p3).dot(-expected) > 3.0, "reversal %s turns the heroine" % dir_name, [p4.x - p3.x, p4.y - p3.y])


func package_pose_count() -> Dictionary:
	if not FileAccess.file_exists(index_path):
		return {"ok": false, "reason": "index missing"}
	var index: Variant = JSON.parse_string(FileAccess.get_file_as_string(index_path))
	if not index is Dictionary or not index.get("sets") is Dictionary or not index["sets"].get("hero:female") is String:
		return {"ok": false, "reason": "index shape"}
	var manifest_path := index_path.get_base_dir().path_join(String(index["sets"]["hero:female"]))
	if not FileAccess.file_exists(manifest_path):
		return {"ok": false, "reason": "manifest missing", "manifest": manifest_path}
	var manifest: Variant = JSON.parse_string(FileAccess.get_file_as_string(manifest_path))
	if not manifest is Dictionary or not manifest.get("actions") is Dictionary:
		return {"ok": false, "reason": "manifest shape", "manifest": manifest_path}
	var cells := {}
	for action in manifest["actions"].values():
		for f in action.get("frames", []):
			cells[int(f["cell"])] = true
	return {"ok": true, "manifest": manifest_path, "poseCount": cells.size(), "artApproved": manifest.get("art_approved", null), "defaultAdoption": manifest.get("default_adoption", null), "setId": manifest.get("set_id", "")}


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() > 0 and args[0] == "--selfcheck":
		print("PATH16_HARNESS_SELFCHECK_OK name=", "rpg-2-star-ocean-the-second_heroine-playable-path_combined-flow-check_test-only-v16_20261021-015641-e106bdfa.gd")
		quit(0)
		return
	if args.size() < 6:
		print("PATH16_BAD_ARGS expected out config index language tag profile, got=", args)
		quit(2)
		return
	out = args[0]; config_path = args[1]; index_path = args[2]; language = args[3]; tag = args[4]; profile_path = args[5]
	scenario = args[6] if args.size() > 6 else "victory"
	if scenario not in ["victory", "defeat"]:
		quit(2)
		return
	if not language in ["en", "zh"]:
		print("PATH16_BAD_LANGUAGE ", language)
		quit(2)
		return
	var destination := "scifi.outskirts"
	app = root.get_node("AppState")
	arena_script = load(ARENA_SCRIPT)
	save_store = load("res://scripts/save_store.gd")
	var hashes := {}
	for p in SOURCES:
		hashes[p] = FileAccess.get_sha256(p)
	for p in [config_path, index_path]:
		if FileAccess.file_exists(p):
			hashes[p] = FileAccess.get_sha256(p)
	# Shared config owns all setup: fresh run, heroine appearance, language, destination and opt-in overrides.
	var config_script: Variant = load(config_path)
	ck(config_script != null and config_script is GDScript, "shared combined config module loads", config_path)
	if config_script == null:
		print("PATH16_FAILED language=%s failures=%s" % [language, failures])
		quit(1)
		return
	var config_result: Variant = config_script.configure(app, language, destination)
	ck(config_result is Dictionary and config_result.get("ok", false), "shared config accepted pinned heroine packages", config_result)
	if not config_result is Dictionary or not config_result.get("ok", false):
		quit(1)
		return
	ck(app.hero_appearance == "female", "config selects the heroine appearance", app.hero_appearance)
	ck(String(app.language) == language, "config applies the requested language", app.language)
	ck(app.active_party_ids.size() == 1 and String(app.active_party_ids[0]) == "hero", "config leaves the solo heroine party untouched", app.active_party_ids)
	if profile_path != "":
		var user_dir := ProjectSettings.globalize_path("user://").replace("\\", "/").trim_suffix("/")
		var expected_profile := profile_path.replace("\\", "/").trim_suffix("/")
		ck(user_dir.begins_with(expected_profile), "saves are isolated to the runner profile", {"user": user_dir, "profile": expected_profile})
	ck(change_scene_to_file(EXPLORE_PATH) == OK, "normal exploration scene entry %s %s" % [destination, language])
	for i in 3:
		await tick()
	explore = current_scene
	ck(explore != null and explore.enemy_visible, "enemy is visible in exploration", explore.enemy_position if explore != null else null)
	if explore == null:
		print("PATH16_FAILED language=%s failures=%s" % [language, failures])
		quit(1)
		return
	driver_check(explore, "before encounter")
	shot("explore-start")
	# All four directions through normal Input at disclosed safe points, with physical stop, re-press and reversal.
	await probe_direction("east", "move_right", "move_left", Vector2(1, 0), Vector2(300, 160))
	await probe_direction("west", "move_left", "move_right", Vector2(-1, 0), Vector2(450, 160))
	await probe_direction("north", "move_up", "move_down", Vector2(0, -1), Vector2(450, 230))
	await probe_direction("south", "move_down", "move_up", Vector2(0, 1), Vector2(450, 120))
	driver_check(explore, "after four-direction input")
	# Disclosed once-only encounter placement: 70 px left of the visible enemy, then walk in with move_right only.
	var enemy_pos: Vector2 = explore.enemy_position
	explore.hero.position = enemy_pos + Vector2(-70, 0)
	trace.append({"frame": frame, "phase": "encounter-placement", "declaredPlacement": [explore.hero.position.x, explore.hero.position.y]})
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
	ck(battle != null and battle.get_script() == arena_script and battle.enemy_id == "patrol", "walking into the enemy opens the real patrol battle", {"frames": guard})
	ck(app.battle_return_position.distance_to(enemy_pos) > 43.0, "return position is the natural >43 px safe point", [app.battle_return_position.x, app.battle_return_position.y])
	ck(save_store.list_entries().size() == before_saves + 1, "exactly one pre-battle autosave written by the encounter")
	ck(battle.enemy_hp == int(arena_script.ENEMIES["patrol"]["max_hp"]) and battle.fighters.size() == 1 and battle.fighters[0]["id"] == "hero", "normal enemy max HP and solo heroine party", {"hp": battle.enemy_hp, "party": app.active_party_ids})
	ck(battle.combat_sprite_sets != null and battle.combat_sprite_sets.index_path == index_path and battle.combat_sprite_sets.index_status == "loaded" and battle.combat_sprite_sets.has_set(0), "real combat package is loaded from the supplied index", {"index": battle.combat_sprite_sets.index_path if battle.combat_sprite_sets != null else "", "status": battle.combat_sprite_sets.index_status if battle.combat_sprite_sets != null else ""})
	ck(battle.fighters[0].has("contact_event_id"), "heroine contact timing mode is active")
	var pkg := package_pose_count()
	ck(pkg.get("ok", false) and int(pkg.get("poseCount", 0)) == 29, "runtime package exposes all 29 authored poses", pkg)
	ck(pkg.get("artApproved", null) == false and pkg.get("defaultAdoption", null) == false, "package keeps unapproved/default-off metadata", pkg)
	if scenario == "defeat":
		await loss_and_reload(battle, pkg)
		return
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
		# Real engine loop; no direct damage/timer/AI writes. Inputs land at frame start for the arena's just-pressed read.
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
	ck(sum >= int(arena_script.ENEMIES["patrol"]["max_hp"]) and int(hits[hits.size() - 1]["enemy_hp"]) == 0, "enemy HP was removed only by logged heroine contacts", {"sum": sum})
	ck(int(app.hero_state["hp"]) > 0 and battle.enemy_attack_count >= 0, "heroine survived normal enemy AI", {"heroHP": growth_before["hp"], "enemyAttacks": battle.enemy_attack_count})
	ck(finishing_frame >= 0 and result_frame > finishing_frame, "result waited for the finishing contact recovery", {"finishing": finishing_frame, "result": result_frame, "waitFrames": result_frame - finishing_frame})
	var xp_reward: int = battle.result_reward_xp
	var jp_reward: int = battle.result_reward_jp
	var g_after := growth()
	ck(xp_reward == 26 and jp_reward == 12, "normal patrol reward XP/JP", [xp_reward, jp_reward])
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
		driver_check(dest, "after return")
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
	if reloaded != null:
		driver_check(reloaded, "after reload")
	ck(growth()["xp"] == g_after["xp"] and growth()["jp"] == g_after["jp"] and growth()["hp"] == g_after["hp"], "reload grants no reward and applies no damage", [g_after, growth()])
	ck(save_store.list_entries().size() == saves_before_reload, "reload writes no new save")
	var report := {"harness": "combined-playable-path-v16", "destination": destination, "language": language, "fixedFps": Engine.physics_ticks_per_second, "engineMaxFps": Engine.max_fps, "party": app.active_party_ids, "configPath": config_path, "packageIndex": index_path, "profilePath": profile_path, "declaredSetup": "shared config configure(app, language, destination); four-direction probes at disclosed safe points; one 70 px-left walk-in for the actual encounter; no battle placement", "checks": checks, "failures": failures, "contactLog": elog, "inputs": inputs, "trace": trace, "captures": captures, "package": pkg, "growthBefore": growth_before, "growthAfterVictory": g_after, "rewardXP": xp_reward, "rewardJP": jp_reward, "sourceSha256Raw": hashes, "configResultType": typeof(config_result), "humanPlaytest": false, "artApproved": false, "defaultAdoption": false}
	var f := FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_heroine-playable-path_%s-combined-flow-report_test-only-v16_%s.json" % [language, tag]), FileAccess.WRITE)
	f.store_string(JSON.stringify(report, " "))
	f.close()
	if failures.is_empty():
		print("PATH16_ALL_PASS language=%s checks=%d" % [language, checks.size()])
		quit(0)
	else:
		print("PATH16_FAILED language=%s failures=%s" % [language, failures])
		quit(1)


# A separate normal loss path: no attack, no artificial HP/damage/timer changes.
func loss_and_reload(battle: Node, pkg: Dictionary) -> void:
	var before := growth()
	var before_after_saves := after_notes().size()
	var saw_hit := false
	for n in 1800:
		await tick()
		if not is_instance_valid(battle) or current_scene != battle:
			break
		var pose: Dictionary = battle.combat_sprite_sets.current_frame(0)
		if pose.get("action") == "hit" and not saw_hit:
			saw_hit = true
			shot("natural-hit")
		if battle.battle_finished:
			break
	ck(is_instance_valid(battle) and current_scene == battle and battle.battle_finished and not battle.battle_won, "normal enemy AI naturally defeats heroine without attack")
	if not is_instance_valid(battle) or current_scene != battle:
		quit(1)
		return
	ck(int(app.hero_state["hp"]) == 0 and battle.player_attack_count == 0 and battle.enemy_hp == int(arena_script.ENEMIES["patrol"]["max_hp"]), "loss uses real enemy damage; no player attacks or enemy HP edits")
	ck(saw_hit, "authored hit action observed under real enemy damage")
	for n in 18:
		await tick()
	var down: Dictionary = battle.combat_sprite_sets.current_frame(0)
	ck(down.get("action") == "defeat" and int(down.get("frame", -1)) == 2, "natural down animation reaches and holds its final authored frame", down)
	shot("natural-defeat")
	ck(growth()["xp"] == before["xp"] and growth()["jp"] == before["jp"] and after_notes().size() == before_after_saves, "loss awards no XP/JP and no after-battle victory autosave")
	for n in 100:
		await tick()
		trace.append({"phase":"loss-menu-transition", "frame":frame, "scene":current_scene.scene_file_path if current_scene != null else "<handoff-null>"})
		if current_scene != null and current_scene.scene_file_path == "res://scenes/main_menu.tscn" and current_scene.is_node_ready():
			break
	ck(current_scene != null and current_scene.scene_file_path == "res://scenes/main_menu.tscn" and current_scene.is_node_ready(), "normal defeat timer returns to the ready main menu")
	shot("loss-menu")
	var saves: Array = save_store.list_entries().filter(func(e): return String(e.get("snapshot", {}).get("note", "")) == "before_battle")
	ck(not saves.is_empty(), "natural encounter retained a pre-battle recovery save")
	var count: int = save_store.list_entries().size()
	var loaded: bool = not saves.is_empty() and app.load_save(String(saves[0]["id"]))
	ck(loaded, "pre-battle save loads after natural defeat")
	ck(change_scene_to_file(EXPLORE_PATH) == OK, "retry returns through normal exploration scene")
	for n in 4:
		await tick()
	var retry: Node = current_scene
	driver_check(retry, "after defeat and pre-battle reload")
	ck(int(app.hero_state["hp"]) == before["hp"] and retry.enemy_visible and not app.enemy_cleared_for_return and app.battle_enemy_id == "", "pre-battle retry restores heroine health and the uncleared enemy")
	ck(growth()["xp"] == before["xp"] and growth()["jp"] == before["jp"] and save_store.list_entries().size() == count, "retry grants no reward and writes no extra save")
	shot("retry")
	var f := FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_heroine-playable-path_%s-combined-flow-report_test-only-v16_%s.json" % [language,tag]), FileAccess.WRITE)
	f.store_string(JSON.stringify({"scenario":"defeat", "trace":trace, "checks":checks, "failures":failures, "captures":captures, "package":pkg, "inputs":inputs, "sourceSetup":"same shared opt-in entry; actual enemy damage; no gameplay state edits", "humanPlaytest":false, "artApproved":false}," "))
	f.close()
	if failures.is_empty():
		print("PATH16_ALL_PASS language=%s scenario=defeat checks=%d" % [language,checks.size()])
		quit(0)
	else:
		print("PATH16_FAILED ",failures)
		quit(1)
