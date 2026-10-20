extends SceneTree

# Independent timing/cancellation checks for the OPT-IN heroine contact pilot (--heroine-sea-contact-pilot) and the loader's
# optional tick_rate / loop_start / explicit event clock. TECHNICAL only: the sprite set used is the SYNTHETIC half-scale
# diagnostic fixture (NOT ART). No art approval, no default adoption. The battle node's own _process is disabled and driven
# with explicit deltas; attack/dodge/skill requests go through Input.action_press + _process (the normal input path).
const BATTLE_SCENE_PATH := "res://scenes/battle_arena.tscn"
const BATTLE_SCRIPT_PATH := "res://scripts/battle_arena.gd"
const HELPER_PATH := "res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd"
const HALF_DIR := "res://tests/fixtures/csp-half-scale-v01_7d4bddce"
const HALF_MANIFEST := HALF_DIR + "/rpg-2-star-ocean-the-second_combat-half-scale_fixture_not-art-v01_20261020-154048-7d4bddce.json"
const HALF_INDEX := HALF_DIR + "/rpg-2-star-ocean-the-second_combat-half-scale_fixture-index_not-art-v01_20261020-154048-7d4bddce.json"
const HALF_SHEET := HALF_DIR + "/rpg-2-star-ocean-the-second_combat-half-scale_sheet_not-art-v01_20261020-154048-7d4bddce.png"
const TMP_DIR := "user://heroine-contact-check-c7e41a2d"
const CONTACT := 5.0 / 30.0
const RECOVERY_END := 12.0 / 30.0
const HERO_DAMAGE := 19

var app: Node
var battle_script: GDScript
var helper: GDScript
var pass_count := 0
var failed := false


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	app = root.get_node("AppState")
	battle_script = load(BATTLE_SCRIPT_PATH)
	helper = load(HELPER_PATH)
	SaveStore.root_path = "user://test-saves/heroine-contact-c7e41a2d"
	await _default_parity()
	await _boundaries()
	await _cancellations()
	await _bonus_range_facing()
	await _pause_result_exit()
	await _repress()
	_schema()
	if failed:
		print("HEROINE_CONTACT FAIL checks_passed=%d" % pass_count)
		quit(1)
		return
	print("HEROINE_CONTACT PASS checks=%d" % pass_count)
	quit(0)


func _check(condition: bool, label: String) -> bool:
	if condition:
		pass_count += 1
		print("PASS " + label)
	else:
		failed = true
		print("FAIL " + label)
	return condition


func _open(appearance: String, contact: int, sprites: int = 0) -> Node2D:
	if current_scene != null:
		current_scene.queue_free()
		current_scene = null
		await process_frame
	app.begin_new_run()
	app.hero_appearance = appearance
	app.select_destination("scifi.outskirts")
	battle_script.heroine_sea_contact_override = contact
	battle_script.combat_sprite_set_override = sprites
	battle_script.combat_sprite_set_index_override = HALF_INDEX if sprites == 1 else ""
	helper.clear_cache()
	app.begin_battle("patrol", Vector2(330, 215))
	var battle: Node2D = load(BATTLE_SCENE_PATH).instantiate()
	battle.set_process(false)
	root.add_child(battle)
	current_scene = battle
	await process_frame
	battle.set_process(false)
	battle.fighters[0]["x"] = 200.0
	battle.enemy_x = 240.0
	battle.enemy_cooldown = 999.0
	battle.enemy_windup = 0.0
	return battle


func _press(battle: Node2D, action: String, dt: float) -> void:
	Input.action_press(action)
	battle._process(dt)
	Input.action_release(action)
	# Advance one real engine frame so is_action_just_pressed cannot fire again in later manual steps.
	await process_frame


func _step(battle: Node2D, dt: float, count: int) -> void:
	for i in count:
		battle._process(dt)


func _outcomes(battle: Node2D) -> Array:
	var result := []
	for entry in battle.contact_event_log:
		result.append(String(entry["outcome"]))
	return result


func _default_parity() -> void:
	var battle := await _open("female", 0)
	var hp0: int = battle.enemy_hp
	await _press(battle, "battle_attack", 1.0 / 60.0)
	_check(not battle.fighters[0].has("contact_event_id"), "flag off: female hero has no event keys")
	_check(battle.enemy_hp == hp0 - HERO_DAMAGE, "flag off: input attack damages in the request frame (immediate legacy path)")
	_check(is_equal_approx(float(battle.fighters[0]["attack_cooldown"]), 0.43) and battle.player_attack_count == 1, "flag off: cooldown 0.43 and count 1")
	battle = await _open("male", 1)
	hp0 = battle.enemy_hp
	await _press(battle, "battle_attack", 1.0 / 60.0)
	_check(not battle.fighters[0].has("contact_event_id") and battle.enemy_hp == hp0 - HERO_DAMAGE, "flag on, male hero: unchanged immediate path (scoped to hero:female)")
	battle = await _open("female", 1)
	_check(battle.fighters[0].has("contact_event_id"), "flag on, female hero: event keys present")


func _boundaries() -> void:
	for fps in [30, 60]:
		var battle := await _open("female", 1)
		var hp0: int = battle.enemy_hp
		var dt: float = 1.0 / fps
		await _press(battle, "battle_attack", dt)
		_check(battle.enemy_hp == hp0 and float(battle.fighters[0]["contact_event_clock"]) == 0.0, "%d fps: request frame applies no damage and newborn clock is 0" % fps)
		var frames_before: int = 5 * fps / 30 - 1
		_step(battle, dt, frames_before)
		_check(battle.enemy_hp == hp0, "%d fps: no hit after %d frames (%.4f s < 5/30)" % [fps, frames_before, frames_before * dt])
		_step(battle, dt, 1)
		_check(battle.enemy_hp == hp0 - HERO_DAMAGE and _outcomes(battle) == ["hit"], "%d fps: exactly one hit on the frame reaching 5/30" % fps)
		_step(battle, dt, 7 * fps / 30 - 1)
		_check(bool(battle.fighters[0]["contact_event_active"]), "%d fps: still in recovery before 12/30" % fps)
		_step(battle, dt, 1)
		_check(not bool(battle.fighters[0]["contact_event_active"]) and String(battle.fighters[0]["contact_event_state"]) == "ended", "%d fps: recovery ends at 12/30" % fps)
		_step(battle, dt, 30)
		_check(battle.enemy_hp == hp0 - HERO_DAMAGE and _outcomes(battle).size() == 1, "%d fps: no double award afterwards" % fps)
	# Exact boundary with explicit deltas: just before, exactly at, after.
	var b := await _open("female", 1)
	var hp := int(b.enemy_hp)
	await _press(b, "battle_attack", 0.5)
	_check(float(b.fighters[0]["contact_event_clock"]) == 0.0 and b.enemy_hp == hp, "newborn after a 0.5 s frame is not advanced by that frame")
	_step(b, CONTACT - 0.001, 1)
	_check(b.enemy_hp == hp, "5/30 - 1 ms: no premature hit")
	_step(b, 0.001, 1)
	_check(b.enemy_hp == hp - HERO_DAMAGE, "5/30 reached exactly (sum of deltas): hit")
	b = await _open("female", 1)
	hp = int(b.enemy_hp)
	await _press(b, "battle_attack", 1.0 / 60.0)
	_step(b, CONTACT, 1)
	_check(b.enemy_hp == hp - HERO_DAMAGE, "single exact 5/30 delta: hit")
	b = await _open("female", 1)
	hp = int(b.enemy_hp)
	await _press(b, "battle_attack", 1.0 / 60.0)
	_step(b, 0.5, 1)
	_check(b.enemy_hp == hp - HERO_DAMAGE and _outcomes(b) == ["hit"] and String(b.fighters[0]["contact_event_state"]) == "ended", "large 0.5 s delta crossing contact and recovery: one hit, event ended")
	_step(b, 0.5, 3)
	_check(_outcomes(b).size() == 1 and b.enemy_hp == hp - HERO_DAMAGE, "large delta: no later duplicate")


func _cancellations() -> void:
	for action in ["battle_dodge", "battle_skill", "battle_job_skill"]:
		var battle := await _open("female", 1)
		app.member_state("hero")["energy"] = 60
		app.member_state("hero")["job_stage"] = maxi(1, int(app.member_state("hero").get("job_stage", 1)))
		var hp0: int = battle.enemy_hp
		await _press(battle, "battle_attack", 1.0 / 60.0)
		_step(battle, 1.0 / 60.0, 3)
		var hp_before_action: int = battle.enemy_hp
		await _press(battle, action, 1.0 / 60.0)
		var job_damage: int = hp_before_action - int(battle.enemy_hp)
		var cooldown := float(battle.fighters[0]["attack_cooldown"])
		_step(battle, 1.0 / 60.0, 30)
		var outcomes := _outcomes(battle)
		if action == "battle_job_skill" and outcomes.is_empty():
			# The job skill can be unavailable for a fresh hero; then it never ran, so the attack must hit normally.
			_check(false, "job skill was not available in this fixture state (cancellation not exercised)")
			continue
		_check(outcomes.size() == 1 and String(outcomes[0]).begins_with("cancelled_"), "%s before contact cancels the pending attack (%s)" % [action, str(outcomes)])
		_check(int(battle.enemy_hp) == hp0 - job_damage, "%s: no orphan attack damage (only the action's own effect, %d)" % [action, job_damage])
		_check(cooldown > 0.3, "%s: attack cooldown not refunded (%.3f)" % [action, cooldown])
	# Same-frame attack + dodge: dodge is processed after attack in the frame, so it cancels it.
	var b := await _open("female", 1)
	app.member_state("hero")["energy"] = 60
	var hp := int(b.enemy_hp)
	Input.action_press("battle_attack")
	Input.action_press("battle_dodge")
	b._process(1.0 / 60.0)
	Input.action_release("battle_attack")
	Input.action_release("battle_dodge")
	await process_frame
	_step(b, 1.0 / 60.0, 30)
	_check(b.enemy_hp == hp and _outcomes(b) == ["cancelled_dodge"] and b.player_attack_count == 1, "same-frame attack+dodge: cancelled, count kept at request")
	# Enemy hit before contact.
	b = await _open("female", 1)
	hp = int(b.enemy_hp)
	await _press(b, "battle_attack", 1.0 / 60.0)
	b.enemy_target_index = 0
	b._apply_enemy_hit()
	_step(b, 1.0 / 60.0, 30)
	_check(b.enemy_hp == hp and _outcomes(b) == ["cancelled_hit"], "enemy hit before contact cancels")
	# Down before contact.
	b = await _open("female", 1)
	hp = int(b.enemy_hp)
	await _press(b, "battle_attack", 1.0 / 60.0)
	app.member_state("hero")["hp"] = 1
	b.enemy_target_index = 0
	b._apply_enemy_hit()
	b._process(1.0 / 60.0)
	_check(b.enemy_hp == hp and _outcomes(b) == ["cancelled_down"], "down before contact cancels, no orphan damage")
	# Hit after contact (recovery): damage already done once, recovery interrupted.
	b = await _open("female", 1)
	hp = int(b.enemy_hp)
	await _press(b, "battle_attack", 1.0 / 60.0)
	_step(b, 1.0 / 60.0, 11)
	b.enemy_target_index = 0
	b._apply_enemy_hit()
	_step(b, 1.0 / 60.0, 30)
	_check(b.enemy_hp == hp - HERO_DAMAGE and _outcomes(b) == ["hit"] and String(b.fighters[0]["contact_event_state"]) == "interrupted", "hit during recovery: one hit kept, recovery interrupted")


func _bonus_range_facing() -> void:
	# Hero skill keeps its semantic effect at request (shared bonus); bonus is consumed only at a successful contact.
	var b := await _open("female", 1)
	app.member_state("hero")["energy"] = 60
	var hp := int(b.enemy_hp)
	await _press(b, "battle_skill", 1.0 / 60.0)
	var bonus := int(b.next_attack_bonus)
	_check(bonus > 0, "hero personal skill adds shared bonus at request (%d)" % bonus)
	_step(b, 0.5, 1)
	await _press(b, "battle_attack", 1.0 / 60.0)
	_check(int(b.next_attack_bonus) == bonus, "bonus not reserved/consumed at request")
	b.enemy_x = 200.0 + 140.0
	_step(b, 1.0 / 60.0, 12)
	_check(_outcomes(b) == ["missed"] and int(b.next_attack_bonus) == bonus and b.enemy_hp == hp and b.feedback_key == "battle_far", "out of range at contact: miss, bonus retained, far feedback")
	_check(b.player_attack_count == 1, "miss still counts the request")
	b.enemy_x = 240.0
	_step(b, 0.5, 1)
	await _press(b, "battle_attack", 1.0 / 60.0)
	_step(b, 1.0 / 60.0, 10)
	_check(b.enemy_hp == hp - HERO_DAMAGE - bonus and int(b.next_attack_bonus) == 0, "next successful contact consumes bonus once (damage %d)" % (HERO_DAMAGE + bonus))
	# Range recheck the other way: out of range at request, in range at contact -> hit.
	b = await _open("female", 1)
	hp = int(b.enemy_hp)
	b.enemy_x = 200.0 + 100.0
	await _press(b, "battle_attack", 1.0 / 60.0)
	b.enemy_x = 240.0
	_step(b, 1.0 / 60.0, 10)
	_check(b.enemy_hp == hp - HERO_DAMAGE, "range rechecked at contact (far at request, near at contact: hit)")
	# Facing latched with the loader's explicit event clock (synthetic fixture, not art).
	b = await _open("female", 1, 1)
	_check(b.combat_sprite_sets != null and b.combat_sprite_sets.has_set(0), "synthetic hero:female half-scale set loaded for event-clock checks")
	await _press(b, "battle_attack", 1.0 / 60.0)
	var frame: Dictionary = b.combat_sprite_sets.current_frame(0)
	_check(String(frame["action"]) == "attack" and int(frame["facing"]) == 1, "request frame: loader shows attack facing right")
	b.enemy_x = 170.0
	_step(b, 1.0 / 60.0, 3)
	frame = b.combat_sprite_sets.current_frame(0)
	_check(int(frame["facing"]) == 1 and is_equal_approx(float(b.combat_sprite_sets.states[0]["clock"]), float(b.fighters[0]["contact_event_clock"])), "enemy crosses behind: facing stays latched, loader clock == event clock")
	_step(b, 1.0 / 60.0, 30)
	frame = b.combat_sprite_sets.current_frame(0)
	_check(String(frame["action"]) != "attack" and int(frame["facing"]) == -1, "after recovery: attack ends and facing follows enemy again")


func _pause_result_exit() -> void:
	var b := await _open("female", 1)
	var hp := int(b.enemy_hp)
	await _press(b, "battle_attack", 1.0 / 60.0)
	b._toggle_pause()
	_step(b, 1.0 / 60.0, 60)
	_check(b.enemy_hp == hp and float(b.fighters[0]["contact_event_clock"]) == 0.0, "paused: event clock frozen, no damage")
	b._toggle_pause()
	_step(b, 1.0 / 60.0, 9)
	_check(b.enemy_hp == hp, "after unpause: still no hit before 5/30 of unpaused time")
	_step(b, 1.0 / 60.0, 1)
	_check(b.enemy_hp == hp - HERO_DAMAGE, "after unpause: hit at 5/30")
	# Final hit: kills once, finishes once.
	b = await _open("female", 1)
	b.enemy_hp = 5
	await _press(b, "battle_attack", 1.0 / 60.0)
	_step(b, 1.0 / 60.0, 10)
	var xp := int(b.result_reward_xp)
	_check(b.battle_finished and b.battle_won and b.enemy_hp == 0 and _outcomes(b) == ["hit"], "final contact: enemy 0, battle won once")
	_step(b, 1.0 / 60.0, 30)
	_check(_outcomes(b) == ["hit"] and int(b.result_reward_xp) == xp, "after result: no further contact or reward change")
	# Result from another cause while pending: never resolves behind the result screen.
	b = await _open("female", 1)
	hp = int(b.enemy_hp)
	await _press(b, "battle_attack", 1.0 / 60.0)
	b._finish_battle(true)
	_step(b, 1.0 / 60.0, 30)
	_check(_outcomes(b) == ["cancelled_result"] and b.enemy_hp == hp, "pending at result: cancelled, no orphan damage")
	# Scene exit while pending: the node is freed; nothing outside it applies damage later.
	b = await _open("female", 1)
	hp = int(b.enemy_hp)
	await _press(b, "battle_attack", 1.0 / 60.0)
	var hero_hp := int(app.member_state("hero")["hp"])
	current_scene.queue_free()
	current_scene = null
	for i in 6:
		await process_frame
	_check(int(app.member_state("hero")["hp"]) == hero_hp and not is_instance_valid(b), "scene exit while pending: node freed, no deferred effect (event state is node-local)")


func _repress() -> void:
	var b := await _open("female", 1)
	var hp := int(b.enemy_hp)
	var dt := 1.0 / 60.0
	await _press(b, "battle_attack", dt)
	await _press(b, "battle_attack", dt)
	_check(b.player_attack_count == 1 and int(b.fighters[0]["contact_event_id"]) == 1, "repress before contact: rejected by cooldown, same event")
	_step(b, dt, 12)
	await _press(b, "battle_attack", dt)
	_check(b.player_attack_count == 1, "repress during recovery: rejected")
	# Cooldown 0.43 = 25.8 frames at 60 fps; frame 26 after the request reaches it.
	var frames := 14
	while float(b.fighters[0]["attack_cooldown"]) > 0.0 and frames < 40:
		b._process(dt)
		frames += 1
	await _press(b, "battle_attack", dt)
	_check(b.player_attack_count == 2 and int(b.fighters[0]["contact_event_id"]) == 2 and float(b.fighters[0]["contact_event_clock"]) == 0.0, "repress at cooldown boundary: new monotonic id 2, clock 0")
	_step(b, dt, 10)
	_check(b.enemy_hp == hp - 2 * HERO_DAMAGE and _outcomes(b) == ["hit", "hit"], "two requests, two hits, no duplicate")


func _write_manifest(name: String, mutate: Callable) -> String:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(HALF_MANIFEST))
	data["sheet"] = HALF_SHEET
	mutate.call(data)
	DirAccess.make_dir_recursive_absolute(TMP_DIR)
	var path := TMP_DIR + "/" + name + ".json"
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(data))
	file.close()
	return path


func _ticks(action: Dictionary, rate: Variant, ticks: Array) -> void:
	action["tick_rate"] = rate
	for i in action["frames"].size():
		action["frames"][i].erase("ms")
		action["frames"][i]["ticks"] = ticks[i % ticks.size()]


func _schema() -> void:
	helper.clear_cache()
	var key := "hero:female"
	var base := _write_manifest("base", func(d): pass)
	_check(String(helper.load_set(base, key)["status"]) == "loaded", "schema: unmodified ms manifest still loads")
	var cases := {
		"rate0": [func(d): _ticks(d["actions"]["attack"], 0, [2, 3]), "invalid_tick_rate"],
		"rate1001": [func(d): _ticks(d["actions"]["attack"], 1001, [2, 3]), "invalid_tick_rate"],
		"ratefrac": [func(d): _ticks(d["actions"]["attack"], 29.5, [2, 3]), "invalid_tick_rate"],
		"ratebool": [func(d): _ticks(d["actions"]["attack"], true, [2, 3]), "invalid_tick_rate"],
		"ratestr": [func(d): _ticks(d["actions"]["attack"], "30", [2, 3]), "invalid_tick_rate"],
		"ticks0": [func(d): _ticks(d["actions"]["attack"], 30, [0, 3]), "invalid_frame"],
		"ticksfrac": [func(d): _ticks(d["actions"]["attack"], 30, [2.5, 3]), "invalid_frame"],
		"both": [func(d): (func(): _ticks(d["actions"]["attack"], 30, [2, 3]); d["actions"]["attack"]["frames"][0]["ms"] = 66).call(), "invalid_frame"],
		"msonly": [func(d): d["actions"]["attack"]["tick_rate"] = 30, "invalid_frame"],
		"tickswithoutrate": [func(d): d["actions"]["attack"]["frames"][0]["ticks"] = 2, "invalid_frame"],
		"mixedframes": [func(d): (func(): _ticks(d["actions"]["attack"], 30, [2, 3]); d["actions"]["attack"]["frames"][1].erase("ticks"); d["actions"]["attack"]["frames"][1]["ms"] = 100).call(), "invalid_frame"],
		"loopstartnonloop": [func(d): d["actions"]["attack"]["loop_start"] = 0, "invalid_loop_start"],
		"loopstartrange": [func(d): d["actions"]["idle"]["loop_start"] = d["actions"]["idle"]["frames"].size(), "invalid_loop_start"],
		"loopstartneg": [func(d): d["actions"]["idle"]["loop_start"] = -1, "invalid_loop_start"],
		"loopstartfrac": [func(d): d["actions"]["idle"]["loop_start"] = 0.5, "invalid_loop_start"],
	}
	for name in cases:
		var path := _write_manifest(name, cases[name][0])
		var status := String(helper.load_set(path, key)["status"])
		_check(status == cases[name][1], "schema reject %s -> %s (got %s)" % [name, cases[name][1], status])
	# Valid tick timing: exact rational ends, no millisecond rounding.
	var good := _write_manifest("ticks30", func(d): _ticks(d["actions"]["attack"], 30, [2, 3]))
	var loaded: Dictionary = helper.load_set(good, key)
	_check(String(loaded["status"]) == "loaded", "schema: tick_rate 30 attack loads")
	if String(loaded["status"]) == "loaded":
		var attack: Dictionary = loaded["actions"]["attack"]
		var ends := []
		var cum := 0
		var exact := true
		for i in attack["frames"].size():
			cum += [2, 3][i % 2]
			exact = exact and float(attack["frames"][i]["end"]) == float(cum) / 30.0
		_check(exact and int(attack["duration_ticks"]) == cum, "tick ends are exactly cumulative_ticks/30 (not rounded ms)")
		_check(helper.frame_at(attack, 5.0 / 30.0 - 0.001) == 1 and helper.frame_at(attack, 5.0 / 30.0) == 2, "frame_at: 5/30 - 1 ms is frame 1, exactly 5/30 is frame 2 (shared contact boundary)")
	# loop_start: intro once, then loop from that index.
	var looped := _write_manifest("loopstart", func(d): d["actions"]["idle"]["loop_start"] = 2)
	var ls: Dictionary = helper.load_set(looped, key)
	_check(String(ls["status"]) == "loaded", "schema: idle loop_start 2 loads")
	if String(ls["status"]) == "loaded":
		var idle: Dictionary = ls["actions"]["idle"]
		var n: int = idle["frames"].size()
		var start_t := float(idle["frames"][1]["end"])
		var dur := float(idle["duration"])
		_check(helper.frame_at(idle, 0.0) == 0 and helper.frame_at(idle, dur - 0.001) == n - 1, "loop_start: intro frame 0 plays first")
		_check(helper.frame_at(idle, dur) == 2 and helper.frame_at(idle, dur + (dur - start_t)) == 2 and helper.frame_at(idle, dur + (dur - start_t) - 0.001) == n - 1, "loop_start: wraps to frame 2, never back to the intro")
	var plain: Dictionary = helper.load_set(base, key)
	_check(not plain["actions"]["idle"].has("loop_start") and not plain["actions"]["attack"].has("tick_rate"), "schema: legacy ms action carries no new keys")
