extends SceneTree

# Targeted deterministic checks for the optional combat-sprite-set logical_scale 0.5 path.
# The fixture is a SYNTHETIC diagnostic mannequin sheet (NOT ART): it proves loader, cache, fallback and exact draw
# geometry/timing only. It is never inserted into the runtime, and no action requirement is relaxed.
const HELPER_PATH := "res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd"
const HALF_DIR := "res://tests/fixtures/csp-half-scale-v01_7d4bddce"
const HALF_MANIFEST := HALF_DIR + "/rpg-2-star-ocean-the-second_combat-half-scale_fixture_not-art-v01_20261020-154048-7d4bddce.json"
const HALF_INDEX := HALF_DIR + "/rpg-2-star-ocean-the-second_combat-half-scale_fixture-index_not-art-v01_20261020-154048-7d4bddce.json"
const OLD_MANIFEST := "res://tests/fixtures/csp-fixture-v01_03f4172a/rpg-2-star-ocean-the-second_combat-set_liang-xu-manifest_not-art-v01_20261018-153656-3d9c6f18.json"
const OLD_KEY := "liang-xu"
const HALF_KEY := "hero:female"
const ANCHOR_X := 300
const FLOOR_Y := 272
const TMP_ROOT := "user://combat-half-scale-check"
const OUT_DIR := "res://../outputs/combat-half-scale-v01"

var helper: GDScript
var half_data: Dictionary
var old_data: Dictionary
var run_id := "%08x" % (randi() & 0xffffffff)
var checks := 0
var failures := 0
var report := {}


func _initialize() -> void:
	call_deferred("_run")


func _check(ok: bool, message: String) -> bool:
	checks += 1
	if ok:
		print("PASS ", message)
	else:
		failures += 1
		print("FAIL ", message)
	return ok


func _run() -> void:
	helper = load(HELPER_PATH)
	if helper == null:
		_check(false, "helper script loads")
		_finish()
		return
	var probe = helper.new()
	if not _check(probe != null and probe.has_method("frame_geometry") and probe.has_method("is_supported_logical_scale"), "helper parses and exposes the half-scale geometry/scale API"):
		_finish()
		return
	helper.clear_cache()
	half_data = _read_json(HALF_MANIFEST)
	old_data = _read_json(OLD_MANIFEST)
	if not _check(not half_data.is_empty() and not old_data.is_empty(), "synthetic half-scale and frozen scale-1 manifests parse"):
		_finish()
		return
	var half_loaded: Dictionary = helper.load_set(HALF_MANIFEST, HALF_KEY)
	var old_loaded: Dictionary = helper.load_set(OLD_MANIFEST, OLD_KEY)
	if not _check(String(half_loaded.get("status", "")) == "loaded" and String(old_loaded.get("status", "")) == "loaded", "valid 0.5 and 1.0 sets load (statuses %s, %s)" % [half_loaded.get("status", "?"), old_loaded.get("status", "?")]):
		_finish()
		return
	_check_scale_values()
	_check_half_metadata(half_loaded)
	_check_rejections()
	_check_cache(half_loaded)
	_check_scale1_geometry(old_loaded)
	_check_half_geometry(half_loaded)
	_check_playback(half_loaded)
	_check_index()
	_finish()


func _finish() -> void:
	var status := "PASS" if failures == 0 else "FAIL"
	print("COMBAT_HALF_SCALE %s checks=%d failures=%d" % [status, checks, failures])
	_write_report(status)
	quit(0 if failures == 0 else 1)


func _read_json(path: String) -> Dictionary:
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return data if data is Dictionary else {}


func _write_temp(name: String, data: Variant) -> String:
	var dir := TMP_ROOT + "/" + run_id
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(dir))
	var path := dir + "/" + name
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		return ""
	file.store_string(data if data is String else JSON.stringify(data))
	file.close()
	return path


func _write_raw(name: String, text: String) -> String:
	return _write_temp(name, text)


func _mutate(base: Dictionary, mutate: Callable) -> Dictionary:
	var copy := base.duplicate(true)
	mutate.call(copy)
	var sheet := String(copy.get("sheet", ""))
	if not sheet.is_empty() and not sheet.contains("://"):
		copy["sheet"] = HALF_DIR + "/" + sheet
	return copy


func _mutator(field: String, value: Variant) -> Callable:
	return func(data: Dictionary) -> void: data[field] = value


func _load_mutation(label: String, mutate: Callable, key: String = HALF_KEY) -> Dictionary:
	var path := _write_temp("half-%s-%s.json" % [label, run_id], _mutate(half_data, mutate))
	return helper.load_set(path, key)


func _expect_reject(label: String, mutate: Callable, expected: String) -> void:
	var path := _write_temp("half-%s-%s.json" % [label, run_id], _mutate(half_data, mutate))
	var first: Dictionary = helper.load_set(path, HALF_KEY)
	var second: Dictionary = helper.load_set(path, HALF_KEY)
	var stable: bool = first.size() == 1 and second.size() == 1 and first == second
	if not _check(String(first.get("status", "")) == expected and stable, "%s rejects atomically as %s (got %s)" % [label, expected, first.get("status", "?")]):
		return


func _check_scale_values() -> void:
	var accepted := [1, 1.0, 0.5, 0.50]
	for value in accepted:
		_check(helper.is_supported_logical_scale(value), "accepts supported logical_scale %s" % str(value))
	var rejected := [0, 0.0, -0.5, -1, 2, 0.25, 0.75, 0.5000001, 1.0000001, "0.5", "1", "", true, false, null, [], {}, Vector2(0.5, 0.5), NAN, INF, -INF]
	for value in rejected:
		_check(not helper.is_supported_logical_scale(value), "rejects unsupported logical_scale %s" % str(value))
	var json_cases := {
		"scale-zero": 0,
		"scale-negative": -1,
		"scale-two": 2,
		"scale-quarter": 0.25,
		"scale-three-quarter": 0.75,
		"scale-string": "0.5",
		"scale-true": true,
		"scale-false": false,
		"scale-null": null,
		"scale-array": [],
		"scale-object": {},
	}
	var statuses := {}
	for label in json_cases:
		var result := _load_mutation(label, _mutator("logical_scale", json_cases[label]))
		statuses[label] = String(result.get("status", "?"))
		_check(String(result.get("status", "")) == "unsupported_scale" and result.size() == 1, "%s (JSON) rejects as unsupported_scale (got %s)" % [label, result.get("status", "?")])
	var missing := _load_mutation("scale-missing", func(data: Dictionary) -> void: data.erase("logical_scale"))
	statuses["scale-missing"] = String(missing.get("status", "?"))
	_check(String(missing.get("status", "")) == "unsupported_scale" and missing.size() == 1, "missing logical_scale rejects as unsupported_scale")
	var raw_status := "not-attempted"
	var raw_text := JSON.stringify(half_data).replace('"logical_scale": 0.5', '"logical_scale": 1e999').replace('"logical_scale":0.5', '"logical_scale":1e999')
	var raw_path := _write_raw("half-scale-inf-json-%s.json" % run_id, raw_text)
	if raw_path != "":
		raw_status = String(helper.load_set(raw_path, HALF_KEY).get("status", "?"))
		# Some JSON parsers reject the literal before the loader sees it; both outcomes reject the set.
		if raw_status == "invalid_json":
			_check(true, "non-finite JSON literal is rejected by the parser (invalid_json) before scale validation")
		else:
			_check(raw_status == "unsupported_scale", "non-finite JSON scale rejects as unsupported_scale (got %s)" % raw_status)
	report["scaleStatuses"] = statuses
	report["nonFiniteJsonStatus"] = raw_status


func _check_half_metadata(loaded: Dictionary) -> void:
	_check(loaded["key"] == HALF_KEY and loaded["art_approved"] == false, "half fixture loads as hero:female and stays labelled unapproved diagnostic data")
	_check(loaded["cell"] == Vector2i(136, 144) and loaded["pivot"] == Vector2i(68, 140), "source cell 136x144 and source pivot [68,140] are preserved")
	_check(loaded["logical_scale"] == 0.5 and loaded["draw_cell"] == Vector2i(68, 72) and loaded["scale_divisor"] == 2, "0.5 maps the source cell to a whole 68x72 logical draw cell")
	_check(loaded["display_proportion"] == "0.65", "0.65 display-proportion metadata remains accepted")
	_check(loaded["actions"].size() == 8, "all 8 actions load (7 required plus skill)")
	var required := ["idle", "move", "guard", "attack", "dodge", "hit", "defeat"]
	for action in required:
		_check(loaded["actions"].has(action) and not loaded["actions"][action]["frames"].is_empty(), "required action %s is present with frames" % action)
	_check(loaded["actions"].has("skill") and loaded["actions"]["skill"]["source"] == "skill", "authored skill action loads instead of falling back")
	var frames_ok := true
	var override_ok := true
	for action in loaded["actions"]:
		var frames: Array = loaded["actions"][action]["frames"]
		for index in frames.size():
			var pivot: Vector2i = frames[index]["pivot"]
			var expected := Vector2i(66, 140) if action == "dodge" and (index == 1 or index == 2) else Vector2i(68, 140)
			frames_ok = frames_ok and pivot == expected and pivot.x % 2 == 0 and pivot.y % 2 == 0
			override_ok = override_ok and (index != 1 or action != "dodge" or pivot == Vector2i(66, 140))
	_check(frames_ok, "every source pivot is even; the two dodge overrides keep [66,140]")
	_check(override_ok, "per-frame dodge pivot override [66,140] is preserved")
	_check(loaded["actions"]["dodge"]["frames"][1]["pivot"] == Vector2i(66, 140) and loaded["actions"]["dodge"]["frames"][2]["pivot"] == Vector2i(66, 140), "both authored dodge override frames are exact")
	_check(loaded["actions"]["idle"]["frames"][0]["origin"] == Vector2i(0, 0) and loaded["actions"]["defeat"]["frames"][3]["origin"] == Vector2i(6 * 136, 3 * 144), "source cell origins remain integer sheet coordinates")


func _check_rejections() -> void:
	_expect_reject("odd-cell-x", _mutator("cell_size", [135, 144]), "invalid_cell")
	_expect_reject("odd-cell-y", _mutator("cell_size", [136, 143]), "invalid_cell")
	_expect_reject("odd-cell-both", _mutator("cell_size", [135, 143]), "invalid_cell")
	_expect_reject("odd-pivot-x", _mutator("pivot", [67, 140]), "invalid_pivot")
	_expect_reject("odd-pivot-y", _mutator("pivot", [68, 139]), "invalid_pivot")
	_expect_reject("out-of-bounds-pivot", _mutator("pivot", [136, 140]), "invalid_pivot")
	_expect_reject("odd-frame-pivot-x", func(data: Dictionary) -> void: data["actions"]["dodge"]["frames"][1]["pivot"] = [67, 140], "invalid_pivot")
	_expect_reject("odd-frame-pivot-y", func(data: Dictionary) -> void: data["actions"]["dodge"]["frames"][2]["pivot"] = [66, 139], "invalid_pivot")
	_expect_reject("out-of-bounds-frame-pivot", func(data: Dictionary) -> void: data["actions"]["dodge"]["frames"][1]["pivot"] = [136, 140], "invalid_pivot")
	_expect_reject("missing-required-action", func(data: Dictionary) -> void: data["actions"].erase("guard"), "missing_action")
	_expect_reject("unknown-action", func(data: Dictionary) -> void: data["actions"]["taunt"] = data["actions"]["idle"], "unknown_action")
	_expect_reject("invalid-mode", func(data: Dictionary) -> void: data["actions"]["attack"]["loop"] = true, "invalid_mode")
	_expect_reject("out-of-range-frame", func(data: Dictionary) -> void: data["actions"]["move"]["frames"][0]["cell"] = 40, "frame_out_of_range")
	_expect_reject("bad-display-proportion", _mutator("display_proportion", "1.0"), "unsupported_proportion")


func _check_cache(loaded: Dictionary) -> void:
	helper.clear_cache()
	var before: int = int(helper.validation_count)
	var first: Dictionary = helper.load_set(HALF_MANIFEST, HALF_KEY)
	var after_first: int = int(helper.validation_count)
	var second: Dictionary = helper.load_set(HALF_MANIFEST, HALF_KEY)
	var after_second: int = int(helper.validation_count)
	_check(before == 0 and after_first == 1 and after_second == 1 and first == second and first["status"] == "loaded", "valid 0.5 set is validated once and reused from cache (%d -> %d)" % [after_first, after_second])
	var bad_path := _write_temp("half-cache-odd-cell-%s.json" % run_id, _mutate(half_data, _mutator("cell_size", [135, 144])))
	var bad_first: Dictionary = helper.load_set(bad_path, HALF_KEY)
	var bad_count: int = int(helper.validation_count)
	var bad_second: Dictionary = helper.load_set(bad_path, HALF_KEY)
	var bad_count_second: int = int(helper.validation_count)
	_check(bad_first == bad_second and bad_first["status"] == "invalid_cell" and bad_count == bad_count_second and bad_count == 2, "malformed 0.5 set stays atomically rejected and cached (status invalid_cell)")
	var again: Dictionary = helper.load_set(HALF_MANIFEST, HALF_KEY)
	_check(again["status"] == "loaded" and helper.validation_count == bad_count_second, "a cached valid set still loads after a cached malformed set")
	_check(loaded["status"] == "loaded" and loaded["draw_cell"] == Vector2i(68, 72), "the original loaded half-scale dictionary is unchanged")


func _view_for(loaded: Dictionary):
	var view = helper.new()
	view.sets.append(loaded)
	view.statuses.append("loaded")
	view.states.append({"action": "", "clock": 0.0, "facing": 1, "last_visual_action": "", "last_visual_elapsed": 0.0, "last_dodge_time": 0.0})
	return view


func _show(view, loaded: Dictionary, action: String, frame_index: int, facing: int) -> void:
	var frames: Array = loaded["actions"][action]["frames"]
	var clock := 0.0 if frame_index == 0 else float(frames[frame_index - 1]["end"])
	view.states[0]["action"] = action
	view.states[0]["clock"] = clock
	view.states[0]["facing"] = facing


func _check_scale1_geometry(loaded: Dictionary) -> void:
	var view = _view_for(loaded)
	var cell: Vector2i = loaded["cell"]
	var sheet_width: int = int(loaded["sheet_size"].x)
	var cases := 0
	for action in loaded["actions"]:
		var frames: Array = loaded["actions"][action]["frames"]
		for frame_index in frames.size():
			for facing in [1, -1]:
				_show(view, loaded, action, frame_index, facing)
				var shown: Dictionary = view.current_frame(0)
				var geometry: Dictionary = view.frame_geometry(0, float(ANCHOR_X) + 0.4, float(FLOOR_Y))
				var pivot: Vector2i = shown["pivot"]
				var left := ANCHOR_X - pivot.x if facing == 1 else ANCHOR_X - (cell.x - 1 - pivot.x)
				var expected_dest := Rect2(Vector2(left, FLOOR_Y - pivot.y), Vector2(cell))
				var expected_origin: Vector2i = shown["origin"]
				if shown["mirrored"]:
					expected_origin.x = sheet_width - expected_origin.x - cell.x
				var expected_src := Rect2(Vector2(expected_origin), Vector2(cell))
				var expected_texture: Texture2D = loaded["mirrored"] if shown["mirrored"] else loaded["texture"]
				var ok: bool = geometry["dest"] == expected_dest and geometry["src"] == expected_src and geometry["texture"] == expected_texture
				ok = ok and view.cell_screen_origin(0, float(ANCHOR_X) + 0.4, float(FLOOR_Y)) == Vector2i(expected_dest.position)
				ok = ok and geometry["draw_cell"] == cell and geometry["draw_pivot"] == pivot and loaded["logical_scale"] == 1.0
				if not _check(ok, "scale 1 exact old geometry %s frame %d facing %d (dest %s src %s)" % [action, frame_index, facing, str(geometry["dest"]), str(geometry["src"])]):
					return
				cases += 1
	_check(cases == 74, "scale 1 covers every frame/facing with the unchanged old transform (%d cases)" % cases)


func _check_half_geometry(loaded: Dictionary) -> void:
	var view = _view_for(loaded)
	var cell: Vector2i = loaded["cell"]
	var draw_cell: Vector2i = loaded["draw_cell"]
	var sheet_width: int = int(loaded["sheet_size"].x)
	var lefts := {}
	var cases := 0
	for action in loaded["actions"]:
		var frames: Array = loaded["actions"][action]["frames"]
		for frame_index in frames.size():
			for facing in [1, -1]:
				_show(view, loaded, action, frame_index, facing)
				var shown: Dictionary = view.current_frame(0)
				var geometry: Dictionary = view.frame_geometry(0, float(ANCHOR_X) + 0.4, float(FLOOR_Y))
				var pivot: Vector2i = shown["pivot"]
				var draw_pivot := Vector2i(pivot.x / 2, pivot.y / 2)
				var dest: Rect2 = geometry["dest"]
				var src: Rect2 = geometry["src"]
				var expected_origin: Vector2i = shown["origin"]
				if shown["mirrored"]:
					expected_origin.x = sheet_width - expected_origin.x - cell.x
				var planted_x: int = int(dest.position.x) + (draw_pivot.x if facing == 1 else draw_cell.x - 1 - draw_pivot.x)
				var whole: bool = float(dest.position.x) == floorf(dest.position.x) and float(dest.position.y) == floorf(dest.position.y) and float(dest.size.x) == floorf(dest.size.x) and float(dest.size.y) == floorf(dest.size.y)
				var ok: bool = dest.size == Vector2(draw_cell) and src.size == Vector2(cell) and geometry["draw_cell"] == draw_cell
				ok = ok and geometry["draw_pivot"] == draw_pivot and geometry["pivot"] == pivot and geometry["mirrored"] == shown["mirrored"]
				ok = ok and planted_x == ANCHOR_X and int(dest.position.y) + draw_pivot.y == FLOOR_Y and whole
				ok = ok and src.position == Vector2(expected_origin)
				ok = ok and view.cell_screen_origin(0, float(ANCHOR_X) + 0.4, float(FLOOR_Y)) == Vector2i(dest.position)
				ok = ok and geometry["texture"] == (loaded["mirrored"] if shown["mirrored"] else loaded["texture"])
				if not _check(ok, "half exact draw geometry %s frame %d facing %d (dest %s drawPivot %s src %s)" % [action, frame_index, facing, str(dest), str(draw_pivot), str(src)]):
					return
				lefts["%s:%d:%d" % [action, frame_index, facing]] = int(dest.position.x)
				cases += 1
	var symmetric := true
	for action in loaded["actions"]:
		var frames: Array = loaded["actions"][action]["frames"]
		for frame_index in frames.size():
			var right: int = int(lefts["%s:%d:1" % [action, frame_index]])
			var left: int = int(lefts["%s:%d:-1" % [action, frame_index]])
			symmetric = symmetric and right + (left + draw_cell.x) == 2 * ANCHOR_X + 1
			symmetric = symmetric and (right + draw_cell.x) + left == 2 * ANCHOR_X + 1
	_check(symmetric, "half-scale unmirrored and mirrored cells reflect about the same logical pivot column for every frame")
	_check(cases == 74, "half-scale covers every frame/facing with whole logical geometry (%d cases)" % cases)
	var overrides_ok := true
	for frame_index in [1, 2]:
		for facing in [1, -1]:
			_show(view, loaded, "dodge", frame_index, facing)
			var geometry: Dictionary = view.frame_geometry(0, float(ANCHOR_X), float(FLOOR_Y))
			var expected_left := ANCHOR_X - 33 if facing == 1 else ANCHOR_X - (draw_cell.x - 1 - 33)
			overrides_ok = overrides_ok and geometry["draw_pivot"] == Vector2i(33, 70) and geometry["dest"].position == Vector2(expected_left, FLOOR_Y - 70)
	_check(overrides_ok, "per-frame dodge override [66,140] draws at logical pivot [33,70], planted for both facings")
	report["geometry"] = {"scale1Cases": 74, "halfCases": cases, "mirrorSymmetric": symmetric, "dodgeOverridePlanted": overrides_ok}


func _reset_state(view) -> void:
	var state: Dictionary = view.states[0]
	state["action"] = ""
	state["clock"] = 0.0
	state["facing"] = 1
	state["last_visual_action"] = ""
	state["last_visual_elapsed"] = -1.0
	state["last_dodge_time"] = 0.0


func _simulate(view, loaded: Dictionary, action: String, dt: float, ticks: int) -> Array:
	_reset_state(view)
	var fighter := {
		"x": 100.0,
		"visual_action": action if action in ["attack", "hit", "skill"] else "",
		"visual_elapsed": 0.0,
		"dodge_time": 0.0,
		"guard": action == "guard",
		"visual_moving": action == "move",
	}
	var samples := []
	for tick in ticks:
		view.advance(0, fighter, true, 200.0, 0.0 if tick == 0 else dt)
		var frame: Dictionary = view.current_frame(0)
		samples.append([tick * dt, int(frame["frame"]), String(frame["action"])])
	return samples


func _check_playback(loaded: Dictionary) -> void:
	var timing_cases := 0
	for action_name in loaded["actions"]:
		var action: Dictionary = loaded["actions"][action_name]
		var frames: Array = action["frames"]
		for index in range(frames.size() - 1):
			var boundary: float = frames[index]["end"]
			var before_ok: bool = helper.frame_at(action, boundary - 0.0001) == index
			var at_ok: bool = helper.frame_at(action, boundary) == index + 1
			if not _check(before_ok and at_ok, "%s boundary %.6f: frame %d before, %d at the exact boundary" % [action_name, boundary, index, index + 1]):
				return
			timing_cases += 1
		var duration: float = action["duration"]
		if bool(action["loop"]):
			var loop_ok: bool = helper.frame_at(action, duration) == 0 and helper.frame_at(action, duration - 0.0001) == frames.size() - 1
			if not _check(loop_ok, "%s loop wraps to frame 0 exactly at %.6f" % [action_name, duration]):
				return
		else:
			var hold_ok: bool = helper.frame_at(action, duration) == frames.size() - 1 and helper.frame_at(action, duration + 0.5) == frames.size() - 1
			if not _check(hold_ok, "%s one-shot holds its last frame at and after %.6f" % [action_name, duration]):
				return
		timing_cases += 2
	# Shared 30/60 timestamps, both through frame_at and through the real advance() clock.
	for action_name in loaded["actions"]:
		var action: Dictionary = loaded["actions"][action_name]
		for tick in range(121):
			var t30 := float(tick) / 30.0
			var t60 := float(tick * 2) / 60.0
			if helper.frame_at(action, t30) != helper.frame_at(action, t60):
				_check(false, "%s differs between shared 30/60 timestamps %.6f" % [action_name, t30])
				return
		timing_cases += 1
	_check(timing_cases > 0, "all action boundaries and shared 30/60 frame_at timestamps are deterministic (%d cases)" % timing_cases)
	var view = _view_for(loaded)
	var playback := {}
	for action_name in ["idle", "move", "guard", "attack"]:
		var s30 := _simulate(view, loaded, action_name, 1.0 / 30.0, 60)
		var s60 := _simulate(view, loaded, action_name, 1.0 / 60.0, 120)
		var same := true
		var oracle_ok := true
		for tick in s30.size():
			var a: Array = s30[tick]
			var b: Array = s60[tick * 2]
			same = same and absf(float(a[0]) - float(b[0])) < 0.000001 and int(a[1]) == int(b[1]) and String(a[2]) == String(b[2])
			if String(a[2]) == action_name:
				oracle_ok = oracle_ok and int(a[1]) == helper.frame_at(loaded["actions"][action_name], float(a[0]))
		if not _check(same and oracle_ok, "%s playback at 30 and 60 fps agrees at every shared tick and matches the manifest boundary (%d/%d ticks)" % [action_name, s30.size(), s60.size()]):
			return
		playback[action_name] = {"ticks30": s30.size(), "ticks60": s60.size(), "frames": s30.map(func(sample): return sample[1])}
	report["playback"] = playback


func _check_index() -> void:
	helper.clear_cache()
	var index: Dictionary = helper.load_index(HALF_INDEX)
	if not _check(String(index.get("status", "")) == "loaded" and index["sets"].has(HALF_KEY), "half-scale index loads and resolves the heroine key"):
		return
	var view = helper.new()
	var keys: Array[String] = [HALF_KEY]
	view.configure(HALF_INDEX, keys)
	_check(view.index_status == "loaded" and view.loaded_count() == 1 and view.set_status(0) == "loaded" and view.sets[0]["draw_cell"] == Vector2i(68, 72), "configure loads the 0.5 set for the heroine without a runtime insertion")
	var cached_before: int = int(helper.validation_count)
	var loaded_again: Dictionary = helper.load_set(HALF_MANIFEST, HALF_KEY)
	_check(loaded_again["status"] == "loaded" and helper.validation_count == cached_before, "index/configure reuse the validated cache")


func _write_report(status: String) -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
	report["status"] = status
	report["checks"] = checks
	report["failures"] = failures
	report["runId"] = run_id
	report["helperPath"] = HELPER_PATH
	report["helperSha256Bytes"] = FileAccess.get_sha256(ProjectSettings.globalize_path(HELPER_PATH))
	report["helperSha256TextLF"] = FileAccess.get_file_as_string(HELPER_PATH).replace("\r\n", "\n").sha256_text()
	report["fixtureManifest"] = HALF_MANIFEST
	report["fixtureManifestSha256Bytes"] = FileAccess.get_sha256(ProjectSettings.globalize_path(HALF_MANIFEST))
	report["fixtureSheetSha256Bytes"] = FileAccess.get_sha256(ProjectSettings.globalize_path(HALF_DIR + "/rpg-2-star-ocean-the-second_combat-half-scale_sheet_not-art-v01_20261020-154048-7d4bddce.png"))
	report["oldManifestSha256Bytes"] = FileAccess.get_sha256(ProjectSettings.globalize_path(OLD_MANIFEST))
	var path := ProjectSettings.globalize_path(OUT_DIR).path_join("rpg-2-star-ocean-the-second_combat-half-scale_check-report_v01_20261020-154048-7d4bddce.json")
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file != null:
		file.store_string(JSON.stringify(report, "  ") + "\n")
		file.close()
		print("REPORT ", path)
