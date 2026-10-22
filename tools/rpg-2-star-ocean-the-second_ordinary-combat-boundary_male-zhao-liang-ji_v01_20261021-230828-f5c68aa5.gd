extends SceneTree
# Ordinary-default combat boundary support for qa.combat.{protagonist-male,zhao-ling,liang-xu,ji-cheng}.set-check.
# READ-ONLY against the current canonical checkout: no runtime/art/default/source edits, no ledger/Bible/index/account/commit.
# Ordinary assertions use the actual arena defaults: no combat-sprite-set flag/override, no candidate index, no enable override.
# The only overrides are clearly declared temporary user:// malformed fixtures in the rejection section; every override is
# restored before the final ordinary fallback check. Exact frame boundaries and action priority use the existing loader API.
# Technical inspection only: no visual/motion/art/human acceptance and no full 8-clip normal-speed playback claim.

const BASE_COMMIT := "78000e24b3bf0668b8fa41fbcd8758e00bcdc494"
const LOADER_PATH := "res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd"
const Loader = preload("res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd")
const ARENA_SCRIPT := "res://scripts/battle_arena.gd"
const ARENA_SCENE := "res://scenes/battle_arena.tscn"
const APP_STATE := "res://scripts/app_state.gd"
const M_CFG := "res://scripts/mpath24/rpg-2-star-ocean-the-second_male-playable-path_config_opt-in-v01_20261021-170200-5e1c24a7.gd"
const M_DRV := "res://scripts/mpath24/rpg-2-star-ocean-the-second_male-playable-path_explore-driver_opt-in-v01_20261021-170200-5e1c24a7.gd"
const Z_CFG := "res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_config_opt-in-v01_20261021-223218-3246d731.gd"
const L_CFG := "res://scripts/lpath30/rpg-2-star-ocean-the-second_liang-playable-path_config_opt-in-v01_20261021-202247-ca439d91.gd"
const J_CFG := "res://scripts/jpath33/rpg-2-star-ocean-the-second_ji-playable-path_config_opt-in-v01_20261021-222438-7d4b2e91.gd"
const M_INDEX := "res://data/mcombat22/rpg-2-star-ocean-the-second_protagonist-male-combat_runtime-index_unapproved-v01_20261021-154716-8dee0dda.json"
const Z_INDEX := "res://data/zcombat26/rpg-2-star-ocean-the-second_zhao-ling-combat_runtime-index_unapproved-zcombat26-v01_20261021-180157-63cae05d.json"
const L_INDEX := "res://data/lcombat29/rpg-2-star-ocean-the-second_liang-xu-combat_runtime-index_unapproved-lcombat29-v01_20261021-201025-69179dd4.json"
const J_INDEX := "res://data/jcombat32/rpg-2-star-ocean-the-second_ji-cheng-combat_runtime-index_unapproved-jcombat32-v01_20261021-220632-089ef67c.json"
const ACTIONS := ["idle", "move", "guard", "attack", "dodge", "skill", "hit", "defeat"]
const INDEX_SCHEMA := "worlds-between.combat-sprite-set-index/1"

# Current ordinary source packages (actor -> index/key/set id/package directory).
const SETS := {
	"male": {"index": M_INDEX, "key": "hero:male", "set_id": "protagonist-male-combat-mcombat22-v01", "dir": "res://data/mcombat22/"},
	"zhao-ling": {"index": Z_INDEX, "key": "zhao-ling", "set_id": "zhao-ling-combat-zcombat26-v01", "dir": "res://data/zcombat26/"},
	"liang-xu": {"index": L_INDEX, "key": "liang-xu", "set_id": "liang-xu-combat-lcombat29-v01", "dir": "res://data/lcombat29/"},
	"ji-cheng": {"index": J_INDEX, "key": "ji-cheng", "set_id": "ji-cheng-combat-jcombat32-v01", "dir": "res://data/jcombat32/"},
}

var checks := 0
var failures: Array[String] = []
var bindings := {}
var timing := {}
var rejections := {}
var canon := {}
var temp_files: Array[String] = []
var temp_dir := ""
var out_dir := ""
var harness_path := ""
var app: Node
var arena_script
var M
var MD
var Z
var L
var J
var serial := 0
var stamp := ""
var run_id := ""


func ck(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures.append(label)
		print("ORDINARY_COMBAT_BOUNDARY_FAIL ", label)


func _initialize() -> void:
	call_deferred("run")
	create_timer(120.0).timeout.connect(func(): print("ORDINARY_COMBAT_BOUNDARY_TIMEOUT"); quit(2))


func arg_value(name: String) -> String:
	var args := OS.get_cmdline_user_args()
	for i in args.size():
		if args[i] == name and i + 1 < args.size():
			return args[i + 1]
	return ""


func any_combat_flag() -> bool:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--combat-sprite-set"):
			return true
	return false


func sorted_keys(d: Dictionary) -> Array:
	var keys := d.keys()
	keys.sort()
	return keys


func fighter(overrides: Dictionary = {}) -> Dictionary:
	var f: Dictionary = {"x": 135.0, "visual_action": "", "visual_elapsed": 0.0, "dodge_time": 0.0, "guard": false, "visual_moving": false}
	f.merge(overrides, true)
	return f


func fresh(index_path: String, key: String):
	var model = Loader.new()
	var keys: Array[String] = [key]
	model.configure(index_path, keys)
	return model


func first_action(model, overrides: Dictionary, alive: bool) -> String:
	model.advance(0, fighter(overrides), alive, 493.0, 0.0)
	return String(model.states[0]["action"])


func make_arena():
	var host = load(ARENA_SCENE).instantiate()
	root.add_child(host)
	host.set_process(false)
	host.set_physics_process(false)
	return host


func temp_path(name: String) -> String:
	serial += 1
	var p := temp_dir.path_join("%02d_%s" % [serial, name])
	temp_files.append(p)
	return p


func write_text(name: String, text: String) -> String:
	var p := temp_path(name)
	var f := FileAccess.open(p, FileAccess.WRITE)
	if f == null:
		ck(false, "temporary fixture writable " + name)
		return p
	f.store_string(text)
	f.close()
	return p


func write_json(name: String, data: Variant) -> String:
	return write_text(name, JSON.stringify(data))


func expect_index_status(label: String, path: String, expected: String) -> Dictionary:
	var result: Dictionary = Loader.load_index(path)
	var actual := String(result.get("status", ""))
	rejections[label] = actual
	ck(actual == expected, label + " expected " + expected + " got " + actual)
	return result


func expect_set_status(label: String, path: String, key: String, expected: String) -> void:
	var result: Dictionary = Loader.load_set(path, key)
	var actual := String(result.get("status", ""))
	rejections[label] = actual
	ck(actual == expected, label + " expected " + expected + " got " + actual)


func boundary_suite(name: String, loaded: Dictionary) -> Dictionary:
	var summary := {}
	for action_name in ACTIONS:
		var clip: Dictionary = loaded["actions"][action_name]
		var frames: Array = clip["frames"]
		var rate := int(clip.get("tick_rate", 0))
		var bad: Array[String] = []
		if rate <= 0:
			bad.append("no tick_rate")
		var ends: Array[int] = []
		for i in frames.size():
			var t := 0.0 if i == 0 else float(frames[i - 1]["end"])
			if Loader.frame_at(clip, t) != i:
				bad.append("start %d" % i)
			var end := float(frames[i]["end"])
			var k := roundi(end * float(rate)) if rate > 0 else -1
			if rate > 0 and absf(end - float(k) / float(rate)) > 1e-12:
				bad.append("tick-align %d" % i)
			ends.append(k)
		var dur := float(clip["duration"])
		var dur_ticks := int(clip.get("duration_ticks", -1))
		if rate > 0 and absf(dur - float(dur_ticks) / float(rate)) > 1e-12:
			bad.append("duration-rational")
		if ends.size() > 0 and dur_ticks != ends[ends.size() - 1]:
			bad.append("ticks-total")
		var end_frame := Loader.frame_at(clip, dur)
		var expected_end := int(clip.get("loop_start", 0)) if bool(clip["loop"]) else frames.size() - 1
		if end_frame != expected_end:
			bad.append("end %d!=%d" % [end_frame, expected_end])
		if Loader.frame_at(clip, dur - 0.00001) != frames.size() - 1:
			bad.append("pre-end")
		ck(bad.is_empty(), "frame boundaries %s/%s %s" % [name, action_name, ",".join(bad)])
		summary[action_name] = {
			"ok": bad.is_empty(), "frames": frames.size(), "tick_rate": rate,
			"duration_ticks": dur_ticks, "duration": dur,
			"loop": bool(clip["loop"]), "loop_start": int(clip.get("loop_start", 0)),
			"ends_ticks": ends,
		}
	return summary


func priority_suite(name: String, spec: Dictionary) -> void:
	var idx := String(spec["index"])
	var key := String(spec["key"])
	var label := name
	var guard_model = fresh(idx, key)
	if not guard_model.has_set(0):
		ck(false, label + " priority set required")
		return
	ck(first_action(fresh(idx, key), {"dodge_time": 1.0, "guard": true, "visual_moving": true}, false) == "defeat", label + " priority defeat over dodge/guard/move")
	ck(first_action(fresh(idx, key), {"visual_action": "hit", "visual_elapsed": 0.01, "dodge_time": 1.0, "guard": true, "visual_moving": true}, true) == "dodge", label + " priority dodge over hit/guard/move")
	ck(first_action(fresh(idx, key), {"visual_action": "attack", "visual_elapsed": 0.01, "guard": true, "visual_moving": true}, true) == "attack", label + " priority attack event over guard/move")
	ck(first_action(fresh(idx, key), {"visual_action": "hit", "visual_elapsed": 0.01, "guard": true, "visual_moving": true}, true) == "hit", label + " priority hit event over guard/move")
	ck(first_action(fresh(idx, key), {"visual_action": "skill", "visual_elapsed": 0.01, "guard": true, "visual_moving": true}, true) == "skill", label + " priority skill event over guard/move")
	ck(first_action(fresh(idx, key), {"guard": true, "visual_moving": true}, true) == "guard", label + " priority guard over move")
	ck(first_action(fresh(idx, key), {"visual_moving": true}, true) == "move", label + " priority move when idle")
	ck(first_action(fresh(idx, key), {}, true) == "idle", label + " priority idle fallback")

	var m = fresh(idx, key)
	var df := fighter({})
	m.advance(0, df, false, 493.0, 0.0)
	df = fighter({})
	m.advance(0, df, false, 493.0, 10.0)
	var cf: Dictionary = m.current_frame(0)
	var defeat_clip: Dictionary = m.sets[0]["actions"]["defeat"]
	ck(String(cf["action"]) == "defeat" and int(cf["frame"]) == defeat_clip["frames"].size() - 1, label + " defeat holds last authored frame")

	m = fresh(idx, key)
	var hf := fighter({"visual_action": "hit", "visual_elapsed": 0.01, "guard": true})
	m.advance(0, hf, true, 493.0, 0.0)
	var h0 := float(m.states[0]["clock"])
	hf["visual_elapsed"] = 0.02
	m.advance(0, hf, true, 493.0, 0.1)
	ck(String(m.states[0]["action"]) == "hit" and float(m.states[0]["clock"]) > h0, label + " hit one-shot continues")
	hf["visual_elapsed"] = 0.0
	m.advance(0, hf, true, 493.0, 0.0)
	ck(String(m.states[0]["action"]) == "hit" and float(m.states[0]["clock"]) == 0.0, label + " hit restarts on elapsed reset")
	hf["visual_elapsed"] = 0.0
	m.advance(0, hf, true, 493.0, 10.0)
	ck(String(m.states[0]["action"]) == "guard", label + " hit one-shot ends into guard")

	m = fresh(idx, key)
	var dd := fighter({"dodge_time": 0.1})
	m.advance(0, dd, true, 493.0, 0.0)
	dd["dodge_time"] = 0.2
	m.advance(0, dd, true, 493.0, 0.0)
	ck(String(m.states[0]["action"]) == "dodge" and float(m.states[0]["clock"]) == 0.0, label + " dodge restarts on new dodge")
	dd["dodge_time"] = 0.2
	m.advance(0, dd, true, 493.0, 0.05)
	ck(String(m.states[0]["action"]) == "dodge" and float(m.states[0]["clock"]) > 0.0, label + " dodge continues")
	dd["dodge_time"] = 0.0
	dd["guard"] = true
	m.advance(0, dd, true, 493.0, 0.0)
	ck(String(m.states[0]["action"]) == "guard", label + " dodge ends into guard")

	m = fresh(idx, key)
	var af := fighter({"visual_action": "attack", "visual_elapsed": 0.01})
	m.advance(0, af, true, 493.0, 0.0)
	af["visual_elapsed"] = 0.02
	m.advance(0, af, true, 493.0, 0.1)
	ck(String(m.states[0]["action"]) == "attack" and float(m.states[0]["clock"]) > 0.0, label + " attack one-shot continues")
	af["visual_elapsed"] = 0.0
	m.advance(0, af, true, 493.0, 0.0)
	ck(String(m.states[0]["action"]) == "attack" and float(m.states[0]["clock"]) == 0.0, label + " attack restarts on elapsed reset")
	af["visual_elapsed"] = 0.0
	af["guard"] = false
	af["visual_moving"] = true
	m.advance(0, af, true, 493.0, 10.0)
	ck(String(m.states[0]["action"]) == "move", label + " attack one-shot ends into move")


func snapshot_bindings(host) -> Dictionary:
	var hero_slot: int = app.active_party_ids.find("hero")
	var snap := {
		"party": app.active_party_ids.duplicate(),
		"hero_slot": hero_slot,
		"hero_index": host.combat_sprite_sets.index_path if host.combat_sprite_sets != null else "",
		"hero_index_status": host.combat_sprite_sets.index_status if host.combat_sprite_sets != null else "null",
		"hero_loaded": host.combat_sprite_sets != null and host.combat_sprite_sets.has_set(hero_slot),
		"hero_count": host.combat_sprite_sets.loaded_count() if host.combat_sprite_sets != null else -1,
		"heroine_default_active": host.heroine_default_active,
		"companions": {},
		"alias_index": host.companion_sprite_sets.index_path if host.companion_sprite_sets != null else "",
	}
	for name in ["zhao-ling", "liang-xu", "ji-cheng"]:
		if host.companion_sets_by_member.has(name):
			var model = host.companion_sets_by_member[name]
			var slot: int = app.active_party_ids.find(name)
			snap["companions"][name] = {
				"slot": slot,
				"index": model.index_path,
				"index_status": model.index_status,
				"loaded": model.has_set(slot),
				"count": model.loaded_count(),
				"set_id": String(model.sets[slot]["set_id"]) if model.has_set(slot) else "",
				"key": String(model.sets[slot]["key"]) if model.has_set(slot) else "",
				"manifest": String(model.sets[slot]["manifest"]) if model.has_set(slot) else "",
			}
	return snap


func check_ordinary(host, label: String) -> void:
	var hero_slot: int = app.active_party_ids.find("hero")
	ck(hero_slot == 0, label + " hero is slot 0")
	ck(host.combat_sprite_sets != null, label + " male hero ordinary set present")
	ck(not host.heroine_default_active, label + " female heroine default inactive for male")
	if host.combat_sprite_sets != null:
		var hero = host.combat_sprite_sets
		ck(hero.index_path == M_INDEX, label + " male index is mcombat22 ordinary")
		ck(hero.index_status == "loaded", label + " male index loaded")
		ck(hero.has_set(hero_slot), label + " male hero set bound")
		ck(hero.loaded_count() == 1, label + " exactly one hero set")
		ck(hero.set_status(hero_slot) == "loaded", label + " male hero status loaded")
		if hero.has_set(hero_slot):
			var hs: Dictionary = hero.sets[hero_slot]
			ck(String(hs["key"]) == "hero:male", label + " male key hero:male")
			ck(String(hs["set_id"]) == "protagonist-male-combat-mcombat22-v01", label + " male current set id")
			if canon.has("male"):
				ck(String(hs["manifest"]) == String(canon["male"]["manifest"]), label + " male current manifest")
		for i in app.active_party_ids.size():
			if i != hero_slot:
				ck(not hero.has_set(i), label + " male model isolates slot " + str(i))
	ck(host.companion_sets_by_member.size() == 3, label + " three companion models")
	for name in ["zhao-ling", "liang-xu", "ji-cheng"]:
		var slot: int = app.active_party_ids.find(name)
		ck(host.companion_sets_by_member.has(name), label + " " + name + " model present")
		if host.companion_sets_by_member.has(name):
			var model = host.companion_sets_by_member[name]
			ck(int(host.companion_slot_by_member.get(name, -1)) == slot, label + " " + name + " slot binding")
			ck(model.index_path == String(SETS[name]["index"]), label + " " + name + " ordinary index")
			ck(model.index_status == "loaded", label + " " + name + " index loaded")
			ck(model.has_set(slot), label + " " + name + " set bound")
			ck(model.loaded_count() == 1, label + " " + name + " exactly one set")
			ck(model.set_status(slot) == "loaded", label + " " + name + " status loaded")
			if model.has_set(slot):
				var ms: Dictionary = model.sets[slot]
				ck(String(ms["key"]) == name, label + " " + name + " key matches member")
				ck(String(ms["set_id"]) == String(SETS[name]["set_id"]), label + " " + name + " current set id")
				if canon.has(name):
					ck(String(ms["manifest"]) == String(canon[name]["manifest"]), label + " " + name + " current manifest")
			for i in app.active_party_ids.size():
				if i != slot:
					ck(not model.has_set(i), label + " " + name + " isolates slot " + str(i))
			if host.combat_sprite_sets != null:
				ck(not host.combat_sprite_sets.has_set(slot), label + " hero model excludes " + name)
	ck(host.companion_sprite_sets != null and host.companion_sets_by_member.has("zhao-ling") and host.companion_sprite_sets == host.companion_sets_by_member["zhao-ling"], label + " companion alias is zhao")
	ck(host.companion_index == 1, label + " companion alias slot is zhao")
	if host.companion_sets_by_member.size() == 3:
		ck(host.companion_sets_by_member["zhao-ling"] != host.companion_sets_by_member["liang-xu"] and host.companion_sets_by_member["liang-xu"] != host.companion_sets_by_member["ji-cheng"] and host.companion_sets_by_member["zhao-ling"] != host.companion_sets_by_member["ji-cheng"], label + " companion models are distinct")
	bindings[label] = snapshot_bindings(host)


func exercise_liang_refusal(path: String, label: String) -> void:
	L.combat_index_override = path
	var host = make_arena()
	var hero_slot: int = app.active_party_ids.find("hero")
	ck(host.combat_sprite_sets != null and host.combat_sprite_sets.has_set(hero_slot), label + " preserves male hero")
	var keys := sorted_keys(host.companion_sets_by_member)
	ck(not keys.has("liang-xu"), label + " refuses liang")
	ck(keys.has("zhao-ling") and keys.has("ji-cheng"), label + " preserves zhao and ji")
	ck(host.companion_sets_by_member.size() == 2, label + " loads exactly the two preserved companions")
	rejections[label] = {"keys": keys, "hero": host.combat_sprite_sets != null and host.combat_sprite_sets.has_set(hero_slot)}
	host.free()
	L.combat_index_override = ""


func exercise_male_refusal(path: String, label: String) -> void:
	arena_script.male_playable_path_index_override = path
	var host = make_arena()
	var keys := sorted_keys(host.companion_sets_by_member)
	ck(host.combat_sprite_sets == null, label + " refuses male hero set")
	ck(not host.heroine_default_active, label + " does not switch male to female default")
	ck(keys.has("zhao-ling") and keys.has("liang-xu") and keys.has("ji-cheng"), label + " preserves all three companions")
	rejections[label] = {"companions": keys, "hero": host.combat_sprite_sets != null}
	host.free()
	arena_script.male_playable_path_index_override = ""


func direct_rejections() -> void:
	if not canon.has("male"):
		ck(false, "male canonical set required for malformed copies")
		return
	var missing_index := temp_dir.path_join("absent_index.json")
	expect_index_status("missing index", missing_index, "missing_manifest")
	var missing_model = Loader.new()
	var one_key: Array[String] = ["hero:male"]
	missing_model.configure(missing_index, one_key)
	ck(missing_model.index_status == "missing_manifest" and not missing_model.has_set(0) and missing_model.loaded_count() == 0 and missing_model.set_status(0) == "missing_manifest", "missing index falls back atomically")

	var invalid_index := write_text("invalid_index.json", "{bad")
	expect_index_status("invalid json index", invalid_index, "invalid_json")
	var unknown_index := write_json("unknown_index.json", {"schema": "worlds-between.combat-sprite-set-index/0", "sets": {}})
	expect_index_status("unknown schema index", unknown_index, "unknown_index_schema")
	var invalid_entry := write_json("invalid_entry_index.json", {"schema": INDEX_SCHEMA, "sets": {"hero:male": 42}})
	expect_index_status("invalid entry index", invalid_entry, "invalid_index")

	var missing_manifest_index := write_json("missing_manifest_index.json", {"schema": INDEX_SCHEMA, "sets": {"hero:male": "absent_manifest.json"}})
	var mi: Dictionary = Loader.load_index(missing_manifest_index)
	var mi_sets: Dictionary = mi.get("sets", {})
	ck(String(mi.get("status", "")) == "loaded", "missing manifest index itself loads")
	if mi_sets.has("hero:male"):
		expect_set_status("missing manifest", String(mi_sets["hero:male"]), "hero:male", "missing_manifest")

	var invalid_manifest := write_text("invalid_manifest.json", "{bad")
	expect_set_status("invalid json manifest", invalid_manifest, "hero:male", "invalid_json")

	var parsed = JSON.parse_string(FileAccess.get_file_as_string(String(canon["male"]["manifest"])))
	if not parsed is Dictionary:
		ck(false, "canonical male manifest readable")
		return
	var base: Dictionary = parsed
	base["sheet"] = String(canon["male"]["sheet"])

	var wrong_schema: Dictionary = base.duplicate(true)
	wrong_schema["schema"] = "worlds-between.combat-sprite-set/0"
	expect_set_status("unknown schema manifest", write_json("unknown_schema_manifest.json", wrong_schema), "hero:male", "unknown_schema")

	var partial: Dictionary = base.duplicate(true)
	partial["actions"].erase("hit")
	expect_set_status("partial manifest missing hit", write_json("partial_missing_hit.json", partial), "hero:male", "missing_action")

	var mode: Dictionary = base.duplicate(true)
	mode["actions"]["attack"]["loop"] = true
	expect_set_status("wrong action mode", write_json("wrong_action_mode.json", mode), "hero:male", "invalid_mode")

	var scale: Dictionary = base.duplicate(true)
	scale["logical_scale"] = 0.75
	expect_set_status("unsupported scale", write_json("unsupported_scale.json", scale), "hero:male", "unsupported_scale")

	var out_of_range: Dictionary = base.duplicate(true)
	out_of_range["actions"]["attack"]["frames"][0]["cell"] = 9999
	expect_set_status("frame out of range", write_json("frame_out_of_range.json", out_of_range), "hero:male", "frame_out_of_range")

	var tick_rate: Dictionary = base.duplicate(true)
	tick_rate["actions"]["attack"]["tick_rate"] = 0
	expect_set_status("invalid tick rate", write_json("invalid_tick_rate.json", tick_rate), "hero:male", "invalid_tick_rate")

	var mixed: Dictionary = base.duplicate(true)
	mixed["actions"]["attack"]["frames"][0]["ms"] = 67
	expect_set_status("mixed time units", write_json("mixed_time_units.json", mixed), "hero:male", "invalid_frame")

	var unknown: Dictionary = base.duplicate(true)
	unknown["actions"]["cast"] = {"loop": false, "tick_rate": 30, "frames": [{"cell": 0, "ticks": 1}]}
	expect_set_status("unknown action", write_json("unknown_action.json", unknown), "hero:male", "unknown_action")

	# Wrong-member canonical manifests, read-only.
	if canon.has("zhao-ling"):
		expect_set_status("wrong member zhao manifest as liang-xu", String(canon["zhao-ling"]["manifest"]), "liang-xu", "identity_mismatch")
	if canon.has("liang-xu"):
		expect_set_status("wrong member liang manifest as ji-cheng", String(canon["liang-xu"]["manifest"]), "ji-cheng", "identity_mismatch")
	expect_set_status("wrong member male manifest as hero:female", String(canon["male"]["manifest"]), "hero:female", "identity_mismatch")

	var no_set_model = Loader.new()
	var zhao_key: Array[String] = ["zhao-ling"]
	no_set_model.configure(M_INDEX, zhao_key)
	ck(no_set_model.set_status(0) == "no_set" and not no_set_model.has_set(0) and no_set_model.loaded_count() == 0, "male index under companion key is no_set")


func arena_rejections() -> void:
	var invalid_index := write_text("arena_invalid_index.json", "{bad")
	exercise_liang_refusal(invalid_index, "arena liang invalid json index")
	if canon.has("zhao-ling"):
		var wrong_member := write_json("arena_wrong_member_index.json", {"schema": INDEX_SCHEMA, "sets": {"liang-xu": String(canon["zhao-ling"]["manifest"])}})
		exercise_liang_refusal(wrong_member, "arena liang wrong-member manifest")
	if canon.has("liang-xu") and canon.has("zhao-ling"):
		var multi := write_json("arena_multi_member_index.json", {"schema": INDEX_SCHEMA, "sets": {"liang-xu": String(canon["liang-xu"]["manifest"]), "zhao-ling": String(canon["zhao-ling"]["manifest"])}})
		exercise_liang_refusal(multi, "arena liang multi-member index")
	var missing := write_json("arena_missing_manifest_index.json", {"schema": INDEX_SCHEMA, "sets": {"liang-xu": "absent_manifest.json"}})
	exercise_liang_refusal(missing, "arena liang missing manifest")
	if canon.has("zhao-ling"):
		var male_wrong := write_json("arena_male_wrong_member_index.json", {"schema": INDEX_SCHEMA, "sets": {"hero:male": String(canon["zhao-ling"]["manifest"])}})
		exercise_male_refusal(male_wrong, "arena male wrong-member manifest")
	exercise_male_refusal(temp_dir.path_join("absent_male_index.json"), "arena male missing index")

	L.combat_index_override = ""
	arena_script.male_playable_path_index_override = ""
	ck(MD.male_enabled_override == -1 and Z.enabled_override == -1 and J.enabled_override == -1 and L.enabled_override == -1, "rejection tests restore policy enable state")
	ck(L.combat_index_override == "" and arena_script.male_playable_path_index_override == "", "rejection tests restore override paths")
	ck(arena_script.combat_sprite_set_override == -1 and arena_script.combat_sprite_set_index_override == "" and arena_script.companion_combat_member_override == "" and arena_script.companion_combat_index_override == "", "rejection tests restore arena defaults")
	var restored = make_arena()
	check_ordinary(restored, "restored")
	restored.free()


func source_hashes() -> Dictionary:
	var paths := {
		"app_state": APP_STATE,
		"battle_arena": ARENA_SCRIPT,
		"battle_arena_scene": ARENA_SCENE,
		"combat_loader": LOADER_PATH,
		"male_config": M_CFG,
		"male_driver": M_DRV,
		"zhao_config": Z_CFG,
		"liang_config": L_CFG,
		"ji_config": J_CFG,
		"male_index": M_INDEX,
		"zhao_index": Z_INDEX,
		"liang_index": L_INDEX,
		"ji_index": J_INDEX,
		"project": "res://project.godot",
		"harness": harness_path,
	}
	for name in canon:
		paths[name + "_manifest"] = String(canon[name]["manifest"])
		paths[name + "_sheet"] = String(canon[name]["sheet"])
	var out := {}
	for label in paths:
		var path := String(paths[label])
		out[label] = {"path": path, "sha256": FileAccess.get_sha256(path)}
	return out


func finish() -> void:
	var cleanup_note := "not attempted"
	if temp_dir.begins_with("user://") and failures.is_empty():
		var removed := 0
		for p in temp_files:
			if p.begins_with("user://") and DirAccess.remove_absolute(ProjectSettings.globalize_path(p)) == OK:
				removed += 1
		var dir_removed := DirAccess.remove_absolute(ProjectSettings.globalize_path(temp_dir)) == OK
		cleanup_note = "removed %d/%d fixtures dir=%s" % [removed, temp_files.size(), str(dir_removed)]
		if removed != temp_files.size() or not dir_removed:
			ck(false, "temporary user:// fixture cleanup")
	elif not failures.is_empty():
		cleanup_note = "retained at " + temp_dir
	elif not temp_dir.begins_with("user://"):
		cleanup_note = "temp dir outside user://"
		ck(false, "temporary fixtures stay inside user://")

	var ordinary_bind: Dictionary = bindings.get("ordinary", {})
	var companions_bind: Dictionary = ordinary_bind.get("companions", {})
	var report := {
		"schema": "worlds-between.ordinary-combat-boundary/1",
		"baseCommit": BASE_COMMIT,
		"createdLocal": Time.get_datetime_string_from_system(false, true),
		"scope": "Ordinary-default load/binding/isolation/refusal, action priority and exact authored frame boundaries for male/Zhao/Liang/Ji; technical only.",
		"ordinaryDefaults": {
			"combatSpriteSetOverride": arena_script.combat_sprite_set_override if arena_script != null else null,
			"combatSpriteSetIndexOverride": arena_script.combat_sprite_set_index_override if arena_script != null else null,
			"malePlayablePathIndexOverride": arena_script.male_playable_path_index_override if arena_script != null else null,
			"companionCombatMemberOverride": arena_script.companion_combat_member_override if arena_script != null else null,
			"companionCombatIndexOverride": arena_script.companion_combat_index_override if arena_script != null else null,
			"combatFlagOnCommandLine": any_combat_flag(),
		},
		"bindings": bindings,
		"timing": timing,
		"rejections": rejections,
		"checks": checks,
		"failures": failures,
		"passed": failures.is_empty(),
		"engine": Engine.get_version_info(),
		"os": OS.get_name(),
		"displayServer": DisplayServer.get_name(),
		"language": app.language if app != null else "",
		"heroAppearance": app.hero_appearance if app != null else "",
		"party": app.active_party_ids.duplicate() if app != null else [],
		"hashNormalization": "raw file bytes; no line-ending normalization",
		"sourceHashes": source_hashes(),
		"tempFixtures": {"dir": temp_dir, "files": temp_files, "cleanup": cleanup_note},
		"environmentNotes": [
			"Headless checked run; no window capture.",
			"Godot/engine diagnostics are retained in the checked-runner log, not filtered.",
			"Canonical checkout read-only; no runtime/art/default/source edits.",
			"Temporary user:// malformed manifests/indexes are declared rejection fixtures; every override was restored before the final ordinary fallback.",
		],
		"limitations": [
			"Technical inspection only; no visual, motion, art or human-playthrough acceptance.",
			"Female ordinary set is not rechecked here (separate check already exists).",
			"Full 8-clip normal-speed playback/motion review is left to the companion check; this harness checks load, exact frame boundaries, action priority and isolation/refusal.",
			"No normal-input recruitment/battle flow, save/reload or combined build rerun is claimed.",
		],
	}
	var base_name := "rpg-2-star-ocean-the-second_ordinary-combat-boundary_technical-check_v01_%s-%s" % [stamp, run_id]
	var report_path := out_dir.path_join(base_name + ".json")
	var text_path := out_dir.path_join(base_name + ".txt")
	var f := FileAccess.open(report_path, FileAccess.WRITE)
	if f == null:
		print("ORDINARY_COMBAT_BOUNDARY_FAIL report_write")
		quit(1)
		return
	f.store_string(JSON.stringify(report, "  ") + "\n")
	f.close()
	var summary := [
		"ORDINARY_COMBAT_BOUNDARY " + ("PASS" if failures.is_empty() else "FAIL"),
		"base_commit=" + BASE_COMMIT,
		"checks=" + str(checks) + " failures=" + str(failures.size()),
		"hero=" + str(ordinary_bind.get("hero_index", "")),
		"companions=" + str(sorted_keys(companions_bind)),
		"timing_sets=" + str(sorted_keys(timing)),
		"cleanup=" + cleanup_note,
		"report=" + report_path,
	]
	if not failures.is_empty():
		summary.append("failures=" + "; ".join(failures))
	var t := FileAccess.open(text_path, FileAccess.WRITE)
	if t != null:
		t.store_string("\n".join(summary) + "\n")
		t.close()
	Loader.clear_cache()
	canon.clear()
	if MD != null:
		MD.clear_male_cache()
	if Z != null:
		Z.clear_cache()
	if L != null:
		L.clear_cache()
	if J != null:
		J.clear_cache()
	var generic = load("res://scripts/exploration_sprite_set_pilot.gd")
	if generic != null:
		generic.clear_cache()
	if failures.is_empty():
		print("ORDINARY_COMBAT_BOUNDARY_PASS checks=", checks)
	else:
		print("ORDINARY_COMBAT_BOUNDARY_FAIL checks=", checks, " failures=", failures.size())
	quit(0 if failures.is_empty() else 1)


func run() -> void:
	out_dir = arg_value("--out")
	harness_path = arg_value("--harness")
	if out_dir == "" or harness_path == "":
		print("ORDINARY_COMBAT_BOUNDARY_USAGE --out <dir> --harness <path>")
		quit(2)
		return
	DirAccess.make_dir_recursive_absolute(out_dir)
	stamp = Time.get_datetime_string_from_system(false, true).replace("-", "").replace(" ", "-").replace(":", "")
	run_id = "%08x" % (Time.get_ticks_usec() & 0xffffffff)
	temp_dir = "user://ordinary-combat-boundary_%s_%s" % [stamp, run_id]
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(temp_dir))
	app = root.get_node_or_null("AppState")
	ck(app != null, "AppState autoload present")
	if app == null:
		finish()
		return
	app.begin_new_run()
	app.hero_appearance = "male"
	app.show_initial_guide = false
	var z_ok: bool = app.recruit_member("zhao-ling")
	var l_ok: bool = app.recruit_member("liang-xu")
	app.ji_records_checked = true
	var j_ok: bool = app.recruit_member("ji-cheng")
	ck(z_ok and l_ok and j_ok, "ordinary party recruitment")
	ck(app.active_party_ids == ["hero", "zhao-ling", "liang-xu", "ji-cheng"], "ordinary party order")

	arena_script = load(ARENA_SCRIPT)
	M = load(M_CFG)
	MD = load(M_DRV)
	Z = load(Z_CFG)
	L = load(L_CFG)
	J = load(J_CFG)
	ck(arena_script != null and M != null and MD != null and Z != null and L != null and J != null, "current source scripts load")
	if arena_script == null or M == null or MD == null or Z == null or L == null or J == null:
		finish()
		return

	ck(arena_script.combat_sprite_set_override == -1, "no combat set enable override")
	ck(arena_script.combat_sprite_set_index_override == "", "no combat set index override")
	ck(arena_script.male_playable_path_index_override == "", "no male candidate index override")
	ck(arena_script.companion_combat_member_override == "", "no companion member override")
	ck(arena_script.companion_combat_index_override == "", "no companion index override")
	ck(not any_combat_flag(), "no combat sprite set command-line flag")
	ck(MD.DEFAULT_ADOPTED == true and MD.male_enabled_override == -1 and MD.registry_path_override == "" and MD.supplement_path_override == "", "male ordinary default enabled without overrides")
	ck(M.COMBAT_INDEX_PATH == M_INDEX, "male ordinary index is mcombat22")
	ck(Z.DEFAULT_ADOPTED == true and Z.enabled_override == -1 and Z.combat_index_override == "" and Z.registry_path_override == "" and Z.supplement_path_override == "", "zhao ordinary default enabled without overrides")
	ck(Z.COMBAT_INDEX_PATH == Z_INDEX, "zhao ordinary index is zcombat26")
	ck(L.DEFAULT_ADOPTED == true and L.enabled_override == -1 and L.combat_index_override == "" and L.registry_path_override == "" and L.supplement_path_override == "", "liang ordinary default enabled without overrides")
	ck(L.COMBAT_INDEX_PATH == L_INDEX, "liang ordinary index is lcombat29")
	ck(J.DEFAULT_ADOPTED == true and J.enabled_override == -1 and J.combat_index_override == "" and J.registry_path_override == "" and J.supplement_path_override == "", "ji ordinary default enabled without overrides")
	ck(J.COMBAT_INDEX_PATH == J_INDEX, "ji ordinary index is jcombat32")

	for name in SETS:
		var spec: Dictionary = SETS[name]
		var index: Dictionary = Loader.load_index(String(spec["index"]))
		ck(String(index.get("status", "")) == "loaded", name + " index loads")
		var sets: Dictionary = index.get("sets", {})
		ck(sets.size() == 1 and sets.has(String(spec["key"])), name + " index lists exactly its member key")
		if not sets.has(String(spec["key"])):
			continue
		var manifest := String(sets[String(spec["key"])])
		var loaded: Dictionary = Loader.load_set(manifest, String(spec["key"]))
		ck(String(loaded.get("status", "")) == "loaded", name + " set loads")
		if String(loaded.get("status", "")) != "loaded":
			continue
		canon[name] = loaded
		ck(String(loaded["key"]) == String(spec["key"]), name + " set key matches member")
		ck(String(loaded["set_id"]) == String(spec["set_id"]), name + " current set id")
		ck(String(loaded["manifest"]) == manifest, name + " current manifest path")
		ck(String(loaded["sheet"]).begins_with(String(spec["dir"])), name + " sheet stays in its package")
		ck(loaded["cell"] == Vector2i(136, 144), name + " current cell size")
		ck(loaded["pivot"] == Vector2i(64, 136), name + " current pivot")
		ck(absf(float(loaded["logical_scale"]) - 0.5) < 1e-9, name + " logical scale 0.5")
		ck(String(loaded["display_proportion"]) == "0.65", name + " display proportion 0.65")
		ck(int(loaded["facing"]) == 1, name + " authored facing right")
		var has_all := true
		for a in ACTIONS:
			if not loaded["actions"].has(a):
				has_all = false
		ck(has_all and loaded["actions"].size() == ACTIONS.size(), name + " all eight authored actions")
		timing[name] = boundary_suite(name, loaded)

	for name in SETS:
		priority_suite(name, SETS[name])

	var host = make_arena()
	check_ordinary(host, "ordinary")
	host.free()

	direct_rejections()
	arena_rejections()
	finish()
