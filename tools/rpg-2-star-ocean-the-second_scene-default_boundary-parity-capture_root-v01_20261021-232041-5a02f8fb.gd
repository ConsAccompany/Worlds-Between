extends SceneTree
# sdef35 scene-default boundary/parity/capture probe (support evidence only; root owns integration/status).
# Direct deterministic scene setup, NOT physical game input: fixed 640x360, frozen nodes, isolated profile.
# Modes:
#   --mode=baseline : capture ordinary default-off frames before the prepared policy exists (policy optional).
#   --mode=parity   : capture again after the policy copy; require policy all-false, no preview flags,
#                     then pixel-equal the baseline and check scene scripts/actor transforms.
#   --mode=preview  : --scene=city|ruins|room2|loop; turn on only that existing reversible switch,
#                     prove the other three targets and accepted controls stay equal, then roll back.
# No runtime/art/default/source/ledger/index edits. No new assets. Technical only, no art/human approval.

const POLICY_PATH := "res://scripts/sdef35/rpg-2-star-ocean-the-second_mvp-scene-defaults_policy_prepared-v01_20261021-231349-a83c4bae.gd"
const LOOP_SCENE := "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn"
const V05_SELECTOR_PATH := "res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-scene-opt-in-selector_unapproved-v05_20261017-234337-84862412.gd"
const V05_SCENE := "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v05_20261017-234337-84862412.tscn"
const V13_SELECTOR_PATH := "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v13_20261018-135539-63201688.gd"
const CITY_V06_PATH := "res://scripts/city_hall_park_v06_scene.gd"
const ROOM2_FLAG := "--wdc-records-chamber-v01"
const TARGET_IDS := ["scifi.city", "scifi.ruins", "scifi.ruins-survey-inner", "scifi.loop"]
const TARGETS := [
	{"id": "city", "destination": "scifi.city", "scene": "res://scenes/scifi_exploration_area.tscn", "room": 1},
	{"id": "ruins", "destination": "scifi.ruins", "scene": "res://scenes/scifi_exploration_area.tscn", "room": 1},
	{"id": "room2", "destination": "scifi.ruins", "scene": "res://scenes/survey_annex.tscn", "room": 2},
	{"id": "loop", "destination": "scifi.loop", "scene": LOOP_SCENE, "room": 1},
]
const CONTROLS := [
	{"id": "annex-room1", "destination": "scifi.ruins", "scene": "res://scenes/survey_annex.tscn", "room": 1},
	{"id": "city-room2-accepted", "destination": "scifi.city", "scene": "res://scenes/survey_annex.tscn", "room": 2},
]
const PREVIEW_FLAGS := ["--city-hall-park-v06", "--wdc-capitol-west-v13", "--wdc-capitol-west-v12r2", "--wdc-capitol-west-v12r1", "--wdc-capitol-west-v12", ROOM2_FLAG, "--chicago-state-lake-v05", "--chicago-state-lake-v04", "--chicago-state-lake-v03r1", "--chicago-state-lake-v03"]
const SOURCES := ["res://scripts/scifi_exploration_area.gd", "res://scripts/survey_annex.gd", CITY_V06_PATH, V13_SELECTOR_PATH, V05_SELECTOR_PATH, "res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v02_20261017-160959-55667f46.gd", "res://scripts/app_state.gd"]

var checks := 0
var failures: Array[String] = []
var out_dir := ""
var tag := ""
var mode := ""
var revision := ""
var baseline: Dictionary = {}
var cases: Array = []
var policy: Dictionary = {}
var source_before: Dictionary = {}
var scene_overrides := {}
var actual_game_input := false


func ck(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures.append(label)
		print("SDEF35_FAIL ", label)


func _initialize() -> void:
	call_deferred("run")
	create_timer(180.0).timeout.connect(func(): print("SDEF35_TIMEOUT"); quit(2))


func arg(name: String, fallback: String = "") -> String:
	var args := OS.get_cmdline_user_args()
	for i in args.size():
		if args[i] == name and i + 1 < args.size():
			return args[i + 1]
		if String(args[i]).begins_with(name + "="):
			return String(args[i]).substr(name.length() + 1)
	return fallback


func sha(path: String) -> String:
	return FileAccess.get_sha256(path) if FileAccess.file_exists(path) else ""


func image_sha(image: Image) -> String:
	if image == null:
		return ""
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	image.convert(Image.FORMAT_RGBA8)
	ctx.update(image.get_data())
	return ctx.finish().hex_encode()


func diff_pixels(a: Image, b: Image) -> int:
	if a == null or b == null or a.get_size() != b.get_size():
		return -1
	a.convert(Image.FORMAT_RGBA8)
	b.convert(Image.FORMAT_RGBA8)
	var x := a.get_data()
	var y := b.get_data()
	var total := 0
	for i in range(0, x.size(), 4):
		if x[i] != y[i] or x[i + 1] != y[i + 1] or x[i + 2] != y[i + 2] or x[i + 3] != y[i + 3]:
			total += 1
	return total


func freeze(node: Node) -> void:
	node.process_mode = Node.PROCESS_MODE_DISABLED
	node.set_process(false)
	node.set_physics_process(false)
	node.set_process_input(false)
	node.set_process_unhandled_input(false)
	if node is AnimationPlayer:
		node.stop()
	if node is AnimatedSprite2D:
		node.stop()
	if node is Timer:
		node.stop()
	for child in node.get_children():
		freeze(child)


func detach_audio(node: Node) -> void:
	for child in node.get_children():
		if child is AudioStreamPlayer or child is AudioStreamPlayer2D or child is AudioStreamPlayer3D:
			child.stop()
			child.stream = null
		detach_audio(child)


func kill_tweens() -> void:
	for tween in get_processed_tweens():
		tween.kill()


func make_image(c: Dictionary, language: String) -> Dictionary:
	begin_state(c, language)
	var node: Node
	if c.id == "loop":
		ck(change_scene_to_file(c.scene) == OK, "actual Loop entry scene loads")
		for i in 6:
			await process_frame
		node = current_scene
	else:
		node = load(c.scene).instantiate()
		root.add_child(node)
	freeze(node)
	if node.has_method("_refresh_text"):
		node._refresh_text()
	kill_tweens()
	for i in 3:
		await process_frame
	await RenderingServer.frame_post_draw
	var image: Image = root.get_texture().get_image()
	image.convert(Image.FORMAT_RGBA8)
	var hero = node.get("hero")
	var has_hero := hero != null
	var info := {"id":c.id,"language":language,"scene":c.scene,"room":c.room,
		"sceneScript":node.get_script().resource_path,
		"heroPosition":var_to_str(hero.position) if has_hero else "",
		"heroScale":var_to_str(hero.scale) if has_hero else "",
		"heroOffset":var_to_str(hero.offset) if has_hero else "",
		"heroFlipH":hero.flip_h if has_hero else false,
		"heroTextureSha256":image_sha(hero.texture.get_image()) if has_hero and hero.texture != null else "",
		"room2DirectSetup":false,"native640":image.get_size()==Vector2i(640,360)}
	detach_audio(node)
	if current_scene == node:
		current_scene = null
	root.remove_child(node)
	node.free()
	await process_frame
	info["image"] = image
	info["rgbaSha256"] = image_sha(image)
	return info


func begin_state(c: Dictionary, language: String) -> void:
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = "female"
	app.language = language
	app.current_destination_id = c.destination
	app.current_annex_room = c.room
	app.show_initial_guide = false
	app.returning_from_battle = false
	app.resume_area_pending = false
	app.resume_annex_pending = false
	app.play_time_seconds = 84.0
	app.run_active = false
	app.set_process(false)


func save_case(c: Dictionary, language: String, label: String) -> Dictionary:
	var first: Dictionary = await make_image(c, language)
	var second: Dictionary = await make_image(c, language)
	var image: Image = first.image
	var row: Dictionary = first.duplicate()
	row.erase("image")
	row["label"] = label
	row["repeatDiffPixels"] = diff_pixels(image, second.image)
	row["file"] = "rpg-2-star-ocean-the-second_scene-defaults_%s_%s_%s_640_sdef35-v01_%s.png" % [c.id, language, label, tag]
	ck(image.save_png(out_dir.path_join(row.file)) == OK, "save png " + row.file)
	row["pngSha256"] = sha(out_dir.path_join(row.file))
	row["baselineDiffPixels"] = -2
	if not baseline.is_empty():
		var found := 0
		for item in baseline.get("cases", []):
			if String(item.get("id", "")) == c.id and String(item.get("language", "")) == language:
				found += 1
				var src := Image.load_from_file(String(baseline["outDir"]).path_join(String(item["file"])))
				ck(src != null, "baseline image loads " + c.id + " " + language)
				row["baselineDiffPixels"] = diff_pixels(src, image)
		ck(found == 1, "one baseline row " + c.id + " " + language)
	return row


func case_by_id(id: String) -> Dictionary:
	for c in TARGETS:
		if c.id == id:
			return c
	for c in CONTROLS:
		if c.id == id:
			return c
	return {}


func collect_policy_pairs(value: Variant, depth: int, out: Dictionary) -> void:
	if depth > 4:
		return
	if typeof(value) == TYPE_DICTIONARY:
		for key in value:
			var k := String(key)
			var v = value[key]
			if TARGET_IDS.has(k) and typeof(v) == TYPE_BOOL:
				out[k] = v
			else:
				collect_policy_pairs(v, depth + 1, out)
	elif typeof(value) == TYPE_ARRAY:
		for item in value:
			collect_policy_pairs(item, depth + 1, out)


func probe_policy() -> Dictionary:
	var result := {"present":false,"loaded":false,"defaults":{},"allFourFalse":false,"constants":[]}
	if not ResourceLoader.exists(POLICY_PATH):
		return result
	result["present"] = true
	var script = load(POLICY_PATH)
	if script == null:
		return result
	result["loaded"] = true
	var constants: Dictionary = script.get_script_constant_map()
	result["constants"] = constants.keys()
	var defaults := {}
	var all_false := true
	for key in ["CITY_V06_DEFAULT","RUINS_V13_DEFAULT","RECORDS_ROOM2_DEFAULT","CHICAGO_V05_DEFAULT"]:
		if not constants.has(key) or typeof(constants[key]) != TYPE_BOOL:
			all_false = false
		else:
			defaults[key] = constants[key]
			all_false = all_false and not constants[key]
	result["defaults"] = defaults
	result["allFourFalse"] = all_false and defaults.size() == 4
	return result


func preview_flags() -> Array:
	var found := []
	for a in OS.get_cmdline_user_args():
		if PREVIEW_FLAGS.has(a):
			found.append(a)
	return found


func switch_state() -> Dictionary:
	var city = load(CITY_V06_PATH)
	var v13 = load(V13_SELECTOR_PATH)
	var v05 = load(V05_SELECTOR_PATH)
	return {
		"cityV06Enabled": city.enabled(),
		"ruinsV13Enabled": v13.v13_enabled(),
		"loopV05Enabled": v05.v05_enabled(),
		"room2Flag": OS.get_cmdline_user_args().has(ROOM2_FLAG),
		"cityOverride": city.enabled_override,
		"ruinsOverride": v13.v13_override,
		"loopOverride": v05.v05_override,
	}


func reset_overrides() -> void:
	load(CITY_V06_PATH).enabled_override = -1
	load(V13_SELECTOR_PATH).v13_override = -1
	load(V05_SELECTOR_PATH).v05_override = -1
	if ResourceLoader.exists(POLICY_PATH):
		load(POLICY_PATH).clear_preview()
	scene_overrides.clear()


func apply_preview(scene_id: String) -> Dictionary:
	reset_overrides()
	var keys := {"city":"city","ruins":"ruins","room2":"ruins_survey_inner","loop":"chicago_loop"}
	var detail := {"scene":scene_id,"kind":"prepared policy override only; actual scene entry, no direct build call","applied":false}
	if ResourceLoader.exists(POLICY_PATH) and keys.has(scene_id):
		var script = load(POLICY_PATH)
		script.preview_override[keys[scene_id]] = true
		detail["applied"] = script.default_on(keys[scene_id])
	return detail


func loop_root_script() -> String:
	var node: Node = load(LOOP_SCENE).instantiate()
	var path := String(node.get_script().resource_path)
	node.free()
	return path


func write_report(result: String) -> void:
	var after := {}
	for path in SOURCES:
		after[path] = sha(path)
	var report := {
		"mode": mode, "result": result, "failed": failures, "checkCount": checks,
		"testedRevision": revision, "policyPath": POLICY_PATH, "policy": policy,
		"policyPresent": policy.get("present", false), "policyAllFourFalse": policy.get("allFourFalse", false),
		"previewFlags": preview_flags(), "switchState": switch_state(),
		"loopNormalSceneRootScript": loop_root_script(),
		"sourceRawSha256Before": source_before, "sourceRawSha256After": after,
		"probePath": get_script().resource_path, "probeRawSha256": sha(get_script().resource_path),
		"tag": tag, "outDir": out_dir, "baselinePath": String(baseline.get("path", "")),
		"cases": cases, "inputKind": "direct deterministic scene setup", "actualGameInput": actual_game_input,
		"directSetup": true, "motionOrArtApproval": false, "humanPlaytest": false,
		"scope": "sdef35 boundary/parity/capture support only; root owns integration comparison and final gate",
		"completedAt": Time.get_datetime_string_from_system(true),
	}
	var f := FileAccess.open(out_dir.path_join("rpg-2-star-ocean-the-second_scene-defaults_%s_proof_sdef35-v01_%s.json" % [mode, tag]), FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(report, "  ") + "\n")
		f.close()
	else:
		failures.append("report writable")


func finish() -> void:
	var ok := failures.is_empty()
	write_report("PASS" if ok else "FAIL")
	print("SDEF35_RESULT ", "PASS" if ok else "FAIL", " mode=", mode, " checks=", checks, " failures=", failures.size())
	if ok:
		print("SDEF35_PASS mode=", mode, " checks=", checks)
		quit(0)
	else:
		print("SDEF35_FAILURES ", JSON.stringify(failures))
		quit(1)


func run() -> void:
	mode = arg("--mode")
	out_dir = arg("--out")
	tag = arg("--tag")
	revision = arg("--revision", "unknown")
	var baseline_path := arg("--baseline")
	var scene_id := arg("--scene")
	ck(mode in ["baseline","parity","preview"], "valid mode")
	ck(out_dir != "" and tag != "", "output directory and tag")
	ck(mode != "preview" or scene_id in ["city","ruins","room2","loop"], "valid preview target")
	DirAccess.make_dir_recursive_absolute(out_dir)
	root.size = Vector2i(640,360)
	root.gui_disable_input = true
	SaveStore.root_path = "user://test-saves/sdef35-" + tag
	for path in SOURCES:
		source_before[path] = sha(path)
	policy = probe_policy()
	if baseline_path != "" and FileAccess.file_exists(baseline_path):
		baseline = JSON.parse_string(FileAccess.get_file_as_string(baseline_path))
		baseline["path"] = baseline_path
	if mode != "baseline":
		ck(not baseline.is_empty(), "baseline report present")
		ck(policy.get("loaded",false) and policy.get("allFourFalse",false), "four actual bool defaults remain false")
		ck(preview_flags().is_empty(), "no candidate CLI flags: policy-only test")
	var all_cases: Array = TARGETS.duplicate()
	all_cases.append_array(CONTROLS)
	for language in ["en","zh"]:
		reset_overrides()
		if mode != "preview":
			for c in all_cases:
				var row: Dictionary = await save_case(c,language,"default")
				ck(row.repeatDiffPixels == 0, "repeat pixels exact " + c.id + " " + language)
				ck(row.native640, "native640 " + c.id)
				if mode != "baseline":
					ck(row.baselineDiffPixels == 0, "ordinary default-off pixels exact " + c.id + " " + language)
					var old := {}
					for item in baseline["cases"]:
						if item.id == c.id and item.language == language:
							old = item
					ck(not old.is_empty(), "matching baseline metadata " + c.id)
					for key in ["heroTextureSha256","heroPosition","heroScale","heroOffset","heroFlipH"]:
						ck(row[key] == old[key], "actor " + key + " preserved " + c.id)
					if c.id == "loop":
						var v04 := "res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-scene-opt-in-selector_unapproved-v04_20261017-230650-c0d4b7f0.gd"
						ck(old.sceneScript == v04 and row.sceneScript == V05_SELECTOR_PATH, "Loop intentional inert v04-to-v05 selector wiring; exact pixels above")
					else:
						ck(row.sceneScript == old.sceneScript, "ordinary script preserved " + c.id)
				cases.append(row)
		if mode == "preview":
			var detail := apply_preview(scene_id)
			ck(detail.applied, "only target policy preview enabled")
			var target: Dictionary = await save_case(case_by_id(scene_id),language,"preview")
			ck(target.repeatDiffPixels == 0 and target.baselineDiffPixels > 0, "preview deterministic and differs from old target")
			if scene_id == "loop":
				var expected: Node = load(V05_SCENE).instantiate()
				var expected_script: String = expected.get_script().resource_path
				expected.free()
				ck(target.sceneScript == expected_script, "actual Loop entry hands off to v05 block")
			cases.append(target)
			for c in all_cases:
				if c.id != scene_id:
					var control: Dictionary = await save_case(c,language,"preview-control")
					ck(control.repeatDiffPixels == 0 and control.baselineDiffPixels == 0, "other scene unchanged under target preview " + c.id)
					cases.append(control)
			reset_overrides()
			var rolled: Dictionary = await save_case(case_by_id(scene_id),language,"rollback")
			ck(rolled.repeatDiffPixels == 0 and rolled.baselineDiffPixels == 0, "exact policy rollback restores target " + scene_id)
			cases.append(rolled)
	reset_overrides()
	finish()
