extends SceneTree

# TEST-ONLY evidence probe for the prepared heroine normal default (creator adoption pending; art UNAPPROVED).
#   godot --path game -s <abs path to this> -- --hnd18-mode=female|male|disable|missing --hnd18-out=<abs dir>
# Prints HND18_CHECK lines, writes a JSON report (and real viewport PNGs when not headless) and ends with
# HND18_<MODE>_ALL_OK only if every check passed. No game script, default, save or preference is changed.

const SPRITE_SET_PILOT_PATH := "res://scripts/exploration_sprite_set_pilot.gd"
const SEA_DRIVER_PATH := "res://scripts/hsea09/rpg-2-star-ocean-the-second_heroine-sea_distance-driver_opt-in-v01_20261020-214620-4be375a2.gd"
const BATTLE_ARENA_PATH := "res://scripts/battle_arena.gd"
const POLICY_PATH := "res://scripts/hsea18/rpg-2-star-ocean-the-second_heroine-normal-default_policy_runtime-v01_20261021-032237-7c02af94.gd"
const CONFIG_PATH := "res://scripts/hsea16/rpg-2-star-ocean-the-second_heroine-playable-path_config_opt-in-v01_20261021-015453-1036fbad.gd"
const EXPLORATION_SCENE := "res://scenes/scifi_exploration_area.tscn"
const BATTLE_SCENE := "res://scenes/battle_arena.tscn"
const CONTACT_KEYS := ["contact_event_id", "contact_event_clock", "contact_event_facing", "contact_event_active", "contact_event_state"]

var mode := ""
var out_dir := ""
var checks: Array[Dictionary] = []
var report := {}
var failed := false


func _initialize() -> void:
	_run.call_deferred()


func _arg(prefix: String) -> String:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with(prefix):
			return argument.trim_prefix(prefix)
	return ""


func _check(name: String, ok: bool, detail = null) -> void:
	checks.append({"name": name, "ok": ok, "detail": detail})
	print("HND18_CHECK %s %s %s" % ["PASS" if ok else "FAIL", name, JSON.stringify(detail)])
	if not ok:
		failed = true


func _app() -> Node:
	return root.get_node("AppState")


func _reset_overrides() -> void:
	var loader = load(SPRITE_SET_PILOT_PATH)
	loader.enabled_override = -1
	loader.registry_override = ""
	loader.clear_cache()
	load(SEA_DRIVER_PATH).enabled_override = -1
	var arena = load(BATTLE_ARENA_PATH)
	arena.combat_sprite_set_override = -1
	arena.combat_sprite_set_index_override = ""
	arena.heroine_sea_contact_override = -1


func _overrides() -> Dictionary:
	var loader = load(SPRITE_SET_PILOT_PATH)
	var arena = load(BATTLE_ARENA_PATH)
	return {"generic": loader.enabled_override, "registry": loader.registry_override, "sea": load(SEA_DRIVER_PATH).enabled_override,
		"combat": arena.combat_sprite_set_override, "index": arena.combat_sprite_set_index_override, "contact": arena.heroine_sea_contact_override,
		"user_args": Array(OS.get_cmdline_user_args()).filter(func(a): return not String(a).begins_with("--hnd18-"))}


func _new_run(appearance: String) -> void:
	var app := _app()
	app.begin_new_run()
	app.hero_appearance = appearance
	app.show_initial_guide = false
	if app.language != "en":
		app.toggle_language()
	app.select_destination("scifi.outskirts")


func _open(path: String) -> Node:
	if change_scene_to_file(path) != OK:
		return null
	for _frame in 240:
		await process_frame
		var scene := current_scene
		if scene != null and scene.scene_file_path == path and scene.is_node_ready():
			for _settle in 6:
				await process_frame
			return current_scene
	return null


func _capture(label: String) -> String:
	if DisplayServer.get_name() == "headless":
		return ""
	await RenderingServer.frame_post_draw
	var image := root.get_viewport().get_texture().get_image()
	var file := out_dir.path_join("rpg-2-star-ocean-the-second_heroine-default18_%s-%s_capture-v01_20261021-032350-9ea26e1f.png" % [mode, label])
	image.save_png(file)
	return file


func _exploration(label: String) -> Dictionary:
	var scene := await _open(EXPLORATION_SCENE)
	var info := {"scene": scene != null}
	if scene == null:
		return info
	var driver = scene.get("sprite_pilot")
	info["driver_script"] = driver.get_script().resource_path if driver != null and is_instance_valid(driver) else ""
	if info["driver_script"] == SEA_DRIVER_PATH:
		info["set_id"] = driver.sprite_set["set_id"]
		info["phase_dirs"] = driver.bridges.get("phase_bridges", {}).keys()
		info["texture"] = driver.sprite.texture.resource_path
		info["state"] = driver.state()
	var hero = scene.get("hero")
	info["hero_texture"] = hero.texture.resource_path if hero != null and hero.texture != null else ""
	info["hero_scale"] = str(hero.scale) if hero != null else ""
	info["capture"] = await _capture("explore-" + label)
	return info


func _battle(label: String) -> Dictionary:
	_app().battle_enemy_id = "patrol"
	var scene := await _open(BATTLE_SCENE)
	var info := {"scene": scene != null}
	if scene == null:
		return info
	var hero_index: int = _app().active_party_ids.find("hero")
	var fighter: Dictionary = scene.fighters[hero_index]
	var sets = scene.combat_sprite_sets
	info["default_active"] = scene.heroine_default_active
	info["combat_sets"] = sets != null
	info["hero_set"] = sets != null and sets.has_set(hero_index)
	info["hero_status"] = sets.set_status(hero_index) if sets != null else "none"
	info["index_path"] = sets.index_path if sets != null else ""
	info["loaded_count"] = sets.loaded_count() if sets != null else 0
	info["contact_keys"] = CONTACT_KEYS.filter(func(k): return fighter.has(k))
	info["capture"] = await _capture("battle-" + label)
	# Synchronous contact probe in one frame: hero placed in reach, one attack request, explicit contact clock.
	scene.paused = true
	fighter["x"] = scene.enemy_x - 20.0
	fighter["attack_cooldown"] = 0.0
	var hp0: int = scene.enemy_hp
	var requested: bool = scene._try_attack(hero_index)
	var hp_request: int = scene.enemy_hp
	var timeline := []
	if fighter.has("contact_event_id"):
		for tick in range(1, 13):
			scene._advance_contact_events(1.0 / 30.0)
			timeline.append({"tick": tick, "state": String(fighter["contact_event_state"]), "hp": scene.enemy_hp})
	info["contact"] = {"requested": requested, "hp0": hp0, "hp_after_request": hp_request, "timeline": timeline}
	return info


func _contact_tick(info: Dictionary) -> int:
	for row in info.get("contact", {}).get("timeline", []):
		if row["state"] == "recovery":
			return int(row["tick"])
	return -1


func _end_tick(info: Dictionary) -> int:
	for row in info.get("contact", {}).get("timeline", []):
		if row["state"] == "ended":
			return int(row["tick"])
	return -1


func _immediate(info: Dictionary) -> bool:
	var c: Dictionary = info.get("contact", {})
	return bool(c.get("requested", false)) and int(c["hp_after_request"]) < int(c["hp0"]) and c["timeline"].is_empty()


func _legacy_battle(info: Dictionary, name: String) -> void:
	_check(name + "_battle_legacy_frames", info.get("scene", false) and not info["default_active"] and not info["combat_sets"], info)
	_check(name + "_battle_immediate_attack", info.get("contact_keys", ["x"]).is_empty() and _immediate(info), info.get("contact"))


func _run() -> void:
	mode = _arg("--hnd18-mode=")
	out_dir = _arg("--hnd18-out=")
	DirAccess.make_dir_recursive_absolute(out_dir)
	_reset_overrides()
	report["overrides_at_start"] = _overrides()
	_check("no_overrides_or_flags_at_start", report["overrides_at_start"]["user_args"].is_empty())
	var policy = load(POLICY_PATH)
	_check("creator_default_authorized_art_still_unapproved", policy.ART_APPROVED == false and policy.CREATOR_DEFAULT_ADOPTED == true)
	match mode:
		"female":
			await _female(policy)
		"male":
			_new_run("male")
			var ex := await _exploration("default")
			report["exploration"] = ex
			_check("male_no_driver_legacy_texture", ex["driver_script"] == "" and not String(ex["hero_texture"]).contains("hsea-front17"), ex)
			_check("male_default_not_applicable", not policy.exploration_default_applies("protagonist-male"))
			var bt := await _battle("default")
			report["battle"] = bt
			_legacy_battle(bt, "male")
		"disable":
			await _disable(policy)
		"missing":
			_new_run("female")
			var status: Dictionary = policy.package_status()
			report["package_status"] = status
			_check("missing_package_refused", not status["ok"], status)
			var ex := await _exploration("missing")
			report["exploration"] = ex
			_check("missing_exploration_legacy", ex["driver_script"] == "" and not String(ex["hero_texture"]).contains("hsea-front17"), ex)
			var bt := await _battle("missing")
			report["battle"] = bt
			_legacy_battle(bt, "missing")
		_:
			_check("known_mode", false, mode)
	report["checks"] = checks
	report["mode"] = mode
	report["passed"] = not failed
	var file := FileAccess.open(out_dir.path_join("rpg-2-star-ocean-the-second_heroine-default18_%s-report_probe-v01_20261021-032350-9ea26e1f.json" % mode), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  ") + "\n")
	file.close()
	_reset_overrides()
	print("HND18_SUMMARY mode=%s checks=%d failed=%s" % [mode, checks.size(), str(failed)])
	if not failed:
		print("HND18_%s_ALL_OK" % mode.to_upper())
	quit(1 if failed else 0)


func _female(policy) -> void:
	_new_run("female")
	_check("female_default_applies", policy.exploration_default_applies("protagonist-female"))
	_check("female_package_ok", policy.package_ok(), policy.package_status())
	var ex := await _exploration("default")
	report["exploration_default"] = ex
	_check("female_default_front17_driver", ex["driver_script"] == SEA_DRIVER_PATH and String(ex.get("texture", "")).contains("hsea-front17"), ex)
	_check("female_default_phase_bridges_4dir", ex.get("phase_dirs", []).size() == 4, ex.get("phase_dirs"))
	var bt := await _battle("default")
	report["battle_default"] = bt
	_check("female_default_battle_set", bt["default_active"] and bt["hero_set"] and bt["index_path"] == policy.COMBAT_INDEX_PATH, bt)
	_check("female_default_contact_keys", bt["contact_keys"].size() == CONTACT_KEYS.size(), bt["contact_keys"])
	var c: Dictionary = bt["contact"]
	_check("female_default_no_damage_at_request", c["requested"] and c["hp_after_request"] == c["hp0"], c)
	_check("female_default_contact_5_of_30_recovery_end_12_of_30", _contact_tick(bt) == 5 and _end_tick(bt) == 12 and int(c["timeline"][4]["hp"]) < int(c["hp0"]) and int(c["timeline"][3]["hp"]) == int(c["hp0"]), c["timeline"])
	_check("no_overrides_mutated_by_default", _overrides() == report["overrides_at_start"], _overrides())
	# Existing opt-in heroine path (hsea16 config) in the same process for an exact comparison.
	var configured: Dictionary = load(CONFIG_PATH).configure(_app(), "en", "scifi.outskirts")
	_check("optin_configure_ok", configured["ok"], configured)
	var ex_opt := await _exploration("optin")
	report["exploration_optin"] = ex_opt
	var same_ex := true
	for key in ["driver_script", "set_id", "phase_dirs", "texture", "hero_scale", "state"]:
		same_ex = same_ex and str(ex_opt.get(key)) == str(ex.get(key))
	_check("optin_exploration_matches_default", same_ex, {"default": ex, "optin": ex_opt})
	var bt_opt := await _battle("optin")
	report["battle_optin"] = bt_opt
	_check("optin_battle_explicit_not_default", not bt_opt["default_active"] and bt_opt["hero_set"])
	var same_bt: bool = bt_opt["hero_status"] == bt["hero_status"] and bt_opt["index_path"] == bt["index_path"] and bt_opt["loaded_count"] == bt["loaded_count"] \
		and str(bt_opt["contact_keys"]) == str(bt["contact_keys"]) and str(bt_opt["contact"]) == str(bt["contact"])
	_check("optin_battle_matches_default", same_bt, {"default": bt["contact"], "optin": bt_opt["contact"]})


func _disable(policy) -> void:
	var loader = load(SPRITE_SET_PILOT_PATH)
	var sea = load(SEA_DRIVER_PATH)
	var arena = load(BATTLE_ARENA_PATH)
	_new_run("female")
	sea.enabled_override = 0
	var ex := await _exploration("sea0")
	report["exploration_sea0"] = ex
	_check("sea_override0_disables_driver", ex["driver_script"] == "" and not String(ex["hero_texture"]).contains("hsea-front17"), ex)
	_reset_overrides()
	loader.enabled_override = 0
	_check("generic_override0_disables_default", not policy.exploration_default_applies("protagonist-female"))
	_reset_overrides()
	loader.registry_override = "res://data/exploration-sprite-sets/rpg-2-star-ocean-the-second_exploration-sprite-set-registry_no-approved-sets-v01_20261018-153932-9f31902d.json"
	_check("explicit_registry_override_not_default", not policy.exploration_default_applies("protagonist-female"))
	_reset_overrides()
	arena.combat_sprite_set_override = 0
	var bt0 := await _battle("combat0")
	report["battle_combat0"] = bt0
	_legacy_battle(bt0, "combat_override0")
	_reset_overrides()
	arena.heroine_sea_contact_override = 0
	var btc := await _battle("contact0")
	report["battle_contact0"] = btc
	_check("contact_override0_keeps_default_art", btc["default_active"] and btc["hero_set"], btc)
	_check("contact_override0_immediate_attack", btc["contact_keys"].is_empty() and _immediate(btc), btc["contact"])
	_reset_overrides()
	arena.combat_sprite_set_override = 1
	var bt1 := await _battle("combat1-fixture")
	report["battle_combat1_fixture"] = bt1
	_check("explicit_combat1_old_fixture_profile", not bt1["default_active"] and bt1["index_path"] == arena.COMBAT_SPRITE_SET_INDEX and bt1["contact_keys"].is_empty(), bt1)
	_reset_overrides()
	arena.heroine_sea_contact_override = 1
	var btk := await _battle("contact1-only")
	report["battle_contact1_only"] = btk
	_check("explicit_contact1_only_old_profile", not btk["default_active"] and not btk["combat_sets"] and btk["contact_keys"].size() == CONTACT_KEYS.size(), btk)
	_reset_overrides()
