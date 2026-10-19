extends SceneTree

# Focused guard contract for the opt-in female complete-exploration driver.
# Malformed cases are one-field mutations of the representative package/runtime plus a few
# tiny generated fixtures (corrupt/short ZIP, wrong-size PNG, CRLF model copy). Integration
# cases prove whole-package refusal, off-path/flag-off no-IO, rejected-attach atomicity,
# two-driver gait isolation, valid source rest and unchanged turn/re-press/floor/contact
# behavior with the body and shadow oracles on.

const Pilot := preload("res://scripts/fexp/rpg-2-star-ocean-the-second_female-complete-explore_driver_pilot-v01_20261019-184900-f2c0a7e1.gd")
const Guard := preload("res://scripts/fexp/rpg-2-star-ocean-the-second_female-complete-explore_input-guard_v01_20261019-190507-a7d3e9b1.gd")
const PACKAGE := "res://data/fexp/rpg-2-star-ocean-the-second_female-complete-explore_package_v01_20261019-184500-f2c0a7e1.json"
const RUNTIME := "res://data/fexp/rpg-2-star-ocean-the-second_female-complete-explore_south-runtime_v01_20261019-184900-f2c0a7e1.json"
const FIXTURE_DIR := "res://tests/fixtures/rpg-2-star-ocean-the-second_fexp-guard-fixtures_v01_20261019-190507-a7d3e9b1"
const FIXTURE_REL := "tests/fixtures/rpg-2-star-ocean-the-second_fexp-guard-fixtures_v01_20261019-190507-a7d3e9b1"

var failures: Array[String] = []
var checks := 0
var package_base: Dictionary
var runtime_base: Dictionary
var fixtures := {}
var created_fixtures: Array[String] = []
var targets: Array = []


func _init() -> void:
	package_base = _load_json(PACKAGE)
	runtime_base = _load_json(RUNTIME)
	if package_base.is_empty() or runtime_base.is_empty():
		_finish()
		return
	_make_fixtures()
	_run_malformed_cases()
	_run_integration_cases()
	_finish()


func _finish() -> void:
	Pilot.clear_cache()
	for t in targets:
		if is_instance_valid(t):
			t.free()
	targets.clear()
	if failures.is_empty():
		_cleanup()
		print("FEXP_GUARD_TESTS_OK checks=%d" % checks)
		quit(0)
	else:
		print("FEXP_GUARD_TESTS_FAIL checks=%d failures=%d" % [checks, failures.size()])
		for f in failures:
			print("FAIL_DETAIL " + f)
		quit(1)


func _check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures.append(label)
		print("FAIL " + label)


func _contains(errors: Array, needle: String) -> bool:
	for e in errors:
		if String(e).find(needle) >= 0:
			return true
	return false


func _load_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		_check(false, "missing JSON " + path)
		return {}
	var data = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not data is Dictionary:
		_check(false, "JSON is not an object " + path)
		return {}
	return data


func _set_path(root, path: Array, value) -> bool:
	var cur = root
	for i in range(path.size() - 1):
		if cur is Dictionary and path[i] is String and cur.has(path[i]):
			cur = cur[path[i]]
		elif cur is Array and path[i] is int and path[i] >= 0 and path[i] < cur.size():
			cur = cur[path[i]]
		else:
			return false
	if cur is Dictionary and path[path.size() - 1] is String:
		cur[path[path.size() - 1]] = value
		return true
	if cur is Array and path[path.size() - 1] is int and path[path.size() - 1] < cur.size():
		cur[path[path.size() - 1]] = value
		return true
	return false


func _entry(package: Dictionary, role: String) -> Dictionary:
	for e in package.get("entries", []):
		if e is Dictionary and String(e.get("role", "")) == role:
			return e
	return {}


func _package_case(label: String, path: Array, value, needle: String, opts := {}) -> void:
	var p := package_base.duplicate(true)
	if not _set_path(p, path, value):
		_check(false, label + " setup path")
		return
	var r := Guard.validate_package(p, opts)
	_check(not r["ok"] and _contains(r["errors"], needle), label + " -> " + str(r["errors"]))


func _runtime_case(label: String, path: Array, value, needle: String, opts := {}) -> void:
	var p := runtime_base.duplicate(true)
	if not _set_path(p, path, value):
		_check(false, label + " setup path")
		return
	var r := Guard.validate_runtime(p, opts)
	_check(not r["ok"] and _contains(r["errors"], needle), label + " -> " + str(r["errors"]))


func _run_malformed_cases() -> void:
	var base_pkg := Guard.validate_package(package_base, {})
	_check(base_pkg["ok"], "representative package validates: " + str(base_pkg["errors"]))
	var base_rt := Guard.validate_runtime(runtime_base, {})
	_check(base_rt["ok"], "representative SOUTH runtime validates: " + str(base_rt["errors"]))

	var empty_read := Guard._read_bytes(fixtures["empty"], true)
	_check(empty_read["ok"] and empty_read["bytes"].is_empty() and empty_read["sha256"] == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "empty bytes hash is exact without engine error")
	var empty_text := Guard.text_lf_sha256(fixtures["empty"])
	_check(empty_text["ok"] and empty_text["sha256"] == empty_read["sha256"], "empty text-LF hash is exact without engine error")
	var empty_pin := Guard.load_pinned(fixtures["empty"], RUNTIME)
	_check(not empty_pin["ok"] and empty_pin["stage"] == "package_pin", "empty package refused at raw pin")
	empty_pin = Guard.load_pinned(PACKAGE, fixtures["empty"])
	_check(not empty_pin["ok"] and empty_pin["stage"] == "runtime_pin", "empty runtime refused at raw pin")
	_package_case("three wrong model keys", ["models"], {"one": "x", "two": "y", "three": "z"}, "exactly east")
	_package_case("Dictionary model value", ["models", "east"], {}, "path is not a string")

	# Package-level nested types/paths/phase arrays.
	_package_case("package schema type", ["schema"], 7, "schema")
	_package_case("package entries type", ["entries"], {}, "entries")
	_package_case("package models missing north", ["models"], {"east": package_base["models"]["east"], "west": package_base["models"]["west"]}, "models")
	_package_case("model external path", ["models", "east"], "C:/outside.gd", "res://")
	_package_case("model traversal path", ["models", "east"], "res://scripts/fexp/../../outside.gd", "normalized")
	_package_case("model missing path", ["models", "east"], "res://scripts/fexp/missing-model.gd", "does not exist")
	_package_case("south model wrong root", ["south_model"], "res://assets/fexp/not-a-script.gd", "known roots")
	_package_case("idle phase_seconds type", ["idle", "phase_seconds"], "0.4", "phase_seconds")
	_package_case("idle phase count", ["idle", "phase_seconds"], package_base["idle"]["phase_seconds"].slice(0, 11), "phase_seconds")
	_package_case("idle negative duration", ["idle", "phase_seconds", 0], -1.0, "out of range")
	_package_case("idle non-finite duration", ["idle", "phase_seconds", 0], "nan", "finite")
	_package_case("idle direction missing", ["idle", "directions"], {"south": package_base["idle"]["directions"]["south"]}, "directions")
	_package_case("idle frame count", ["idle", "directions", "north"], package_base["idle"]["directions"]["north"].slice(0, 11), "exactly 12")
	_package_case("idle frame external path", ["idle", "directions", "south", 0, "file"], "user://outside.png", "res://")
	_package_case("idle frame traversal", ["idle", "directions", "south", 0, "file"], "res://assets/fexp/../outside.png", "normalized")
	_package_case("idle frame missing", ["idle", "directions", "south", 0, "file"], "res://assets/fexp/missing.png", "does not exist")
	_package_case("idle frame hash", ["idle", "directions", "south", 0, "sha256"], "0".repeat(64), "raw sha256")
	_package_case("idle cell shape", ["idle", "cell"], [80], "two-item")

	var p := package_base.duplicate(true)
	var em := _entry(p, "east-model")
	em["copy_sha256_text_lf_v1"] = "0".repeat(64)
	var r := Guard.validate_package(p, {"verify_pixels": false})
	_check(not r["ok"] and _contains(r["errors"], "text-LF copy hash"), "model text-LF copy hash -> " + str(r["errors"]))

	p = package_base.duplicate(true)
	var ep = _entry(p, "east-pxo")
	ep["sha256_bytes"] = "0".repeat(64)
	r = Guard.validate_package(p, {"verify_pixels": false})
	_check(not r["ok"] and _contains(r["errors"], "raw sha256"), "east PXO raw hash -> " + str(r["errors"]))

	p = package_base.duplicate(true)
	p["entries"].append({"role": "unknown-runtime-input", "source": "x", "copy": "game/assets/fexp/x.pxo", "sha256_bytes": "0".repeat(64)})
	r = Guard.validate_package(p, {"verify_pixels": false})
	_check(not r["ok"] and _contains(r["errors"], "unknown role"), "unknown package role -> " + str(r["errors"]))

	# ZIP open/required entries/expected layer bytes before constructors.
	p = package_base.duplicate(true)
	ep = _entry(p, "east-pxo")
	ep["copy"] = fixtures["corrupt_zip"]
	ep["sha256_bytes"] = _hash(fixtures["corrupt_zip"])
	r = Guard.validate_package(p, {"allow_fixtures": true, "verify_pixels": false})
	_check(not r["ok"] and _contains(r["errors"], "ZIP open"), "corrupt ZIP -> " + str(r["errors"]))

	p = package_base.duplicate(true)
	ep = _entry(p, "east-pxo")
	ep["copy"] = fixtures["missing_layer_zip"]
	ep["sha256_bytes"] = _hash(fixtures["missing_layer_zip"])
	r = Guard.validate_package(p, {"allow_fixtures": true, "verify_pixels": false})
	_check(not r["ok"] and _contains(r["errors"], "missing image_data"), "ZIP missing layer -> " + str(r["errors"]))

	p = package_base.duplicate(true)
	ep = _entry(p, "east-pxo")
	ep["copy"] = fixtures["short_layer_zip"]
	ep["sha256_bytes"] = _hash(fixtures["short_layer_zip"])
	r = Guard.validate_package(p, {"allow_fixtures": true, "verify_pixels": false})
	_check(not r["ok"] and _contains(r["errors"], "expected 35840"), "ZIP short layer -> " + str(r["errors"]))

	p = package_base.duplicate(true)
	var f0 = p["idle"]["directions"]["south"][0]
	f0["file"] = fixtures["wrong_size_png"]
	f0["sha256"] = _hash(fixtures["wrong_size_png"])
	r = Guard.validate_package(p, {"allow_fixtures": true, "verify_pixels": true})
	_check(not r["ok"] and _contains(r["errors"], "not (80, 112)"), "wrong-size idle PNG -> " + str(r["errors"]))

	# sha256-text-lf-v1 must normalize CRLF only; a CRLF copy with the LF hash is legitimate.
	p = package_base.duplicate(true)
	var lf_hash: String = Guard.text_lf_sha256(fixtures["crlf_model"])["sha256"]
	p["models"]["east"] = fixtures["crlf_model"]
	var em2 := _entry(p, "east-model")
	em2["copy"] = fixtures["crlf_model"]
	em2["copy_sha256_text_lf_v1"] = lf_hash
	r = Guard.validate_package(p, {"allow_fixtures": true, "verify_pixels": false})
	_check(r["ok"], "CRLF model copy matches text-LF hash: " + str(r["errors"]))

	var nv := Guard.validate_pxo(Guard.NORTH_PXO, Guard.NORTH_PXO_SHA256, Guard.CELL)
	_check(nv["ok"], "NORTH PXO pinned ZIP validates: " + str(nv["errors"]))
	var nb := Guard.validate_pxo(Guard.NORTH_PXO, "0".repeat(64), Guard.CELL)
	_check(not nb["ok"], "NORTH PXO wrong hash refused")

	# Runtime nested types/paths/part hashes and ranges.
	_runtime_case("runtime schema type", ["schema"], 7, "schema")
	_runtime_case("runtime part_lists type", ["part_lists"], {}, "part_lists")
	_runtime_case("runtime part dir external", ["part_lists", 0, 1], "C:/outside/", "res://")
	_runtime_case("runtime part dir traversal", ["part_lists", 0, 1], "res://assets/characters/../fexp/", "normalized")
	_runtime_case("runtime part missing", ["part_lists", 0, 0, 0, "file"], "missing-part.png", "does not exist")
	_runtime_case("runtime part traversal", ["part_lists", 0, 0, 0, "file"], "../outside.png", "plain file name")
	_runtime_case("runtime part hash", ["part_lists", 0, 0, 0, "sha256"], "0".repeat(64), "raw sha256")
	_runtime_case("runtime part opaque count", ["part_lists", 0, 0, 0, "opaque_texels"], -1, "out of range")
	_runtime_case("runtime part file_dir mismatch", ["part_lists", 0, 0, 0, "file_dir"], "game/assets/characters/run-v99-unapproved", "file_dir does not match")
	_runtime_case("runtime island count", ["island_max_texels"], -1, "range")
	_runtime_case("runtime shadow alpha type", ["shadow_alpha"], "0.38", "finite")
	_runtime_case("runtime ground row type", ["manifest", "rig", "ground_rows", "vl"], "100", "finite")
	_runtime_case("runtime hip/boot order", ["manifest", "rig", "boot_top_row"], 10, "above boot_top")
	_runtime_case("runtime leg rule type", ["leg_rule", "n_fold_rows"], null, "finite")
	_runtime_case("runtime tuck views type", ["leg_rule", "tuck_views"], "kick", "non-empty array")
	_runtime_case("runtime gait stride", ["manifest", "gait", "stride_px"], 0, "range")
	_runtime_case("runtime stop bool", ["manifest", "stop", "no_pose_skip"], "yes", "boolean")
	_runtime_case("runtime swing key shape", ["manifest", "gait", "swing_keys", 0], [0.0, 0.0], "malformed swing key")
	_runtime_case("runtime art colour", ["art_amendment", "shin_shade_rgb"], {"not-a-colour": "#ffffff"}, "invalid colour")
	_runtime_case("runtime v8 missing", ["v8_path"], "res://assets/characters/missing-v8.png", "does not exist")
	_runtime_case("runtime v8 hash", ["v8_sha256"], "0".repeat(64), "raw sha256")

	var part_errs: Array[String] = []
	Guard._check_part_image(fixtures["wrong_size_png"], "fixture part", 0, part_errs)
	_check(not part_errs.is_empty(), "wrong-size part PNG refused: " + str(part_errs))
	part_errs = []
	Guard._check_part_image(fixtures["alpha_part_png"], "fixture alpha part", 0, part_errs)
	_check(not part_errs.is_empty(), "partial-alpha part PNG refused: " + str(part_errs))
	part_errs = []
	Guard._check_part_image(fixtures["real_part_png"], "fixture real part", 50, part_errs)
	_check(part_errs.is_empty(), "real part PNG accepted: " + str(part_errs))


func _run_integration_cases() -> void:
	# Flag off before any IO.
	Pilot.enabled_override = 0
	Pilot.package_override = ""
	Pilot.runtime_override = ""
	Pilot.clear_cache()
	Guard.reset_counters()
	var off_target := _target(Vector2(2, 2), true)
	var off_children := off_target.get_child_count()
	var off := Pilot.attach(off_target, "protagonist-female", "south")
	_check(off == null, "flag-off attach returns null")
	_check(Pilot.load_count == 0 and Guard.io_reads == 0, "flag-off attach performs no IO")
	_check(off_target.get_child_count() == off_children and off_target.scale == Vector2(2, 2) and off_target.flip_h, "flag-off leaves target unchanged")

	# Off-path package override is refused before any file read.
	Pilot.enabled_override = 1
	Pilot.package_override = "user://outside-package.json"
	Pilot.clear_cache()
	Guard.reset_counters()
	var offpath_target := _target(Vector2(3, 3), true)
	var offpath_children := offpath_target.get_child_count()
	var offpath := Pilot.attach(offpath_target, "protagonist-female", "south")
	_check(offpath == null and String(Pilot.refusal().get("stage", "")) == "package_path", "off-path package refused")
	_check(Guard.io_reads == 0, "off-path package performs no file read")
	_check(offpath_target.get_child_count() == offpath_children and offpath_target.scale == Vector2(3, 3) and offpath_target.flip_h, "off-path leaves target unchanged")

	# Mutated whole package is refused at the raw pin before JSON indexing/constructors.
	Pilot.package_override = fixtures["mutated_package"]
	Pilot.clear_cache()
	var mut_target := _target(Vector2(4, 4), true)
	var mut_children := mut_target.get_child_count()
	var mut := Pilot.attach(mut_target, "protagonist-female", "south")
	_check(mut == null and String(Pilot.refusal().get("stage", "")) == "package_pin", "mutated package refused at pin: " + str(Pilot.refusal()))
	_check(Pilot.construct_count == 0, "mutated package never constructs models")
	_check(mut_target.get_child_count() == mut_children and mut_target.scale == Vector2(4, 4) and mut_target.flip_h, "mutated package leaves target unchanged")

	Pilot.package_override = fixtures["empty"]
	Pilot.clear_cache()
	var empty_target := _target(Vector2(4, 3), true)
	var empty_children := empty_target.get_child_count()
	var empty_driver = Pilot.attach(empty_target, "protagonist-female", "south")
	_check(empty_driver == null and Pilot.refusal().get("stage") == "package_pin", "empty package attach refuses cleanly")
	_check(Pilot.construct_count == 0 and empty_target.get_child_count() == empty_children and empty_target.scale == Vector2(4, 3) and empty_target.flip_h, "empty attach atomic before constructors and target mutation")

	# Mutated runtime is refused at its raw pin.
	Pilot.package_override = ""
	Pilot.runtime_override = fixtures["mutated_runtime"]
	Pilot.clear_cache()
	var rt_target := _target(Vector2(5, 5), true)
	var rt_children := rt_target.get_child_count()
	var rt := Pilot.attach(rt_target, "protagonist-female", "south")
	_check(rt == null and String(Pilot.refusal().get("stage", "")) == "runtime_pin", "mutated runtime refused at pin: " + str(Pilot.refusal()))
	_check(Pilot.construct_count == 0, "mutated runtime never constructs models")
	_check(rt_target.get_child_count() == rt_children and rt_target.scale == Vector2(5, 5) and rt_target.flip_h, "mutated runtime leaves target unchanged")

	# Off-path runtime override is refused before reading it.
	Pilot.runtime_override = "user://outside-runtime.json"
	Pilot.clear_cache()
	var rto_target := _target(Vector2(6, 6), true)
	var rto_children := rto_target.get_child_count()
	var rto := Pilot.attach(rto_target, "protagonist-female", "south")
	_check(rto == null and String(Pilot.refusal().get("stage", "")) == "runtime_path", "off-path runtime refused")
	_check(rto_target.get_child_count() == rto_children and rto_target.scale == Vector2(6, 6) and rto_target.flip_h, "off-path runtime leaves target unchanged")

	# Valid package: two independent drivers.
	Pilot.package_override = ""
	Pilot.runtime_override = ""
	Pilot.clear_cache()
	Guard.reset_counters()
	var ta := _target(Vector2.ONE, false)
	var tb := _target(Vector2.ONE, false)
	var a = Pilot.attach(ta, "protagonist-female", "south")
	var b = Pilot.attach(tb, "protagonist-female", "south")
	_check(a != null and b != null, "two valid drives attach: " + str(Pilot.refusal()))
	if a == null or b == null:
		return
	_check(ta.scale == Vector2(0.5, 0.5) and not ta.flip_h, "valid attach applies target scale/flip")
	_check(a.runtime["models"]["north"] != b.runtime["models"]["north"], "drivers own distinct NORTH models")
	_check(a.runtime["south_comp"] != b.runtime["south_comp"], "drivers own distinct SOUTH compositors")
	_check(a.runtime["south_rest_shadow"] != b.runtime["south_rest_shadow"], "drivers own distinct SOUTH rest shadows")

	# Valid source rest: model originals/rest snapshots and SOUTH shadow are real.
	var east_original: Image = a.runtime["models"]["east"].original
	_check(east_original != null and east_original.get_size() == Vector2i(80, 112) and not east_original.is_empty(), "EAST source rest image is valid")
	_check(a.runtime["rests"]["north"].has("q") and a.runtime["rests"]["north"].has("mode"), "NORTH rest snapshot captured")
	_check(a.runtime["south_rest_shadow"] is ImageTexture, "SOUTH rest shadow is an ImageTexture")

	# South idle -> move -> stop with body/shadow oracles on.
	a.oracle = true
	a.step(0.016, Vector2(10, 10), Vector2(10, 10), "south")
	_check(a.showing_idle and a.model_mode == "rest", "south rest starts idle")
	_check(a.last_texture == a.assets["idle"]["south"][a.idle_phase()]["texture"], "south rest uses idle phase texture")
	_check(a.shadow.visible, "south rest shows contact shadow")
	_check(_floor_ok(a), "south rest draws on the floor pin")
	a.step(0.1, Vector2(10, 10), Vector2(10, 12), "south")
	_check(not a.showing_idle and String(a.last_key).begins_with("south:"), "south actual move leaves idle")
	_check(a.shadow.visible and a.shadow.texture != null, "south move keeps the contact shadow")
	_check(_floor_ok(a), "south move draws on the floor pin")
	var south_hits := int(a.stats["hits"])
	a.oracle = true
	var south_state = a.last_state.duplicate(true)
	a._show_south(south_state)
	a._show_south(south_state)
	_check(int(a.stats["hits"]) > south_hits and a.oracle_mismatch == 0, "south body/shadow oracle matches on a repeated state")
	var stopped := false
	for i in 30:
		a.step(0.05, Vector2(10, 12), Vector2(10, 12), "south")
		if a.showing_idle and a.model_mode == "rest":
			stopped = true
			break
	_check(stopped, "south stop returns to rest")
	_check(a.shadow.visible and a.oracle_mismatch == 0, "south stop keeps shadow and oracle exact")

	# NORTH turn/re-press + per-driver isolation (north forward = decreasing y).
	var switches := int(a.stats["switches"])
	a.step(0.1, Vector2(10, 12), Vector2(10, 4), "north")
	_check(a.facing == "north" and a.stats["switches"] == switches + 1, "turn to NORTH resets once")
	var a_q := float(a.runtime["models"]["north"].q)
	a.step(0.1, Vector2(10, 4), Vector2(10, 0), "north")
	_check(a.facing == "north" and a.stats["switches"] == switches + 1, "same-facing NORTH re-press keeps live model")
	_check(float(a.runtime["models"]["north"].q) != a_q, "same-facing NORTH re-press advances gait")
	var north_hits := int(a.stats["hits"])
	a.oracle = true
	var north_state = a.last_state.duplicate(true)
	a._show_model(a.runtime["models"]["north"], north_state)
	a._show_model(a.runtime["models"]["north"], north_state)
	_check(int(a.stats["hits"]) > north_hits and a.oracle_mismatch == 0, "NORTH body oracle matches on a cached state")
	_check(_floor_ok(a), "NORTH move draws on the floor pin")
	var a_snapshot := _model_snapshot(a.runtime["models"]["north"])
	b.step(0.1, Vector2(10, 12), Vector2(10, 4), "north")
	_check(_model_snapshot(a.runtime["models"]["north"]) == a_snapshot, "driver B cannot advance driver A's NORTH gait")
	_check(b.runtime["models"]["north"] != a.runtime["models"]["north"], "driver B uses its own NORTH gait")
	b.step(0.1, Vector2(10, 4), Vector2(10, 0), "north")
	a_snapshot = _model_snapshot(a.runtime["models"]["north"])
	_check(_model_snapshot(a.runtime["models"]["north"]) == a_snapshot, "driver B's second step still cannot touch A")

	# SOUTH loco is per driver too.
	a.step(0.1, Vector2(10, 0), Vector2(10, 1), "south")
	b.step(0.1, Vector2(10, 0), Vector2(10, 1), "south")
	_check(a.runtime["south_loco"] != b.runtime["south_loco"], "drivers own distinct SOUTH locos")
	var a_loco_clk := float(a.runtime["south_loco"].clock)
	b.step(0.2, Vector2(10, 1), Vector2(10, 3), "south")
	_check(float(a.runtime["south_loco"].clock) == a_loco_clk, "driver B cannot advance driver A's SOUTH loco")

	# Idle clocks are per driver (settle both SOUTH locos first).
	for i in 30:
		a.step(0.05, Vector2(10, 1), Vector2(10, 1), "south")
		b.step(0.05, Vector2(10, 3), Vector2(10, 3), "south")
	a.step(0.7, Vector2(10, 1), Vector2(10, 1), "south")
	b.step(0.1, Vector2(10, 3), Vector2(10, 3), "south")
	_check(a.idle_clock > b.idle_clock, "idle clocks are per driver")
	_check(a.idle_phase() != b.idle_phase(), "idle phases can differ between drivers")
	_check(a.oracle_mismatch == 0 and b.oracle_mismatch == 0, "per-driver oracles stay exact")


func _floor_ok(driver) -> bool:
	if driver.last_texture == null:
		return false
	return driver.sprite.offset == Vector2(driver.last_texture.get_size()) * 0.5 - Vector2(40.0, 104.0) + Vector2(0.0, 2.0)


func _target(initial_scale: Vector2, initial_flip: bool) -> Sprite2D:
	var t := Sprite2D.new()
	t.scale = initial_scale
	t.flip_h = initial_flip
	t.add_child(Node2D.new())
	targets.append(t)
	return t


func _model_snapshot(model) -> String:
	return "%s|%s|%s" % [str(model.q), str(model.mode), str(model.feet)]


func _make_fixtures() -> void:
	var d := DirAccess.open("res://")
	if d == null:
		_check(false, "cannot open res:// for fixtures")
		return
	var err := d.make_dir_recursive(FIXTURE_REL)
	if err != OK and err != ERR_ALREADY_EXISTS:
		_check(false, "cannot create fixture dir: " + str(err))
		return
	fixtures["empty"] = FIXTURE_DIR + "/rpg-2-star-ocean-the-second_fexp-guard_empty-input_v02_20261019-192404-8ab21e47.bin"
	fixtures["corrupt_zip"] = FIXTURE_DIR + "/corrupt_v01.pxo"
	fixtures["missing_layer_zip"] = FIXTURE_DIR + "/missing-layer_v01.pxo"
	fixtures["short_layer_zip"] = FIXTURE_DIR + "/short-layer_v01.pxo"
	fixtures["wrong_size_png"] = FIXTURE_DIR + "/wrong-size_v01.png"
	fixtures["alpha_part_png"] = FIXTURE_DIR + "/alpha-part_v01.png"
	fixtures["real_part_png"] = FIXTURE_DIR + "/real-part_v01.png"
	fixtures["crlf_model"] = FIXTURE_DIR + "/crlf-model_v01.gd"
	fixtures["mutated_package"] = FIXTURE_DIR + "/mutated-package_v01.json"
	fixtures["mutated_runtime"] = FIXTURE_DIR + "/mutated-runtime_v01.json"
	for k in fixtures:
		_remove(fixtures[k])

	_write_text(fixtures["empty"], "")
	_write_text(fixtures["corrupt_zip"], "this is not a zip")
	var data_json := JSON.stringify({"size_x": 80, "size_y": 112, "layers": [{"name": "body"}]}).to_utf8_buffer()
	_zip(fixtures["missing_layer_zip"], {"data.json": data_json})
	_zip(fixtures["short_layer_zip"], {"data.json": data_json, "image_data/frames/1/layer_1": PackedByteArray([0, 1, 2, 3])})

	var wrong := Image.create(8, 8, false, Image.FORMAT_RGBA8)
	wrong.fill(Color(1, 0, 0, 1))
	_save_png(wrong, fixtures["wrong_size_png"])
	var alpha := Image.create(80, 120, false, Image.FORMAT_RGBA8)
	alpha.fill(Color(0, 0, 0, 0))
	alpha.set_pixel(40, 60, Color(1, 1, 1, 0.5))
	_save_png(alpha, fixtures["alpha_part_png"])
	var real_part := FIXTURE_DIR + "/real-part-source_v01.png"
	_write_text(fixtures["real_part_png"], "")
	var part_src := "res://assets/characters/run-v06-unapproved/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-part-arm-vl-B1-back_unapproved-nonruntime_20261017-211600-57b94879.png"
	var part_bytes := FileAccess.get_file_as_bytes(part_src)
	var pf := FileAccess.open(fixtures["real_part_png"], FileAccess.WRITE)
	if pf != null:
		pf.store_buffer(part_bytes)
		pf.close()
	_write_text(fixtures["crlf_model"], "extends RefCounted\r\nfunc _init():\r\n\tpass\r\n")
	_write_text(fixtures["mutated_package"], FileAccess.get_file_as_string(PACKAGE).replace("\"approved\": false", "\"approved\": true"))
	_write_text(fixtures["mutated_runtime"], FileAccess.get_file_as_string(RUNTIME).replace("\"approved\": false", "\"approved\": true"))


func _zip(path: String, entries: Dictionary) -> void:
	var packer := ZIPPacker.new()
	var err := packer.open(path)
	if err != OK:
		_check(false, "cannot open ZIPPacker " + path + ": " + str(err))
		return
	for name in entries:
		packer.start_file(name)
		packer.write_file(entries[name])
		packer.close_file()
	packer.close()


func _save_png(image: Image, path: String) -> void:
	var err := image.save_png(path)
	if err != OK:
		_check(false, "cannot save fixture PNG " + path + ": " + str(err))


func _write_text(path: String, text: String) -> void:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		_check(false, "cannot write fixture " + path)
		return
	f.store_string(text)
	f.close()
	created_fixtures.append(path)


func _hash(path: String) -> String:
	return FileAccess.get_sha256(path)


func _remove(path: String) -> void:
	if FileAccess.file_exists(path):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))


func _cleanup() -> void:
	for path in created_fixtures:
		_remove(path)
	for k in fixtures:
		_remove(fixtures[k])
	var rel := FIXTURE_REL
	if DirAccess.dir_exists_absolute(ProjectSettings.globalize_path(FIXTURE_DIR)):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(FIXTURE_DIR))
