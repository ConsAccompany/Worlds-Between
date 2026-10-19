extends RefCounted

# ONE immutable-input guard for the opt-in female complete-exploration pilot.
#
# The representative package is an immutable asset contract: the exact known package JSON and
# SOUTH runtime JSON are pinned by raw SHA-256 and are rejected before JSON indexing if unknown,
# mutated or malformed. This is deliberately NOT a general/custom package loader.
#
# Every actual runtime file the driver/constructors read is then checked before any model
# constructor runs:
#   * east/west PXO raw bytes (from package entries) and north PXO raw bytes (known source);
#   * model copy text hashes with sha256-text-lf-v1 (CRLF -> LF only), including NORTH;
#   * 12 idle PNGs per direction (raw bytes, path, decodability, 80x112);
#   * SOUTH v8 PNG raw bytes;
#   * every SOUTH part PNG (raw bytes, 80x120, binary alpha, opaque-texel count);
#   * ZIP open + data.json + required layer entries with exact 80x112 RGBA layer bytes.
# Paths must be normalized res:// paths below the package's asset/script roots; traversal,
# external, user://, absolute and missing paths are refused. All nested values used by the
# driver/constructors are type/range/finiteness checked here.
#
# ROOT: after the 4 model renderers are optimized and the package is regenerated, re-pin
# PINNED_PACKAGE_RAW_SHA256 / PINNED_RUNTIME_RAW_SHA256 (and NORTH_PXO_SHA256 if the source
# PXO changes) and rerun the guard tests.

const PACKAGE_SCHEMA := "worlds-between.female-complete-explore-package.v1"
const RUNTIME_SCHEMA := "worlds-between.female-complete-explore-south-runtime.v1"

const PINNED_PACKAGE_RAW_SHA256 := "8918ccf5ea4517514595091c2b0b90102c49dc70903caead11cc67a8d61bc6b6"
const PINNED_RUNTIME_RAW_SHA256 := "90fcf3ed873be0b67dec823cb09c596550db23553def89f6e899a4976a7a5da8"

const NORTH_PXO := "res://assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-editable_unapproved-v01_20261018-090713-99e861ce.pxo"
const NORTH_PXO_SHA256 := "7ca7dbdffe9787948ea56ae033b55e738cbd3f80bfbd694ed2d3a9a110756ef9"

const DIRECTIONS := ["south", "west", "north", "east"]
const CELL := Vector2i(80, 112)
const SOUTH_CELL := Vector2i(80, 120)
const IDLE_PHASES := 12
const MAX_PHASE_SECONDS := 10.0

const DIR_PREFIXES := {
	"idle": ["res://assets/fexp/"],
	"model": ["res://scripts/fexp/"],
	"pxo": ["res://assets/fexp/", "res://assets/characters/"],
	"parts": ["res://assets/characters/"],
	"v8": ["res://assets/characters/"],
}

static var io_reads := 0
static var zip_opens := 0
static var png_decodes := 0

static func reset_counters() -> void:
	io_reads = 0
	zip_opens = 0
	png_decodes = 0


static func text_lf_sha256(path: String) -> Dictionary:
	var r := _read_bytes(path)
	if not r["ok"]:
		return r
	var src: PackedByteArray = r["bytes"]
	var out := PackedByteArray()
	out.resize(src.size())
	var j := 0
	for i in src.size():
		if src[i] == 13 and i + 1 < src.size() and src[i + 1] == 10:
			continue
		out[j] = src[i]
		j += 1
	out.resize(j)
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(out)
	return {"ok": true, "sha256": ctx.finish().hex_encode()}


# Pinned package/runtime load. Raw SHA is checked BEFORE JSON parse/index; only the two
# representative files are accepted, regardless of the override path spelling.
static func load_pinned(package_path: String, runtime_path: String) -> Dictionary:
	var pp := _res_path(package_path, ["res://"], false)
	if not pp["ok"]:
		return {"ok": false, "stage": "package_path", "error": pp["error"]}
	var pr := _read_bytes(pp["path"], true)
	if not pr["ok"]:
		return {"ok": false, "stage": "package_missing", "error": pr["error"]}
	if String(pr["sha256"]) != PINNED_PACKAGE_RAW_SHA256:
		return {"ok": false, "stage": "package_pin", "error": "package raw sha256 is not the pinned known package"}
	var pj := _parse_json(String(pr["text"]))
	if not pj["ok"]:
		return {"ok": false, "stage": "package_json", "error": pj["error"]}

	var rp := _res_path(runtime_path, ["res://"], false)
	if not rp["ok"]:
		return {"ok": false, "stage": "runtime_path", "error": rp["error"]}
	var rr := _read_bytes(rp["path"], true)
	if not rr["ok"]:
		return {"ok": false, "stage": "runtime_missing", "error": rr["error"]}
	if String(rr["sha256"]) != PINNED_RUNTIME_RAW_SHA256:
		return {"ok": false, "stage": "runtime_pin", "error": "SOUTH runtime raw sha256 is not the pinned known runtime"}
	var rj := _parse_json(String(rr["text"]))
	if not rj["ok"]:
		return {"ok": false, "stage": "runtime_json", "error": rj["error"]}

	var pv := validate_package(pj["data"], {})
	if not pv["ok"]:
		return {"ok": false, "stage": "package_contract", "error": (pv["errors"] as Array)[0]}
	var rv := validate_runtime(rj["data"], {})
	if not rv["ok"]:
		return {"ok": false, "stage": "runtime_contract", "error": (rv["errors"] as Array)[0]}
	return {"ok": true, "package": pj["data"], "runtime": rj["data"],
		"package_path": pp["path"], "runtime_path": rp["path"]}


static func validate_package(data, opts := {}) -> Dictionary:
	var errors: Array[String] = []
	if not data is Dictionary:
		errors.append("package is not a JSON object")
		return {"ok": false, "errors": errors}
	if not data.get("schema") is String or data["schema"] != PACKAGE_SCHEMA:
		errors.append("package schema is not " + PACKAGE_SCHEMA)
	_check_bool(data.get("approved"), "package approved", errors)
	_check_bool(data.get("runtimeDefault"), "package runtimeDefault", errors)
	_check_pair(data.get("pivot"), "package pivot", errors)
	_check_number(data.get("scale"), "package scale", errors, 0.000001, 16.0)
	_check_int(data.get("body_logical_px"), "package body_logical_px", errors, 1, 4096)
	if data.get("pivot") is Array and data["pivot"].size() == 2:
		if _num(data["pivot"][0]) != 40.0 or _num(data["pivot"][1]) != 104.0:
			errors.append("package pivot is not the known [40, 104]")

	var allow_fixtures := bool(opts.get("allow_fixtures", false))
	var verify_pixels := bool(opts.get("verify_pixels", true))

	var models = data.get("models")
	if not models is Dictionary or models.size() != 3 or not models.has_all(["east", "west", "north"]):
		errors.append("package models must be exactly east, west and north")
	if models is Dictionary and models.size() == 3:
		for d in ["east", "west", "north"]:
			_check_res(models[d], "package model " + d, DIR_PREFIXES["model"], allow_fixtures, errors, true)

	var south_model = data.get("south_model")
	_check_res(south_model, "package south_model", DIR_PREFIXES["model"], allow_fixtures, errors, true)

	_validate_idle(data.get("idle"), allow_fixtures, verify_pixels, errors)
	var model_copies := _validate_entries(data.get("entries"), allow_fixtures, verify_pixels, errors)
	if models is Dictionary and models.size() == 3:
		for d in ["east", "west", "north"]:
			if model_copies.has(d) and model_copies[d] != String(models.get(d, "")):
				errors.append("package %s model copy does not match models.%s" % [d, d])
	if south_model is String and model_copies.has("south") and model_copies["south"] != String(south_model):
		errors.append("package south model copy does not match south_model")
	return {"ok": errors.is_empty(), "errors": errors}


static func validate_runtime(data, opts := {}) -> Dictionary:
	var errors: Array[String] = []
	if not data is Dictionary:
		errors.append("SOUTH runtime is not a JSON object")
		return {"ok": false, "errors": errors}
	if not data.get("schema") is String or data["schema"] != RUNTIME_SCHEMA:
		errors.append("SOUTH runtime schema is not " + RUNTIME_SCHEMA)
	_check_bool(data.get("approved"), "SOUTH runtime approved", errors)
	var runtime_manifest = data.get("manifest")
	if runtime_manifest is Dictionary:
		_check_pair(runtime_manifest.get("cell"), "SOUTH runtime manifest.cell", errors)
		_check_pair(runtime_manifest.get("v8_cell"), "SOUTH runtime manifest.v8_cell", errors)
		_check_pair(runtime_manifest.get("ground_pin_cell"), "SOUTH runtime manifest.ground_pin_cell", errors)
		if runtime_manifest.get("cell") is Array and runtime_manifest["cell"].size() == 2:
			if _num(runtime_manifest["cell"][0]) != 80.0 or _num(runtime_manifest["cell"][1]) != 120.0:
				errors.append("SOUTH manifest.cell is not the known [80, 120]")
		if runtime_manifest.get("v8_cell") is Array and runtime_manifest["v8_cell"].size() == 2:
			if _num(runtime_manifest["v8_cell"][0]) != 80.0 or _num(runtime_manifest["v8_cell"][1]) != 112.0:
				errors.append("SOUTH manifest.v8_cell is not the known [80, 112]")
		if runtime_manifest.get("ground_pin_cell") is Array and runtime_manifest["ground_pin_cell"].size() == 2:
			if _num(runtime_manifest["ground_pin_cell"][0]) != 40.0 or _num(runtime_manifest["ground_pin_cell"][1]) != 104.0:
				errors.append("SOUTH manifest.ground_pin_cell is not the known [40, 104]")

	var allow_fixtures := bool(opts.get("allow_fixtures", false))
	var verify_pixels := bool(opts.get("verify_pixels", true))
	var manifest = data.get("manifest")
	if not manifest is Dictionary:
		errors.append("SOUTH manifest is not an object")
	else:
		_validate_manifest(manifest, errors)
	_validate_art(data.get("art_amendment"), errors)
	_validate_leg_rule(data.get("leg_rule"), errors)
	_check_int(data.get("island_max_texels"), "SOUTH island_max_texels", errors, 1, 4096)
	_check_bool(data.get("stagger"), "SOUTH stagger", errors)
	_check_number(data.get("shadow_alpha"), "SOUTH shadow_alpha", errors, 0.0, 1.0)

	var v8 = data.get("v8_path")
	_check_res(v8, "SOUTH v8_path", DIR_PREFIXES["v8"], allow_fixtures, errors, true)
	var v8_sha = data.get("v8_sha256")
	_check_hash(v8_sha, "SOUTH v8_sha256", errors)
	if v8 is String and v8_sha is String:
		_check_raw_hash(v8, String(v8_sha), "SOUTH v8_path", errors)
		if verify_pixels:
			_check_image(v8, CELL, "SOUTH v8_path", errors, false)
	_check_string(data.get("v10r1_manifest"), "SOUTH v10r1_manifest", errors)
	_check_hash(data.get("v10r1_manifest_sha256_text_lf_v1"), "SOUTH v10r1_manifest_sha256_text_lf_v1", errors)

	_validate_parts(data.get("part_lists"), allow_fixtures, verify_pixels, errors)
	return {"ok": errors.is_empty(), "errors": errors}


static func validate_pxo(path: String, expected_sha: String, cell: Vector2i) -> Dictionary:
	var errors: Array[String] = []
	if not path.begins_with("res://") or not FileAccess.file_exists(path):
		errors.append("PXO does not exist: " + path)
		return {"ok": false, "errors": errors}
	_check_raw_hash(path, expected_sha, "PXO " + path, errors)
	if not errors.is_empty():
		return {"ok": false, "errors": errors}
	var z := ZIPReader.new()
	zip_opens += 1
	var err := z.open(ProjectSettings.globalize_path(path))
	if err != OK:
		errors.append("PXO ZIP open failed (%d): %s" % [err, path])
		return {"ok": false, "errors": errors}
	var files := z.get_files()
	if not files.has("data.json"):
		errors.append("PXO has no data.json: " + path)
		z.close()
		return {"ok": false, "errors": errors}
	var dj := _parse_json(z.read_file("data.json").get_string_from_utf8())
	if not dj["ok"] or not dj["data"] is Dictionary:
		errors.append("PXO data.json is not a JSON object: " + path)
		z.close()
		return {"ok": false, "errors": errors}
	var d: Dictionary = dj["data"]
	if _num(d.get("size_x")) != float(cell.x) or _num(d.get("size_y")) != float(cell.y):
		errors.append("PXO data.json size is not %dx%d: %s" % [cell.x, cell.y, path])
	var layers = d.get("layers")
	if not layers is Array or layers.is_empty() or layers.size() > 256:
		errors.append("PXO layers must be a non-empty array: " + path)
		z.close()
		return {"ok": false, "errors": errors}
	for i in layers.size():
		var layer = layers[i]
		if not layer is Dictionary:
			errors.append("PXO layer %d is not an object: %s" % [i + 1, path])
			continue
		var name = layer.get("name")
		if not name is String or String(name).is_empty():
			errors.append("PXO layer %d has no name: %s" % [i + 1, path])
			continue
		if String(name) == "guides":
			continue
		var entry := "image_data/frames/1/layer_%d" % (i + 1)
		if not files.has(entry):
			errors.append("PXO is missing %s: %s" % [entry, path])
			continue
		var bytes := z.read_file(entry)
		if bytes.size() != cell.x * cell.y * 4:
			errors.append("PXO %s is %d bytes, expected %d: %s" % [entry, bytes.size(), cell.x * cell.y * 4, path])
	z.close()
	return {"ok": errors.is_empty(), "errors": errors}


static func _validate_idle(idle, allow_fixtures: bool, verify_pixels: bool, errors: Array[String]) -> void:
	if not idle is Dictionary:
		errors.append("package idle is not an object")
		return
	_check_pair(idle.get("cell"), "package idle cell", errors)
	_check_pair(idle.get("pivot"), "package idle pivot", errors)
	_check_number(idle.get("scale"), "package idle scale", errors, 0.000001, 16.0)
	if idle.get("cell") is Array and idle["cell"].size() == 2:
		if _num(idle["cell"][0]) != 80.0 or _num(idle["cell"][1]) != 112.0:
			errors.append("package idle cell is not the known [80, 112]")
	var seconds = idle.get("phase_seconds")
	if not seconds is Array or seconds.size() != IDLE_PHASES:
		errors.append("package idle phase_seconds must be exactly %d numbers" % IDLE_PHASES)
	else:
		for i in seconds.size():
			_check_number(seconds[i], "package idle phase_seconds[%d]" % i, errors, 0.000001, MAX_PHASE_SECONDS)
	var dirs = idle.get("directions")
	if not dirs is Dictionary or dirs.size() != 4 or not dirs.has_all(DIRECTIONS):
		errors.append("package idle directions must be exactly south, west, north and east")
		return
	for d in DIRECTIONS:
		var frames = dirs[d]
		if not frames is Array or frames.size() != IDLE_PHASES:
			errors.append("package idle %s must have exactly %d frames" % [d, IDLE_PHASES])
			continue
		var by_sha := {}
		for i in frames.size():
			var f = frames[i]
			var where := "package idle %s[%d]" % [d, i]
			if not f is Dictionary:
				errors.append(where + " is not an object")
				continue
			if not f.get("file") is String:
				errors.append(where + " file is not a string")
				continue
			var fp := _res_path(f["file"], DIR_PREFIXES["idle"], allow_fixtures, true)
			if not fp["ok"]:
				errors.append(where + ": " + fp["error"])
				continue
			if not _check_hash(f.get("sha256"), where + " sha256", errors):
				continue
			if f.has("source") and not f["source"] is String:
				errors.append(where + " source is not a string")
			if not _check_raw_hash(fp["path"], String(f["sha256"]), where, errors):
				continue
			if verify_pixels and not by_sha.has(String(f["sha256"])):
				by_sha[String(f["sha256"])] = true
				_check_image(fp["path"], CELL, where, errors, false)


static func _validate_entries(entries, allow_fixtures: bool, verify_pixels: bool, errors: Array[String]) -> Dictionary:
	var copies := {}
	if not entries is Array or entries.is_empty():
		errors.append("package entries must be a non-empty array")
		return copies
	var seen := {}
	var roles := ["east-pxo", "west-pxo", "east-model", "west-model", "north-model", "south-model", "south-chain", "idle-manifest"]
	for i in entries.size():
		var e = entries[i]
		var where := "package entries[%d]" % i
		if not e is Dictionary:
			errors.append(where + " is not an object")
			continue
		var role = e.get("role")
		if not role is String or not roles.has(String(role)):
			errors.append(where + " has an unknown role")
			continue
		var r := String(role)
		if r != "south-chain":
			if seen.has(r):
				errors.append("package has more than one %s entry" % r)
				continue
			seen[r] = true
		if e.has("source"):
			if not e["source"] is String or String(e["source"]).is_empty():
				errors.append(where + " source is not a non-empty string")
		elif r == "south-chain" or r == "idle-manifest":
			errors.append(where + " source is not a non-empty string")
		if e.has("source_sha256_text_lf_v1") and not _check_hash(e["source_sha256_text_lf_v1"], where + " source_sha256_text_lf_v1", errors):
			pass
		if r == "south-chain":
			if not e.get("classes") is Array or (e["classes"] as Array).is_empty():
				errors.append(where + " classes must be a non-empty array")
			else:
				for c in e["classes"]:
					if not c is String or String(c).is_empty():
						errors.append(where + " has a non-string class")
			continue
		if r == "idle-manifest":
			continue
		if not e.get("copy") is String:
			errors.append(where + " copy is not a string")
			continue
		var prefixes := DIR_PREFIXES["model"] if r.ends_with("-model") else DIR_PREFIXES["pxo"]
		var cp := _res_path(_copy_path(e["copy"]), prefixes, allow_fixtures, true)
		if not cp["ok"]:
			errors.append(where + ": " + cp["error"])
			continue
		if not _check_file_exists(cp["path"], where, errors):
			continue
		if r.ends_with("-pxo"):
			var sha = e.get("sha256_bytes")
			if not _check_hash(sha, where + " sha256_bytes", errors):
				continue
			if not _check_raw_hash(cp["path"], String(sha), where, errors):
				continue
			if not verify_pixels:
				# ZIP structure is still mandatory.
				pass
			var pv := validate_pxo(cp["path"], String(sha), CELL)
			for x in pv["errors"]:
				errors.append(String(x))
		elif r.ends_with("-model"):
			var lf = e.get("copy_sha256_text_lf_v1")
			if not _check_hash(lf, where + " copy_sha256_text_lf_v1", errors):
				continue
			var got := text_lf_sha256(cp["path"])
			if not got["ok"]:
				errors.append(where + ": " + got["error"])
			elif String(got["sha256"]) != String(lf).to_lower():
				errors.append(where + " text-LF copy hash mismatch")
			if r == "east-model":
				copies["east"] = cp["path"]
			elif r == "west-model":
				copies["west"] = cp["path"]
			elif r == "north-model":
				copies["north"] = cp["path"]
			elif r == "south-model":
				copies["south"] = cp["path"]
	for required in ["east-pxo", "west-pxo", "east-model", "west-model", "north-model", "south-model"]:
		if not seen.has(required):
			errors.append("package is missing the " + required + " entry")
	if seen.has("north-model"):
		var nv := validate_pxo(NORTH_PXO, NORTH_PXO_SHA256, CELL)
		for x in nv["errors"]:
			errors.append("NORTH " + String(x))
	return copies


static func _validate_manifest(m: Dictionary, errors: Array[String]) -> void:
	var display = m.get("display")
	if not display is Dictionary:
		errors.append("SOUTH manifest.display is not an object")
	else:
		_check_number(display.get("scale"), "SOUTH display scale", errors, 0.000001, 16.0)
		_check_number(display.get("logical_height_px"), "SOUTH display logical_height_px", errors, 1.0, 4096.0)
		var shadow = display.get("shadow")
		if not shadow is Dictionary:
			errors.append("SOUTH display.shadow is not an object")
		else:
			_check_number(shadow.get("opacity"), "SOUTH display.shadow.opacity", errors, 0.0, 1.0)
			_check_string(shadow.get("colour"), "SOUTH display.shadow.colour", errors)
	var rig = m.get("rig")
	if not rig is Dictionary:
		errors.append("SOUTH manifest.rig is not an object")
	else:
		for side in ["vl", "vr"]:
			var gr = rig.get("ground_rows")
			if not gr is Dictionary:
				errors.append("SOUTH rig.ground_rows is not an object")
				break
			_check_number(gr.get(side), "SOUTH rig.ground_rows." + side, errors, 0.0, float(SOUTH_CELL.y))
			var kb = rig.get("knee_band_rows")
			if not kb is Dictionary:
				errors.append("SOUTH rig.knee_band_rows is not an object")
				break
			var band = kb.get(side)
			if not band is Array or band.size() != 2:
				errors.append("SOUTH rig.knee_band_rows." + side + " must be two rows")
			else:
				_check_number(band[0], "SOUTH rig.knee_band_rows." + side + "[0]", errors, 0.0, float(SOUTH_CELL.y))
				_check_number(band[1], "SOUTH rig.knee_band_rows." + side + "[1]", errors, 0.0, float(SOUTH_CELL.y))
				if _num(band[1]) < _num(band[0]):
					errors.append("SOUTH rig.knee_band_rows." + side + " is reversed")
			var inward = rig.get("inward_dx")
			if not inward is Dictionary:
				errors.append("SOUTH rig.inward_dx is not an object")
				break
			_check_int(inward.get(side), "SOUTH rig.inward_dx." + side, errors, -8, 8)
		_check_int(rig.get("hip_row"), "SOUTH rig.hip_row", errors, 0, SOUTH_CELL.y)
		_check_int(rig.get("boot_top_row"), "SOUTH rig.boot_top_row", errors, 0, SOUTH_CELL.y)
		if _num(rig.get("hip_row", -1)) >= _num(rig.get("boot_top_row", -1)):
			errors.append("SOUTH rig hip_row must be above boot_top_row")
		_check_string_array(rig.get("boot_views"), "SOUTH rig.boot_views", errors)
		_check_string_array(rig.get("stance_views"), "SOUTH rig.stance_views", errors)
		_check_string_array(rig.get("arm_poses"), "SOUTH rig.arm_poses", errors)
		_check_number_array(rig.get("hair_cape_dy"), "SOUTH rig.hair_cape_dy", errors)
		_check_number_array(rig.get("torso_shift_dx"), "SOUTH rig.torso_shift_dx", errors)
	var gait = m.get("gait")
	if not gait is Dictionary:
		errors.append("SOUTH manifest.gait is not an object")
	else:
		_check_int(gait.get("stride_px"), "SOUTH gait.stride_px", errors, 1, 4096)
		_check_int(gait.get("stance_px"), "SOUTH gait.stance_px", errors, 1, 4096)
		_check_int(gait.get("land_offset"), "SOUTH gait.land_offset", errors, -4096, 4096)
		_check_int(gait.get("liftoff_offset"), "SOUTH gait.liftoff_offset", errors, -4096, 4096)
		_check_pair_dict(gait.get("phase_offset_px"), "SOUTH gait.phase_offset_px", errors)
		_check_number_array(gait.get("bob_stance_q"), "SOUTH gait.bob_stance_q", errors)
		_check_number_array(gait.get("torso_shift_stance_q"), "SOUTH gait.torso_shift_stance_q", errors)
		_check_side_dict(gait.get("arm_peak_px"), "SOUTH gait.arm_peak_px", ["L", "R"], errors)
		_check_number_array(gait.get("arm_pose_bands_px"), "SOUTH gait.arm_pose_bands_px", errors)
		_check_number(gait.get("hair_lag_px"), "SOUTH gait.hair_lag_px", errors, 0.0, 4096.0)
		_check_number(gait.get("cape_shift_lag_px"), "SOUTH gait.cape_shift_lag_px", errors, 0.0, 4096.0)
		_check_key_pairs(gait.get("stance_roll"), "SOUTH gait.stance_roll", errors, 2)
		_check_key_pairs(gait.get("stance_knee_kin"), "SOUTH gait.stance_knee_kin", errors, 2)
		_check_key_pairs(gait.get("bob_levels"), "SOUTH gait.bob_levels", errors, 2)
		_check_swing_keys(gait.get("swing_keys"), "SOUTH gait.swing_keys", errors)
	var stop = m.get("stop")
	if not stop is Dictionary:
		errors.append("SOUTH manifest.stop is not an object")
	else:
		_check_number(stop.get("settle_gap_ms"), "SOUTH stop.settle_gap_ms", errors, 0.000001, 10000.0)
		_check_number(stop.get("hold_shift_ms"), "SOUTH stop.hold_shift_ms", errors, 0.0, 10000.0)
		_check_bool(stop.get("no_pose_skip"), "SOUTH stop.no_pose_skip", errors)
		for key in ["arm_step_ms", "settle_ms", "land_ms_base", "land_ms_per_px", "land_ms_per_lift",
				"land_ms_max", "shuffle_ms_base", "shuffle_ms_per_px", "shuffle_ms_max",
				"stop_hair_lag_ms", "hair_lag_ms", "stop_cape_lag_ms"]:
			_check_number(stop.get(key), "SOUTH stop." + key, errors, 0.0, 10000.0)
	var restart = m.get("restart")
	if not restart is Dictionary:
		errors.append("SOUTH manifest.restart is not an object")
	else:
		_check_int(restart.get("replan_lift_min"), "SOUTH restart.replan_lift_min", errors, -64, 64)
		_check_int(restart.get("replan_lift_max"), "SOUTH restart.replan_lift_max", errors, -64, 64)
		if restart.has("v07_rise_lock"):
			_check_bool(restart["v07_rise_lock"], "SOUTH restart.v07_rise_lock", errors)


static func _validate_art(art, errors: Array[String]) -> void:
	if not art is Dictionary:
		errors.append("SOUTH art_amendment is not an object")
		return
	_check_int(art.get("coat_hem_row"), "SOUTH art.coat_hem_row", errors, 0, SOUTH_CELL.y)
	_check_int(art.get("seam_row0"), "SOUTH art.seam_row0", errors, 0, SOUTH_CELL.y)
	_check_number(art.get("kick_drop_rows"), "SOUTH art.kick_drop_rows", errors, -64.0, 64.0)
	var shades = art.get("shin_shade_rgb")
	if not shades is Dictionary:
		errors.append("SOUTH art.shin_shade_rgb is not an object")
	else:
		for k in shades:
			if not k is String or not Color.html_is_valid(String(k)):
				errors.append("SOUTH art.shin_shade_rgb has an invalid colour key")
			if not shades[k] is String or not Color.html_is_valid(String(shades[k])):
				errors.append("SOUTH art.shin_shade_rgb has an invalid colour value")
	var kick = art.get("kick_boot_rows")
	if not kick is Dictionary:
		errors.append("SOUTH art.kick_boot_rows is not an object")
	else:
		for side in ["vl", "vr"]:
			var rows = kick.get(side)
			if not rows is Array or rows.is_empty():
				errors.append("SOUTH art.kick_boot_rows." + side + " is not a non-empty array")
				continue
			for row in rows:
				if not row is Array or row.size() != 2 or not _finite(row[0]) or not row[1] is String:
					errors.append("SOUTH art.kick_boot_rows." + side + " has a malformed row")
	var knee = art.get("knee_fwd")
	if not knee is Dictionary:
		errors.append("SOUTH art.knee_fwd is not an object")


static func _validate_leg_rule(rule, errors: Array[String]) -> void:
	if not rule is Dictionary:
		errors.append("SOUTH leg_rule is not an object")
		return
	_check_int(rule.get("n_fold_rows"), "SOUTH leg_rule.n_fold_rows", errors, 1, 128)
	_check_int(rule.get("hips_bottom_row"), "SOUTH leg_rule.hips_bottom_row", errors, 0, SOUTH_CELL.y)
	_check_string_array(rule.get("tuck_views"), "SOUTH leg_rule.tuck_views", errors)
	_check_string(rule.get("rule"), "SOUTH leg_rule.rule", errors)


static func _validate_parts(part_lists, allow_fixtures: bool, verify_pixels: bool, errors: Array[String]) -> void:
	if not part_lists is Array or part_lists.is_empty() or part_lists.size() != 3:
		errors.append("SOUTH part_lists must be the three known source layers")
		return
	var roles := {}
	for pi in part_lists.size():
		var pair = part_lists[pi]
		if not pair is Array or pair.size() != 2:
			errors.append("SOUTH part_lists[%d] is not [entries, dir]" % pi)
			continue
		var entries = pair[0]
		var dir = pair[1]
		if not entries is Array or entries.is_empty():
			errors.append("SOUTH part_lists[%d] entries must be a non-empty array" % pi)
			continue
		var dp := _res_dir(dir, DIR_PREFIXES["parts"], allow_fixtures, true)
		if not dp["ok"]:
			errors.append("SOUTH part_lists[%d]: %s" % [pi, dp["error"]])
			continue
		for ei in entries.size():
			var e = entries[ei]
			var where := "SOUTH part_lists[%d][%d]" % [pi, ei]
			if not e is Dictionary:
				errors.append(where + " is not an object")
				continue
			var role = e.get("role")
			if not role is String or String(role).is_empty():
				errors.append(where + " role is not a non-empty string")
				continue
			roles[String(role)] = true
			var file = e.get("file")
			if not file is String:
				errors.append(where + " file is not a string")
				continue
			var f := String(file)
			if f.is_empty() or f.contains("/") or f.contains("\\") or f.contains(".."):
				errors.append(where + " file must be a plain file name")
				continue
			var file_dir = e.get("file_dir")
			if file_dir != null:
				if not file_dir is String:
					errors.append(where + " file_dir is not a string")
				else:
					var fd := _res_dir(_copy_path(file_dir), DIR_PREFIXES["parts"], allow_fixtures, false)
					if not fd["ok"]:
						errors.append(where + " file_dir: " + fd["error"])
					elif fd["path"] != dp["path"]:
						errors.append(where + " file_dir does not match part_lists dir")
			var full := String(dp["path"]) + f
			var fp := _res_path(full, DIR_PREFIXES["parts"], allow_fixtures, true)
			if not fp["ok"]:
				errors.append(where + ": " + fp["error"])
				continue
			if not _check_file_exists(fp["path"], where, errors):
				continue
			var sha = e.get("sha256")
			if not _check_hash(sha, where + " sha256", errors):
				continue
			if not _check_raw_hash(fp["path"], String(sha), where, errors):
				continue
			_check_number(e.get("opaque_texels"), where + " opaque_texels", errors, 0.0, float(SOUTH_CELL.x * SOUTH_CELL.y))
			if verify_pixels and _finite(e.get("opaque_texels")):
				_check_part_image(fp["path"], where, int(_num(e.get("opaque_texels"))), errors)
	var required := []
	for side in ["vl", "vr"]:
		required.append("leg-src-" + side)
		required.append("knee-" + side + "-fwd")
		for v in ["v8", "strike", "heelup", "toe", "hang", "reach", "kick"]:
			required.append("boot-%s-%s" % [side, v])
		for l in range(4):
			required.append("shadow-%s-l%d" % [side, l])
		for pose in ["B1", "B2", "N", "F1", "F2"]:
			for part in ["back", "seam", "front"]:
				required.append("arm-%s-%s-%s" % [side, pose, part])
	for h in ["m1", "0", "p1"]:
		required.append("hair-hdy-" + h)
		required.append("cape-hdy-" + h)
	for r in ["hips", "coat-skirt", "torso", "head"]:
		required.append(r)
	for r in required:
		if not roles.has(r):
			errors.append("SOUTH part_lists is missing role " + r)


static func _check_part_image(path: String, where: String, expected_opaque: int, errors: Array[String]) -> void:
	if not FileAccess.file_exists(path):
		errors.append(where + " file does not exist: " + path)
		return
	png_decodes += 1
	var img := Image.load_from_file(ProjectSettings.globalize_path(path))
	if img == null:
		errors.append(where + " PNG did not decode")
		return
	if img.is_empty():
		errors.append(where + " PNG is empty")
		return
	if img.get_size() != SOUTH_CELL:
		errors.append(where + " PNG is %s, not %s" % [str(img.get_size()), str(SOUTH_CELL)])
		return
	img.convert(Image.FORMAT_RGBA8)
	var bytes := img.get_data()
	var opaque := 0
	var partial := 0
	for i in range(3, bytes.size(), 4):
		var a := bytes[i]
		if a == 255:
			opaque += 1
		elif a != 0:
			partial += 1
	if partial > 0:
		errors.append(where + " PNG has %d partial-alpha texels" % partial)
	if opaque != expected_opaque:
		errors.append(where + " PNG has %d opaque texels, metadata says %d" % [opaque, expected_opaque])


static func _check_image(path: String, expected: Vector2i, where: String, errors: Array[String], expect_opaque: bool) -> void:
	if not FileAccess.file_exists(path):
		errors.append(where + " file does not exist: " + path)
		return
	png_decodes += 1
	var img := Image.load_from_file(ProjectSettings.globalize_path(path))
	if img == null:
		errors.append(where + " PNG did not decode")
		return
	if img.is_empty():
		errors.append(where + " PNG is empty")
		return
	if img.get_size() != expected:
		errors.append(where + " PNG is %s, not %s" % [str(img.get_size()), str(expected)])
		return
	if expect_opaque:
		img.convert(Image.FORMAT_RGBA8)
		if img.get_used_rect().size.x <= 0:
			errors.append(where + " PNG has no opaque texels")


static func _read_bytes(path: String, decode_text := false) -> Dictionary:
	if not (path.begins_with("res://") or path.begins_with("user://")) or not FileAccess.file_exists(path):
		return {"ok": false, "error": "file does not exist: " + path}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {"ok": false, "error": "cannot open: " + path}
	io_reads += 1
	var n := f.get_length()
	var bytes := f.get_buffer(n)
	f.close()
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(bytes)
	return {"ok": true, "bytes": bytes, "text": bytes.get_string_from_utf8() if decode_text else "", "sha256": ctx.finish().hex_encode()}


static func _parse_json(text: String) -> Dictionary:
	var j := JSON.new()
	if j.parse(text) != OK:
		return {"ok": false, "error": "JSON parse failed at line %d: %s" % [j.get_error_line(), j.get_error_message()]}
	return {"ok": true, "data": j.data}


static func _check_res(raw, where: String, prefixes: Array, allow_fixtures: bool, errors: Array[String], must_exist: bool = false) -> bool:
	var r := _res_path(raw, prefixes, allow_fixtures, must_exist)
	if not r["ok"]:
		errors.append(where + ": " + String(r["error"]))
		return false
	return true


static func _res_path(raw, prefixes: Array, allow_fixtures: bool, must_exist: bool = false) -> Dictionary:
	if not raw is String:
		return {"ok": false, "error": "path is not a string"}
	var s := String(raw)
	if s.is_empty() or not s.begins_with("res://"):
		return {"ok": false, "error": "path is not below res://: " + s}
	var rest := s.substr(6)
	if rest.is_empty() or rest.contains("..") or rest.contains("\\") or rest.contains("//") or rest.contains(":"):
		return {"ok": false, "error": "path is not a normalized res:// path: " + s}
	if s.ends_with("/"):
		return {"ok": false, "error": "path names a directory: " + s}
	if s.simplify_path() != s:
		return {"ok": false, "error": "path is not normalized: " + s}
	var allowed: Array = prefixes.duplicate()
	if allow_fixtures:
		allowed.append("res://tests/fixtures/")
	var ok := false
	for p in allowed:
		if s.begins_with(String(p)):
			ok = true
			break
	if not ok:
		return {"ok": false, "error": "path is outside the known roots: " + s}
	if must_exist and not FileAccess.file_exists(s):
		return {"ok": false, "error": "path does not exist: " + s}
	return {"ok": true, "path": s}


static func _res_dir(raw, prefixes: Array, allow_fixtures: bool, require_slash := true) -> Dictionary:
	if not raw is String:
		return {"ok": false, "error": "directory is not a string"}
	var s := String(raw)
	if s.is_empty() or not s.begins_with("res://"):
		return {"ok": false, "error": "directory is not a res:// path: " + s}
	if not s.ends_with("/"):
		if require_slash:
			return {"ok": false, "error": "directory is not a trailing-slash res:// path: " + s}
		s += "/"
	var rest := s.substr(6, s.length() - 7)
	if rest.is_empty() or rest.contains("..") or rest.contains("\\") or rest.contains("//") or rest.contains(":"):
		return {"ok": false, "error": "directory is not normalized: " + s}
	var simplified := s.simplify_path()
	if not simplified.ends_with("/"):
		simplified += "/"
	if simplified != s:
		return {"ok": false, "error": "directory is not normalized: " + s}
	var allowed: Array = prefixes.duplicate()
	if allow_fixtures:
		allowed.append("res://tests/fixtures/")
	var ok := false
	for p in allowed:
		if s.begins_with(String(p)):
			ok = true
			break
	if not ok:
		return {"ok": false, "error": "directory is outside the known roots: " + s}
	return {"ok": true, "path": s}


static func _copy_path(raw) -> String:
	if raw is String and String(raw).begins_with("game/"):
		return "res://" + String(raw).substr(5)
	return raw


static func _check_file_exists(path: String, where: String, errors: Array[String]) -> bool:
	if not FileAccess.file_exists(path):
		errors.append(where + " file does not exist: " + path)
		return false
	return true


static func _check_raw_hash(path: String, expected: String, where: String, errors: Array[String]) -> bool:
	if not FileAccess.file_exists(path):
		errors.append(where + " file does not exist: " + path)
		return false
	io_reads += 1
	var got := FileAccess.get_sha256(path)
	if got != String(expected).to_lower():
		errors.append(where + " raw sha256 mismatch")
		return false
	return true


static func _check_hash(value, where: String, errors: Array[String]) -> bool:
	if not value is String:
		errors.append(where + " is not a string")
		return false
	var s := String(value)
	if s.length() != 64:
		errors.append(where + " is not a 64-hex SHA-256")
		return false
	for i in s.length():
		var c := s.substr(i, 1)
		if not ((c >= "0" and c <= "9") or (c >= "a" and c <= "f") or (c >= "A" and c <= "F")):
			errors.append(where + " is not a 64-hex SHA-256")
			return false
	return true


static func _finite(value) -> bool:
	return (value is int) or (value is float and is_finite(value))


static func _num(value) -> float:
	if value is int:
		return float(value)
	if value is float and is_finite(value):
		return value
	return NAN


static func _check_number(value, where: String, errors: Array[String], minv: float, maxv: float) -> bool:
	if not _finite(value):
		errors.append(where + " is not a finite number")
		return false
	var v := _num(value)
	if v < minv or v > maxv:
		errors.append(where + " is out of range")
		return false
	return true


static func _check_int(value, where: String, errors: Array[String], minv: int, maxv: int) -> bool:
	if not _finite(value):
		errors.append(where + " is not a finite integer")
		return false
	var v := _num(value)
	if v != floor(v) or v < float(minv) or v > float(maxv):
		errors.append(where + " is not an integer in range")
		return false
	return true


static func _check_bool(value, where: String, errors: Array[String]) -> bool:
	if not value is bool:
		errors.append(where + " is not a boolean")
		return false
	return true


static func _check_string(value, where: String, errors: Array[String]) -> bool:
	if not value is String or String(value).is_empty():
		errors.append(where + " is not a non-empty string")
		return false
	return true


static func _check_string_array(value, where: String, errors: Array[String]) -> bool:
	if not value is Array or (value as Array).is_empty():
		errors.append(where + " is not a non-empty array")
		return false
	for v in value:
		if not v is String or String(v).is_empty():
			errors.append(where + " has a non-string item")
			return false
	return true


static func _check_number_array(value, where: String, errors: Array[String]) -> bool:
	if not value is Array or (value as Array).is_empty():
		errors.append(where + " is not a non-empty array")
		return false
	for v in value:
		if not _finite(v):
			errors.append(where + " has a non-finite item")
			return false
	return true


static func _check_pair(value, where: String, errors: Array[String]) -> bool:
	if not value is Array or (value as Array).size() != 2:
		errors.append(where + " is not a two-item array")
		return false
	for v in value:
		if not _finite(v):
			errors.append(where + " has a non-finite item")
			return false
	return true


static func _check_pair_dict(value, where: String, errors: Array[String]) -> bool:
	return _check_side_dict(value, where, ["vl", "vr"], errors)


static func _check_side_dict(value, where: String, keys: Array, errors: Array[String]) -> bool:
	if not value is Dictionary or not value.has_all(keys):
		errors.append(where + " is not a " + str(keys) + " object")
		return false
	var ok := true
	for k in keys:
		ok = _check_number(value[k], where + "." + String(k), errors, -4096.0, 4096.0) and ok
	return ok


static func _check_key_pairs(value, where: String, errors: Array[String], width: int) -> bool:
	if not value is Array or (value as Array).is_empty():
		errors.append(where + " is not a non-empty key array")
		return false
	for item in value:
		if not item is Array or (item as Array).size() != width:
			errors.append(where + " has a malformed key")
			return false
		if not _finite(item[0]):
			errors.append(where + " has a non-finite key coordinate")
			return false
		if width == 2 and not (_finite(item[1]) or item[1] is String):
			errors.append(where + " has a malformed key value")
			return false
	return true


static func _check_swing_keys(value, where: String, errors: Array[String]) -> bool:
	if not value is Array or (value as Array).is_empty():
		errors.append(where + " is not a non-empty key array")
		return false
	for item in value:
		if not item is Array or (item as Array).size() != 5:
			errors.append(where + " has a malformed swing key")
			return false
		for i in [0, 1, 2, 4]:
			if not _finite(item[i]):
				errors.append(where + " has a non-finite swing value")
				return false
		if not item[3] is String:
			errors.append(where + " has a non-string swing view")
			return false
	return true
