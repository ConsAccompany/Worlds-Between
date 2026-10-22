extends SceneTree
# Ordinary-default combat-set technical check (cts34). One reusable checker for the four creator-authorized ordinary
# combat sets (protagonist-male, zhao-ling, liang-xu, ji-cheng) plus a heroine-preservation control, through the ACTUAL
# battle_arena ordinary path: no combat_sprite_set / index / member / companion override and no policy configure().
# Setup uses existing AppState methods (begin_new_run / recruit_member): a render fixture, not proof of real recruitment.
# State-machine sections drive the real loaded model with LABELED deterministic fighter fixtures; the handler section uses
# the real arena attack/dodge/skill/enemy-hit handlers. Technical evidence only: no art, motion-fluidity or human acceptance.
# Usage: --script <this> -- <out_dir> <tag> <en|zh> [capture=1|0]
const Loader = preload("res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd")
const ARENA_SCRIPT := "res://scripts/battle_arena.gd"
const ARENA_SCENE := "res://scenes/battle_arena.tscn"
const MALE_DRIVER := "res://scripts/mpath24/rpg-2-star-ocean-the-second_male-playable-path_explore-driver_opt-in-v01_20261021-170200-5e1c24a7.gd"
const HEROINE_POLICY := "res://scripts/hsea18/rpg-2-star-ocean-the-second_heroine-normal-default_policy_runtime-v01_20261021-032237-7c02af94.gd"
const POLICIES := {
	"zhao-ling": "res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_config_opt-in-v01_20261021-223218-3246d731.gd",
	"liang-xu": "res://scripts/lpath30/rpg-2-star-ocean-the-second_liang-playable-path_config_opt-in-v01_20261021-202247-ca439d91.gd",
	"ji-cheng": "res://scripts/jpath33/rpg-2-star-ocean-the-second_ji-playable-path_config_opt-in-v01_20261021-222438-7d4b2e91.gd",
}
const TARGETS := ["protagonist-male", "zhao-ling", "liang-xu", "ji-cheng"]
const COMPANIONS := ["liang-xu", "zhao-ling", "ji-cheng"]
const ACTIONS := ["idle", "move", "guard", "attack", "dodge", "skill", "hit", "defeat"]
const LOOPS := ["idle", "move", "guard"]
const EVENTS := ["attack", "skill", "hit"]
const RATES := [30, 60]
const EPS := 0.000000001

var checks: Array = []
var failures: Array = []
var captures: Array = []
var fixtures_used: Array = []
var target_reports := {}
var current := ""


func ck(ok: bool, label: String) -> void:
	checks.append({"target": current, "check": label, "passed": ok})
	if not ok:
		failures.append(current + ": " + label)
		print("CTS34_FAIL ", current, ": ", label)


func _initialize() -> void:
	call_deferred("run")
	create_timer(240.0).timeout.connect(func(): print("CTS34_TIMEOUT"); quit(2))


func tick() -> void:
	await process_frame
	await RenderingServer.frame_post_draw


func read_json(path: String) -> Variant:
	var text := FileAccess.get_file_as_string(path)
	return JSON.parse_string(text) if text != "" else null


func fixture(label: String) -> void:
	if not fixtures_used.has(label):
		fixtures_used.append(label)


func run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 3 or not args[2] in ["en", "zh"]:
		print("CTS34_USAGE")
		quit(2)
		return
	var out: String = args[0]
	var tag: String = args[1]
	var language: String = args[2]
	var capture := args.size() < 4 or args[3] != "capture=0"
	DirAccess.make_dir_recursive_absolute(out)
	root.size = Vector2i(640, 360)
	current = "preconditions"
	var host = load(ARENA_SCRIPT)
	# Ordinary defaults: every generic and member override must be at its shipped "off" value; this checker sets none.
	ck(host.combat_sprite_set_override == -1, "no generic combat-set enable override")
	ck(host.combat_sprite_set_index_override == "", "no generic combat-set index override")
	ck(host.male_playable_path_index_override == "", "no male actor index override")
	ck(host.companion_combat_member_override == "" and host.companion_combat_index_override == "", "no companion member/index override")
	ck(host.heroine_sea_contact_override == -1, "no heroine contact override")
	for arg in OS.get_cmdline_user_args():
		ck(not arg.begins_with("--combat-sprite-set"), "no combat-set CLI flag " + arg)
	ck(not host.combat_sprite_set_enabled(), "explicit generic combat-set path is off")
	var male_driver = load(MALE_DRIVER)
	ck(male_driver.DEFAULT_ADOPTED == true, "male ordinary default adopted")
	for member in POLICIES:
		var policy = load(POLICIES[member])
		ck(policy.DEFAULT_ADOPTED == true and policy.enabled(), member + " ordinary default adopted and enabled")
		ck(policy.ART_APPROVED == false, member + " art remains unapproved (scope label)")
	for target in TARGETS:
		await check_target(target, language, out, tag, capture)
	await check_female_preserved(language, out, tag, capture)
	var report := {
		"schema": "worlds-between.combat-ordinary-default-check/cts34-v1",
		"scope": "technical: actual battle_arena ordinary defaults; deterministic labeled fixtures + real arena handlers; not art/motion/human acceptance",
		"language": language, "tag": tag, "display": DisplayServer.get_name(),
		"fixturesUsed": fixtures_used, "targets": target_reports,
		"checks": checks, "checkCount": checks.size(), "failures": failures, "captures": captures,
		"passed": failures.is_empty(),
	}
	var path := out.path_join("rpg-2-star-ocean-the-second_combat-set_%s_ordinary-default-check-v01_%s.json" % [language, tag])
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  ") + "\n")
	file.close()
	if failures.is_empty():
		print("CTS34_ALL_PASS language=%s checks=%d captures=%d" % [language, checks.size(), captures.size()])
	else:
		print("CTS34_FAILED language=%s failures=%d checks=%d" % [language, failures.size(), checks.size()])
	quit(0 if failures.is_empty() else 1)


func setup_party(appearance: String, language: String, enemy: String) -> Node:
	var app = root.get_node("AppState")
	app.begin_new_run()
	app.hero_appearance = appearance
	app.language = language
	app.recruit_member("liang-xu")
	app.recruit_member("zhao-ling")
	app.ji_records_checked = true
	app.recruit_member("ji-cheng")
	app.select_destination("ruins" if language == "zh" else "city")
	app.battle_enemy_id = enemy
	return app


func spawn_arena() -> Node:
	var scene = load(ARENA_SCENE).instantiate()
	root.add_child(scene)
	# The arena never steps on its own: every state change below is explicit and recorded.
	scene.set_process(false)
	scene.set_physics_process(false)
	await tick()
	return scene


func free_arena(scene: Node) -> void:
	scene.queue_free()
	await tick()


# Integer oracle in half-ticks (tick_rate 30 -> 60 half-ticks per second), independent of the loader's float clock.
func oracle(raw_action: Dictionary, half_ticks: int) -> int:
	var frames: Array = raw_action["frames"]
	var ends: Array = []
	var total := 0
	for f in frames:
		total += int(f["ticks"]) * 2
		ends.append(total)
	var t := half_ticks
	if bool(raw_action["loop"]) and t >= total:
		var ls := int(raw_action.get("loop_start", 0))
		var start := 0 if ls == 0 else int(ends[ls - 1])
		t = start + (t - start) % (total - start)
	for i in ends.size():
		if t < int(ends[i]):
			return i
	return frames.size() - 1


func fresh_state(model, slot: int) -> void:
	model.states[slot] = {"action": "", "clock": 0.0, "facing": int(model.sets[slot]["facing"]), "last_visual_action": "", "last_visual_elapsed": 0.0, "last_dodge_time": 0.0, "last_event_id": 0}


func base_fixture(scene: Node, slot: int) -> Dictionary:
	var f: Dictionary = scene.fighters[slot].duplicate(true)
	f["visual_action"] = ""
	f["visual_elapsed"] = 0.0
	f["guard"] = false
	f["visual_moving"] = false
	f["dodge_time"] = 0.0
	return f


func drive(f: Dictionary, action: String) -> bool:
	# Returns `alive` for the fixture; sets the fighter fields the loader reads to select `action`.
	match action:
		"move": f["visual_moving"] = true
		"guard": f["guard"] = true
		"dodge": f["dodge_time"] = 100.0
		"attack", "skill", "hit": f["visual_action"] = action
	return action != "defeat"


func expected_geometry(raw: Dictionary, raw_frame: Dictionary, x: float, floor_y: float, mirrored: bool) -> Vector2i:
	var divisor := 2 if float(raw["logical_scale"]) == 0.5 else 1
	var cell_w := int(raw["cell_size"][0]) / divisor
	var pv: Array = raw_frame.get("pivot", raw["pivot"])
	var px := int(pv[0]) / divisor
	var py := int(pv[1]) / divisor
	var ax := roundi(x)
	return Vector2i(ax - px if not mirrored else ax - (cell_w - 1 - px), int(floor_y) - py)


func check_target(target: String, language: String, out: String, tag: String, capture: bool) -> void:
	current = target
	var app = setup_party("male", language, "sentry" if language == "zh" else "patrol")
	var member_id := "hero" if target == "protagonist-male" else target
	var slot: int = app.active_party_ids.find(member_id)
	ck(slot >= 0, "target in active party (fixture recruit)")
	fixture("party via begin_new_run/recruit_member (render fixture, not real recruit proof)")
	var party_before: Array = app.active_party_ids.duplicate()
	var scene = await spawn_arena()
	var host = load(ARENA_SCRIPT)
	ck(not scene.heroine_default_active, "heroine default inactive for male party")
	var model = null
	var index_path := ""
	if target == "protagonist-male":
		index_path = load(MALE_DRIVER).COMBAT_INDEX_PATH
		model = scene.combat_sprite_sets
		ck(model != null, "male ordinary set loaded via combat_sprite_sets")
		if model != null:
			ck(model.index_path == index_path, "male model uses male driver index")
			ck(model.loaded_count() == 1 and model.has_set(slot), "male model holds exactly the hero slot")
		for m in COMPANIONS:
			ck(scene.companion_sets_by_member.has(m), "companion %s also ordinary-loaded alongside male" % m)
	else:
		index_path = load(POLICIES[target]).COMBAT_INDEX_PATH
		ck(scene.companion_sets_by_member.has(target), "companion model present")
		model = scene.companion_sets_by_member.get(target)
		if model != null:
			ck(model.index_path == index_path, "companion model uses its policy index")
			ck(model.loaded_count() == 1 and model.has_set(slot), "companion model holds exactly its own slot")
			ck(int(scene.companion_slot_by_member[target]) == slot, "companion slot map = party slot")
		ck(scene.combat_sprite_sets == null or not scene.combat_sprite_sets.has_set(slot), "hero model does not draw this companion slot")
		for other in scene.companion_sets_by_member:
			if other != target:
				ck(not scene.companion_sets_by_member[other].has_set(slot), "%s model does not take %s slot" % [other, target])
				ck(scene.companion_sets_by_member[other] != model, "%s model object distinct" % other)
	if model == null or not model.has_set(slot):
		target_reports[target] = {"loaded": false}
		await free_arena(scene)
		return
	# Authored-source binding: index has exactly one entry, the target's key, resolving to the manifest the model loaded.
	var index: Variant = read_json(index_path)
	var key: String = Loader.set_key(member_id, "male")
	ck(index is Dictionary and index["sets"].size() == 1 and index["sets"].has(key), "index has exactly the target key " + key)
	var manifest_path: String = index_path.get_base_dir().path_join(String(index["sets"][key]))
	var raw: Variant = read_json(manifest_path)
	ck(raw is Dictionary, "manifest parses")
	var src: Dictionary = model.sets[slot]
	ck(String(raw["character"]["member_id"]) == member_id, "manifest character = target")
	ck(String(src["set_id"]) == String(raw["set_id"]) and src["art_approved"] == false, "loaded set_id matches manifest; art_approved false")
	ck(int(src["facing"]) == (1 if raw["authored_facing"] == "right" else -1), "authored facing")
	var sheet_path: String = manifest_path.get_base_dir().path_join(String(raw["sheet"]))
	var sheet_sha := FileAccess.get_sha256(sheet_path)
	var columns: int = int(src["sheet_size"].x) / int(raw["cell_size"][0])
	for action in ACTIONS:
		ck(raw["actions"].has(action), "authored action present (no fallback) " + action)
		if not raw["actions"].has(action):
			continue
		var ra: Dictionary = raw["actions"][action]
		var la: Dictionary = src["actions"][action]
		ck(String(la["source"]) == action, "clip source is own action " + action)
		ck(bool(la["loop"]) == (action in LOOPS) and bool(ra["loop"]) == (action in LOOPS), "loop mode " + action)
		ck(la["frames"].size() == ra["frames"].size(), "frame count " + action)
		var cum := 0
		for i in ra["frames"].size():
			var rf: Dictionary = ra["frames"][i]
			var lf: Dictionary = la["frames"][i]
			cum += int(rf["ticks"])
			ck(int(lf["cell"]) == int(rf["cell"]), "cell %s/%d" % [action, i])
			var cell_i := int(rf["cell"])
			ck(lf["origin"] == Vector2i(cell_i % columns * int(raw["cell_size"][0]), cell_i / columns * int(raw["cell_size"][1])), "origin %s/%d" % [action, i])
			var pv: Array = rf.get("pivot", raw["pivot"])
			ck(lf["pivot"] == Vector2i(int(pv[0]), int(pv[1])), "pivot %s/%d" % [action, i])
			ck(absf(float(lf["end"]) - float(cum) / float(ra["tick_rate"])) < EPS, "tick end %s/%d" % [action, i])
		ck(int(la.get("duration_ticks", -1)) == cum and absf(float(la["duration"]) - float(cum) / float(ra["tick_rate"])) < EPS, "duration " + action)
		if action in LOOPS:
			ck(int(la.get("loop_start", 0)) == int(ra.get("loop_start", 0)), "loop_start " + action)
		# Exact frame boundaries of the loader's own frame_at, at and just before each authored end.
		for i in la["frames"].size():
			var t0: float = 0.0 if i == 0 else float(la["frames"][i - 1]["end"])
			ck(Loader.frame_at(la, t0) == i, "frame_at start boundary %s/%d" % [action, i])
			ck(Loader.frame_at(la, float(la["frames"][i]["end"]) - 0.0001) == i, "frame_at pre-end %s/%d" % [action, i])
		var end_frame: int = Loader.frame_at(la, float(la["duration"]))
		ck(end_frame == (int(la.get("loop_start", 0)) if la["loop"] else la["frames"].size() - 1), "frame_at end wrap/hold " + action)
		ck(Loader.frame_at(la, float(la["duration"]) * 7.0) == oracle(ra, cum * 2 * 7), "frame_at 7x duration vs oracle " + action)
	await state_machine(scene, model, slot, raw, target)
	await real_handlers(scene, model, slot, target, app)
	ck(app.active_party_ids == party_before, "party order untouched")
	if capture:
		scene.enemy_x = 560.0
		fixture("capture-only: enemy reset to x560 after handler tests so the target actor remains visible")
		for action in ["attack", "defeat"]:
			fresh_state(model, slot)
			var f := base_fixture(scene, slot)
			var alive := drive(f, action)
			model.advance(slot, f, alive, float(f["x"]) + 120.0, 0.0)
			model.states[slot]["clock"] = float(src["actions"][action]["duration"]) * (0.45 if action == "attack" else 2.0)
			scene.queue_redraw()
			await tick()
			var img: Image = root.get_texture().get_image()
			var path := out.path_join("rpg-2-star-ocean-the-second_%s-combat_%s-%s_ordinary-default-capture-v01_%s.png" % [target, language, action, tag])
			ck(img.get_size() == Vector2i(640, 360) and DisplayServer.get_name() != "headless", "native 640x360 window capture " + action)
			ck(img.save_png(path) == OK, "capture saved " + action)
			captures.append({"target": target, "action": action, "path": path, "sha256": FileAccess.get_sha256(path), "frame": model.current_frame(slot)})
		fixture("capture pose: state clock placed at 0.45x attack / held defeat (render fixture)")
	target_reports[target] = {"loaded": true, "slot": slot, "indexPath": index_path, "indexSha256": FileAccess.get_sha256(index_path),
		"manifestPath": manifest_path, "manifestSha256": FileAccess.get_sha256(manifest_path), "sheetPath": sheet_path, "sheetSha256": sheet_sha,
		"setId": String(src["set_id"]), "logicalScale": raw["logical_scale"]}
	await free_arena(scene)


func state_machine(scene: Node, model, slot: int, raw: Dictionary, target: String) -> void:
	fixture("state-machine: deterministic fighter dict copies drive model.advance (fixture; arena not stepped)")
	var floor_y: float = scene.ARENA_FLOOR_Y
	var auth_facing := int(model.sets[slot]["facing"])
	for action in ACTIONS:
		var ra: Dictionary = raw["actions"][action]
		var la: Dictionary = model.sets[slot]["actions"][action]
		var total_half := int(la["duration_ticks"]) * 2
		for hz in RATES:
			var step_half: int = 60 / int(hz)
			for side in [1, -1]:
				fresh_state(model, slot)
				var f := base_fixture(scene, slot)
				var alive := drive(f, action)
				var enemy: float = float(f["x"]) + 150.0 * side
				model.advance(slot, f, alive, enemy, 0.0)
				var tag := "%s@%dHz facing%+d" % [action, hz, side]
				var ok_frames := true
				var ok_geom := true
				var released_at := -1
				var steps := int(ceil(float(total_half) * (2.5 if action in LOOPS or action in ["dodge", "defeat"] else 1.0) / step_half)) + 2
				for n in range(0, steps):
					if n > 0:
						if action in EVENTS:
							f["visual_elapsed"] = float(f["visual_elapsed"]) + 1.0 / hz
						if action == "dodge":
							f["dodge_time"] = float(f["dodge_time"]) - 1.0 / hz
						model.advance(slot, f, alive, enemy, 1.0 / hz)
					var cur: Dictionary = model.current_frame(slot)
					if action in EVENTS and String(cur["action"]) != action:
						released_at = n
						ck(String(cur["action"]) == "idle" and float(model.states[slot]["clock"]) == 0.0, "release to idle with clock 0 " + tag)
						break
					var expect := oracle(ra, n * step_half)
					if String(cur["action"]) != action or int(cur["frame"]) != expect or int(cur["cell"]) != int(ra["frames"][expect]["cell"]):
						ok_frames = false
					if int(cur["facing"]) != side or bool(cur["mirrored"]) != (side != auth_facing):
						ok_geom = false
					var g: Dictionary = model.frame_geometry(slot, float(f["x"]), floor_y)
					if Vector2i(g["dest"].position) != expected_geometry(raw, ra["frames"][expect], float(f["x"]), floor_y, side != auth_facing):
						ok_geom = false
				ck(ok_frames, "every step frame/cell = integer oracle " + tag)
				ck(ok_geom, "facing/mirror/pivot geometry every step " + tag)
				if action in EVENTS:
					# Release exactly on the first step whose clock reaches the authored duration.
					ck(released_at == int(ceil(float(total_half) / step_half)), "one-shot releases on exact step %d " % int(ceil(float(total_half) / step_half)) + tag)
	# Release / retrigger / precedence / recovery, 60 Hz, enemy to the right.
	var d := 1.0 / 60.0
	for action in LOOPS:
		fresh_state(model, slot)
		var f := base_fixture(scene, slot)
		drive(f, action)
		var e := float(f["x"]) + 150.0
		for i in 20:
			model.advance(slot, f, true, e, d)
		var g := base_fixture(scene, slot)
		model.advance(slot, g, true, e, d)
		var back := "idle" if action != "idle" else "idle"
		ck(String(model.current_frame(slot)["action"]) == back, "loop release %s -> idle" % action)
		if action != "idle":
			ck(float(model.states[slot]["clock"]) == 0.0, "loop release resets clock " + action)
			model.advance(slot, f, true, e, d)
			ck(String(model.current_frame(slot)["action"]) == action and float(model.states[slot]["clock"]) == 0.0 and int(model.current_frame(slot)["frame"]) == 0, "loop retrigger from frame 0 " + action)
	for action in EVENTS:
		fresh_state(model, slot)
		var f := base_fixture(scene, slot)
		drive(f, action)
		var e := float(f["x"]) + 150.0
		model.advance(slot, f, true, e, 0.0)
		for i in 3:
			f["visual_elapsed"] = float(f["visual_elapsed"]) + d
			model.advance(slot, f, true, e, d)
		ck(int(model.current_frame(slot)["frame"]) == oracle(raw["actions"][action], 3), "one-shot mid frame " + action)
		f["visual_elapsed"] = 0.0
		model.advance(slot, f, true, e, d)
		ck(String(model.current_frame(slot)["action"]) == action and float(model.states[slot]["clock"]) == 0.0, "same-action retrigger restarts at 0 " + action)
		# Guard while the one-shot plays: one-shot holds until its end, then guard.
		f["guard"] = true
		f["visual_elapsed"] = d
		model.advance(slot, f, true, e, d)
		ck(String(model.current_frame(slot)["action"]) == action, "one-shot not cut by guard " + action)
		for i in 400:
			f["visual_elapsed"] = float(f["visual_elapsed"]) + d
			model.advance(slot, f, true, e, d)
		ck(String(model.current_frame(slot)["action"]) == "guard", "one-shot releases into guard " + action)
	# Dodge retrigger / release.
	fresh_state(model, slot)
	var fd := base_fixture(scene, slot)
	fd["dodge_time"] = 0.27
	var ed := float(fd["x"]) + 150.0
	model.advance(slot, fd, true, ed, 0.0)
	for i in 4:
		fd["dodge_time"] = float(fd["dodge_time"]) - d
		model.advance(slot, fd, true, ed, d)
	ck(String(model.current_frame(slot)["action"]) == "dodge" and absf(float(model.states[slot]["clock"]) - 4 * d) < EPS, "dodge plays on its clock")
	fd["dodge_time"] = 0.27
	model.advance(slot, fd, true, ed, d)
	ck(String(model.current_frame(slot)["action"]) == "dodge" and float(model.states[slot]["clock"]) == 0.0, "dodge retrigger restarts at 0")
	fd["dodge_time"] = 0.0
	model.advance(slot, fd, true, ed, d)
	ck(String(model.current_frame(slot)["action"]) == "idle" and float(model.states[slot]["clock"]) == 0.0, "dodge release to idle when dodge_time ends")
	# Precedence: defeat > dodge > new event; hit cuts attack; attack cuts hit.
	for pair in [["hit", "attack"], ["attack", "hit"], ["skill", "hit"], ["hit", "skill"]]:
		fresh_state(model, slot)
		var fp := base_fixture(scene, slot)
		var ep := float(fp["x"]) + 150.0
		fp["visual_action"] = pair[1]
		model.advance(slot, fp, true, ep, 0.0)
		fp["visual_elapsed"] = 2 * d
		model.advance(slot, fp, true, ep, 2 * d)
		fp["visual_action"] = pair[0]
		fp["visual_elapsed"] = 0.0
		model.advance(slot, fp, true, ep, d)
		ck(String(model.current_frame(slot)["action"]) == pair[0] and float(model.states[slot]["clock"]) == 0.0, "%s cuts %s at frame 0" % [pair[0], pair[1]])
	fresh_state(model, slot)
	var fx := base_fixture(scene, slot)
	var ex := float(fx["x"]) + 150.0
	fx["visual_action"] = "attack"
	fx["dodge_time"] = 0.27
	model.advance(slot, fx, true, ex, 0.0)
	ck(String(model.current_frame(slot)["action"]) == "dodge", "dodge has precedence over a new attack event")
	fx["visual_action"] = "hit"
	fx["guard"] = true
	model.advance(slot, fx, false, ex, d)
	ck(String(model.current_frame(slot)["action"]) == "defeat" and float(model.states[slot]["clock"]) == 0.0, "defeat has precedence over dodge/hit/guard")
	for i in 200:
		fx["visual_action"] = "attack" if i % 2 == 0 else "hit"
		fx["visual_elapsed"] = 0.0
		model.advance(slot, fx, false, ex, d)
	var last: int = raw["actions"]["defeat"]["frames"].size() - 1
	ck(String(model.current_frame(slot)["action"]) == "defeat" and int(model.current_frame(slot)["frame"]) == last, "defeat holds last frame under repeated events")
	var fr := base_fixture(scene, slot)
	model.advance(slot, fr, true, ex, d)
	ck(String(model.current_frame(slot)["action"]) == "idle" and float(model.states[slot]["clock"]) == 0.0 and int(model.current_frame(slot)["frame"]) == 0, "revive recovery to idle frame 0")
	# Facing hysteresis: within half a pixel keeps the previous facing.
	fresh_state(model, slot)
	var fh := base_fixture(scene, slot)
	model.advance(slot, fh, true, float(fh["x"]) - 150.0, 0.0)
	model.advance(slot, fh, true, float(fh["x"]) + 0.25, d)
	ck(int(model.current_frame(slot)["facing"]) == -1, "facing kept within half pixel")


func snapshot(scene: Node, app) -> Dictionary:
	var members := {}
	for id in app.active_party_ids:
		members[id] = app.member_state(id).duplicate(true)
	var fighters: Array = []
	for f in scene.fighters:
		fighters.append(f.duplicate(true))
	return {"members": members, "fighters": fighters, "enemy_hp": scene.enemy_hp, "enemy_x": scene.enemy_x,
		"enemy_cooldown": scene.enemy_cooldown, "enemy_windup": scene.enemy_windup, "finished": scene.battle_finished}


# Rendering (advance + draw) must never change HP, energy, cooldowns, positions or enemy state.
func render_is_pure(scene: Node, app, label: String) -> void:
	var before := snapshot(scene, app)
	scene._advance_combat_sprite_sets(1.0 / 60.0)
	scene.queue_redraw()
	await tick()
	ck(snapshot(scene, app) == before, "render does not mutate combat state after " + label)


func real_handlers(scene: Node, model, slot: int, target: String, app) -> void:
	fresh_state(model, slot)
	var fighter: Dictionary = scene.fighters[slot]
	var member_id := String(fighter["id"])
	var ms: Dictionary = app.member_state(member_id)
	scene.enemy_x = float(fighter["x"]) + 30.0
	fixture("handlers: enemy_x placed 30 px right of target so attack/hit are in range")
	scene._advance_combat_sprite_sets(0.0)
	ck(String(model.current_frame(slot)["action"]) == "idle", "ordinary arena starts idle")
	await render_is_pure(scene, app, "idle")
	var hp0 := int(scene.enemy_hp)
	ck(scene._try_attack(slot), "real _try_attack accepted")
	ck(int(scene.enemy_hp) == hp0 - int(app.MEMBER_DEFS[member_id]["attack_damage"]), "real attack applied its existing damage (immediate path, no contact keys)")
	ck(not fighter.has("contact_event_id"), "no heroine contact keys on " + member_id)
	scene._advance_combat_sprite_sets(0.0)
	ck(String(model.current_frame(slot)["action"]) == "attack" and int(model.current_frame(slot)["facing"]) == 1, "attack handler selects attack facing enemy")
	await render_is_pure(scene, app, "attack")
	var energy0 := int(ms["energy"])
	ck(scene._try_dodge(slot), "real _try_dodge accepted")
	ck(int(ms["energy"]) == energy0 - int(scene.DODGE_COST), "dodge spent existing energy cost")
	scene._advance_combat_sprite_sets(0.0)
	ck(String(model.current_frame(slot)["action"]) == "dodge", "dodge handler selects dodge (over attack)")
	await render_is_pure(scene, app, "dodge")
	fighter["dodge_time"] = 0.0
	fixture("handlers: dodge_time cleared before skill/hit (fixture instead of stepping the arena)")
	ck(scene._use_skill(slot), "real _use_skill accepted")
	ck(float(fighter["skill_cooldown"]) == 2.2, "skill set its existing cooldown")
	scene._advance_combat_sprite_sets(0.0)
	ck(String(model.current_frame(slot)["action"]) == "skill" and String(model.current_frame(slot)["source"]) == "skill", "skill handler selects authored skill")
	await render_is_pure(scene, app, "skill")
	scene.enemy_target_index = slot
	var hp1 := int(ms["hp"])
	scene._apply_enemy_hit()
	ck(int(ms["hp"]) == hp1 - int(scene.enemy["damage"]), "real enemy hit applied existing damage")
	scene._advance_combat_sprite_sets(0.0)
	ck(String(model.current_frame(slot)["action"]) == "hit" and float(model.states[slot]["clock"]) == 0.0, "hit handler selects hit at frame 0")
	await render_is_pure(scene, app, "hit")
	ms["hp"] = 1
	fixture("handlers: member hp set to 1 before the defeating enemy hit; hp restored to max_hp as revive")
	scene._apply_enemy_hit()
	ck(int(ms["hp"]) == 0 and not scene._is_alive(slot) and not scene.battle_finished, "real enemy hit defeats target; others keep battle open")
	scene._advance_combat_sprite_sets(0.0)
	ck(String(model.current_frame(slot)["action"]) == "defeat", "defeat selected from real down")
	await render_is_pure(scene, app, "defeat")
	ck(not scene._try_attack(slot) and not scene._try_dodge(slot), "defeated target cannot act (unchanged rules)")
	ms["hp"] = int(ms.get("max_hp", app.MEMBER_DEFS[member_id]["max_hp"]))
	fighter["visual_action"] = ""
	scene._advance_combat_sprite_sets(0.0)
	ck(String(model.current_frame(slot)["action"]) == "idle" and float(model.states[slot]["clock"]) == 0.0, "revive returns to idle frame 0")
	await render_is_pure(scene, app, "revive")


func check_female_preserved(language: String, out: String, tag: String, capture: bool) -> void:
	current = "protagonist-female-control"
	var app = setup_party("female", language, "patrol")
	var scene = await spawn_arena()
	var hero: int = app.active_party_ids.find("hero")
	var heroine = load(HEROINE_POLICY)
	ck(scene.heroine_default_active, "heroine ordinary default active for female party")
	var model = scene.combat_sprite_sets
	ck(model != null and model.index_path == heroine.COMBAT_INDEX_PATH, "heroine model uses heroine default index")
	if model != null:
		ck(model.loaded_count() == 1 and model.has_set(hero), "heroine model holds only the hero slot")
		ck(String(model.sets[hero]["set_id"]) != "protagonist-male-combat-mcombat22-v01", "female hero not drawn with male set")
	ck(scene.fighters[hero].has("contact_event_id"), "heroine contact event path preserved")
	for m in COMPANIONS:
		var slot: int = app.active_party_ids.find(m)
		var cm = scene.companion_sets_by_member.get(m)
		ck(cm != null and cm.has_set(slot) and cm.loaded_count() == 1 and not cm.has_set(hero), "companion %s ordinary alongside heroine, own slot only" % m)
		ck(not scene.fighters[slot].has("contact_event_id"), "no contact keys on " + m)
	if capture:
		scene.queue_redraw()
		await tick()
		var img: Image = root.get_texture().get_image()
		var path := out.path_join("rpg-2-star-ocean-the-second_female-party-combat_%s-idle_ordinary-default-capture-v01_%s.png" % [language, tag])
		ck(img.get_size() == Vector2i(640, 360) and img.save_png(path) == OK, "female party capture saved")
		captures.append({"target": current, "action": "party-idle", "path": path, "sha256": FileAccess.get_sha256(path)})
	target_reports[current] = {"heroineIndex": heroine.COMBAT_INDEX_PATH, "heroineIndexSha256": FileAccess.get_sha256(heroine.COMBAT_INDEX_PATH)}
	await free_arena(scene)
