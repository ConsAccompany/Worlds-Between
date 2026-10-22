extends SceneTree
# TEST-ONLY jpath33 Ji real-input flow (scripted normal input; NOT a human playtest, art/motion approval or default adoption).
# SETUP FIXTURE (declared): jpath33 config.configure(app, language, "male") starts a fresh demo run at scifi.ruins (Ji not recruited, ji_records_checked false).
# Everything after setup goes through the real handlers via Input.parse_input_event key/mouse events only:
#   WASD walk -> E at the actual ji-cheng field NPC (Invite disabled) -> Later click -> E at the existing records console
#   (ji_records_checked) -> E at Ji -> mouse click on the real Invite button (recruit through _invite_companion) ->
#   walk into the ruins sentry -> Tab to Ji -> Q skill, L guard, K dodge, R job skill attempt (recorded, not required),
#   D move, J attack -> natural victory -> mouse click on the result button -> exploration return -> reload of the
#   after-battle autosave the game itself wrote (AppState.load_save + normal scene entry; NOT the Save/Load UI).
# Defeat scenario: same route, Ji is controlled and only retreats (no player attack); outcome is whatever the normal AI
# produces. No recruit_member, HP/energy/damage/cooldown/AI writes, hero placement or _finish_battle/_try_attack calls.
# Args: <out_dir> <language en|zh> <tag> <profile_dir> <victory|defeat>
const CONFIG := "res://scripts/jpath33/rpg-2-star-ocean-the-second_ji-playable-path_config_opt-in-v01_20261021-222438-7d4b2e91.gd"
const EXPLORE := "res://scenes/scifi_exploration_area.tscn"
const PINS := ["res://scripts/jpath33/rpg-2-star-ocean-the-second_ji-playable-path_config_opt-in-v01_20261021-222438-7d4b2e91.gd",
	"res://scripts/jpath33/rpg-2-star-ocean-the-second_ji-playable-path_npc-driver_opt-in-v01_20261021-222438-7d4b2e91.gd",
	"res://scripts/jpath33/rpg-2-star-ocean-the-second_ji-playable-path_entry_opt-in-v01_20261021-222438-7d4b2e91.gd",
	"res://scripts/battle_arena.gd", "res://scripts/scifi_exploration_area.gd", "res://scripts/app_state.gd",
	"res://scripts/save_store.gd", "res://scenes/battle_arena.tscn", "res://scenes/scifi_exploration_area.tscn",
	"res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd",
	"res://data/jcombat32/rpg-2-star-ocean-the-second_ji-cheng-combat_runtime-index_unapproved-jcombat32-v01_20261021-220632-089ef67c.json"]
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
var ji_actions := {}
var frame := 0
var held := {}


func _initialize() -> void:
	call_deferred("_run")
	create_timer(170.0).timeout.connect(func(): print("JRIF_WATCHDOG"); _write_report(); quit(2))


func ck(ok: bool, label: String, detail: Variant = null) -> void:
	checks.append({"check": label, "passed": ok, "detail": detail})
	print("JRIF ", "PASS " if ok else "FAIL ", label, "" if detail == null else " " + str(detail))
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
	var file := "rpg-2-star-ocean-the-second_ji-rif_%s-%s_%s_capture-640_%s.png" % [language, scenario, label, tag]
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


func ji_row(battle: Node, slot: int) -> Dictionary:
	var f: Dictionary = battle.fighters[slot]
	var pose: Dictionary = battle.companion_sets_by_member.get("ji-cheng").current_frame(slot) if battle.companion_sets_by_member.get("ji-cheng") != null else {}
	var row := {"frame": frame, "controlled": battle.controlled_index, "action": String(pose.get("action", "")), "cell": int(pose.get("cell", -1)),
		"poseFrame": int(pose.get("frame", -1)), "jiX": snappedf(float(f["x"]), 0.01), "enemyX": snappedf(float(battle.enemy_x), 0.01),
		"enemyHP": int(battle.enemy_hp), "jiHP": int(app.member_state("ji-cheng")["hp"]), "heroHP": int(app.member_state("hero")["hp"]),
		"jiEnergy": int(app.member_state("ji-cheng")["energy"]), "guard": bool(f["guard"]), "finished": battle.battle_finished}
	trace.append(row)
	if row["action"] != "" and not ji_actions.has(row["action"]):
		ji_actions[row["action"]] = row.duplicate()
		shot("battle-ji-" + String(row["action"]))
	return row


func btick(battle: Node, slot: int) -> Dictionary:
	await tick()
	return ji_row(battle, slot)


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 5 or not args[1] in ["en", "zh"] or not args[4] in ["victory", "defeat", "defeat-boundary"]:
		print("JRIF_BAD_ARGS ", args)
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
		var arena = load("res://scripts/battle_arena.gd")
		ck(not config.DEFAULT_ADOPTED and config.enabled_override == -1 and not config.enabled(), "ordinary Ji policy default OFF without override")
		ck(area.field_npc_presenter_override == "" and arena.companion_combat_member_override == "" and arena.companion_combat_index_override == "", "no preview presenter/member/index host overrides")
		app.begin_new_run()
		app.hero_appearance = appearance
		app.show_initial_guide = false
		if app.language != language:
			app.toggle_language()
		r = {"ok": app.select_destination(config.DESTINATION)}
		ck(r["ok"], "SETUP FIXTURE fresh ordinary run and destination; configure() never called")
		ck(change_scene_to_file(EXPLORE) == OK, "ordinary ruins scene entry")
		for i in 4:
			await tick()
		var off: Node = current_scene
		ck(off != null and off.destination_id == "scifi.ruins" and off.field_npc != null and off.field_npc.visible and off.field_npc_driver == null and not config.npc_attached(off), "default OFF: existing static Ji NPC texture, no jpath33 driver")
		shot("default-off-ruins")
		_finish()
		return
	else:
		r = config.configure(app, language, appearance)
		ck(r.get("ok", false), "SETUP FIXTURE configure preview", r)
	if not r.get("ok", false):
		_finish()
		return
	ck(not app.recruited_members.has("ji-cheng") and app.active_party_ids == ["hero"] and not app.ji_records_checked, "fresh run: Ji not recruited, records unchecked, solo hero", app.active_party_ids)
	ck(change_scene_to_file(EXPLORE) == OK, "normal ruins exploration scene entry")
	for i in 4:
		await tick()
	var ex: Node = current_scene
	ck(ex != null and ex.destination_id == "scifi.ruins" and config.npc_attached(ex), "jpath33 driver on the actual ji-cheng field NPC")
	if ex == null or ex.destination_id != "scifi.ruins" or ex.field_npc == null:
		_finish()
		return
	ck(ex.field_npc.position == Vector2(200, 145) and ex.field_npc.visible, "field NPC at source anchor 200,145 and visible", ex.field_npc.position)
	ck(ex.sprite_pilot == null or ex.sprite_pilot.get_script().resource_path != config.DRIVER_PATH, "hero is not driven by the Ji driver")
	ck(ex.records_label.visible, "records console marker visible before the check")
	var spawn: Vector2 = ex.hero.position
	trace.append({"phase": "spawn", "frame": frame, "hero": [spawn.x, spawn.y]})
	shot("explore-start")
	# Prerequisite gate proof by real input: talk to Ji before the records console; Invite must stay disabled.
	await walk_axis(ex, KEY_W, 1, 160.0)
	await walk_axis(ex, KEY_D, 0, 185.0)
	ck(ex.hero.position.distance_to(ex.npc_position) < 50.0, "walked into Ji talk range by WASD (before records)", ex.hero.position)
	await tap(KEY_E)
	await tick()
	ck(ex.dialogue_open and ex.dialogue_mode == "recruit" and ex.invite_button.disabled and not app.ji_records_checked, "before records: E opens Ji dialogue with Invite disabled (no bypass)")
	shot("explore-ji-locked")
	await click(ex.later_button)
	for i in 2:
		await tick()
	ck(not ex.dialogue_open and not app.recruited_members.has("ji-cheng"), "Later click closes the locked dialogue; Ji not recruited")
	# Existing records console at (320,250).
	await walk_axis(ex, KEY_S, 1, 250.0)
	await walk_axis(ex, KEY_D, 0, 305.0)
	ck(ex.hero.position.distance_to(ex.RECORDS_POSITION) < 43.0, "walked to the records console by WASD", ex.hero.position)
	await tap(KEY_E)
	await tick()
	ck(app.ji_records_checked and not ex.records_label.visible, "E at the actual records console sets ji_records_checked through the real handler")
	shot("explore-records")
	await walk_axis(ex, KEY_W, 1, 160.0)
	await walk_axis(ex, KEY_A, 0, 222.0)
	trace.append({"phase": "at-npc", "frame": frame, "hero": [ex.hero.position.x, ex.hero.position.y], "dist": ex.hero.position.distance_to(ex.npc_position)})
	ck(ex.hero.position.distance_to(ex.npc_position) < 50.0, "walked back into Ji talk range by WASD", ex.hero.position)
	await tap(KEY_E)
	await tick()
	ck(ex.dialogue_open and ex.dialogue_mode == "recruit" and ex.dialogue_overlay.visible, "E opens the real Ji recruit dialogue")
	ck(ex.dialogue_title.text == app.member_name("ji-cheng") and not ex.invite_button.disabled, "dialogue speaker Ji with enabled Invite", ex.dialogue_title.text)
	shot("explore-ji-talk")
	var saves0: int = save_store.list_entries().size()
	await click(ex.invite_button)
	for i in 3:
		await tick()
	ck(app.recruited_members.has("ji-cheng") and app.active_party_ids.has("ji-cheng"), "Invite click recruits Ji through the real handler", app.active_party_ids)
	ck(not ex.dialogue_open and not ex.field_npc.visible, "dialogue closed and field NPC hidden after joining; no follower")
	ck(save_store.list_entries().size() == saves0 + 1, "game wrote its own post-invite autosave")
	shot("explore-ji-joined")
	# DECLARED BOUNDARY FIXTURE, not a healthy-new-run defeat: load a valid low-health/empty-energy checkpoint.
	# Live combat stats/HP are never assigned and no result is forced. The enemy causes the subsequent deaths.
	if scenario == "defeat-boundary":
		var fixture: Dictionary = app.make_snapshot("area", ex.hero.position, "test_low_health_boundary_fixture")
		fixture["hero"]["hp"] = 1
		fixture["hero"]["energy"] = 0
		fixture["members"]["ji-cheng"]["hp"] = 1
		fixture["members"]["ji-cheng"]["energy"] = 0
		var fixture_id: String = save_store.write_entry("manual", 1, fixture)
		ck(fixture_id != "" and app.load_save(fixture_id), "DECLARED SETUP: valid low-health/empty-energy save checkpoint loads")
		ck(change_scene_to_file(EXPLORE) == OK, "boundary fixture enters ordinary exploration scene")
		for i in 4:
			await tick()
		ex = current_scene
		ck(int(app.hero_state["hp"]) == 1 and int(app.member_state("ji-cheng")["hp"]) == 1, "fixture precondition: both actors enter with saved 1HP")
		shot("declared-low-health-save-fixture")
	# Walk into the visible sentry at (420,225): S down to y>=225, then D right until the battle opens.
	ck(ex.enemy_visible, "sentry visible before encounter")
	await walk_axis(ex, KEY_S, 1, 225.0)
	var before_saves: int = save_store.list_entries().size()
	key(KEY_D, true)
	var n := 0
	while current_scene == ex and n < 3000:
		await tick()
		n += 1
	release_all()
	for i in 3:
		await tick()
	var battle: Node = current_scene
	ck(battle != null and battle.scene_file_path == "res://scenes/battle_arena.tscn" and battle.enemy_id == "sentry", "walking into the sentry opens the real battle", {"frames": n})
	if battle == null or battle.scene_file_path != "res://scenes/battle_arena.tscn":
		_finish()
		return
	ck(save_store.list_entries().size() == before_saves + 1, "encounter wrote one pre-battle autosave")
	var slot: int = app.active_party_ids.find("ji-cheng")
	ck(battle.fighters.size() == 2 and slot == 1 and String(battle.fighters[slot]["id"]) == "ji-cheng", "party in battle is hero + Ji", app.active_party_ids)
	ck(battle.companion_sets_by_member.get("ji-cheng") != null and battle.companion_slot_by_member.get("ji-cheng", -1) == slot, "Ji companion combat model loaded for the Ji slot only", battle.companion_slot_by_member.get("ji-cheng", -1))
	ck(battle.enemy_hp == int(battle.ENEMIES["sentry"]["max_hp"]), "sentry starts at normal max HP", battle.enemy_hp)
	ck(battle.controlled_index == 0, "hero controlled at battle start")
	await btick(battle, slot)
	shot("battle-start")
	# Real input: move the hero left first so its normal AI cannot win before Ji's short-range input sequence.
	if scenario == "victory":
		key(KEY_A, true)
		var retreat_frames := 0
		while float(battle.fighters[0]["x"]) > 35.0 and retreat_frames < 90 and not battle.battle_finished:
			await btick(battle, slot)
			retreat_frames += 1
		key(KEY_A, false)
		ck(float(battle.fighters[0]["x"]) <= 35.0,"real A input moves hero aside before Tab; no AI or position writes")
	await tap(KEY_TAB)
	ji_row(battle, slot)
	ck(battle.controlled_index == slot and not battle.auto_mode, "Tab switches control to Ji", battle.controlled_index)
	shot("battle-tab-ji")
	if scenario.begins_with("defeat"):
		await _defeat(battle, slot)
		return
	# Skill (Q), guard (L held), dodge (K), then move (D) + attack (J) until the natural result.
	var e0: int = int(app.member_state("ji-cheng")["energy"])
	await tap(KEY_Q)
	for i in 16:
		await btick(battle, slot)
	ck(ji_actions.has("skill") and int(app.member_state("ji-cheng")["energy"]) < e0, "Q fired Ji's skill (energy spent, skill pose)", [e0, app.member_state("ji-cheng")["energy"]])
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
	ck(guard_seen and ji_actions.has("guard"), "L held = Ji guard state and guard pose")
	var e1: int = int(app.member_state("ji-cheng")["energy"])
	await tap(KEY_K)
	for i in 16:
		await btick(battle, slot)
	ck(ji_actions.has("dodge") and int(app.member_state("ji-cheng")["energy"]) < e1, "K fired Ji's dodge", [e1, app.member_state("ji-cheng")["energy"]])
	# R = existing battle_job_skill input; recorded honestly (level/energy gates of the normal rules decide).
	var e2: int = int(app.member_state("ji-cheng")["energy"])
	await tap(KEY_R)
	for i in 8:
		await btick(battle, slot)
	var job_used: bool = int(app.member_state("ji-cheng")["energy"]) < e2
	trace.append({"phase": "job-skill-attempt", "frame": frame, "energyBefore": e2, "energyAfter": int(app.member_state("ji-cheng")["energy"]), "used": job_used, "level": int(app.member_state("ji-cheng").get("level", 1))})
	print("JRIF INFO job-skill R used=", job_used, " level=", app.member_state("ji-cheng").get("level", 1))
	var reach := float(app.MEMBER_DEFS["ji-cheng"]["attack_range"])
	var attacks0: int = battle.player_attack_count
	var g := 0
	var commanded_j := false
	var controlled_attack_seen := false
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
			commanded_j = true
		var attack_row: Dictionary = await btick(battle, slot)
		controlled_attack_seen = controlled_attack_seen or (commanded_j and attack_row["action"] == "attack" and int(attack_row["controlled"]) == slot)
		g += 1
	release_all()
	ck(ji_actions.has("move"), "D moved Ji (move pose)")
	ck(controlled_attack_seen and ji_actions.has("attack") and battle.player_attack_count > attacks0, "J attacks by controlled Ji", battle.player_attack_count - attacks0)
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
		ck(app.active_party_ids.has("ji-cheng") and dest.recruit_id == "ji-cheng" and not dest.field_npc.visible, "Ji stays party member; recruited field NPC stays hidden (no duplicate, no follower)")
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
	ck(rl != null and not rl.enemy_visible and app.recruited_members.has("ji-cheng") and app.active_party_ids.has("ji-cheng"), "reload keeps Ji recruited and the encounter cleared", app.active_party_ids)
	ck(rl != null and rl.recruit_id == "ji-cheng" and not rl.field_npc.visible and app.ji_records_checked and int(app.hero_state["xp"]) == xp_mid and save_store.list_entries().size() == count, "reload: no NPC duplicate, no reward, no new save")
	shot("explore-reloaded")
	_finish()


func _defeat(battle: Node, slot: int) -> void:
	# Ji controlled, retreating with A only; never J/Q/K. The hero is on the normal AI; outcome is natural.
	var enemy_max: int = int(battle.ENEMIES["sentry"]["max_hp"])
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
	ck(rt != null and rt.enemy_visible and app.active_party_ids.has("ji-cheng") and int(app.member_state("ji-cheng")["hp"]) > 0, "retry: sentry back, Ji still recruited and alive at saved health")
	shot("defeat-retry")
	_finish()


func _write_report() -> void:
	if out == "":
		return
	var pins := {}
	for p in PINS:
		pins[p] = FileAccess.get_sha256(p) if FileAccess.file_exists(p) else null
	var obs: Array = ji_actions.keys()
	obs.sort()
	var report := {"harness": "ji-real-input-flow-v01", "scenario": scenario, "language": language, "appearance": appearance, "mode": mode,
		"godot": Engine.get_version_info().get("string", ""), "display": DisplayServer.get_name(), "maxFps": Engine.max_fps,
		"declaredLowHealthBoundaryFixture": scenario == "defeat-boundary", "ordinaryDefaultSetup": "ordinary-default mode starts a fresh ordinary AppState run and selects the destination, without configure() or host overrides; all subsequent inputs are real handlers.", "declaredSetup": "PREVIEW MODE ONLY: For defeat-boundary only, after real recruitment a valid saved checkpoint supplies both actors at1HP/0energy; subsequent deaths/results are engine-caused. SETUP FIXTURE: jpath33 configure(app, language, 'male') = fresh demo run at scifi.ruins; records console and recruit are real E/click inputs. All later steps are Input.parse_input_event keys (WASD/E/Tab/Q/L/K/D/J) and left-clicks on the real Invite/Result buttons. Reload = AppState.load_save of the game-written autosave + normal scene entry, not the Save/Load UI.",
		"jiActionsObserved": obs, "jiActionFirstRows": ji_actions, "checks": checks, "failures": failures, "inputs": inputs,
		"captures": captures, "trace": trace, "sourceSha256Raw": pins, "harnessSha256Raw": FileAccess.get_sha256(ProjectSettings.globalize_path("res://").path_join("../tools/rpg-2-star-ocean-the-second_ji-playable-path_real-input-flow_test-only-v01_20261021-222438-7d4b2e91.gd")),
		"humanPlaytest": false, "artApproved": false, "defaultAdopted": config.DEFAULT_ADOPTED}
	var f := FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_ji-rif_%s-%s_report_%s.json" % [language, scenario, tag]), FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(report, " "))
		f.close()


func _finish() -> void:
	release_all()
	config.rollback()
	_write_report()
	if failures.is_empty():
		print("JRIF_ALL_PASS language=%s scenario=%s checks=%d" % [language, scenario, checks.size()])
		quit(0)
	else:
		print("JRIF_FAILED language=%s scenario=%s failures=%s" % [language, scenario, failures])
		quit(1)
