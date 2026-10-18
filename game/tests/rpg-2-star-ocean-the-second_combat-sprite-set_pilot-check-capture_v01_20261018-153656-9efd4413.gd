extends SceneTree

# Targeted check and captures for the OPT-IN combat sprite set pilot (code.runtime.combat-sprite-pipeline, TECHNICAL only).
# The sets it loads are SYNTHETIC DIAGNOSTIC fixtures (not art): they prove loader and playback behaviour (identity, frame
# source and pivot, timing, loop vs one-shot, facing, fallback), not smooth motion or character design. Fighter art stays 0/52.
# Run windowed (not --headless) with a fresh APPDATA so no settings file exists. Options after `--`:
#   --capture-dir=<absolute dir>   output dir (default <repo>/outputs/combat-set-pilot-v01_<stamp>-<id>)
#   --baseline-only                flag-off captures + 600-step traces only, using API that exists at the base commit too;
#                                  run it in an isolated base-commit tree to make the parity baseline
#   --baseline-dir=<absolute dir>  compare this run's flag-off captures and traces with that baseline
#   --no-capture                   logic checks only
const BATTLE_SCENE_PATH := "res://scenes/battle_arena.tscn"
const BATTLE_SCRIPT_PATH := "res://scripts/battle_arena.gd"
const HELPER_PATH := "res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd"
const FIXTURE_DIR := "res://tests/fixtures/csp-fixture-v01_03f4172a"
const INDEX_PATH := FIXTURE_DIR + "/rpg-2-star-ocean-the-second_combat-set_fixture-index_not-art-v01_20261018-153656-03f4172a.json"
const CHECK_SCRIPT := "game/tests/rpg-2-star-ocean-the-second_combat-sprite-set_pilot-check-capture_v01_20261018-153656-9efd4413.gd"
const PREFIX := "rpg-2-star-ocean-the-second_combat-set-pilot"
const CLI_FLAG := "--combat-sprite-set-pilot"
const FLOOR_Y := 272
const WINDOW := Vector2i(640, 360)
const MAGENTA := 0xff00ffff
const PARTY := ["hero", "liang-xu", "zhao-ling", "ji-cheng"]
const KEYS := ["hero:male", "liang-xu", "zhao-ling", "ji-cheng"]
# Flag-off combinations that must render exactly as at the base commit.
const OFF_COMBOS := [
	{"key": "off-patrol", "enemy": "patrol", "sentry": 0, "backdrop": 0},
	{"key": "off-sentry-noflag", "enemy": "sentry", "sentry": 0, "backdrop": 0},
	{"key": "off-sentry", "enemy": "sentry", "sentry": 1, "backdrop": 0},
	{"key": "off-backdrop", "enemy": "patrol", "sentry": 0, "backdrop": 1},
	{"key": "off-sentry-backdrop", "enemy": "sentry", "sentry": 1, "backdrop": 1},
]
const SIM_COMBOS := [
	{"key": "sentry-plain", "enemy": "sentry", "sentry": 0, "backdrop": 0},
	{"key": "sentry-v2-backdrop", "enemy": "sentry", "sentry": 1, "backdrop": 1},
	{"key": "patrol-plain", "enemy": "patrol", "sentry": 0, "backdrop": 0},
]

var app: Node
var battle_script: GDScript
var helper_script: GDScript
var stamp := ""
var run_id := ""
var capture_dir := ""
var baseline_dir := ""
var capture_enabled := true
var pass_count := 0
var report := {}
var records: Array = []
var manifests := {}


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	app = root.get_node("AppState")
	battle_script = load(BATTLE_SCRIPT_PATH)
	SaveStore.root_path = "user://test-saves/combat-set-pilot"
	var args := OS.get_cmdline_user_args()
	capture_enabled = not args.has("--no-capture") and DisplayServer.get_name() != "headless"
	stamp = Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	run_id = "%08x" % (randi() & 0xffffffff)
	for argument in args:
		if argument.begins_with("--capture-dir="):
			capture_dir = argument.trim_prefix("--capture-dir=")
		if argument.begins_with("--baseline-dir="):
			baseline_dir = argument.trim_prefix("--baseline-dir=")
	if capture_dir.is_empty():
		capture_dir = ProjectSettings.globalize_path("res://../outputs/combat-set-pilot-v01_%s-%s" % [stamp, run_id])
	if not _check(not args.has(CLI_FLAG), "runs without %s (it sets combat_sprite_set_override itself)" % CLI_FLAG):
		return
	if not _check(app.settings.load_status == "missing" and app.language == "zh", "fresh profile: no settings file (load_status missing), default language zh"):
		return
	if capture_enabled:
		DirAccess.make_dir_recursive_absolute(capture_dir)
		root.size = WINDOW
		for i in 4:
			await process_frame
	if args.has("--baseline-only"):
		if await _baseline_only():
			print("COMBAT_SET_PILOT BASELINE PASS checks=%d" % pass_count)
			quit(0)
		return
	helper_script = load(HELPER_PATH)
	helper_script.clear_cache()
	if not await _check_default_off() or not await _check_loader() or not await _check_fallbacks() or not await _check_timing():
		return
	if not _check_pivots() or not await _check_state_selection() or not await _check_parity() or not await _check_off_renders():
		return
	if not await _run_captures():
		return
	if not _write_manifest():
		return
	battle_script.combat_sprite_set_override = -1
	print("COMBAT_SET_PILOT PASS checks=%d captures=%d" % [pass_count, records.size()])
	quit(0)


# ---------------------------------------------------------------- setup helpers

func _prepare_party(destination: String, appearance: String = "male") -> void:
	app.begin_new_run()
	app.hero_appearance = appearance
	app.recruit_member("liang-xu")
	app.recruit_member("zhao-ling")
	app.ji_records_checked = true
	app.recruit_member("ji-cheng")
	app.select_destination(destination)


# Ji guards (cautious) and Zhao uses her skill (aggressive), so real auto combat exercises guard and skill too.
func _set_policies() -> void:
	app.member_state("ji-cheng")["ai_policy"] = "cautious"
	app.member_state("zhao-ling")["ai_policy"] = "aggressive"


func _set_flags(combo: Dictionary, pilot: int) -> void:
	battle_script.sentry_v2_override = int(combo.get("sentry", 0))
	battle_script.battle_backdrop_override = int(combo.get("backdrop", 0))
	if pilot >= 0:
		battle_script.combat_sprite_set_override = pilot


func _open_battle(enemy_id: String, settings: Dictionary = {}) -> Node2D:
	if current_scene != null:
		current_scene.queue_free()
		current_scene = null
		await process_frame
	app.begin_battle(enemy_id, Vector2(330, 215))
	var battle: Node2D = load(BATTLE_SCENE_PATH).instantiate()
	for key in settings:
		battle.set(key, settings[key])
	root.add_child(battle)
	current_scene = battle
	await process_frame
	await process_frame
	return battle


func _place(battle: Node2D, xs: Array, enemy_x: float) -> void:
	for index in battle.fighters.size():
		battle.fighters[index]["x"] = float(xs[index])
	battle.enemy_x = enemy_x


# Rendering-only stepping (no combat step): the fighter visual clocks and, when present, the pilot playback.
func _step_visuals(battle: Node2D, seconds: float, moving: Array = [], dt: float = 1.0 / 60.0) -> void:
	var t := 0.0
	while t < seconds - 0.0001:
		var initial: Array[float] = []
		for index in battle.fighters.size():
			initial.append(float(battle.fighters[index]["x"]) - (1.0 if moving.has(index) else 0.0))
		battle._advance_fighter_visuals(dt, initial)
		if battle.has_method("_advance_combat_sprite_sets"):
			battle._advance_combat_sprite_sets(dt)
		t += dt


# A fixed mix through the real combat functions: hero attack, Liang guard, Zhao skill, Ji takes a hit; 0.2 s of visuals.
func _drive_action_mix(battle: Node2D) -> void:
	_place(battle, [150, 230, 310, 390], 450.0)
	battle._try_attack(0)
	battle.fighters[1]["guard"] = true
	battle._use_skill(2)
	battle.enemy_target_index = 3
	battle._apply_enemy_hit()
	_step_visuals(battle, 0.2)


# Hero right of the enemy (faces left) mid-dodge, Liang down and holding, Zhao walking, Ji right of the enemy idle (faces left).
func _drive_dodge_defeat(battle: Node2D) -> void:
	_place(battle, [430, 120, 210, 540], 330.0)
	app.member_state("liang-xu")["hp"] = 0
	battle._set_fighter_visual_action(battle.fighters[1], "down")
	_step_visuals(battle, 0.3, [2])
	battle._try_dodge(0)
	_step_visuals(battle, 0.12, [2])


func _snapshot_without_clock() -> String:
	var snapshot: Dictionary = app.make_snapshot("area", Vector2(330, 215), "parity")
	snapshot.erase("playTimeSeconds")
	for event in snapshot["playtestEvents"]:
		event.erase("atSeconds")
	return JSON.stringify(snapshot)


func _manifest(key: String) -> Dictionary:
	if manifests.is_empty():
		var index: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(INDEX_PATH))
		for set_key in index["sets"]:
			manifests[set_key] = JSON.parse_string(FileAccess.get_file_as_string(index["sets"][set_key]))
	return manifests[key]


# Independent timing oracle straight from the manifest JSON (not the helper's frame_at).
func _oracle_frame(key: String, action: String, clock: float) -> int:
	var data: Dictionary = _manifest(key)["actions"].get(action, _manifest(key)["actions"]["attack"])
	var total := 0
	for frame in data["frames"]:
		total += int(frame["ms"])
	var ms := clock * 1000.0
	if bool(data["loop"]):
		ms = fposmod(ms + 0.001, float(total)) - 0.001
	var end := 0
	for index in data["frames"].size():
		end += int(data["frames"][index]["ms"])
		if ms + 0.001 < end:
			return index
	return data["frames"].size() - 1


# ---------------------------------------------------------------- checks

func _check_default_off() -> bool:
	var constants: Dictionary = battle_script.get_script_constant_map()
	if not _check(battle_script.combat_sprite_set_override == -1 and not battle_script.combat_sprite_set_enabled(), "pilot off by default (override -1, no %s)" % CLI_FLAG):
		return false
	if not _check(constants.get("COMBAT_SPRITE_SET_ART_APPROVED") == false and constants.get("COMBAT_SPRITE_SET_INDEX") == INDEX_PATH, "COMBAT_SPRITE_SET_ART_APPROVED = false; default index is the synthetic fixture index"):
		return false
	for combo in OFF_COMBOS:
		_prepare_party("scifi.outskirts")
		_set_flags(combo, -1)
		var battle: Node2D = await _open_battle(combo["enemy"], {"paused": true})
		if not _check(battle.combat_sprite_sets == null, "%s: no helper created with the flag off" % combo["key"]):
			return false
	var index: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(INDEX_PATH))
	var labelled: bool = index["art_status"] == "synthetic-diagnostic-test-fixture-not-art" and index["art_approved"] == false
	for key in KEYS:
		labelled = labelled and _manifest(key)["art_status"] == "synthetic-diagnostic-test-fixture-not-art" and _manifest(key)["art_approved"] == false
	return _check(labelled and index["sets"].has("hero:female"), "fixtures labelled synthetic-diagnostic-test-fixture-not-art, art_approved false; both hero appearances present")


func _check_loader() -> bool:
	_prepare_party("scifi.ruins")
	_set_flags({}, 1)
	var battle: Node2D = await _open_battle("patrol", {"paused": true})
	var sets: RefCounted = battle.combat_sprite_sets
	if not _check(sets != null and sets.index_status == "loaded" and sets.loaded_count() == 4, "pilot on: index loaded, 4/4 party sets loaded (%s)" % (str(sets.statuses) if sets != null else "null")):
		return false
	var ids_ok := true
	for index in 4:
		var loaded: Dictionary = sets.sets[index]
		ids_ok = ids_ok and battle.fighters[index]["id"] == PARTY[index] and loaded["key"] == KEYS[index] and loaded["art_approved"] == false
		ids_ok = ids_ok and loaded["cell"] == Vector2i(96, 80) and loaded["actions"].size() == 8
	if not _check(ids_ok, "each set matches its fighter identity, party order unchanged, 96x80 cells, 8 playable actions"):
		return false
	var zhao_fallback: bool = sets.sets[2]["actions"]["skill"]["source"] == "attack" and sets.sets[0]["actions"]["skill"]["source"] == "skill"
	if not _check(zhao_fallback, "Zhao's set has no skill action: skill plays the attack frames; the hero's own skill plays"):
		return false
	var validations: int = helper_script.validation_count
	battle = await _open_battle("sentry", {"paused": true})
	if not _check(helper_script.validation_count == validations and battle.combat_sprite_sets.loaded_count() == 4, "second battle reuses the cached sets (validations %d -> %d)" % [validations, helper_script.validation_count]):
		return false
	_prepare_party("scifi.ruins", "female")
	battle = await _open_battle("patrol", {"paused": true})
	sets = battle.combat_sprite_sets
	report["loader"] = {"statuses": sets.statuses.duplicate(), "validations": helper_script.validation_count}
	if not _check(sets.set_status(0) == "loaded" and sets.loaded_count() == 4 and sets.sets[0]["key"] == "hero:female", "female protagonist loads her own synthetic set, other party sets unchanged"):
		return false
	var wrong: Dictionary = helper_script.load_set(index_path_for_key("hero:male"), "hero:female")
	return _check(wrong["status"] == "identity_mismatch", "male manifest requested for female identity falls back atomically")


func index_path_for_key(key: String) -> String:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(INDEX_PATH))
	return data["sets"][key]


func _write_temp(name: String, data: Variant) -> String:
	var path := "user://combat-set-pilot-fallback/" + name
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("user://combat-set-pilot-fallback"))
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(data if data is String else JSON.stringify(data))
	file.close()
	return path


func _broken(mutate: Callable) -> Dictionary:
	var data: Dictionary = _manifest("liang-xu").duplicate(true)
	data["sheet"] = FIXTURE_DIR + "/" + String(data["sheet"])
	mutate.call(data)
	return data


func _check_fallbacks() -> bool:
	var cases := {
		"missing_manifest": null,
		"invalid_json": "{not json",
		"unknown_schema": _broken(func(d): d["schema"] = "worlds-between.combat-sprite-set/9"),
		"identity_mismatch": _broken(func(d): d["character"]["member_id"] = "zhao-ling"),
		"missing_action": _broken(func(d): d["actions"].erase("guard")),
		"unknown_action": _broken(func(d): d["actions"]["taunt"] = d["actions"]["idle"]),
		"invalid_mode": _broken(func(d): d["actions"]["attack"]["loop"] = true),
		"invalid_frame": _broken(func(d): d["actions"]["hit"]["frames"][1]["ms"] = 0),
		"frame_out_of_range": _broken(func(d): d["actions"]["move"]["frames"][3]["cell"] = 40),
		"empty_frame": _broken(func(d): d["actions"]["idle"]["frames"][0]["cell"] = 39),
		"invalid_pivot": _broken(func(d): d["actions"]["dodge"]["frames"][1]["pivot"] = [96, 76]),
		"missing_sheet": _broken(func(d): d["sheet"] = FIXTURE_DIR + "/missing-sheet.png"),
		"sheet_not_cell_multiple": _broken(func(d): d["cell_size"] = [100, 80]),
		"unsupported_scale": _broken(func(d): d["logical_scale"] = 2),
		"unsupported_proportion": _broken(func(d): d["display_proportion"] = "1.0"),
	}
	# Different invalid JSON types must reject without a String constructor or narrowing error.
	for bad in [{}, [], 123, true, null]:
		var suffix := "__type-%d" % cases.size()
		cases["unknown_schema" + suffix] = _broken(func(d): d["schema"] = bad)
		cases["identity_mismatch" + suffix] = _broken(func(d): d["character"]["member_id"] = bad)
		cases["identity_mismatch" + suffix + "-appearance"] = _broken(func(d): d["character"]["appearance"] = bad)
		cases["unsupported_proportion" + suffix] = _broken(func(d): d["display_proportion"] = bad)
		cases["invalid_facing" + suffix] = _broken(func(d): d["authored_facing"] = bad)
		cases["missing_sheet" + suffix] = _broken(func(d): d["sheet"] = bad)
		cases["invalid_metadata" + suffix] = _broken(func(d): d["set_id"] = bad)
	for bad in [{}, [], "10", true, null, 1.5, 1e30]:
		var suffix := "__number-%d" % cases.size()
		cases["invalid_cell" + suffix] = _broken(func(d): d["cell_size"] = [bad, 80])
		cases["invalid_pivot" + suffix] = _broken(func(d): d["pivot"] = [bad, 76])
		cases["invalid_frame" + suffix] = _broken(func(d): d["actions"]["hit"]["frames"][0]["ms"] = bad)
		cases["frame_out_of_range" + suffix] = _broken(func(d): d["actions"]["hit"]["frames"][0]["cell"] = bad)
	for bad in [{}, [], "bad", true, null]:
		var suffix := "__shape-%d" % cases.size()
		cases["unsupported_scale" + suffix] = _broken(func(d): d["logical_scale"] = bad)
		cases["identity_mismatch" + suffix] = _broken(func(d): d["character"] = bad)
		cases["missing_action" + suffix] = _broken(func(d): d["actions"] = bad)
		cases["invalid_action" + suffix] = _broken(func(d): d["actions"]["idle"]["frames"] = bad)
		if not bad is String:
			cases["invalid_metadata" + suffix] = _broken(func(d): d["art_status"] = bad)
	for bad in [{}, [], "true", 1, null]:
		var suffix := "__boolean-%d" % cases.size()
		cases["invalid_metadata" + suffix] = _broken(func(d): d["art_approved"] = bad)
		cases["invalid_action" + suffix] = _broken(func(d): d["actions"]["idle"]["loop"] = bad)
	var index: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(INDEX_PATH))
	var results := {}
	for label in cases:
		var expected: String = label.get_slice("__", 0)
		var manifest_path := "user://combat-set-pilot-fallback/missing-%s.json" % run_id if cases[label] == null else _write_temp("liang-%s-%s.json" % [label, run_id], cases[label])
		var temp_index: Dictionary = index.duplicate(true)
		temp_index["sets"]["liang-xu"] = manifest_path
		battle_script.combat_sprite_set_index_override = _write_temp("index-%s-%s.json" % [label, run_id], temp_index)
		_prepare_party("scifi.ruins")
		_set_flags({}, 1)
		var battle: Node2D = await _open_battle("patrol", {"paused": true})
		var sets: RefCounted = battle.combat_sprite_sets
		results[label] = sets.set_status(1)
		if not _check(sets.set_status(1) == expected and not sets.has_set(1) and sets.loaded_count() == 3, "fallback %s: Liang's whole set rejected (status %s), the other three still load" % [expected, sets.set_status(1)]):
			return false
	for index_case in [["missing_manifest", "user://combat-set-pilot-fallback/no-index-%s.json" % run_id], ["unknown_index_schema", _write_temp("index-bad-schema-%s.json" % run_id, {"schema": "x", "sets": {}})]]:
		battle_script.combat_sprite_set_index_override = index_case[1]
		var battle: Node2D = await _open_battle("patrol", {"paused": true})
		results["index_" + index_case[0]] = battle.combat_sprite_sets.index_status
		if not _check(battle.combat_sprite_sets.index_status == index_case[0] and battle.combat_sprite_sets.loaded_count() == 0, "index %s: every fighter keeps the existing frames" % index_case[0]):
			return false
	for bad in [{}, [], 123, true, null]:
		var bad_index := _write_temp("index-typed-%d-%s.json" % [results.size(), run_id], {"schema": bad, "sets": {}})
		var invalid: Dictionary = helper_script.load_index(bad_index)
		if not _check(invalid["status"] == "unknown_index_schema" and invalid["sets"].is_empty(), "wrong-type index schema rejects without runtime errors"):
			return false
		results["index-type-%d" % results.size()] = invalid["status"]
	for bad in [{}, [], 123, true, null, ""]:
		var bad_index := _write_temp("index-value-%d-%s.json" % [results.size(), run_id], {"schema": "worlds-between.combat-sprite-set-index/1", "sets": {"hero:male": bad}})
		var invalid: Dictionary = helper_script.load_index(bad_index)
		if not _check(invalid["status"] == "invalid_index" and invalid["sets"].is_empty(), "wrong-type or empty index path rejects atomically"):
			return false
		results["index-value-%d" % results.size()] = invalid["status"]
	battle_script.combat_sprite_set_index_override = ""
	report["fallbacks"] = results
	return true


func _attack_samples(dt: float) -> Dictionary:
	_prepare_party("scifi.ruins")
	_set_flags({}, 1)
	var battle: Node2D = await _open_battle("patrol", {"paused": true})
	var sets: RefCounted = battle.combat_sprite_sets
	var samples := {"attack": [], "dodge": []}
	for action in ["attack", "dodge"]:
		battle.fighters[0]["attack_cooldown"] = 0.0
		battle.fighters[0]["dodge_cooldown"] = 0.0
		_place(battle, [150, 230, 310, 390], 493.0)
		if action == "attack":
			battle._try_attack(0)
		else:
			battle._try_dodge(0)
		for tick in 60:
			battle.paused = false
			battle._process(dt)
			battle.paused = true
			var frame: Dictionary = sets.current_frame(0)
			if frame["action"] != action:
				break
			samples[action].append([tick * dt, int(frame["frame"]), float(sets.states[0]["clock"])])
	return samples


func _check_timing() -> bool:
	var results := {}
	for fps in [60, 30]:
		results[fps] = await _attack_samples(1.0 / fps)
	var detail := {}
	for action in ["attack", "dodge"]:
		var by_time := {}
		for fps in [60, 30]:
			var samples: Array = results[fps][action]
			for sample in samples:
				if int(sample[1]) != _oracle_frame("hero:male", action, float(sample[0])):
					return _check(false, "%s at %d fps: t %.4f shows frame %d, manifest says %d" % [action, fps, sample[0], sample[1], _oracle_frame("hero:male", action, float(sample[0]))])
				if not is_equal_approx(float(sample[2]), float(sample[0])):
					return _check(false, "%s at %d fps: playback clock %.4f drifts from real time %.4f" % [action, fps, sample[2], sample[0]])
				by_time["%d:%.4f" % [fps, sample[0]]] = int(sample[1])
			detail["%s_%dfps" % [action, fps]] = {"ticks": samples.size(), "lastClock": snappedf(float(samples[-1][0]), 0.0001), "frames": samples.map(func(s): return s[1])}
		for key in by_time:
			if key.begins_with("30:"):
				var other: String = "60:" + String(key).trim_prefix("30:")
				if by_time.has(other) and by_time[other] != by_time[key]:
					return _check(false, "%s frame differs at shared time %s" % [action, key])
	var attack_end_60: float = float(detail["attack_60fps"]["lastClock"])
	var attack_end_30: float = float(detail["attack_30fps"]["lastClock"])
	if not _check(attack_end_60 < 0.39 and attack_end_60 + 1.0 / 60.0 >= 0.389 and attack_end_30 < 0.39 and attack_end_30 + 1.0 / 30.0 >= 0.389, "attack one-shot (390 ms) ends on the first tick past its duration at 60 fps (%.4f) and 30 fps (%.4f)" % [attack_end_60, attack_end_30]):
		return false
	var dodge_frames_60: Array = detail["dodge_60fps"]["frames"]
	if not _check(dodge_frames_60.has(1) and dodge_frames_60.has(2) and dodge_frames_60.has(3), "real dodge (0.27 s) at 60 fps reaches the per-frame-pivot frames 1-2 and frame 3 (%s)" % str(dodge_frames_60)):
		return false
	# Loops through the helper alone: guard and move cycles at 30 and 60 fps give the manifest frame at every tick.
	var battle: Node2D = current_scene
	var sets: RefCounted = battle.combat_sprite_sets
	for loop_action in ["guard", "move", "idle"]:
		for fps in [60, 30]:
			var fighter := {"x": 150.0, "visual_action": "", "visual_elapsed": 0.0, "dodge_time": 0.0, "guard": loop_action == "guard", "visual_moving": loop_action == "move"}
			sets.states[1]["action"] = ""
			for tick in fps * 2:
				sets.advance(1, fighter, true, 493.0, 0.0 if tick == 0 else 1.0 / fps)
				var frame: Dictionary = sets.current_frame(1)
				if frame["action"] != loop_action or int(frame["frame"]) != _oracle_frame("liang-xu", loop_action, float(tick) / fps):
					return _check(false, "%s loop at %d fps tick %d shows %s/%d" % [loop_action, fps, tick, frame["action"], frame["frame"]])
		pass_count += 1
		print("PASS %s loop: 2 s at 60 and 30 fps match the manifest frame at every tick" % loop_action)
	report["timing"] = detail
	return _check(true, "attack and dodge frames match the manifest at every 60 and 30 fps tick and agree at shared timestamps")


func _check_pivots() -> bool:
	var sets: RefCounted = current_scene.combat_sprite_sets
	var checked := 0
	for index in 4:
		var loaded: Dictionary = sets.sets[index]
		var cell: Vector2i = loaded["cell"]
		for action in loaded["actions"]:
			for frame_index in loaded["actions"][action]["frames"].size():
				var frame: Dictionary = loaded["actions"][action]["frames"][frame_index]
				var clock: float = 0.0 if frame_index == 0 else float(loaded["actions"][action]["frames"][frame_index - 1]["end"])
				for facing in [1, -1]:
					sets.states[index]["action"] = action
					sets.states[index]["clock"] = clock
					sets.states[index]["facing"] = facing
					var shown: Dictionary = sets.current_frame(index)
					var origin: Vector2i = sets.cell_screen_origin(index, 300.4, float(FLOOR_Y))
					var pivot: Vector2i = shown["pivot"]
					var pivot_screen_x: int = origin.x + (pivot.x if facing == 1 else cell.x - 1 - pivot.x)
					if int(shown["frame"]) != frame_index or pivot_screen_x != 300 or origin.y + pivot.y != FLOOR_Y or bool(shown["mirrored"]) != (facing == -1):
						return _check(false, "pivot %s %s f%d facing %d lands at (%d, %d)" % [KEYS[index], action, frame_index, facing, pivot_screen_x, origin.y + pivot.y])
					checked += 1
	report["pivotCases"] = checked
	return _check(checked == 4 * 37 * 2, "every frame of all 4 sets, both facings: the pivot pixel lands on (round(x), floor y) (%d cases)" % checked)


func _check_state_selection() -> bool:
	# Real auto combat: the pilot follows the combat state it reads; defeat comes from a real lethal hit.
	_prepare_party("scifi.ruins")
	_set_policies()
	_set_flags({}, 1)
	var battle: Node2D = await _open_battle("sentry", {"paused": true})
	battle.auto_mode = true
	battle.enemy_hp = 600
	var seen := {}
	var facings := {}
	for step in 600:
		battle.paused = false
		battle._process(1.0 / 60.0)
		battle.paused = true
		for index in 4:
			var frame: Dictionary = battle.combat_sprite_sets.current_frame(index)
			seen[frame["action"]] = true
			facings[frame["facing"]] = true
	var needed := ["idle", "move", "attack", "skill", "dodge", "guard", "hit"]
	for action in needed:
		if not _check(seen.has(action), "real auto combat shows the %s action (%s)" % [action, str(seen.keys())]):
			return false
	app.member_state("zhao-ling")["hp"] = 1
	battle.fighters[2]["x"] = battle.enemy_x - 40.0
	battle.fighters[2]["dodge_time"] = 0.0
	battle.fighters[2]["guard"] = false
	battle.enemy_target_index = 2
	battle._apply_enemy_hit()
	battle.paused = false
	battle._process(1.0 / 60.0)
	battle.paused = true
	var down: Dictionary = battle.combat_sprite_sets.current_frame(2)
	_step_visuals(battle, 1.0)
	var held: Dictionary = battle.combat_sprite_sets.current_frame(2)
	report["stateSelection"] = {"actionsSeen": seen.keys(), "facingsSeen": facings.keys()}
	return _check(down["action"] == "defeat" and int(down["frame"]) == 0 and held["action"] == "defeat" and int(held["frame"]) == 3, "a lethal hit plays defeat from frame 0 and holds its last frame (3) after 1 s")


func _trace_row(battle: Node2D) -> String:
	var row := "%.4f|%d|%.4f|%.4f|%d|%d|%d|%d|%d|%s|%d" % [battle.enemy_x, battle.enemy_hp, battle.enemy_windup, battle.enemy_cooldown, battle.enemy_attack_count, battle.enemy_target_index, battle.player_attack_count, battle.controlled_index, int(battle.battle_finished), battle.feedback_key, battle.next_attack_bonus]
	for fighter in battle.fighters:
		var member: Dictionary = app.member_state(String(fighter["id"]))
		row += "|%s|%.4f|%.4f|%.4f|%.4f|%.4f|%s|%d|%d|%s|%.4f|%d|%d" % [fighter["id"], fighter["x"], fighter["attack_cooldown"], fighter["dodge_cooldown"], fighter["dodge_time"], fighter["skill_cooldown"], fighter["command"], int(fighter["guard"]), int(fighter["boost"]), fighter["visual_action"], fighter["visual_elapsed"], int(member["hp"]), int(member["energy"])]
	return row


func _simulate(combo: Dictionary, pilot: int) -> Dictionary:
	_prepare_party("scifi.outskirts")
	_set_policies()
	_set_flags(combo, pilot)
	var battle: Node2D = await _open_battle(combo["enemy"], {"paused": true})
	var loaded: int = battle.combat_sprite_sets.loaded_count() if battle.get("combat_sprite_sets") != null else 0
	battle.auto_mode = true
	battle.enemy_hp = 600
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	var trace := PackedStringArray()
	for step in 600:
		battle.paused = false
		battle._process(1.0 / 60.0)
		battle.paused = true
		var row := _trace_row(battle)
		trace.append(row)
		context.update((row + "\n").to_utf8_buffer())
	return {"trace": trace, "sha256": context.finish().hex_encode(), "loaded": loaded, "snapshot": _snapshot_without_clock(), "party": app.active_party_ids.duplicate(), "enemyAttacks": battle.enemy_attack_count, "playerAttacks": battle.player_attack_count}


func _check_parity() -> bool:
	var parity := {}
	var baseline := {}
	if baseline_dir != "":
		baseline = _baseline_report()["traces"]
	for combo in SIM_COMBOS:
		var on: Dictionary = await _simulate(combo, 1)
		var off: Dictionary = await _simulate(combo, 0)
		var first_diff := -1
		for i in on["trace"].size():
			if on["trace"][i] != off["trace"][i]:
				first_diff = i
				break
		parity[combo["key"]] = {"steps": 600, "traceSha256": off["sha256"], "firstDifferentStep": first_diff, "pilotSetsLoaded": on["loaded"], "enemyAttacks": on["enemyAttacks"], "playerAttacks": on["playerAttacks"], "saveSnapshotEqual": on["snapshot"] == off["snapshot"]}
		if not _check(int(on["loaded"]) == 4 and int(off["loaded"]) == 0 and first_diff == -1 and on["sha256"] == off["sha256"], "%s: 600-step auto combat identical with the pilot on (4 sets) and off (positions, HP, energy, timers, hits, AI, feedback)" % combo["key"]):
			return false
		if not _check(on["snapshot"] == off["snapshot"] and on["party"] == off["party"] and int(on["enemyAttacks"]) > 0 and int(on["playerAttacks"]) > 0, "%s: save snapshot and party order identical; the fight had real hits both ways" % combo["key"]):
			return false
		if not baseline.is_empty():
			parity[combo["key"]]["baseCommitTraceSha256"] = baseline[combo["key"]]
			if not _check(baseline[combo["key"]] == off["sha256"], "%s: flag-off trace equals the base-commit trace (%s)" % [combo["key"], String(off["sha256"]).left(12)]):
				return false
	report["simulationParity"] = parity
	return true


func _render(battle: Node2D) -> Image:
	battle.queue_redraw()
	await process_frame
	await process_frame
	return root.get_viewport().get_texture().get_image()


func _save(image: Image, key: String, language: String) -> String:
	var name := "%s_%s-%s-640_%s-%s.png" % [PREFIX, key, language, stamp, run_id]
	if not _check(name.length() <= 121, "%s file name %d chars (<= 121)" % [key, name.length()]):
		return ""
	var path := capture_dir.path_join(name)
	image.save_png(path)
	return path


func _off_capture(combo: Dictionary, pilot: int, index_override: String = "") -> Image:
	_prepare_party("scifi.outskirts")
	_set_flags(combo, pilot)
	if pilot >= 0:
		battle_script.combat_sprite_set_index_override = index_override
	var battle: Node2D = await _open_battle(combo["enemy"], {"paused": true})
	_drive_action_mix(battle)
	var image: Image = await _render(battle)
	if pilot >= 0:
		battle_script.combat_sprite_set_index_override = ""
	return image


func _baseline_only() -> bool:
	var traces := {}
	for combo in SIM_COMBOS:
		var off: Dictionary = await _simulate(combo, -1)
		traces[combo["key"]] = off["sha256"]
		print("BASELINE TRACE %s %s" % [combo["key"], off["sha256"]])
	var renders := {}
	if capture_enabled:
		for combo in OFF_COMBOS:
			var image: Image = await _off_capture(combo, -1)
			var path := _save(image, "base-commit-" + String(combo["key"]), "zh")
			if path == "":
				return false
			renders[combo["key"]] = {"file": path.get_file(), "sha256": FileAccess.get_sha256(path)}
	var file := FileAccess.open(capture_dir.path_join("%s_base-commit-report_%s-%s.json" % [PREFIX, stamp, run_id]), FileAccess.WRITE)
	file.store_string(JSON.stringify({"battleScriptSha256": FileAccess.get_file_as_string(BATTLE_SCRIPT_PATH).replace("\r\n", "\n").sha256_text(), "traces": traces, "renders": renders}, "  ") + "\n")
	file.close()
	return _check(traces.size() == SIM_COMBOS.size(), "baseline traces written to %s" % capture_dir)


func _baseline_report() -> Dictionary:
	for name in DirAccess.get_files_at(baseline_dir):
		if name.contains("_base-commit-report_") and name.ends_with(".json"):
			var report_data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(baseline_dir.path_join(name)))
			report_data["file"] = name
			return report_data
	return {"traces": {}, "renders": {}}


func _check_off_renders() -> bool:
	if not capture_enabled:
		return true
	var results := {}
	for combo in OFF_COMBOS:
		var image: Image = await _off_capture(combo, 0)
		var path := _save(image, combo["key"], "zh")
		if path == "":
			return false
		var entry := {"file": path.get_file(), "sha256": FileAccess.get_sha256(path)}
		if baseline_dir != "":
			var base_file: String = _baseline_report()["renders"][combo["key"]]["file"]
			var base := Image.load_from_file(baseline_dir.path_join(base_file))
			entry["baseFile"] = base_file
			entry["baseSha256"] = FileAccess.get_sha256(baseline_dir.path_join(base_file))
			if not _check(base != null and base.get_size() == image.get_size() and base.get_data() == image.get_data(), "%s: flag-off render pixel-identical to the base commit" % combo["key"]):
				return false
		results[combo["key"]] = entry
	# Atomic fallback: the pilot on with an index that does not exist renders exactly the flag-off frame.
	var off_image: Image = await _off_capture(OFF_COMBOS[0], 0)
	var broken_image: Image = await _off_capture(OFF_COMBOS[0], 1, "res://tests/fixtures/no-such-index.json")
	results["pilotOnMissingIndexEqualsOff"] = off_image.get_data() == broken_image.get_data()
	report["flagOffRenders"] = results
	return _check(bool(results["pilotOnMissingIndexEqualsOff"]), "pilot on with a missing index renders pixel-identical to the flag-off frame")


# ---------------------------------------------------------------- captures

func _source_cell(loaded: Dictionary, frame: Dictionary) -> Image:
	var sheet := Image.load_from_file(ProjectSettings.globalize_path(String(loaded["sheet"])))
	var cell := sheet.get_region(Rect2i(frame["origin"], loaded["cell"]))
	if frame["mirrored"]:
		cell.flip_x()
	return cell


# strict_ticks: staged cases place fighters apart, so every pilot ground tick must show; in live auto combat fighters overlap,
# so ticks are only recorded there.
func _verify_render(image: Image, battle: Node2D, label: String, full_cell: Array, strict_ticks: bool = true) -> Dictionary:
	var sets: RefCounted = battle.combat_sprite_sets
	var fighters := []
	for index in battle.fighters.size():
		var x: float = battle.fighters[index]["x"]
		var entry := {"id": battle.fighters[index]["id"], "x": x, "pilot": sets != null and sets.has_set(index)}
		if entry["pilot"]:
			var frame: Dictionary = sets.current_frame(index)
			entry.merge({"action": frame["action"], "source": frame["source"], "frame": frame["frame"], "cell": frame["cell"], "facing": "right" if int(frame["facing"]) == 1 else "left", "mirrored": frame["mirrored"]})
			var ax := roundi(x)
			var tick := [Vector2i(ax, FLOOR_Y), Vector2i(ax, FLOOR_Y + 1), Vector2i(ax - 1, FLOOR_Y + 1), Vector2i(ax + 1, FLOOR_Y + 1)]
			var tick_ok := true
			for p in tick:
				tick_ok = tick_ok and image.get_pixelv(p).to_rgba32() == MAGENTA
			entry["groundTickAtX"] = tick_ok
			if strict_ticks and not _check(tick_ok, "%s: %s ground-anchor tick on screen at (%d, %d-%d)" % [label, entry["id"], ax, FLOOR_Y, FLOOR_Y + 1]):
				return {}
			if full_cell.has(index):
				var cell := _source_cell(sets.sets[index], frame)
				var origin: Vector2i = sets.cell_screen_origin(index, x, float(FLOOR_Y))
				var opaque := 0
				var wrong := 0
				for cy in cell.get_height():
					for cx in cell.get_width():
						var c := cell.get_pixel(cx, cy)
						if c.a > 0.99:
							opaque += 1
							if image.get_pixel(origin.x + cx, origin.y + cy).to_rgba32() != c.to_rgba32():
								wrong += 1
				entry["fullCell"] = {"opaque": opaque, "mismatched": wrong}
				if not _check(opaque > 300 and wrong == 0, "%s: %s on-screen pixels equal source cell %d%s exactly (%d px)" % [label, entry["id"], frame["cell"], " mirrored" if frame["mirrored"] else "", opaque]):
					return {}
		fighters.append(entry)
	return {"fighters": fighters}


func _run_captures() -> bool:
	if not capture_enabled:
		return true
	var fallback_index: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(INDEX_PATH))
	fallback_index["sets"]["liang-xu"] = _write_temp("liang-partial-%s.json" % run_id, _broken(func(d): d["actions"].erase("guard")))
	var fallback_index_path := _write_temp("index-partial-%s.json" % run_id, fallback_index)
	var cases := [
		{"key": "auto-combat", "note": "real auto combat after 170 steps of 1/60 s (sentry with 600 HP as in the parity runs, Ji cautious, Zhao aggressive)", "full": []},
		{"key": "female-action-mix", "appearance": "female", "full": [3], "note": "Synthetic female appearance loads correct identity; no art approval."},
		{"key": "action-mix-right", "note": "hero attack f3, Liang guard, Zhao skill via attack fallback f3, Ji hit f2; all face right", "full": [3]},
		{"key": "dodge-defeat-left", "note": "hero right of the enemy mid-dodge (per-frame pivot, faces left), Liang defeat hold, Zhao walking, Ji faces left (mirrored)", "full": [3]},
		{"key": "fallback-partial", "note": "Liang's set lacks guard: his whole set is rejected and he keeps the existing frames; the other three use the pilot", "full": [3]},
		{"key": "flag-off-action-mix", "note": "same driven state as action-mix-right with the pilot off (existing frames)", "full": []},
	]
	for entry in cases:
		for language in ["zh", "en"]:
			_prepare_party("scifi.ruins", entry.get("appearance", "male"))
			if app.language != language:
				app.toggle_language()
			var pilot := 0 if entry["key"] == "flag-off-action-mix" else 1
			_set_flags({}, pilot)
			battle_script.combat_sprite_set_index_override = fallback_index_path if entry["key"] == "fallback-partial" else ""
			var battle: Node2D
			if entry["key"] == "auto-combat":
				_set_policies()
				battle = await _open_battle("sentry", {"paused": true})
				battle.auto_mode = true
				battle.enemy_hp = 600
				for step in 170:
					battle.paused = false
					battle._process(1.0 / 60.0)
					battle.paused = true
			else:
				battle = await _open_battle("patrol", {"paused": true})
				if entry["key"] == "dodge-defeat-left":
					_drive_dodge_defeat(battle)
				else:
					_drive_action_mix(battle)
			battle._refresh_text()
			var image: Image = await _render(battle)
			battle_script.combat_sprite_set_index_override = ""
			var label := "%s-%s" % [entry["key"], language]
			if not _check(image.get_size() == WINDOW, "%s capture is 640x360" % label):
				return false
			var verified := _verify_render(image, battle, label, entry["full"], entry["key"] != "auto-combat")
			if verified.is_empty() and entry["key"] != "flag-off-action-mix":
				return false
			var sets: RefCounted = battle.combat_sprite_sets
			if entry["key"] == "fallback-partial" and not _check(sets.set_status(1) == "missing_action" and sets.loaded_count() == 3, "%s: Liang rejected (missing_action), 3 pilot sets" % label):
				return false
			if entry["key"] == "flag-off-action-mix" and not _check(sets == null, "%s: no helper, existing frames" % label):
				return false
			if entry["key"] == "female-action-mix" and not _check(sets.sets[0]["key"] == "hero:female", "%s: female identity actually rendered" % label):
				return false
			if entry["key"] == "action-mix-right":
				var expect := [["attack", 3], ["guard", 1], ["skill", 3], ["hit", 2]]
				for index in 4:
					var frame: Dictionary = sets.current_frame(index)
					if not _check(frame["action"] == expect[index][0] and int(frame["frame"]) == expect[index][1] and not frame["mirrored"], "%s: %s shows %s f%d facing right" % [label, PARTY[index], expect[index][0], expect[index][1]]):
						return false
			if entry["key"] == "dodge-defeat-left":
				var expect := [["dodge", 1, true], ["defeat", 3, false], ["move", -1, false], ["idle", -1, true]]
				for index in 4:
					var frame: Dictionary = sets.current_frame(index)
					if not _check(frame["action"] == expect[index][0] and (expect[index][1] < 0 or int(frame["frame"]) == expect[index][1]) and frame["mirrored"] == expect[index][2], "%s: %s shows %s%s" % [label, PARTY[index], expect[index][0], " mirrored (faces left)" if expect[index][2] else " facing right"]):
						return false
			var path := _save(image, entry["key"], language)
			if path == "":
				return false
			records.append({"file": path.get_file(), "sha256": FileAccess.get_sha256(path), "case": entry["key"], "language": language, "window": "native 640x360", "note": entry["note"], "render": verified})
	return true


func _write_manifest() -> bool:
	if not capture_enabled:
		return true
	var path := capture_dir.path_join("%s_capture-manifest_%s-%s.json" % [PREFIX, stamp, run_id])
	var manifest := {
		"project": "rpg-2-star-ocean-the-second",
		"task": "code.runtime.combat-sprite-pipeline",
		"status": "TECHNICAL capability; opt-in --combat-sprite-set-pilot; off by default",
		"createdAt": Time.get_datetime_string_from_system(),
		"engine": "Godot %s gl_compatibility, 640x360 logical, captured in a 640x360 window (1 logical px = 1 px)" % Engine.get_version_info()["string"],
		"battleScriptSha256": FileAccess.get_file_as_string(BATTLE_SCRIPT_PATH).replace("\r\n", "\n").sha256_text(),
		"helperSha256": FileAccess.get_file_as_string(HELPER_PATH).replace("\r\n", "\n").sha256_text(),
		"sourceHashAlgorithm": "sha256-text-lf-v1",
		"checkScriptSha256": FileAccess.get_file_as_string("res://" + CHECK_SCRIPT.trim_prefix("game/")).replace("\r\n", "\n").sha256_text(),
		"fixtureIndex": INDEX_PATH,
		"fixtureArt": "SYNTHETIC DIAGNOSTIC test fixtures, not art, not for review or approval",
		"checkScript": CHECK_SCRIPT,
		"freshProfile": "APPDATA redirected; settings load_status missing",
		"baselineDir": baseline_dir,
		"baselineReport": _baseline_report() if baseline_dir != "" else {},
		"artApproved": false,
		"fighterArtAccepted": "0/52",
		"report": report,
		"captures": records,
	}
	var file := FileAccess.open(path, FileAccess.WRITE)
	if not _check(file != null, "manifest written"):
		return false
	file.store_string(JSON.stringify(manifest, "  ") + "\n")
	file.close()
	print("MANIFEST " + path)
	return true


func _check(condition: bool, label: String) -> bool:
	if condition:
		pass_count += 1
		print("PASS " + label)
		return true
	push_error("FAIL " + label)
	print("FAIL " + label)
	quit(1)
	return false
