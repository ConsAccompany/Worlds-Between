extends SceneTree

# Bounded deterministic checks for the OPTIONAL heroine timing pilot's one-shot facing latch.
# Synthetic/manifest fixtures only; no art approval or default adoption is implied. The loader is loaded from
# --loader=res://... so the same checks can be run against a preserved pre-fix copy and the fixed source.
const DEFAULT_LOADER := "res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd"
const INDEX := "res://tests/fixtures/csp-fixture-v01_03f4172a/rpg-2-star-ocean-the-second_combat-set_fixture-index_not-art-v01_20261018-153656-03f4172a.json"
const KEYS: Array[String] = ["hero:female", "hero:female", "liang-xu"]
# Independent timing oracle from the hero:female manifest (ms): dodge 270, hit 240, skill 450, attack 390, defeat 360.
const DODGE_END := 0.270
const HIT_END := 0.240
const SKILL_END := 0.450
const ATTACK_END := 0.390

var loader_path := DEFAULT_LOADER
var tmp_dir := ""
var checks := 0
var failures := 0


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--loader="):
			loader_path = argument.trim_prefix("--loader=")
		if argument.begins_with("--tmp-dir="):
			tmp_dir = argument.trim_prefix("--tmp-dir=")
	if tmp_dir.is_empty():
		tmp_dir = ProjectSettings.globalize_path("res://").path_join("../outputs/facing-latch-tests")
	var script: GDScript = load(loader_path)
	if script == null:
		print("FACING_TEST FAIL loader_unloadable=%s" % loader_path)
		quit(1)
		return
	_test_dodge_both_facings(script)
	_test_hit_skill_interruption(script)
	_test_defeat_hold(script)
	_test_same_x(script)
	_test_ending_boundaries(script)
	_test_per_fighter_isolation(script)
	_test_shared_time(script)
	_test_legacy_compatibility(script)
	_test_attack_path_and_preemption(script)
	_test_malformed_and_empty(script)
	if failures == 0:
		print("FACING_TEST PASS checks=%d loader=%s" % [checks, loader_path])
		quit(0)
	else:
		print("FACING_TEST FAIL checks=%d failures=%d loader=%s" % [checks, failures, loader_path])
		quit(1)


# ---------------------------------------------------------------- fixture helpers

func _new_sets(script: GDScript):
	var sets = script.new()
	sets.configure(INDEX, KEYS)
	return sets


func _fighter(x: float, visual: String = "", elapsed: float = 0.0, dodge: float = 0.0, active_event: bool = false, event_id: int = 1, event_clock: float = 0.0, event_facing: int = 0, guard: bool = false, moving: bool = false) -> Dictionary:
	return {
		"x": x,
		"visual_action": visual,
		"visual_elapsed": elapsed,
		"dodge_time": dodge,
		"guard": guard,
		"visual_moving": moving,
		"contact_event_id": event_id,
		"contact_event_active": active_event,
		"contact_event_clock": event_clock,
		"contact_event_facing": event_facing,
	}


func _legacy_fighter(x: float, visual: String = "", elapsed: float = 0.0, dodge: float = 0.0, guard: bool = false, moving: bool = false) -> Dictionary:
	return {"x": x, "visual_action": visual, "visual_elapsed": elapsed, "dodge_time": dodge, "guard": guard, "visual_moving": moving}


func _step(sets, index: int, fighter: Dictionary, alive: bool, enemy_x: float, dt: float) -> void:
	fighter["visual_elapsed"] = float(fighter["visual_elapsed"]) + dt
	sets.advance(index, fighter, alive, enemy_x, dt)


func _steps(sets, index: int, fighter: Dictionary, alive: bool, enemy_x: float, dt: float, count: int) -> void:
	for _i in count:
		_step(sets, index, fighter, alive, enemy_x, dt)


func _state(sets, index: int) -> Dictionary:
	return sets.states[index]


func _frame(sets, index: int) -> Dictionary:
	return sets.current_frame(index)


func _expect(condition: bool, label: String) -> void:
	checks += 1
	if condition:
		print("PASS " + label)
	else:
		failures += 1
		print("FAIL " + label)


func _at(value: float, expected: float) -> bool:
	return absf(value - expected) <= 0.000001


# ---------------------------------------------------------------- checks

# A real explicit hero-pilot state: enemy on the right, dodge starts facing right, enemy crosses left during the one-shot.
func _test_dodge_both_facings(script: GDScript) -> void:
	for starts_right in [true, false]:
		var sets = _new_sets(script)
		var x := 100.0 if starts_right else 300.0
		var enemy := 300.0 if starts_right else 100.0
		var initial := 1 if starts_right else -1
		var crossed := -100.0 if starts_right else 500.0
		var fighter := _fighter(x, "dodge", 0.0, DODGE_END)
		_step(sets, 0, fighter, true, enemy, 0.0)
		_expect(String(_state(sets, 0)["action"]) == "dodge" and int(_state(sets, 0)["facing"]) == initial and int(_frame(sets, 0)["facing"]) == initial, "dodge entry facing %d (enemy %s)" % [initial, "right" if starts_right else "left"])
		_steps(sets, 0, fighter, true, crossed, 0.01, 5)
		_expect(String(_state(sets, 0)["action"]) == "dodge" and int(_state(sets, 0)["facing"]) == initial and int(_frame(sets, 0)["facing"]) == initial, "dodge holds facing %d after the enemy crosses to the other side" % initial)
		fighter["dodge_time"] = 0.0
		_step(sets, 0, fighter, true, crossed, 0.01)
		_expect(String(_state(sets, 0)["action"]) == "idle" and int(_state(sets, 0)["facing"]) == -initial and int(_frame(sets, 0)["facing"]) == -initial, "dodge release follows the current enemy (facing %d -> %d)" % [initial, -initial])


func _test_hit_skill_interruption(script: GDScript) -> void:
	var sets = _new_sets(script)
	var fighter := _fighter(100.0, "hit")
	_step(sets, 0, fighter, true, 300.0, 0.0)
	_expect(String(_state(sets, 0)["action"]) == "hit" and int(_state(sets, 0)["facing"]) == 1, "hit entry facing 1")
	_steps(sets, 0, fighter, true, -100.0, 0.01, 5)
	_expect(String(_state(sets, 0)["action"]) == "hit" and int(_state(sets, 0)["facing"]) == 1, "hit holds facing 1 after the enemy crosses")
	# A new skill interrupts the hit (the arena clears the contact event for any non-attack action).
	fighter["visual_action"] = "skill"
	fighter["visual_elapsed"] = 0.0
	fighter["contact_event_active"] = false
	_step(sets, 0, fighter, true, -100.0, 0.0)
	_expect(String(_state(sets, 0)["action"]) == "skill" and int(_state(sets, 0)["facing"]) == -1, "new skill interrupts hit and relatches current enemy facing -1")
	_steps(sets, 0, fighter, true, 500.0, 0.01, 5)
	_expect(String(_state(sets, 0)["action"]) == "skill" and int(_state(sets, 0)["facing"]) == -1, "skill holds facing -1 after a second crossing")


func _test_defeat_hold(script: GDScript) -> void:
	var sets = _new_sets(script)
	var fighter := _fighter(100.0)
	_step(sets, 0, fighter, true, 300.0, 0.0)
	_expect(String(_state(sets, 0)["action"]) == "idle" and int(_state(sets, 0)["facing"]) == 1, "idle entry facing 1")
	_step(sets, 0, fighter, false, 300.0, 0.0)
	_expect(String(_state(sets, 0)["action"]) == "defeat" and int(_state(sets, 0)["facing"]) == 1, "defeat entry facing 1")
	_steps(sets, 0, fighter, false, -100.0, 0.1, 5)
	_expect(String(_state(sets, 0)["action"]) == "defeat" and int(_state(sets, 0)["facing"]) == 1 and int(_frame(sets, 0)["facing"]) == 1, "defeat holds facing 1 for 0.5 s after the enemy crosses")
	# A revive/return to idle is the release boundary; the latch must not stick forever.
	_step(sets, 0, fighter, true, -100.0, 0.0)
	_expect(String(_state(sets, 0)["action"]) == "idle" and int(_state(sets, 0)["facing"]) == -1, "revive to idle follows current enemy facing -1")


func _test_same_x(script: GDScript) -> void:
	for prior in [1, -1]:
		var sets = _new_sets(script)
		var fighter := _fighter(100.0)
		sets.states[0]["facing"] = prior
		_step(sets, 0, fighter, true, 100.0, 0.0)
		_expect(int(_state(sets, 0)["facing"]) == prior, "enemy exactly same x retains previous facing %d while idle" % prior)
	# Same-x during a latch must not relatch or flip either.
	var sets2 = _new_sets(script)
	var dodger := _fighter(100.0, "dodge", 0.0, DODGE_END)
	_step(sets2, 0, dodger, true, 300.0, 0.0)
	dodger["visual_elapsed"] = 0.0
	_step(sets2, 0, dodger, true, 100.0, 0.01)
	_expect(String(_state(sets2, 0)["action"]) == "dodge" and int(_state(sets2, 0)["facing"]) == 1, "enemy exactly same x during dodge keeps the latched facing 1")


func _test_ending_boundaries(script: GDScript) -> void:
	# Hit ends at 0.240 s; cross on the tick that crosses the boundary.
	var sets = _new_sets(script)
	var hit := _fighter(100.0, "hit")
	_step(sets, 0, hit, true, 300.0, 0.0)
	_steps(sets, 0, hit, true, 300.0, 0.01, 23)
	_expect(String(_state(sets, 0)["action"]) == "hit" and _at(float(_state(sets, 0)["clock"]), HIT_END - 0.01), "hit still active at 0.230 s")
	_step(sets, 0, hit, true, -100.0, 0.01)
	_expect(String(_state(sets, 0)["action"]) == "idle" and int(_state(sets, 0)["facing"]) == -1, "hit ending boundary (0.240 s) releases to current enemy facing -1")
	# Skill ends at 0.450 s.
	var sets2 = _new_sets(script)
	var skill := _fighter(100.0, "skill")
	_step(sets2, 0, skill, true, 300.0, 0.0)
	_steps(sets2, 0, skill, true, 300.0, 0.01, 44)
	_step(sets2, 0, skill, true, -100.0, 0.01)
	_expect(String(_state(sets2, 0)["action"]) == "idle" and int(_state(sets2, 0)["facing"]) == -1, "skill ending boundary (0.450 s) releases to current enemy facing -1")
	# Dodge is governed by dodge_time; cross on the tick it reaches zero.
	var sets3 = _new_sets(script)
	var dodge := _fighter(100.0, "dodge", 0.0, DODGE_END)
	_step(sets3, 0, dodge, true, 300.0, 0.0)
	_steps(sets3, 0, dodge, true, 300.0, 0.01, 26)
	dodge["dodge_time"] = 0.0
	_step(sets3, 0, dodge, true, -100.0, 0.01)
	_expect(String(_state(sets3, 0)["action"]) == "idle" and int(_state(sets3, 0)["facing"]) == -1, "dodge ending boundary (dodge_time 0) releases to current enemy facing -1")


func _test_per_fighter_isolation(script: GDScript) -> void:
	var sets = _new_sets(script)
	var left := _fighter(100.0, "dodge", 0.0, DODGE_END)
	var right := _fighter(500.0, "dodge", 0.0, DODGE_END)
	_step(sets, 0, left, true, 300.0, 0.0)
	_step(sets, 1, right, true, 300.0, 0.0)
	_expect(int(_state(sets, 0)["facing"]) == 1 and int(_state(sets, 1)["facing"]) == -1, "two explicit fighters latch opposite facings independently")
	_steps(sets, 0, left, true, 600.0, 0.01, 5)
	_steps(sets, 1, right, true, 600.0, 0.01, 5)
	_expect(int(_state(sets, 0)["facing"]) == 1 and int(_state(sets, 1)["facing"]) == -1, "enemy at 600 latches left fighter 1 and right fighter -1")
	left["dodge_time"] = 0.0
	_step(sets, 0, left, true, 0.0, 0.01)
	var right_clock := float(_state(sets, 1)["clock"])
	_step(sets, 1, right, true, 0.0, 0.01)
	_expect(String(_state(sets, 0)["action"]) == "idle" and int(_state(sets, 0)["facing"]) == -1, "left fighter releases independently to current enemy facing -1")
	_expect(String(_state(sets, 1)["action"]) == "dodge" and int(_state(sets, 1)["facing"]) == -1 and float(_state(sets, 1)["clock"]) > right_clock, "right fighter keeps its own dodge latch and clock")


func _test_shared_time(script: GDScript) -> void:
	var at_60 := _shared_samples(script, 60)
	var at_30 := _shared_samples(script, 30)
	var keys_ok := at_60.size() == 30 and at_30.size() == 30
	for key in at_30:
		if keys_ok and (not at_60.has(key) or at_60[key] != at_30[key]):
			print("DEBUG shared mismatch key=%s 60=%s 30=%s" % [str(key), str(at_60.get(key, [])), str(at_30.get(key, []))])
			keys_ok = false
	_expect(keys_ok, "30 and 60 fps agree on action/facing/frame/mirrored at all 30 shared timestamps")
	var last60: Array = at_60.get(30, [])
	var last30: Array = at_30.get(30, [])
	_expect(last60.size() > 1 and last30.size() > 1 and int(last60[1]) == 1 and int(last30[1]) == 1, "shared-time dodge after an enemy crossing still faces right at t=1.0 s")


func _shared_samples(script: GDScript, fps: int) -> Dictionary:
	var sets = _new_sets(script)
	var fighter := _fighter(100.0, "dodge", 0.0, DODGE_END)
	var samples := {}
	var per_sample: int = int(fps / 30)
	# Prime the action entry so both clock rates start their timed ticks from clock 0 at the same wall time.
	sets.advance(0, fighter, true, 300.0, 0.0)
	for tick in fps:
		var t := float(tick + 1) / float(fps)
		var enemy := 300.0 if t < 0.15 else -100.0
		sets.advance(0, fighter, true, enemy, 1.0 / float(fps))
		if (tick + 1) % per_sample == 0:
			var frame := _frame(sets, 0)
			samples[int((tick + 1) / per_sample)] = [String(_state(sets, 0)["action"]), int(_state(sets, 0)["facing"]), int(frame.get("frame", -1)), bool(frame.get("mirrored", false))]
	return samples


func _test_legacy_compatibility(script: GDScript) -> void:
	var sets = _new_sets(script)
	var explicit := _fighter(100.0)
	var legacy := _legacy_fighter(100.0)
	var mismatches := 0
	for _i in 10:
		_step(sets, 0, explicit, true, 300.0, 0.01)
		_step(sets, 1, legacy, true, 300.0, 0.01)
		mismatches += 0 if _same_playback(sets, 0, 1) else 1
	explicit["dodge_time"] = 0.2
	legacy["dodge_time"] = 0.2
	for _i in 5:
		_step(sets, 0, explicit, true, 300.0, 0.01)
		_step(sets, 1, legacy, true, 300.0, 0.01)
		mismatches += 0 if _same_playback(sets, 0, 1) else 1
	explicit["dodge_time"] = 0.0
	legacy["dodge_time"] = 0.0
	explicit["visual_action"] = "hit"
	legacy["visual_action"] = "hit"
	explicit["visual_elapsed"] = 0.0
	legacy["visual_elapsed"] = 0.0
	for _i in 10:
		_step(sets, 0, explicit, true, 300.0, 0.01)
		_step(sets, 1, legacy, true, 300.0, 0.01)
		mismatches += 0 if _same_playback(sets, 0, 1) else 1
	explicit["visual_action"] = "skill"
	legacy["visual_action"] = "skill"
	explicit["visual_elapsed"] = 0.0
	legacy["visual_elapsed"] = 0.0
	for _i in 10:
		_step(sets, 0, explicit, true, 300.0, 0.01)
		_step(sets, 1, legacy, true, 300.0, 0.01)
		mismatches += 0 if _same_playback(sets, 0, 1) else 1
	for _i in 10:
		_step(sets, 0, explicit, false, 300.0, 0.01)
		_step(sets, 1, legacy, false, 300.0, 0.01)
		mismatches += 0 if _same_playback(sets, 0, 1) else 1
	_expect(mismatches == 0, "explicit fighter without a cross has byte-identical state/render to the same-set legacy fighter at all 45 common ticks")


func _same_playback(sets, a: int, b: int) -> bool:
	# last_event_id is explicit-pilot bookkeeping only; compare every observable playback field and the rendered frame.
	var left: Dictionary = sets.states[a].duplicate()
	var right: Dictionary = sets.states[b].duplicate()
	left.erase("last_event_id")
	right.erase("last_event_id")
	return JSON.stringify(left) == JSON.stringify(right) and JSON.stringify(sets.current_frame(a)) == JSON.stringify(sets.current_frame(b))


func _test_attack_path_and_preemption(script: GDScript) -> void:
	var sets = _new_sets(script)
	var attacker := _fighter(100.0, "attack", 0.0, 0.0, true, 7, 0.0, 1)
	_step(sets, 0, attacker, true, 300.0, 0.0)
	_expect(String(_state(sets, 0)["action"]) == "attack" and _at(float(_state(sets, 0)["clock"]), 0.0) and int(_state(sets, 0)["facing"]) == 1, "explicit attack entry uses event clock 0 and contact facing 1")
	for _i in 5:
		attacker["contact_event_clock"] = float(attacker["contact_event_clock"]) + 0.01
		_step(sets, 0, attacker, true, -100.0, 0.01)
	_expect(String(_state(sets, 0)["action"]) == "attack" and _at(float(_state(sets, 0)["clock"]), 0.05) and int(_state(sets, 0)["facing"]) == 1, "explicit attack keeps event clock/facing after enemy crosses")
	attacker["dodge_time"] = DODGE_END
	_step(sets, 0, attacker, true, -100.0, 0.0)
	_expect(String(_state(sets, 0)["action"]) == "dodge" and int(_state(sets, 0)["facing"]) == -1, "new dodge preempts explicit attack and relatches current enemy facing -1")
	# Skill/hit use the arena's interruption: contact_event_active becomes false for a non-attack action.
	for action in ["skill", "hit"]:
		var sets2 = _new_sets(script)
		var fighter := _fighter(100.0, "attack", 0.0, 0.0, true, 7, 0.0, 1)
		_step(sets2, 0, fighter, true, 300.0, 0.0)
		fighter["contact_event_active"] = false
		fighter["visual_action"] = action
		fighter["visual_elapsed"] = 0.0
		_step(sets2, 0, fighter, true, -100.0, 0.0)
		_expect(String(_state(sets2, 0)["action"]) == action and int(_state(sets2, 0)["facing"]) == -1, "new %s preempts explicit attack and relatches current enemy facing -1" % action)


func _test_malformed_and_empty(script: GDScript) -> void:
	var missing = script.new()
	var one: Array[String] = ["hero:female"]
	missing.configure("res://tests/fixtures/no-such-facing-index.json", one)
	_expect(missing.index_status == "missing_manifest" and missing.loaded_count() == 0 and not missing.has_set(0) and missing.current_frame(0).is_empty(), "missing index falls back with no set and no frame")
	var fighter := _fighter(100.0)
	missing.advance(0, fighter, true, 300.0, 0.1)
	_expect(String(fighter["visual_action"]) == "" and float(fighter["x"]) == 100.0, "advance on a missing set is a no-op and never writes the fighter")
	var empty_index := _write_tmp("empty-index.json", {"schema": "worlds-between.combat-sprite-set-index/1", "sets": {}})
	var empty_set = script.new()
	empty_set.configure(empty_index, one)
	_expect(empty_index != "" and empty_set.index_status == "loaded" and empty_set.loaded_count() == 0 and not empty_set.has_set(0), "empty index sets fall back per fighter")
	var bad_manifest_name := "bad-manifest.json"
	_write_tmp(bad_manifest_name, {"schema": "worlds-between.combat-sprite-set/9"})
	var bad_index := _write_tmp("bad-index.json", {"schema": "worlds-between.combat-sprite-set-index/1", "sets": {"hero:female": bad_manifest_name}})
	var malformed = script.new()
	malformed.configure(bad_index, one)
	_expect(bad_index != "" and malformed.index_status == "loaded" and malformed.set_status(0) == "unknown_schema" and not malformed.has_set(0), "malformed manifest rejects atomically with set_status unknown_schema")
	var no_keys = script.new()
	var empty_keys: Array[String] = []
	no_keys.configure(INDEX, empty_keys)
	_expect(no_keys.index_status == "loaded" and no_keys.loaded_count() == 0, "empty key list loads nothing without errors")


func _write_tmp(name: String, data: Variant) -> String:
	if tmp_dir.is_empty():
		return ""
	DirAccess.make_dir_recursive_absolute(tmp_dir)
	if not DirAccess.dir_exists_absolute(tmp_dir):
		return ""
	var path := tmp_dir.path_join(name)
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		return ""
	file.store_string(JSON.stringify(data))
	file.close()
	return path
