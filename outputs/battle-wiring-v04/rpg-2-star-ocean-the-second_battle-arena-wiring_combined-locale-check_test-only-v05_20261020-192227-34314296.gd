extends SceneTree

# content.scene.battle-arena.wiring: source-bound wiring checks for the normal
# exploration -> battle -> result -> return path, arena bounds/contact ranges, pause/result
# callbacks and the pre-battle/after-battle saves. Test-only; no game source is modified.
#
# v04 reconciliation: copied from the preserved v03 fixture and rebound to commit 39f252e. The
# natural-victory loop is unchanged in method: a fresh normal-entry victory arena, the hero
# positioned ONCE (declared setup, inside the real 61 px attack range), then the real battle
# _process advanced at 1/60 with the real 0.43 s cooldown, real enemy wind-up/AI and real damage.
# _try_attack is called only when that cooldown is naturally ready. No enemy_hp/hero_hp/
# battle_finished/battle_won/reward/timer injection; no per-hit position change and no cooldown
# reset. The boundary-only fixture and the defeat-only fixture are separate labeled instances and
# are never counted as natural victory. The v04 additions are: raw+LF source-hash binding to
# 39f252e, explicit category tags, and an actually executed defeat case.
#
# Run windowed with fresh, physically created APPDATA/LOCALAPPDATA/TEMP under the task worktree:
#   Godot --windowed --path game --resolution 640x360 -s <this> -- --report=<json> --captures=<dir> --log=<raw.log> --base=<commit> --self=<this> --uuid=<uuid>
const ARENA_PATH := "res://scenes/battle_arena.tscn"
const EXPLORE_PATH := "res://scenes/scifi_exploration_area.tscn"
const MAIN_PATH := "res://scenes/main_menu.tscn"
const EXPECTED_COMMIT := "39f252e57c6e67f40e35757aaa5471448ef46522"
# Raw SHA-256 of the Git-clean working-tree bytes in this 39f252e checkout. No game edit is made.
const EXPECTED_SOURCE_RAW := {
	"res://scripts/battle_arena.gd": "41548c86eb04fb12a988c211373601f7c08d579b408d4951aa6d0f03302cb197",
	"res://scripts/scifi_exploration_area.gd": "13f89322c328598fcaeac94536182aef2e936bbf33a61a1bf89f741f9806b4b3",
	"res://scripts/app_state.gd": "e3a162ef3d70aafbb97f4a668b69813dc8aed3e327ee6a87b398aba29fdbc33f",
	"res://scripts/save_store.gd": "88c2d71d1f9faa0c7a840b2098a146808e0a1ef6d1f7315f2951a00eacdd7a0a",
	"res://scripts/battle_rules.gd": "e95400251485fce27d496c0a100ec9fe1a1f2e2430bb5f9c6899497370a3263c",
	"res://scenes/battle_arena.tscn": "dfd2ed1ce9642a4519926e3aa45dae5bd2b6bad11dfa0f3152d5cf80de9d4310",
	"res://scenes/scifi_exploration_area.tscn": "b3be08cde8a8d9c4fa0edaa49c3ef30965291691d1b3c30184776ec3553b8ae8",
}
# Declared normalization for text-source evidence: CRLF -> LF, then UTF-8 SHA-256.
const EXPECTED_SOURCE_LF := {
	"res://scripts/battle_arena.gd": "41548c86eb04fb12a988c211373601f7c08d579b408d4951aa6d0f03302cb197",
	"res://scripts/scifi_exploration_area.gd": "13f89322c328598fcaeac94536182aef2e936bbf33a61a1bf89f741f9806b4b3",
	"res://scripts/app_state.gd": "60f3622f1dfcaa554861391b552442636a7870c7d250de4c4122da9245c4f2ee",
	"res://scripts/save_store.gd": "0980b722686e05a227bee8c71bfe6a04ee71c84826937a552b0248e5ebeff6d1",
	"res://scripts/battle_rules.gd": "98d0ed2e9b723859cdd42782f57e222c66e2b61b3f9772fa2cd72f44c09cca7b",
	"res://scenes/battle_arena.tscn": "a41247599f910aabd35bfd8e4015a2ff3e4ab22dafe19a73b11044ba3743e322",
	"res://scenes/scifi_exploration_area.tscn": "b60cf71490b5aacb0163c3336cefefac7b7ed16de6940924f875d23499a5cdc7",
}
var Arena: GDScript

var app: Node
var checks: Array[Dictionary] = []
var captures: Array[Dictionary] = []
var fail_count := 0
var capture_dir := ""
var stamp := ""
var run_id := ""
var run_uuid := ""
var check_category := "setup"
var log_path := ""
var base_commit := ""
var test_source := ""


func _initialize() -> void:
	call_deferred("_run")
	create_timer(180.0).timeout.connect(_watchdog)


func _watchdog() -> void:
	print("BATTLE_WIRING_WATCHDOG")
	quit(2)


func ck(label: String, passed: bool, detail: Variant = null) -> void:
	checks.append({"check": label, "passed": passed, "detail": detail, "category": check_category})
	print("BATTLE_WIRING ", "PASS " if passed else "FAIL ", label, "" if detail == null else " " + str(detail))
	if not passed:
		fail_count += 1


func category_summary() -> Dictionary:
	var summary := {}
	for row in checks:
		var category := String(row.get("category", ""))
		var counts: Dictionary = summary.get(category, {"passed": 0, "total": 0, "failed": 0})
		counts["total"] = int(counts["total"]) + 1
		if bool(row["passed"]):
			counts["passed"] = int(counts["passed"]) + 1
		else:
			counts["failed"] = int(counts["failed"]) + 1
		summary[category] = counts
	return summary


func key(code: Key, pressed: bool) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.physical_keycode = code
	event.pressed = pressed
	Input.parse_input_event(event)


func pause_event() -> InputEventAction:
	var event := InputEventAction.new()
	event.action = "battle_pause"
	event.pressed = true
	return event


func set_language(code: String) -> void:
	app.language = code
	app.language_changed.emit()


func clear_scene() -> void:
	if current_scene != null:
		current_scene.queue_free()
		current_scene = null
		await process_frame
	await process_frame


func open_explore(destination_id: String, language: String) -> Node:
	await clear_scene()
	app.begin_new_run()
	app.select_destination(destination_id)
	app.language = language
	var err := change_scene_to_file(EXPLORE_PATH)
	await process_frame
	await process_frame
	await process_frame
	ck("normal scene entry: %s %s loads exploration" % [destination_id, language], err == OK and current_scene != null and current_scene.scene_file_path == EXPLORE_PATH)
	return current_scene


func capture(tag: String, node: Node = null) -> void:
	if node != null and node.has_method("queue_redraw"):
		node.queue_redraw()
	await process_frame
	await process_frame
	var image := root.get_viewport().get_texture().get_image()
	var ok := image.get_size() == Vector2i(640, 360)
	var file := "rpg-2-star-ocean-the-second_battle-arena-wiring_%s_640x360_test-only-v04_%s-%s.png" % [tag, stamp, run_id]
	var path := capture_dir.path_join(file)
	var err := image.save_png(path)
	ck("capture %s is a saved 640x360 windowed image" % tag, ok and err == OK and DisplayServer.get_name() != "headless", {"size": [image.get_width(), image.get_height()], "err": err, "file": file, "display": DisplayServer.get_name()})
	captures.append({"tag": tag, "file": file, "sha256": FileAccess.get_sha256(path), "size": "640x360", "display": DisplayServer.get_name()})


func v2(value: Vector2) -> Array:
	return [value.x, value.y]


func auto_notes(note: String) -> Array:
	return SaveStore.list_entries().filter(func(entry): return String(entry.get("snapshot", {}).get("note", "")) == note)


func enter_battle(scene: Node, enemy_id: String) -> Node:
	Arena.battle_backdrop_override = 0
	Arena.combat_sprite_set_override = 0
	Arena.sentry_v2_override = 0
	# Keep the newer opt-in patrol presentation pilot off so the default combat path is tested.
	Arena.patrol_animation_override = 0
	Arena.patrol_animation_package_override = ""
	var enemy_position: Vector2 = scene.enemy_position
	# 44 px: inside the encounter-save suppression radius? No, >43 so the safe position updates.
	scene.hero.position = enemy_position + Vector2(44, 0)
	Input.action_press("move_left")
	scene._process(0.0)
	Input.action_release("move_left")
	var safe: Vector2 = scene.safe_position
	ck("%s: safe position records the >43 px retreat point" % enemy_id, safe == enemy_position + Vector2(44, 0), v2(safe))
	# Exactly 23 px: the source uses < 23, so this is still exploration and the safe point is retained.
	scene.hero.position = enemy_position + Vector2(23, 0)
	Input.action_press("move_left")
	scene._process(0.0)
	Input.action_release("move_left")
	ck("%s: exactly 23 px does not open an encounter" % enemy_id, current_scene == scene and app.battle_enemy_id == "", {"scene": scene != null, "enemy": app.battle_enemy_id})
	ck("%s: safe position is retained inside 43 px" % enemy_id, scene.safe_position == safe, v2(scene.safe_position))
	# 22.999 px: < 23 through the same input/_process path.
	scene.hero.position = enemy_position + Vector2(22.999, 0)
	Input.action_press("move_left")
	scene._process(0.0)
	Input.action_release("move_left")
	ck("%s: <23 px starts the intended encounter with the pre-battle save position" % enemy_id, app.battle_enemy_id == enemy_id and app.battle_return_position == safe, {"enemy": app.battle_enemy_id, "return": v2(app.battle_return_position), "safe": v2(safe)})
	await process_frame
	await process_frame
	await process_frame
	var battle := current_scene
	ck("%s: normal scene change reaches the real battle arena" % enemy_id, battle != null and battle.scene_file_path == ARENA_PATH and battle.enemy_id == enemy_id, {"scene": battle.scene_file_path if battle != null else ""})
	if battle != null:
		# Deterministic harness stepping only: disable automatic engine ticks, then call the real
		# _process explicitly. This is not a cooldown/AI/HP/timer injection.
		battle.process_mode = Node.PROCESS_MODE_DISABLED
	var before := auto_notes("before_battle").filter(func(entry): return String(entry.get("snapshot", {}).get("destination", "")) == app.current_destination_id and entry.get("snapshot", {}).get("position", []) == [safe.x, safe.y] and entry.get("snapshot", {}).get("enemyCleared", true) == false)
	ck("%s: pre-battle autosave exists at the safe point and enemy is not cleared" % enemy_id,
		before.size() >= 1 and before[0]["snapshot"]["position"] == [safe.x, safe.y] and before[0]["snapshot"]["enemyCleared"] == false,
		{"count": before.size(), "id": before[0]["id"], "position": before[0]["snapshot"]["position"], "enemyCleared": before[0]["snapshot"]["enemyCleared"], "destination": before[0]["snapshot"]["destination"]} if before.size() >= 1 else 0)
	return battle


func test_bounds_and_ranges(battle: Node, enemy_id: String) -> void:
	# BOUNDARY-ONLY FIXTURE. This instance is discarded before the fresh normal-entry victory arena
	# is created. It sets enemy_hp=64 for both enemies solely to exercise the 19-damage hit/miss and
	# 61/69 px contact predicates; it also freezes the enemy cooldown and sets explicit x/cooldown
	# values for those boundary probes. None of this setup reaches the victory arena, and this
	# instance is never used to claim a victory, reward or save.
	ck("%s: boundary-only fixture is a separate arena from the victory arena" % enemy_id,
		battle != null and battle.enemy_id == enemy_id)
	ck("%s: protected combat constants unchanged" % enemy_id,
		Arena.MOVE_SPEED == 168.0 and Arena.DODGE_COST == 12 and Arena.GUARD_HIT_COST == 6
		and Arena.ENEMIES["patrol"]["max_hp"] == 64 and Arena.ENEMIES["patrol"]["damage"] == 12
		and Arena.ENEMIES["sentry"]["max_hp"] == 96 and Arena.ENEMIES["sentry"]["damage"] == 18,
		{"move": Arena.MOVE_SPEED, "dodge": Arena.DODGE_COST, "guard": Arena.GUARD_HIT_COST, "patrolHp": Arena.ENEMIES["patrol"]["max_hp"], "patrolDamage": Arena.ENEMIES["patrol"]["damage"], "sentryHp": Arena.ENEMIES["sentry"]["max_hp"], "sentryDamage": Arena.ENEMIES["sentry"]["damage"]})
	var fighter: Dictionary = battle.fighters[0]
	battle.controlled_index = 0
	battle.auto_mode = false
	battle.enemy_cooldown = 999.0
	battle.enemy_windup = 0.0
	fighter["dodge_time"] = 0.0
	# Left/right movement clamp through the real _process and keyboard actions.
	fighter["x"] = 28.5
	Input.action_press("move_left")
	battle._process(0.5)
	Input.action_release("move_left")
	ck("%s: left movement clamps at x=28" % enemy_id, is_equal_approx(float(fighter["x"]), 28.0), fighter["x"])
	fighter["x"] = 611.5
	Input.action_press("move_right")
	battle._process(0.5)
	Input.action_release("move_right")
	ck("%s: right movement clamps at x=612" % enemy_id, is_equal_approx(float(fighter["x"]), 612.0), fighter["x"])
	# Dodge also clamps through the same branch.
	battle.enemy_x = 493.0
	fighter["x"] = 28.5
	fighter["dodge_cooldown"] = 0.0
	fighter["dodge_time"] = 0.0
	app.member_state("hero")["energy"] = 60
	Input.action_press("move_left")
	var dodged: bool = battle._try_dodge()
	battle._process(0.5)
	Input.action_release("move_left")
	ck("%s: dodge movement stays inside left clamp" % enemy_id, dodged and is_equal_approx(float(fighter["x"]), 28.0), fighter["x"])
	# Player contact/attack range: the source hits at exactly attack_range and misses just outside.
	var reach := float(AppState.MEMBER_DEFS["hero"]["attack_range"])
	# Boundary fixture injection only: 64 HP -> 45 after one 19-damage hit. Not a victory arena.
	battle.enemy_hp = 64
	fighter["x"] = battle.enemy_x - reach
	fighter["attack_cooldown"] = 0.0
	var hit_inside: bool = battle._try_attack()
	ck("%s: hero attack hits at exactly %.1f px" % [enemy_id, reach], hit_inside and battle.enemy_hp == 45, battle.enemy_hp)
	fighter["x"] = battle.enemy_x - reach - 0.001
	fighter["attack_cooldown"] = 0.0
	battle.enemy_hp = 64
	var hit_outside: bool = battle._try_attack()
	ck("%s: hero attack misses just outside %.1f px and reports battle_far" % [enemy_id, reach], not hit_outside and battle.enemy_hp == 64 and battle.feedback_key == "battle_far", {"hp": battle.enemy_hp, "feedback": battle.feedback_key})
	# Enemy contact range: the hit applies at exactly 69 px and not at 69.001 px.
	var hp_before := int(app.member_state("hero")["hp"])
	fighter["x"] = battle.enemy_x - 69.0
	fighter["dodge_time"] = 0.0
	fighter["guard"] = false
	battle.enemy_target_index = 0
	battle._apply_enemy_hit()
	var hp_at := int(app.member_state("hero")["hp"])
	fighter["x"] = battle.enemy_x - 69.001
	fighter["dodge_time"] = 0.0
	fighter["guard"] = false
	battle._apply_enemy_hit()
	var hp_out := int(app.member_state("hero")["hp"])
	var contact_damage := int(Arena.ENEMIES[enemy_id]["damage"])
	ck("%s: enemy contact hits at exactly 69 px" % enemy_id, hp_at == hp_before - contact_damage, {"before": hp_before, "after": hp_at, "damage": contact_damage})
	ck("%s: enemy contact misses just outside 69 px" % enemy_id, hp_out == hp_at, {"at": hp_at, "outside": hp_out})
	# Pause callback: real _input Action event, overlay, frozen simulation, toggle back.
	var pause := pause_event()
	battle._input(pause)
	ck("%s: battle_pause _input opens the pause overlay" % enemy_id, battle.paused and battle.pause_overlay.visible)
	var x_paused := float(fighter["x"])
	battle._process(0.5)
	ck("%s: paused _process does not move the fighter" % enemy_id, is_equal_approx(float(fighter["x"]), x_paused))
	set_language("en")
	ck("%s: pause Resume text is English" % enemy_id, battle.pause_resume_button.text == "Resume battle", battle.pause_resume_button.text)
	set_language("zh")
	ck("%s: pause Resume text is Chinese" % enemy_id, battle.pause_resume_button.text == "继续战斗", battle.pause_resume_button.text)
	set_language("en")
	battle._input(pause)
	ck("%s: second battle_pause _input resumes and hides the overlay" % enemy_id, not battle.paused and not battle.pause_overlay.visible)


func capture_battle_backdrops(battle: Node, enemy_id: String, expected_on_status: String) -> void:
	Arena.battle_backdrop_override = 0
	battle._load_battle_backdrop()
	ck("%s: normal backdrop selector off keeps the geometric backdrop" % enemy_id, battle.battle_backdrop_status == "off" and battle.battle_backdrop_texture == null, battle.battle_backdrop_status)
	set_language("en")
	battle._refresh_text()
	await capture("%s-battle-backdrop-off-en" % enemy_id, battle)
	set_language("zh")
	battle._refresh_text()
	await capture("%s-battle-backdrop-off-zh" % enemy_id, battle)
	Arena.battle_backdrop_override = 1
	battle._load_battle_backdrop()
	ck("%s: normal backdrop selector on reports the expected arena status (%s)" % [enemy_id, expected_on_status], battle.battle_backdrop_status == expected_on_status, {"status": battle.battle_backdrop_status, "arena": battle.battle_backdrop_arena_id})
	set_language("en")
	battle._refresh_text()
	await capture("%s-battle-backdrop-on-en" % enemy_id, battle)
	set_language("zh")
	battle._refresh_text()
	await capture("%s-battle-backdrop-on-zh" % enemy_id, battle)
	Arena.battle_backdrop_override = 0
	battle._load_battle_backdrop()
	set_language("en")
	battle._refresh_text()


func finish_victory(battle: Node, enemy_id: String, case_lang: String, expected_hp: int, expected_hits: int, expected_xp: int, expected_jp: int) -> Dictionary:
	var xp_before := int(app.hero_state["xp"])
	var jp_before := int(app.hero_state["jp"])
	var level_before := int(app.hero_state["level"])
	var max_before := int(app.hero_state["max_hp"])
	var hp_start := int(app.hero_state["hp"])
	ck("%s: FRESH normal-entry victory arena starts at real max HP %d (not boundary 64)" % [enemy_id, expected_hp],
		battle.enemy_hp == expected_hp and battle.enemy_hp == int(Arena.ENEMIES[enemy_id]["max_hp"]),
		{"hp": battle.enemy_hp, "expected": expected_hp, "maxHp": Arena.ENEMIES[enemy_id]["max_hp"]})
	ck("%s: victory uses the real hero damage 19" % enemy_id,
		int(AppState.MEMBER_DEFS["hero"]["attack_damage"]) == 19, AppState.MEMBER_DEFS["hero"]["attack_damage"])
	ck("%s: victory arena starts unfinished and unwon (no outcome pre-set)" % enemy_id,
		not battle.battle_finished and not battle.battle_won and battle.enemy_hp > 0,
		{"finished": battle.battle_finished, "won": battle.battle_won, "hp": battle.enemy_hp})
	var after_ids_before := auto_notes("after_battle").map(func(entry): return String(entry["id"]))
	var fighter: Dictionary = battle.fighters[0]
	var reach := float(AppState.MEMBER_DEFS["hero"]["attack_range"])
	# ONE-TIME SETUP (declared): the hero is placed once, inside the real attack range. The victory
	# loop never changes this position again; enemy movement/AI remains live.
	var setup_x: float = float(battle.enemy_x) - 30.0
	fighter["x"] = setup_x
	ck("%s: ONE-TIME SETUP places the hero once at %.1f px from the enemy (within %.1f px reach)" % [enemy_id, 30.0, reach],
		is_equal_approx(float(fighter["x"]), setup_x) and absf(battle.enemy_x - float(fighter["x"])) <= reach,
		{"heroX": fighter["x"], "enemyX": battle.enemy_x, "reach": reach})
	# Advance the real battle _process at a fixed 1/60 step. Real cooldowns, wind-up, enemy AI and
	# attack movement run; only _try_attack is called by the harness, and only when naturally ready.
	var attacks := 0
	var steps := 0
	var hp_trace: Array = []
	var hit_steps: Array = []
	var hero_hp_at_attack: Array = []
	var cooldowns_at_hit: Array = []
	var positions_at_hit: Array = []
	var min_gap := 1 << 30
	var hp_before_final := -1
	while not battle.battle_finished and steps < 1200:
		battle._process(1.0 / 60.0)
		steps += 1
		if battle.battle_finished:
			break
		if float(fighter["attack_cooldown"]) == 0.0 and absf(battle.enemy_x - float(fighter["x"])) <= reach:
			var hp_pre_hit := int(battle.enemy_hp)
			var hero_hp_pre_hit := int(app.hero_state["hp"])
			cooldowns_at_hit.append(float(fighter["attack_cooldown"]))
			positions_at_hit.append(float(fighter["x"]))
			var hit: bool = battle._try_attack()
			if hit:
				attacks += 1
				var hp_post_hit := int(battle.enemy_hp)
				hp_trace.append([hit, hp_pre_hit, hp_post_hit])
				hero_hp_at_attack.append(hero_hp_pre_hit)
				if hit_steps.size() > 0:
					min_gap = mini(min_gap, steps - int(hit_steps[hit_steps.size() - 1]))
				hit_steps.append(steps)
				if hp_post_hit == 0:
					hp_before_final = hero_hp_pre_hit
	ck("%s: 1200-step guard was not exhausted and victory came from the real process" % enemy_id,
		steps < 1200 and battle.battle_finished and battle.battle_won and battle.enemy_hp == 0,
		{"steps": steps, "finished": battle.battle_finished, "won": battle.battle_won, "hp": battle.enemy_hp})
	ck("%s: natural 1/60 stepping takes exactly %d real _try_attack hits from %d HP" % [enemy_id, expected_hits, expected_hp],
		battle.battle_finished and battle.battle_won and battle.enemy_hp == 0 and attacks == expected_hits and hit_steps.size() == expected_hits,
		{"attacks": attacks, "expectedAttacks": expected_hits, "steps": steps, "hitSteps": hit_steps, "trace": hp_trace})
	var damage_exact := true
	for row in hp_trace:
		var hit: bool = row[0]
		var before_hp: int = row[1]
		var after_hp: int = row[2]
		if not hit or after_hp != maxi(0, before_hp - 19):
			damage_exact = false
	ck("%s: every victory hit is a real 19-damage attack (no HP/finished injection)" % enemy_id, damage_exact, hp_trace)
	var cooldowns_ready := true
	for value in cooldowns_at_hit:
		if float(value) != 0.0:
			cooldowns_ready = false
	ck("%s: every harness attack saw a naturally zero cooldown (no timer reset)" % enemy_id,
		cooldowns_ready and cooldowns_at_hit.size() == expected_hits,
		{"cooldownsAtHit": cooldowns_at_hit})
	var positions_unchanged := true
	for value in positions_at_hit:
		if not is_equal_approx(float(value), setup_x):
			positions_unchanged = false
	ck("%s: every harness attack used the same single setup x (no per-hit teleport)" % enemy_id,
		positions_unchanged and positions_at_hit.size() == expected_hits,
		{"setupX": setup_x, "positionsAtHit": positions_at_hit})
	ck("%s: attacks were gated by the real 0.43 s cooldown, not a forced timer" % enemy_id,
		expected_hits > 1 and min_gap >= 26,
		{"minGapSteps": min_gap, "minGapSeconds": min_gap / 60.0, "hitSteps": hit_steps})
	ck("%s: the real attack counter matches exactly %d player attacks" % [enemy_id, expected_hits],
		int(battle.player_attack_count) == expected_hits, battle.player_attack_count)
	ck("%s: hero stayed at the single declared setup position (no per-hit teleport)" % enemy_id,
		is_equal_approx(float(fighter["x"]), setup_x),
		{"setupX": setup_x, "finalX": fighter["x"]})
	ck("%s: normal enemy AI damaged the hero before the final hit (real HP, no injection)" % enemy_id,
		battle.enemy_attack_count >= 1 and hp_before_final >= 0 and hp_before_final < hp_start,
		{"enemyAttacks": battle.enemy_attack_count, "hpStart": hp_start, "hpBeforeFinal": hp_before_final, "heroHpAtAttack": hero_hp_at_attack})
	var enemy_attacks := int(battle.enemy_attack_count)
	var levels_rolled := 0
	for level in range(level_before, int(app.hero_state["level"])):
		levels_rolled += GrowthRules.xp_to_next(level)
	var xp_awarded := int(app.hero_state["xp"]) - xp_before + levels_rolled
	var jp_awarded := int(app.hero_state["jp"]) - jp_before
	ck("%s: victory applies the expected one-time reward (%d xp / %d jp)" % [enemy_id, expected_xp, expected_jp],
		xp_awarded == expected_xp and jp_awarded == expected_jp,
		{"xpAwarded": xp_awarded, "jpAwarded": jp_awarded, "levelBefore": level_before, "levelAfter": app.hero_state["level"], "xpRemainder": app.hero_state["xp"]})
	ck("%s: victory sets the return contract and machine observation" % enemy_id,
		app.enemy_cleared_for_return and app.returning_from_battle and app.machine_observed)
	var level_after := int(app.hero_state["level"])
	var max_after := int(app.hero_state["max_hp"])
	var hp_after := int(app.hero_state["hp"])
	var recovery_expected := max_after if level_after != level_before else mini(max_after, hp_before_final + ceili(float(max_before) * 0.20))
	ck("%s: real post-victory recovery matches the bounded 20%% contract from HP immediately before the final hit" % enemy_id,
		hp_before_final >= 0 and hp_after == recovery_expected and hp_after >= hp_before_final and hp_after <= max_after,
		{"hpBeforeFinal": hp_before_final, "after": hp_after, "maxBefore": max_before, "maxAfter": max_after, "expected": recovery_expected, "levelBefore": level_before, "levelAfter": level_after})
	var all_after := auto_notes("after_battle")
	var new_after := all_after.filter(func(entry): return not after_ids_before.has(String(entry["id"])))
	ck("%s: victory writes exactly one new after-battle autosave" % enemy_id,
		new_after.size() == 1, {"newIds": new_after.map(func(entry): return String(entry["id"])), "total": all_after.size()})
	var dest_after := new_after.filter(func(entry): return String(entry.get("snapshot", {}).get("destination", "")) == app.current_destination_id and entry.get("snapshot", {}).get("position", []) == [app.battle_return_position.x, app.battle_return_position.y] and entry.get("snapshot", {}).get("enemyCleared", false) == true)
	ck("%s: the new after-battle save is destination/position filtered and enemy-cleared" % enemy_id,
		dest_after.size() == 1,
		{"filtered": dest_after.size(), "destination": app.current_destination_id, "position": v2(app.battle_return_position)})
	var save_id := String(dest_after[0]["id"]) if dest_after.size() == 1 else ""
	ck("%s: reload target is the destination-filtered after_battle record, not auto_notes()[0]" % enemy_id,
		save_id != "" and save_id == String(dest_after[0]["id"]),
		{"saveId": save_id, "allFirstId": String(all_after[0]["id"]) if all_after.size() > 0 else ""})
	var rewards_xp := int(app.hero_state["xp"])
	var rewards_jp := int(app.hero_state["jp"])
	var after_total := auto_notes("after_battle").size()
	battle._finish_battle(true)
	ck("%s: repeated finish callback is idempotent (no second reward or save)" % enemy_id,
		int(app.hero_state["xp"]) == rewards_xp and int(app.hero_state["jp"]) == rewards_jp and auto_notes("after_battle").size() == after_total)
	set_language("en")
	battle._refresh_text()
	ck("%s: result Continue text is English" % enemy_id, battle.result_title.text == "Victory" and battle.result_button.text == "Keep exploring", [battle.result_title.text, battle.result_button.text])
	await capture("%s-%s-result-en" % [enemy_id, case_lang], battle)
	set_language("zh")
	battle._refresh_text()
	ck("%s: result Continue text is Chinese" % enemy_id, battle.result_title.text == "战斗胜利" and battle.result_button.text == "继续探索", [battle.result_title.text, battle.result_button.text])
	await capture("%s-%s-result-zh" % [enemy_id, case_lang], battle)
	set_language("en")
	battle._refresh_text()
	# The real button signal is the result click callback; verify the binding, then emit it.
	ck("%s: result button is bound to the real _return_after_result callback" % enemy_id,
		battle.result_button.pressed.is_connected(Callable(battle, "_return_after_result")))
	battle.result_button.pressed.emit()
	await process_frame
	await process_frame
	await process_frame
	var explore := current_scene
	ck("%s: result click returns to the normal exploration scene" % enemy_id, explore != null and explore.scene_file_path == EXPLORE_PATH and explore.destination_id == app.current_destination_id, explore.scene_file_path if explore != null else "")
	ck("%s: return spawn equals the saved battle return position" % enemy_id, explore != null and explore.hero.position == app.battle_return_position, {"hero": v2(explore.hero.position) if explore != null else null, "return": v2(app.battle_return_position)})
	ck("%s: return clears transient battle state and hides the defeated enemy" % enemy_id,
		app.battle_enemy_id == "" and not app.returning_from_battle and app.enemy_cleared_for_return and not explore.enemy_visible,
		{"enemy": app.battle_enemy_id, "returning": app.returning_from_battle, "cleared": app.enemy_cleared_for_return, "visible": explore.enemy_visible})
	await capture("%s-%s-return-en" % [enemy_id, case_lang], explore)
	set_language("zh")
	await capture("%s-%s-return-zh" % [enemy_id, case_lang], explore)
	set_language("en")
	# Save/reload: inspect the exact destination-filtered after-battle entry, never global auto_notes()[0].
	var entry := SaveStore.read_entry(save_id)
	ck("%s: saved snapshot is an area checkpoint with enemyCleared and the return position" % enemy_id,
		not entry.is_empty() and entry["snapshot"]["scene"] == "area" and entry["snapshot"]["destination"] == app.current_destination_id
		and entry["snapshot"]["enemyCleared"] == true and entry["snapshot"]["position"] == [app.battle_return_position.x, app.battle_return_position.y],
		{"id": save_id, "scene": entry.get("snapshot", {}).get("scene"), "position": entry.get("snapshot", {}).get("position")})
	ck("%s: load_save restores the checkpoint and resume position" % enemy_id,
		app.load_save(save_id) and app.resume_area_pending and app.loaded_scene_kind == "area" and app.resume_area_position == app.battle_return_position
		and app.enemy_cleared_for_return and app.battle_enemy_id == "" and not app.returning_from_battle,
		{"resumePending": app.resume_area_pending, "kind": app.loaded_scene_kind, "position": v2(app.resume_area_position)})
	var reload_err := change_scene_to_file(EXPLORE_PATH)
	await process_frame
	await process_frame
	await process_frame
	var reloaded := current_scene
	ck("%s: reloaded checkpoint spawns at the saved position and keeps the enemy cleared" % enemy_id,
		reload_err == OK and reloaded != null and reloaded.scene_file_path == EXPLORE_PATH and reloaded.hero.position == app.battle_return_position and not reloaded.enemy_visible and not app.resume_area_pending,
		{"position": v2(reloaded.hero.position) if reloaded != null else null, "visible": reloaded.enemy_visible if reloaded != null else null})
	await capture("%s-%s-save-reload-en" % [enemy_id, case_lang], reloaded)
	return {"category": "victory", "attacks": attacks, "expectedHits": expected_hits, "steps": steps, "minGapSteps": min_gap, "hitSteps": hit_steps, "hpTrace": hp_trace, "cooldownsAtHit": cooldowns_at_hit, "setupX": setup_x, "positionsAtHit": positions_at_hit, "hpBeforeFinal": hp_before_final, "startHp": expected_hp, "enemyAttacks": enemy_attacks, "save": save_id, "return": [app.battle_return_position.x, app.battle_return_position.y]}


# DEFEAT-ONLY FIXTURE, explicitly labeled and actually executed in v04. It uses real enemy contact
# against a separate normal-entry arena, positions the hero once (defeat setup only), and never
# injects HP or rewards. It is never part of a natural-victory/reward/save claim and its checks are
# tagged category=defeat.
func finish_failure(battle: Node, enemy_id: String) -> Dictionary:
	var xp_before := int(app.hero_state["xp"])
	var jp_before := int(app.hero_state["jp"])
	var after_before := auto_notes("after_battle").size()
	var fighter: Dictionary = battle.fighters[0]
	battle.enemy_cooldown = 0.0
	battle.enemy_target_index = 0
	var setup_x: float = float(battle.enemy_x) - 30.0
	fighter["x"] = setup_x
	fighter["dodge_time"] = 0.0
	fighter["guard"] = false
	ck("%s: DEFEAT-ONLY setup starts at real max HP %d and one declared contact position" % [enemy_id, int(Arena.ENEMIES[enemy_id]["max_hp"])],
		battle.enemy_hp == int(Arena.ENEMIES[enemy_id]["max_hp"]) and is_equal_approx(float(fighter["x"]), setup_x) and absf(battle.enemy_x - setup_x) <= 69.0,
		{"enemyHp": battle.enemy_hp, "setupX": setup_x})
	var hits := 0
	while not battle.battle_finished and hits < 20:
		battle._apply_enemy_hit()
		hits += 1
	var enemy_attacks := int(battle.enemy_attack_count)
	ck("%s: DEFEAT-ONLY repeated real enemy contact defeats the party without injected HP" % enemy_id, battle.battle_finished and not battle.battle_won, {"hits": hits, "hp": app.hero_state["hp"], "enemyAttacks": enemy_attacks})
	ck("%s: DEFEAT-ONLY leaves the single contact position unchanged" % enemy_id,
		is_equal_approx(float(fighter["x"]), setup_x), {"setupX": setup_x, "finalX": fighter["x"]})
	ck("%s: DEFEAT-ONLY grants no reward and no cleared-return state" % enemy_id,
		int(app.hero_state["xp"]) == xp_before and int(app.hero_state["jp"]) == jp_before and not app.enemy_cleared_for_return and not app.returning_from_battle)
	ck("%s: DEFEAT-ONLY does not write an after-battle save" % enemy_id, auto_notes("after_battle").size() == after_before)
	set_language("en")
	battle._refresh_text()
	ck("%s: DEFEAT-ONLY result text/button are English" % enemy_id, battle.result_title.text == "Defeat" and battle.result_button.text == "Main menu", [battle.result_title.text, battle.result_button.text])
	await capture("%s-defeat-result-en" % enemy_id, battle)
	set_language("zh")
	battle._refresh_text()
	ck("%s: DEFEAT-ONLY result text/button are Chinese" % enemy_id, battle.result_title.text == "战斗失败" and battle.result_button.text == "返回主菜单", [battle.result_title.text, battle.result_button.text])
	await capture("%s-defeat-result-zh" % enemy_id, battle)
	set_language("en")
	ck("%s: DEFEAT-ONLY result button is bound to the real _return_after_result callback" % enemy_id,
		battle.result_button.pressed.is_connected(Callable(battle, "_return_after_result")))
	battle.result_button.pressed.emit()
	await process_frame
	await process_frame
	await process_frame
	ck("%s: DEFEAT-ONLY result click returns to the main menu" % enemy_id, current_scene != null and current_scene.scene_file_path == MAIN_PATH, current_scene.scene_file_path if current_scene != null else "")
	ck("%s: DEFEAT-ONLY return clears the pending enemy id and keeps the enemy uncleared" % enemy_id, app.battle_enemy_id == "" and not app.enemy_cleared_for_return and not app.returning_from_battle)
	return {"category": "defeat", "hits": hits, "enemyAttacks": enemy_attacks, "hp": app.hero_state["hp"]}


func sha_text(path: String) -> String:
	var text := FileAccess.get_file_as_string(path)
	return text.replace("\r\n", "\n").sha256_text()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	for argument in args:
		if argument.begins_with("--report="):
			pass
		elif argument.begins_with("--captures="):
			capture_dir = argument.trim_prefix("--captures=")
		elif argument.begins_with("--log="):
			log_path = argument.trim_prefix("--log=")
		elif argument.begins_with("--base="):
			base_commit = argument.trim_prefix("--base=")
		elif argument.begins_with("--self="):
			test_source = argument.trim_prefix("--self=")
		elif argument.begins_with("--uuid="):
			run_uuid = argument.trim_prefix("--uuid=")
	stamp = Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	if run_uuid == "":
		run_uuid = "%08x" % (randi() & 0xffffffff)
	run_id = run_uuid.substr(0, 8)
	if capture_dir == "":
		capture_dir = ProjectSettings.globalize_path("res://../outputs/battle-wiring-v04/captures")
	DirAccess.make_dir_recursive_absolute(capture_dir)
	root.size = Vector2i(640, 360)
	app = root.get_node("AppState")
	Arena = load("res://scripts/battle_arena.gd")
	SaveStore.root_path = "user://battle-wiring-v04/saves"
	ck("windowed renderer is active (not headless)", DisplayServer.get_name() != "headless", DisplayServer.get_name())
	ck("fresh isolated v04 profile under this task worktree",
		OS.get_environment("APPDATA").replace("\\", "/").to_lower().contains("battle-wiring-v04")
		and OS.get_user_data_dir().replace("\\", "/").to_lower().begins_with(OS.get_environment("APPDATA").replace("\\", "/").to_lower()),
		OS.get_user_data_dir())
	ck("test save store is isolated from the normal game saves", SaveStore.root_path == "user://battle-wiring-v04/saves", SaveStore.root_path)
	# Static backdrop selector contract before any battle loads.
	Arena.battle_backdrop_override = -1
	ck("backdrop selector default is off without the CLI flag", not Arena.battle_backdrop_enabled())
	ck("backdrop destination mapping is patrol=outskirts, sentry=ruins, city=city-terrace",
		Arena.battle_backdrop_arena("scifi.outskirts") == "outskirts" and Arena.battle_backdrop_arena("scifi.ruins") == "ruins" and Arena.battle_backdrop_arena("scifi.city") == "city-terrace")
	ck("only the outskirts tracked band exists; ruins/city intentionally fall back",
		Arena.BATTLE_BACKDROP_BANDS.has("outskirts") and not Arena.BATTLE_BACKDROP_BANDS.has("ruins") and not Arena.BATTLE_BACKDROP_BANDS.has("city-terrace"))

	# Four independent destination/language natural-victory cases. Each has a boundary-only arena
	# followed by a FRESH normal-entry victory arena; the boundary instance is never reused for
	# victory. Category tags keep boundary and defeat checks out of the natural-victory counts.
	var cases := [
		{"dest": "scifi.outskirts", "enemy": "patrol", "lang": "en", "hp": 64, "hits": 4, "xp": 26, "jp": 12, "title": "Yonkers outskirts"},
		{"dest": "scifi.outskirts", "enemy": "patrol", "lang": "zh", "hp": 64, "hits": 4, "xp": 26, "jp": 12, "title": "扬克斯郊外"},
		{"dest": "scifi.ruins", "enemy": "sentry", "lang": "en", "hp": 96, "hits": 6, "xp": 44, "jp": 20, "title": "Washington, D.C. ruins · U.S. Capitol"},
		{"dest": "scifi.ruins", "enemy": "sentry", "lang": "zh", "hp": 96, "hits": 6, "xp": 44, "jp": 20, "title": "华盛顿特区废墟 · 国会大厦"},
	]
	for spec in cases:
		var dest := String(spec["dest"])
		var enemy_id := String(spec["enemy"])
		var lang := String(spec["lang"])
		check_category = "boundary"
		var boundary_explore := await open_explore(dest, lang)
		ck("%s %s exploration title is localized" % [enemy_id, lang], boundary_explore.title_label.text == String(spec["title"]), boundary_explore.title_label.text)
		var boundary := await enter_battle(boundary_explore, enemy_id)
		if boundary != null:
			test_bounds_and_ranges(boundary, enemy_id)
		# Fresh normal-entry victory arena: no boundary mutation or injected HP carries over.
		check_category = "victory"
		var victory_explore := await open_explore(dest, lang)
		var victory := await enter_battle(victory_explore, enemy_id)
		if victory != null:
			await capture("%s-%s-victory-start" % [enemy_id, lang], victory)
			var result = await finish_victory(victory, enemy_id, lang, int(spec["hp"]), int(spec["hits"]), int(spec["xp"]), int(spec["jp"]))
			print("BATTLE_WIRING_CASE ", enemy_id, " ", lang, " ", JSON.stringify(result))

	# DEFEAT-ONLY case: explicitly labeled, actually executed, and never counted as natural
	# victory. It uses a separate normal-entry arena and real enemy contact (no HP injection).
	check_category = "defeat"
	var defeat_explore := await open_explore("scifi.outskirts", "en")
	var defeat := await enter_battle(defeat_explore, "patrol")
	var defeat_result: Dictionary = {}
	if defeat != null:
		await capture("patrol-defeat-start", defeat)
		defeat_result = await finish_failure(defeat, "patrol")
		print("BATTLE_WIRING_DEFEAT_CASE patrol en ", JSON.stringify(defeat_result))
	else:
		ck("DEFEAT-ONLY normal-entry patrol arena loaded", false)

	check_category = "source"
	ck("base commit is the declared 39f252e checkout", base_commit == EXPECTED_COMMIT, {"base": base_commit, "expected": EXPECTED_COMMIT})
	var sources_lf := {
		"res://scripts/battle_arena.gd": sha_text("res://scripts/battle_arena.gd"),
		"res://scripts/scifi_exploration_area.gd": sha_text("res://scripts/scifi_exploration_area.gd"),
		"res://scripts/app_state.gd": sha_text("res://scripts/app_state.gd"),
		"res://scripts/save_store.gd": sha_text("res://scripts/save_store.gd"),
		"res://scripts/battle_rules.gd": sha_text("res://scripts/battle_rules.gd"),
		"res://scenes/battle_arena.tscn": sha_text("res://scenes/battle_arena.tscn"),
		"res://scenes/scifi_exploration_area.tscn": sha_text("res://scenes/scifi_exploration_area.tscn"),
	}
	var sources_raw := {
		"res://scripts/battle_arena.gd": FileAccess.get_sha256("res://scripts/battle_arena.gd"),
		"res://scripts/scifi_exploration_area.gd": FileAccess.get_sha256("res://scripts/scifi_exploration_area.gd"),
		"res://scripts/app_state.gd": FileAccess.get_sha256("res://scripts/app_state.gd"),
		"res://scripts/save_store.gd": FileAccess.get_sha256("res://scripts/save_store.gd"),
		"res://scripts/battle_rules.gd": FileAccess.get_sha256("res://scripts/battle_rules.gd"),
		"res://scenes/battle_arena.tscn": FileAccess.get_sha256("res://scenes/battle_arena.tscn"),
		"res://scenes/scifi_exploration_area.tscn": FileAccess.get_sha256("res://scenes/scifi_exploration_area.tscn"),
	}
	for path in EXPECTED_SOURCE_RAW.keys():
		ck("raw source hash binds %s to 39f252e" % path, String(sources_raw.get(path, "")) == String(EXPECTED_SOURCE_RAW[path]), {"actual": sources_raw.get(path, ""), "expected": EXPECTED_SOURCE_RAW[path]})
	for path in EXPECTED_SOURCE_LF.keys():
		ck("LF-normalized text hash binds %s to 39f252e" % path, String(sources_lf.get(path, "")) == String(EXPECTED_SOURCE_LF[path]), {"actual": sources_lf.get(path, ""), "expected": EXPECTED_SOURCE_LF[path]})
	if test_source != "":
		sources_lf[test_source] = sha_text(test_source)
		sources_raw[test_source] = FileAccess.get_sha256(test_source)
	var report_path := ""
	for argument in args:
		if argument.begins_with("--report="):
			report_path = argument.trim_prefix("--report=")
	if report_path == "":
		report_path = capture_dir.path_join("rpg-2-star-ocean-the-second_battle-arena-wiring_natural-victory-report_test-only-v04_%s-%s.json" % [stamp, run_id])
	var report := {
		"task": "content.scene.battle-arena.wiring",
		"variant": "natural-victory-v04",
		"runUuid": run_uuid,
		"runId": run_id,
		"timestampUtc": stamp,
		"testedCommit": EXPECTED_COMMIT,
		"baseCommit": base_commit,
		"checkout": ProjectSettings.globalize_path("res://"),
		"engine": "Godot 4.7.2.stable.official.ed1daf0bf",
		"runMode": "windowed",
		"resolution": "640x360",
		"languages": ["en", "zh"],
		"areas": {"scifi.outskirts": "patrol", "scifi.ruins": "sentry"},
		"passed": checks.size() - fail_count,
		"total": checks.size(),
		"failed": fail_count,
		"categorySummary": category_summary(),
		"naturalVictory": {"cases": cases.size(), "countedAsVictory": true, "expectedHits": {"patrol": 4, "sentry": 6}, "expectedHp": {"patrol": 64, "sentry": 96}},
		"defeat": {"label": "DEFEAT-ONLY", "countedAsVictory": false, "executed": not defeat_result.is_empty(), "result": defeat_result},
		"checks": checks,
		"captures": captures,
		"sourceHashesSha256RawV1": sources_raw,
		"sourceHashesSha256TextLfV1": sources_lf,
		"sourceHashNormalization": "Raw SHA-256 is over the exact Git-clean working-tree bytes; TextLfV1 replaces CRLF with LF before UTF-8 SHA-256. No game edit was made.",
		"protectedStats": {"MOVE_SPEED": Arena.MOVE_SPEED, "DODGE_COST": Arena.DODGE_COST, "GUARD_HIT_COST": Arena.GUARD_HIT_COST, "patrol": {"max_hp": Arena.ENEMIES["patrol"]["max_hp"], "damage": Arena.ENEMIES["patrol"]["damage"], "speed": Arena.ENEMIES["patrol"]["speed"], "windup": Arena.ENEMIES["patrol"]["windup"], "cooldown": Arena.ENEMIES["patrol"]["cooldown"]}, "sentry": {"max_hp": Arena.ENEMIES["sentry"]["max_hp"], "damage": Arena.ENEMIES["sentry"]["damage"], "speed": Arena.ENEMIES["sentry"]["speed"], "windup": Arena.ENEMIES["sentry"]["windup"], "cooldown": Arena.ENEMIES["sentry"]["cooldown"]}, "heroAttackDamage": int(AppState.MEMBER_DEFS["hero"]["attack_damage"]), "heroAttackRange": float(AppState.MEMBER_DEFS["hero"]["attack_range"]), "playerClamp": [28.0, 612.0], "enemyContactPx": 69.0},
		"v03ToV04": "Copied the preserved v03 fixture, rebound it to 39f252e raw+LF source hashes, added category tags, added naturally-zero-cooldown and constant-position evidence, verified the result signal binding, and executed the previously-unused defeat function as a labeled DEFEAT-ONLY case. The natural-victory method is unchanged.",
		"boundaryFixture": "Boundary-only arena instance per destination/language; enemy_hp=64 is set only to test 19 damage at 61/69 px. It retains its clearly labeled cooldown/position setup and is discarded before the victory arena is created and never used for a victory/reward/save claim.",
		"victoryFixture": "Fresh normal-entry arena per destination/language; enemy starts at real max HP (patrol 64, sentry 96), real hero damage 19, exactly 4/6 real _try_attack hits. Hero is positioned once before the loop (declared setup). No enemy_hp/hero_hp/battle_finished/battle_won/reward/timer injection, no cooldown reset, no per-hit position change. The real _process runs at 1/60 with live enemy AI; recovery uses HP immediately before the final hit.",
		"defeatFixture": "Separate normal-entry patrol arena, labeled DEFEAT-ONLY. One declared contact position, real enemy damage, no HP injection. Its checks are category=defeat and are never counted as natural victory.",
		"afterBattleReload": "Reload target is the new destination-filtered after_battle record (destination, return position, enemyCleared=true), never global auto_notes()[0].",
		"saveIsolation": SaveStore.root_path,
		"rawLog": log_path,
		"knownEnvironmentDiagnostic": "Godot 4.7.2 may emit 'ERROR: Failed to read the root certificate store.' in some harness sandboxes. This package never filters it: if it appears, the original checked runner fails the run and the result is BLOCKED. Canonical Codex direct Godot runs are expected clean; the producer did not repeat the model-side sandbox run.",
		"limitations": [
			"Automated technical checks only; not a human playthrough or creator acceptance.",
			"Producer did not execute Godot; the coordinator runner is the only execution path and the evidence is pending until it runs.",
			"Boundary-only fixtures inject 64 HP and a frozen enemy cooldown by design and are excluded from victory claims.",
			"DEFEAT-ONLY is a labeled test setup, not a natural victory and not a second win case.",
			"The victory loop positions the hero once (declared setup), then advances the real _process at 1/60; it does not reset cooldowns or reposition per hit.",
			"The opt-in patrol presentation pilot, backdrop selector, combat sprite set and encounter feedback pilot are kept off.",
		],
	}
	var report_file := FileAccess.open(report_path, FileAccess.WRITE)
	report_file.store_string(JSON.stringify(report, "  ") + "\n")
	report_file.close()
	print("REPORT ", report_path)
	print("BATTLE_WIRING_RESULT ", checks.size() - fail_count, "/", checks.size(), " captures=", captures.size())
	if fail_count == 0:
		print("BATTLE_WIRING_OK")
	else:
		print("BATTLE_WIRING_FAILED ", fail_count)
	quit(0 if fail_count == 0 else 1)
