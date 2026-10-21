extends SceneTree
# TEST-ONLY zpath27 Zhao real-input flow (scripted normal input; NOT a human playtest, art/motion approval or default adoption).
# SETUP FIXTURE (declared): zpath27 config.configure(app, language, "male") starts a fresh demo run at scifi.outskirts.
# Everything after setup goes through the real handlers via Input.parse_input_event key/mouse events only:
#   WASD walk -> E at the actual zhao-ling field NPC -> mouse click on the real Invite button (recruit through
#   _invite_companion) -> E at the existing relay -> walk into the patrol -> Tab to Zhao -> Q skill, L guard, K dodge,
#   D move, J attack -> natural victory -> mouse click on the result button -> exploration return -> reload of the
#   after-battle autosave the game itself wrote (AppState.load_save + normal scene entry; NOT the Save/Load UI).
# Defeat scenario: same route, Zhao is controlled and only retreats (no player attack); outcome is whatever the normal AI
# produces. No recruit_member, HP/energy/damage/cooldown/AI writes, hero placement or _finish_battle/_try_attack calls.
# Args: <out_dir> <language en|zh> <tag> <profile_dir> <victory|defeat>
const CONFIG := "res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_config_opt-in-v01_20261021-223218-3246d731.gd"
const EXPLORE := "res://scenes/scifi_exploration_area.tscn"
const PINS := ["res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_config_opt-in-v01_20261021-223218-3246d731.gd",
	"res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_npc-driver_opt-in-v01_20261021-223218-3246d731.gd",
	"res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_entry_opt-in-v01_20261021-224100-c713ad29.gd",
	"res://scripts/battle_arena.gd", "res://scripts/scifi_exploration_area.gd", "res://scripts/app_state.gd",
	"res://scripts/save_store.gd", "res://scenes/battle_arena.tscn", "res://scenes/scifi_exploration_area.tscn",
	"res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd",
	"res://data/zcombat26/rpg-2-star-ocean-the-second_zhao-ling-combat_runtime-index_unapproved-zcombat26-v01_20261021-180157-63cae05d.json"]
var app: Node
var config
var save_store
var out := ""
var language := ""
var tag := ""
var profile := ""
var scenario := "victory"
var mode := "preview"
var appearance := "male"
var checks: Array = []
var failures: Array = []
var inputs: Array = []
var captures: Array = []
var trace: Array = []
var zhao_actions := {}
var frame := 0
var held := {}


func _initialize() -> void:
	call_deferred("_run")
	create_timer(170.0).timeout.connect(func(): print("ZRIF_WATCHDOG"); _write_report(); quit(2))


func ck(ok: bool, label: String, detail: Variant = null) -> void:
	checks.append({"check": label, "passed": ok, "detail": detail})
	print("ZRIF ", "PASS " if ok else "FAIL ", label, "" if detail == null else " " + str(detail))
	if not ok:
		failures.append(label)


func tick() -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	frame += 1


func key(k: Key, pressed: bool) -> void:
	var ev := InputEventKey.new()
	ev.keycode = k
	ev.physical_keycode = k
	ev.pressed = pressed
	Input.parse_input_event(ev)
	inputs.append({"frame": frame, "key": OS.get_keycode_string(k), "pressed": pressed})
	if pressed:
		held[k] = true
	else:
		held.erase(k)


func tap(k: Key) -> void:
	key(k, true)
	await tick()
	key(k, false)
	await tick()


func click(control: Control) -> void:
	var center: Vector2 = root.get_final_transform() * control.get_global_rect().get_center()
	for pressed in [true, false]:
		var ev := InputEventMouseButton.new()
		ev.button_index = MOUSE_BUTTON_LEFT
		ev.pressed = pressed
		ev.position = center
		ev.global_position = center
		Input.parse_input_event(ev)
		inputs.append({"frame": frame, "mouse": "left", "pressed": pressed, "pos": [center.x, center.y]})
		await tick()


func release_all() -> void:
	for k in held.keys():
		key(k, false)


func shot(label: String) -> void:
	var img: Image = root.get_texture().get_image()
	var file := "rpg-2-star-ocean-the-second_zhao-rif_%s-%s_%s_capture-640_%s.png" % [language, scenario, label, tag]
	var err := img.save_png(out.path_join(file))
	ck(err == OK and img.get_size() == Vector2i(640, 360), "capture %s is native 640x360" % label, [img.get_width(), img.get_height()])
	captures.append({"label": label, "file": file, "frame": frame, "size": [img.get_width(), img.get_height()], "sha256": FileAccess.get_sha256(out.path_join(file))})


# Hold one WASD key until the hero passes `target` on that axis (or the scene changes / limit hits).
func walk_axis(scene: Node, k: Key, axis: int, target: float, limit: int = 6000) -> int:
	var sign_dir := 1.0 if k in [KEY_D, KEY_S] else -1.0
	key(k, true)
	var n := 0
	while n < limit and current_scene == scene and (scene.hero.position[axis] - target) * sign_dir < 0.0:
		await tick()
		n += 1
	key(k, false)
	await tick()
	return n


func zhao_row(battle: Node, slot: int) -> Dictionary:
	var f: Dictionary = battle.fighters[slot]
	var pose: Dictionary = battle.companion_sprite_sets.current_frame(slot) if battle.companion_sprite_sets != null else {}
	var row := {"frame": frame, "controlled": battle.controlled_index, "action": String(pose.get("action", "")), "cell": int(pose.get("cell", -1)),
		"poseFrame": int(pose.get("frame", -1)), "zhaoX": snappedf(float(f["x"]), 0.01), "enemyX": snappedf(float(battle.enemy_x), 0.01),
		"enemyHP": int(battle.enemy_hp), "zhaoHP": int(app.member_state("zhao-ling")["hp"]), "heroHP": int(app.member_state("hero")["hp"]),
		"zhaoEnergy": int(app.member_state("zhao-ling")["energy"]), "guard": bool(f["guard"]), "finished": battle.battle_finished}
	trace.append(row)
	if row["action"] != "" and not zhao_actions.has(row["action"]):
		zhao_actions[row["action"]] = row.duplicate()
		shot("battle-zhao-" + String(row["action"]))
	return row


func btick(battle: Node, slot: int) -> Dictionary:
	await tick()
	return zhao_row(battle, slot)


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 5 or not args[1] in ["en", "zh"] or not args[4] in ["victory", "defeat", "defeat-boundary"]:
		print("ZRIF_BAD_ARGS ", args)
		quit(2)
		return
	out = args[0]; language = args[1]; tag = args[2]; profile = args[3]; scenario = args[4]
	mode = args[5] if args.size() > 5 else "preview"
	appearance = args[6] if args.size() > 6 else "male"
	app = root.get_node("AppState")
	save_store = load("res://scripts/save_store.gd")
	config = load(CONFIG)
	var user_dir := ProjectSettings.globalize_path("user://").replace("\\", "/")
	ck(user_dir.begins_with(profile.replace("\\", "/")), "saves isolated to runner profile", {"user": user_dir, "profile": profile})
	var r: Dictionary
	if mode == "ordinary-default":
		var area = load(config.EXPLORATION_PATH)
		var arena = load(config.BATTLE_ARENA_PATH)
		ck(config.DEFAULT_ADOPTED and config.enabled_override == -1 and config.enabled(), "ordinary Zhao policy enabled without override")
		ck(area.field_npc_presenter_override == "" and arena.companion_combat_member_override == "" and arena.companion_combat_index_override == "", "no preview presenter/member/index host overrides")
		app.begin_new_run()
		app.hero_appearance = appearance
		app.show_initial_guide = false
		if app.language != language:
			app.toggle_language()
		r = {"ok": app.select_destination(config.DESTINATION)}
		ck(r["ok"], "SETUP FIXTURE fresh ordinary run and destination; configure() never called")
	else:
		r = config.configure(app, language, appearance)
		ck(r.get("ok", false), "SETUP FIXTURE configure preview", r)
	if not r.get("ok", false):
		_finish()
		return
	ck(not app.recruited_members.has("zhao-ling") and app.active_party_ids == ["hero"], "fresh run: Zhao not recruited, solo hero", app.active_party_ids)
	ck(change_scene_to_file(EXPLORE) == OK, "normal outskirts exploration scene entry")
	for i in 4:
		await tick()
	var ex: Node = current_scene
	ck(ex != null and ex.destination_id == "scifi.outskirts" and config.npc_attached(ex), "zpath27 driver on the actual zhao-ling field NPC")
	ck(ex.field_npc.position == Vector2(190, 150) and ex.field_npc.visible, "field NPC at source anchor 190,150 and visible", ex.field_npc.position)
	ck(ex.sprite_pilot == null or ex.sprite_pilot.get_script().resource_path != config.DRIVER_PATH, "hero is not driven by the Zhao driver")
	var spawn: Vector2 = ex.hero.position
	trace.append({"phase": "spawn", "frame": frame, "hero": [spawn.x, spawn.y]})
	shot("explore-start")
	# Real input walk to Zhao: W up to y<=150, D right to x>=168.
	await walk_axis(ex, KEY_W, 1, 150.0)
	await walk_axis(ex, KEY_D, 0, 168.0)
	trace.append({"phase": "at-npc", "frame": frame, "hero": [ex.hero.position.x, ex.hero.position.y], "dist": ex.hero.position.distance_to(ex.npc_position)})
	ck(ex.hero.position.distance_to(ex.npc_position) < 50.0, "walked into Zhao talk range by WASD", ex.hero.position)
	await tap(KEY_E)
	await tick()
	ck(ex.dialogue_open and ex.dialogue_mode == "recruit" and ex.dialogue_overlay.visible, "E opens the real Zhao recruit dialogue")
	ck(ex.dialogue_title.text == app.member_name("zhao-ling") and not ex.invite_button.disabled, "dialogue speaker Zhao with enabled Invite", ex.dialogue_title.text)
	shot("explore-zhao-talk")
	var saves0: int = save_store.list_entries().size()
	await click(ex.invite_button)
	for i in 3:
		await tick()
	ck(app.recruited_members.has("zhao-ling") and app.active_party_ids.has("zhao-ling"), "Invite click recruits Zhao through the real handler", app.active_party_ids)
	ck(not ex.dialogue_open and not ex.field_npc.visible, "dialogue closed and field NPC hidden after joining")
	ck(save_store.list_entries().size() == saves0 + 1, "game wrote its own post-invite autosave")
	shot("explore-zhao-joined")
	# Existing relay interaction at (470,128).
	await walk_axis(ex, KEY_W, 1, 130.0)
	await walk_axis(ex, KEY_D, 0, 462.0)
	await tap(KEY_E)
	await tick()
	ck(app.relay_checked, "E at the existing relay sets relay_checked through the real handler", ex.hero.position)
	shot("explore-relay")
	# DECLARED BOUNDARY FIXTURE, not a healthy-new-run defeat: load a valid low-health/empty-energy checkpoint.
	# Live combat stats/HP are never assigned and no result is forced. The enemy causes the subsequent deaths.
	if scenario == "defeat-boundary":
		var fixture: Dictionary = app.make_snapshot("area", ex.hero.position, "test_low_health_boundary_fixture")
		fixture["hero"]["hp"] = 1
		fixture["hero"]["energy"] = 0
		fixture["members"]["zhao-ling"]["hp"] = 1
		fixture["members"]["zhao-ling"]["energy"] = 0
		var fixture_id: String = save_store.write_entry("manual", 1, fixture)
		ck(fixture_id != "" and app.load_save(fixture_id), "DECLARED SETUP: valid low-health/empty-energy save checkpoint loads")
		ck(change_scene_to_file(EXPLORE) == OK, "boundary fixture enters ordinary exploration scene")
		for i in 4:
			await tick()
		ex = current_scene
		ck(int(app.hero_state["hp"]) == 1 and int(app.member_state("zhao-ling")["hp"]) == 1, "fixture precondition: both actors enter with saved 1HP")
		shot("declared-low-health-save-fixture")
	# Walk into the visible patrol at (355,238): S down to y>=238, then A left until the battle opens.
	ck(ex.enemy_visible, "patrol visible before encounter")
	await walk_axis(ex, KEY_S, 1, 238.0)
	var before_saves: int = save_store.list_entries().size()
	key(KEY_A, true)
	var n := 0
	while current_scene == ex and n < 3000:
		await tick()
		n += 1
	release_all()
	for i in 3:
		await tick()
	var battle: Node = current_scene
	ck(battle != null and battle.scene_file_path == "res://scenes/battle_arena.tscn" and battle.enemy_id == "patrol", "walking into the patrol opens the real battle", {"frames": n})
	if battle == null or battle.scene_file_path != "res://scenes/battle_arena.tscn":
		_finish()
		return
	ck(save_store.list_entries().size() == before_saves + 1, "encounter wrote one pre-battle autosave")
	var slot: int = app.active_party_ids.find("zhao-ling")
	ck(battle.fighters.size() == 2 and slot == 1 and String(battle.fighters[slot]["id"]) == "zhao-ling", "party in battle is hero + Zhao", app.active_party_ids)
	ck(battle.companion_sprite_sets != null and battle.companion_index == slot, "Zhao companion combat model loaded for the Zhao slot only", battle.companion_index)
	ck(battle.enemy_hp == int(battle.ENEMIES["patrol"]["max_hp"]), "patrol starts at normal max HP", battle.enemy_hp)
	ck(battle.controlled_index == 0, "hero controlled at battle start")
	await btick(battle, slot)
	shot("battle-start")
	await tap(KEY_TAB)
	zhao_row(battle, slot)
	ck(battle.controlled_index == slot and not battle.auto_mode, "Tab switches control to Zhao", battle.controlled_index)
	shot("battle-tab-zhao")
	if scenario.begins_with("defeat"):
		await _defeat(battle, slot)
		return
	# Skill (Q), guard (L held), dodge (K), then move (D) + attack (J) until the natural result.
	var e0: int = int(app.member_state("zhao-ling")["energy"])
	await tap(KEY_Q)
	for i in 16:
		await btick(battle, slot)
	ck(zhao_actions.has("skill") and int(app.member_state("zhao-ling")["energy"]) < e0, "Q fired Zhao's skill (energy spent, skill pose)", [e0, app.member_state("zhao-ling")["energy"]])
	# Let the skill one-shot finish; the loader plays one-shots over the guard loop.
	for i in 600:
		var sr: Dictionary = await btick(battle, slot)
		if sr["action"] != "skill" or battle.battle_finished:
			break
	key(KEY_L, true)
	var guard_seen := false
	for i in 40:
		var gr: Dictionary = await btick(battle, slot)
		guard_seen = guard_seen or (gr["guard"] and gr["action"] == "guard")
	key(KEY_L, false)
	ck(guard_seen and zhao_actions.has("guard"), "L held = Zhao guard state and guard pose")
	var e1: int = int(app.member_state("zhao-ling")["energy"])
	await tap(KEY_K)
	for i in 16:
		await btick(battle, slot)
	ck(zhao_actions.has("dodge") and int(app.member_state("zhao-ling")["energy"]) < e1, "K fired Zhao's dodge", [e1, app.member_state("zhao-ling")["energy"]])
	var reach := float(app.MEMBER_DEFS["zhao-ling"]["attack_range"])
	var attacks0: int = battle.player_attack_count
	var g := 0
	while g < 1500 and not (battle.battle_finished and battle.result_overlay.visible and not battle.result_button.disabled):
		var f: Dictionary = battle.fighters[slot]
		var dist := absf(battle.enemy_x - float(f["x"]))
		if not battle.battle_finished and dist > reach - 10.0:
			if not held.has(KEY_D):
				key(KEY_D, true)
		elif held.has(KEY_D):
			key(KEY_D, false)
		if held.has(KEY_J):
			key(KEY_J, false)
		elif not battle.battle_finished and float(f["attack_cooldown"]) == 0.0 and dist <= reach - 4.0 and battle.controlled_index == slot:
			key(KEY_J, true)
		await btick(battle, slot)
		g += 1
	release_all()
	ck(zhao_actions.has("move"), "D moved Zhao (move pose)")
	ck(zhao_actions.has("attack") and battle.player_attack_count > attacks0, "J attacks by controlled Zhao", battle.player_attack_count - attacks0)
	ck(battle.battle_finished and battle.battle_won and battle.enemy_hp == 0, "natural victory under the engine loop", {"frames": g})
	ck(battle.result_overlay.visible and not battle.result_button.disabled, "result overlay interactive")
	shot("battle-result")
	var xp_mid := int(app.hero_state["xp"])
	var pending: bool = app.has_pending_job_choice()
	await click(battle.result_button)
	for i in 4:
		await tick()
	var dest: Node = current_scene
	var expected := "res://scenes/growth_screen.tscn" if pending else EXPLORE
	ck(dest != null and dest != battle and dest.scene_file_path == expected, "result click goes to the normal destination", {"scene": dest.scene_file_path if dest != null else "", "pendingJobChoice": pending})
	if dest != null and dest.scene_file_path == EXPLORE:
		ck(not dest.enemy_visible and app.battle_enemy_id == "" and dest.hero.position == app.battle_return_position, "return: encounter cleared at the pre-battle safe point")
		ck(app.active_party_ids.has("zhao-ling") and not dest.field_npc.visible, "Zhao stays a party member (no field follower/NPC) after return")
		shot("explore-return")
	ck(int(app.hero_state["xp"]) == xp_mid, "no reward on result/return")
	# Reload the after-battle autosave written by the game.
	var after: Array = save_store.list_entries().filter(func(e): return String(e.get("snapshot", {}).get("note", "")) == "after_battle")
	var count: int = save_store.list_entries().size()
	ck(after.size() == 1, "exactly one after-battle autosave", after.size())
	var loaded: bool = after.size() > 0 and app.load_save(String(after[0]["id"]))
	ck(loaded, "after-battle autosave loads")
	ck(change_scene_to_file(EXPLORE) == OK, "reloaded exploration scene entry")
	for i in 4:
		await tick()
	var rl: Node = current_scene
	ck(rl != null and not rl.enemy_visible and app.recruited_members.has("zhao-ling") and app.active_party_ids.has("zhao-ling"), "reload keeps Zhao recruited and the encounter cleared", app.active_party_ids)
	ck(rl != null and not rl.field_npc.visible and int(app.hero_state["xp"]) == xp_mid and save_store.list_entries().size() == count, "reload: no NPC duplicate, no reward, no new save")
	shot("explore-reloaded")
	_finish()


func _defeat(battle: Node, slot: int) -> void:
	# Zhao controlled, retreating with A only; never J/Q/K. The hero is on the normal AI; outcome is natural.
	var enemy_max: int = int(battle.ENEMIES["patrol"]["max_hp"])
	key(KEY_A, true)
	var g := 0
	while g < 16000 and not battle.battle_finished:
		await btick(battle, slot)
		g += 1
	release_all()
	ck(battle.battle_finished and not battle.battle_won, "engine-caused defeat under normal enemy AI from declared starting checkpoint", {"frames": g, "enemyHP": battle.enemy_hp, "enemyMax": enemy_max, "won": battle.battle_won})
	if not (battle.battle_finished and not battle.battle_won):
		_finish()
		return
	for i in 40:
		await btick(battle, slot)
		if battle.result_overlay.visible:
			break
	shot("battle-defeat")
	var menu := false
	for i in 3000:
		await tick()
		if current_scene != null and current_scene.scene_file_path == "res://scenes/main_menu.tscn" and current_scene.is_node_ready():
			menu = true
			break
	ck(menu, "defeat returns to the ready main menu")
	shot("defeat-menu")
	var pre: Array = save_store.list_entries().filter(func(e): return String(e.get("snapshot", {}).get("note", "")) == "before_battle")
	var loaded: bool = not pre.is_empty() and app.load_save(String(pre[0]["id"]))
	ck(loaded, "pre-battle autosave loads for retry")
	ck(change_scene_to_file(EXPLORE) == OK, "retry enters the normal exploration scene")
	for i in 4:
		await tick()
	var rt: Node = current_scene
	ck(rt != null and rt.enemy_visible and app.active_party_ids.has("zhao-ling") and int(app.member_state("zhao-ling")["hp"]) > 0, "retry: patrol back, Zhao still recruited and alive at saved health")
	shot("defeat-retry")
	_finish()


func _write_report() -> void:
	if out == "":
		return
	var pins := {}
	for p in PINS:
		pins[p] = FileAccess.get_sha256(p) if FileAccess.file_exists(p) else null
	var obs: Array = zhao_actions.keys()
	obs.sort()
	var report := {"harness": "zhao-real-input-flow-v01", "scenario": scenario, "language": language, "appearance": appearance, "mode": mode,
		"godot": Engine.get_version_info().get("string", ""), "display": DisplayServer.get_name(), "maxFps": Engine.max_fps,
		"declaredLowHealthBoundaryFixture": scenario == "defeat-boundary", "ordinaryDefaultSetup": "ordinary-default mode starts a fresh ordinary AppState run and selects the destination, without configure() or host overrides; all subsequent inputs are real handlers.", "declaredSetup": "PREVIEW MODE ONLY: For defeat-boundary only, after real recruitment a valid saved checkpoint supplies both actors at1HP/0energy; subsequent deaths/results are engine-caused. SETUP FIXTURE: zpath27 configure(app, language, 'male') = fresh demo run at scifi.outskirts. All later steps are Input.parse_input_event keys (WASD/E/Tab/Q/L/K/D/J) and left-clicks on the real Invite/Result buttons. Reload = AppState.load_save of the game-written autosave + normal scene entry, not the Save/Load UI.",
		"zhaoActionsObserved": obs, "zhaoActionFirstRows": zhao_actions, "checks": checks, "failures": failures, "inputs": inputs,
		"captures": captures, "trace": trace, "sourceSha256Raw": pins, "harnessSha256Raw": FileAccess.get_sha256(ProjectSettings.globalize_path("res://").path_join("../tools/rpg-2-star-ocean-the-second_zhao-playable-path_real-input-flow_test-only-v01_20261021-225020-4199f994.gd")),
		"humanPlaytest": false, "artApproved": false, "defaultAdopted": config.DEFAULT_ADOPTED}
	var f := FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_zhao-rif_%s-%s_report_%s.json" % [language, scenario, tag]), FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(report, " "))
		f.close()


func _finish() -> void:
	release_all()
	config.rollback()
	_write_report()
	if failures.is_empty():
		print("ZRIF_ALL_PASS language=%s scenario=%s checks=%d" % [language, scenario, checks.size()])
		quit(0)
	else:
		print("ZRIF_FAILED language=%s scenario=%s failures=%s" % [language, scenario, failures])
		quit(1)
