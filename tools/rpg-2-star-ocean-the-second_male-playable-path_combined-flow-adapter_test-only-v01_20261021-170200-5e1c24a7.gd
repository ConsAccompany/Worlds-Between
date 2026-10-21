extends "rpg-2-star-ocean-the-second_heroine-playable-path_combined-flow-check_test-only-v16_20261021-015641-e106bdfa.gd"
# Male adapter over the v16 combined playable-path harness (TEST-ONLY; scripted normal input, NOT a human playtest or
# art approval). Reuses the v16 input/tick/capture helpers, four-direction probe and natural defeat/retry flow; only the
# setup (mpath24 male config), the driver binding check, the stop-bridge probe and the male battle checks differ.
# Male mechanics are the unchanged legacy immediate attack: no contact event keys, no HP/damage/AI/timer writes.
# Args: <out_dir> <language en|zh> <tag> <profile_path> [victory|defeat]
const MALE_CONFIG := "res://scripts/mpath24/rpg-2-star-ocean-the-second_male-playable-path_config_opt-in-v01_20261021-170200-5e1c24a7.gd"
const MALE_DRIVER := "res://scripts/mpath24/rpg-2-star-ocean-the-second_male-playable-path_explore-driver_opt-in-v01_20261021-170200-5e1c24a7.gd"
const MALE_INDEX := "res://data/mcombat22/rpg-2-star-ocean-the-second_protagonist-male-combat_runtime-index_unapproved-v01_20261021-154716-8dee0dda.json"
const SEA_DRIVER := "res://scripts/hsea09/rpg-2-star-ocean-the-second_heroine-sea_distance-driver_opt-in-v01_20261020-214620-4be375a2.gd"
const SPEED := 140.0
var male_config: GDScript
var male_driver: GDScript


func shot(label: String) -> void:
	var img: Image = root.get_texture().get_image()
	var file := "rpg-2-star-ocean-the-second_male-playable-path_%s-%s_capture_v01_%s.png" % [language, label, tag]
	var size_ok := img.get_size() == Vector2i(1280, 720)
	var display := DisplayServer.get_name()
	var err := img.save_png(out.path_join(file))
	ck(err == OK and size_ok and display != "headless", "capture %s saved at 1280x720 from the live window" % label, {"size": [img.get_width(), img.get_height()], "display": display})
	captures.append({"label": label, "file": file, "frame": frame, "sha256": FileAccess.get_sha256(out.path_join(file))})


func driver_check(host: Node, phase: String) -> void:
	ck(host != null, "exploration host present " + phase)
	if host == null:
		return
	var pilot: Node = host.sprite_pilot
	ck(pilot != null and pilot.get_script() != null and pilot.get_script().resource_path == MALE_DRIVER, "mpath24 male driver active " + phase, pilot.get_script().resource_path if pilot != null and pilot.get_script() != null else null)
	if pilot == null:
		return
	ck(String(pilot.get("actor_id")) == "protagonist-male", "driver binds protagonist-male " + phase, pilot.get("actor_id"))
	ck(host.hero.texture != null and host.hero.texture.get_size() == Vector2(80, 112) and host.hero.scale == Vector2(0.5, 0.5), "male source cell 80x112 at display scale 0.5 " + phase)


func app_snapshot() -> Dictionary:
	return {"appearance": app.hero_appearance, "language": app.language, "destination": app.current_destination_id if "current_destination_id" in app else "", "party": app.active_party_ids.duplicate(), "hp": int(app.hero_state["hp"]), "maleOverride": male_driver.male_enabled_override, "arenaOverride": arena_script.combat_sprite_set_override, "arenaIndex": arena_script.combat_sprite_set_index_override}


func malformed_supplement(kind: String) -> String:
	var path := "user://mpath24_malformed_%s.json" % kind
	var text := "{"
	if kind == "sha":
		var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(male_driver.SUPPLEMENT_PATH))
		for direction in data["phase_bridges"]:
			for phase in data["phase_bridges"][direction]:
				for entry in data["phase_bridges"][direction][phase]:
					if entry.has("file"):
						entry["file"] = "res://data/mexplore23/" + String(entry["file"])
		data["phase_bridges"]["west"]["phase3"][1]["sha256"] = "0".repeat(64)
		text = JSON.stringify(data)
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(text)
	f.close()
	return path


func refusal_and_defaults() -> void:
	ck(male_driver.DEFAULT_ADOPTED == false and male_driver.male_enabled() == false, "dormant male default-adoption switch is false and the male path is off by default")
	var probe := Sprite2D.new()
	root.add_child(probe)
	var legacy_male: Variant = load("res://scripts/exploration_sprite_set_pilot.gd").attach(probe, "protagonist-male", "south")
	ck(legacy_male == null, "ordinary male exploration stays legacy without the opt-in", legacy_male)
	var female: Node = load("res://scripts/exploration_sprite_set_pilot.gd").attach(probe, "protagonist-female", "south")
	ck(female != null and female.get_script().resource_path == SEA_DRIVER, "ordinary female default still uses the authorized heroine Sea driver", female.get_script().resource_path if female != null else null)
	if female != null:
		female.queue_free()
	probe.queue_free()
	ck(not arena_script.heroine_default_battle_applies(["hero"], "male"), "heroine battle default never applies to the male hero")
	ck(arena_script.HEROINE_CONTACT_TICKS == 5 and arena_script.HEROINE_CONTACT_TICK_RATE == 30, "heroine contact constants unchanged (5/30)")
	var before := app_snapshot()
	var cases := {"truncated supplement": [male_config.validate(app, language, "scifi.outskirts", "", malformed_supplement("truncated"))],
		"bridge sha mismatch": [male_config.configure(app, language, "scifi.outskirts", "", malformed_supplement("sha"))],
		"missing registry": [male_config.configure(app, language, "scifi.outskirts", "res://data/mexplore23/missing.json")],
		"missing combat index": [male_config.configure(app, language, "scifi.outskirts", "", "", "res://data/mcombat22/missing.json")]}
	for label in cases:
		var r: Dictionary = cases[label][0]
		ck(not r.get("ok", true), "malformed package refused whole: " + label, r.get("error", ""))
	ck(app_snapshot() == before, "refusals left AppState and every override unchanged", [before, app_snapshot()])


func stop_bridge_probe() -> void:
	var host := explore
	host.hero.position = Vector2(300, 160)
	await tick()
	press("move_right")
	var steps := []
	for i in 12:
		var p0: Vector2 = host.hero.position
		await tick()
		steps.append(snappedf(host.hero.position.x - p0.x, 0.001))
	var steady := steps.slice(2)
	ck(steady.all(func(d): return absf(float(d) - SPEED / Engine.physics_ticks_per_second) < 0.01 or absf(float(d) - SPEED / 30.0) < 0.01), "male walk keeps the unchanged 140 logical px/s", steps)
	release("move_right")
	await tick()
	var stopped: Vector2 = host.hero.position
	var states := []
	var bridge_textures: Array = host.sprite_pilot.bridges["east"][int(host.sprite_pilot.bridge_phase)] if host.sprite_pilot.bridge_active else []
	for i in 6:
		var st: Dictionary = host.sprite_pilot.state()
		states.append({"action": st["action"], "frame": st["frame"], "texture": host.hero.texture.resource_path, "x": host.hero.position.x})
		if i == 1:
			shot("explore-east-stop-bridge")
		ck(host.hero.position == stopped, "immediate physical stop, frame %d" % i)
		await tick()
	var seen: Array = states.map(func(s): return s["texture"])
	var order_ok: bool = bridge_textures.size() == 4 and seen[0] == bridge_textures[0].resource_path and seen.has(bridge_textures[1].resource_path) and seen.has(bridge_textures[2].resource_path) and seen.find(bridge_textures[1].resource_path) < seen.find(bridge_textures[2].resource_path) and seen[-1] == bridge_textures[3].resource_path
	ck(states[0]["action"] == "stop" and order_ok, "release plays the authored east phase bridge [walk p, s1, s2, idle f00] at once", states)
	ck(states[-1]["action"] == "idle", "bridge settles into idle (120 ms inclusive)", states)
	trace.append({"phase": "stop-bridge", "states": states})
	# Re-press during the bridge resumes walking on the next frame (no stuck frame).
	press("move_right")
	for i in 8:
		await tick()
	release("move_right")
	await tick()
	ck(host.sprite_pilot.state()["action"] == "stop", "second release starts a new bridge")
	var rp: Vector2 = host.hero.position
	press("move_right")
	await tick()
	ck(host.sprite_pilot.state()["action"] == "walk" and host.hero.position.x > rp.x, "re-press during the bridge walks immediately", host.sprite_pilot.state())
	release("move_right")
	await tick()
	var rv: Vector2 = host.hero.position
	press("move_left")
	await tick()
	ck(host.sprite_pilot.state()["action"] == "walk" and host.sprite_pilot.state()["facing"] == "west" and host.hero.position.x < rv.x, "reversal during the bridge turns and walks immediately", host.sprite_pilot.state())
	release("move_left")
	for i in 6:
		await tick()
	ck(host.sprite_pilot.state()["action"] == "idle", "reversal stop settles to idle", host.sprite_pilot.state())


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 4 or not args[1] in ["en", "zh"]:
		print("MPATH24_BAD_ARGS ", args)
		quit(2)
		return
	out = args[0]; language = args[1]; tag = args[2]; profile_path = args[3]
	scenario = args[4] if args.size() > 4 else "victory"
	app = root.get_node("AppState")
	arena_script = load(ARENA_SCRIPT)
	save_store = load("res://scripts/save_store.gd")
	male_config = load(MALE_CONFIG)
	male_driver = load(MALE_DRIVER)
	config_path = MALE_CONFIG
	index_path = MALE_INDEX
	var user_dir := ProjectSettings.globalize_path("user://").replace("\\", "/")
	ck(user_dir.begins_with(profile_path.replace("\\", "/")), "saves are isolated to the runner profile", user_dir)
	refusal_and_defaults()
	var result: Dictionary = male_config.configure(app, language, "scifi.outskirts")
	ck(result.get("ok", false), "mpath24 male config accepted the whole package", result)
	if not result.get("ok", false):
		print("MPATH24_FAILED ", failures)
		quit(1)
		return
	ck(app.hero_appearance == "male" and String(app.language) == language and app.active_party_ids == ["hero"], "config selects male, language and the solo party", [app.hero_appearance, app.language])
	ck(change_scene_to_file(EXPLORE_PATH) == OK, "normal exploration scene entry")
	for i in 3:
		await tick()
	explore = current_scene
	driver_check(explore, "before encounter")
	shot("explore-start")
	await stop_bridge_probe()
	await probe_direction("east", "move_right", "move_left", Vector2(1, 0), Vector2(300, 160))
	await probe_direction("west", "move_left", "move_right", Vector2(-1, 0), Vector2(450, 160))
	await probe_direction("north", "move_up", "move_down", Vector2(0, -1), Vector2(450, 230))
	await probe_direction("south", "move_down", "move_up", Vector2(0, 1), Vector2(450, 120))
	driver_check(explore, "after four-direction input")
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
	for i in 2:
		await tick()
	var battle: Node = current_scene
	ck(battle != null and battle.get_script() == arena_script and battle.enemy_id == "patrol", "walking into the enemy opens the real patrol battle", {"frames": guard})
	if battle == null or battle.get_script() != arena_script:
		print("MPATH24_FAILED ", failures)
		quit(1)
		return
	ck(save_store.list_entries().size() == before_saves + 1, "exactly one pre-battle autosave written by the encounter")
	ck(battle.combat_sprite_sets != null and battle.combat_sprite_sets.index_path == MALE_INDEX and battle.combat_sprite_sets.has_set(0), "male combat package loaded from the mcombat22 index")
	ck(not battle.fighters[0].has("contact_event_id") and not battle.heroine_default_active, "male keeps the legacy immediate attack mechanics (no contact retiming)")
	var pkg := {"index": MALE_INDEX, "artApproved": false, "defaultAdoption": false}
	if scenario == "defeat":
		await loss_and_reload(battle, pkg)
		return
	await male_victory(battle)


func male_victory(battle: Node) -> void:
	var fighter: Dictionary = battle.fighters[0]
	var reach := float(app.MEMBER_DEFS["hero"]["attack_range"])
	var growth_before := growth()
	var after_before := after_notes().size()
	var saves0: int = save_store.list_entries().size()
	# Normal input only: approach, hold guard, dodge, skill, then attack until the enemy falls under normal AI.
	for i in 240:
		var row: Dictionary = await action_tick(battle)
		if absf(battle.enemy_x - float(fighter["x"])) <= reach - 10.0:
			break
		press("move_right")
	release("move_right")
	press("battle_guard")
	for i in 30:
		await action_tick(battle)
	release("battle_guard")
	await action_tick(battle)
	await action_press_frame(battle, "battle_dodge")
	for i in 20:
		await action_tick(battle)
	await action_press_frame(battle, "battle_skill")
	for i in 30:
		await action_tick(battle)
	for i in 1500:
		if battle.battle_finished:
			break
		var dist := absf(battle.enemy_x - float(fighter["x"]))
		if dist > reach - 10.0:
			press("move_right")
		else:
			release("move_right")
		if float(fighter["attack_cooldown"]) == 0.0 and dist <= reach - 4.0:
			await action_press_frame(battle, "battle_attack")
		else:
			await action_tick(battle)
	release("move_right")
	for i in 120:
		if battle.result_overlay.visible and not battle.result_button.disabled:
			break
		await action_tick(battle)
	ck(battle.battle_finished and battle.battle_won and battle.enemy_hp == 0, "natural male victory from the real engine loop", {"attacks": battle.player_attack_count, "heroHP": app.hero_state["hp"]})
	ck(int(app.hero_state["hp"]) > 0, "male survived normal enemy AI")
	for name in ["idle", "move", "guard", "dodge", "skill", "attack"]:
		ck(observed_actions.has(name), "authored male %s state observed under normal input" % name)
	ck(after_notes().size() == after_before + 1, "exactly one after-battle autosave")
	var g_after := growth()
	ck(g_after["xp"] > growth_before["xp"], "normal victory reward applied", [growth_before, g_after])
	shot("result")
	var center: Vector2 = root.get_final_transform() * battle.result_button.get_global_rect().get_center()
	var pending_choice: bool = app.has_pending_job_choice()
	for pressed in [true, false]:
		var ev := InputEventMouseButton.new()
		ev.button_index = MOUSE_BUTTON_LEFT
		ev.pressed = pressed
		ev.position = center
		ev.global_position = center
		Input.parse_input_event(ev)
		await tick()
	for i in 3:
		await tick()
	var dest: Node = current_scene
	var expected_dest := "res://scenes/growth_screen.tscn" if pending_choice else EXPLORE_PATH
	ck(dest != null and dest != battle and dest.scene_file_path == expected_dest, "result click returns to the correct destination", {"scene": dest.scene_file_path if dest != null else "", "pending": pending_choice})
	if dest != null and dest.scene_file_path == EXPLORE_PATH:
		ck(not dest.enemy_visible and dest.hero.position == app.battle_return_position, "encounter cleared and hero at the pre-battle safe point")
		driver_check(dest, "after return")
		shot("return")
	var entries := after_notes()
	var loaded: bool = entries.size() > 0 and app.load_save(String(entries[0]["id"]))
	ck(loaded and app.hero_appearance == "male", "after-battle autosave loads the male run")
	ck(change_scene_to_file(EXPLORE_PATH) == OK, "reloaded exploration scene entry")
	for i in 4:
		await tick()
	var reloaded: Node = current_scene
	ck(reloaded != null and not reloaded.enemy_visible, "reloaded save keeps the encounter cleared")
	driver_check(reloaded, "after reload")
	shot("reload")
	ck(growth()["xp"] == g_after["xp"] and growth()["jp"] == g_after["jp"], "reload grants no reward")
	male_config.rollback()
	ck(male_driver.male_enabled_override == -1 and arena_script.combat_sprite_set_override == -1 and arena_script.combat_sprite_set_index_override == "", "rollback restores every process override")
	ck(change_scene_to_file(EXPLORE_PATH) == OK, "post-rollback exploration entry")
	for i in 4:
		await tick()
	ck(current_scene != null and current_scene.sprite_pilot == null, "after rollback the male run shows the ordinary legacy male")
	var report := {"harness": "male-playable-path-adapter-v01 over combined-flow-check v16", "language": language, "scenario": "victory", "checks": checks, "failures": failures, "captures": captures, "inputs": inputs, "trace": trace, "observedActions": observed_actions.keys(), "actionTraceRows": action_trace.size(), "humanPlaytest": false, "artApproved": false, "defaultAdoption": false, "saves": save_store.list_entries().size() - saves0}
	var f := FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_male-playable-path_%s-victory-report_test-only-v01_%s.json" % [language, tag]), FileAccess.WRITE)
	f.store_string(JSON.stringify(report, " "))
	f.close()
	if failures.is_empty():
		print("PATH16_ALL_PASS language=%s scenario=victory checks=%d" % [language, checks.size()])
		quit(0)
	else:
		print("MPATH24_FAILED language=%s failures=%s" % [language, failures])
		quit(1)
