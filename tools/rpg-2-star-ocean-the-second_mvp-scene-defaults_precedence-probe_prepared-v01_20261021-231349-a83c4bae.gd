extends SceneTree

# sdef35 precedence probe (PREPARED policy, nothing adopted). Checks, without touching AppState mechanics:
# 1. all four policy bits are false and default_on() is false for every key;
# 2. per scene: no flag -> off; preview_override -> on; explicit 0 override beats preview; clear_preview()
#    restores off (rollback); Washington older v12r2 override keeps priority over the policy;
# 3. the runtime Chicago Loop .tscn root script is the v05 selector (wired), still inert without a flag.
# Run with no game user args. Prints SDEF35_PROBE_OK only when every check passes.

const POLICY := "res://scripts/sdef35/rpg-2-star-ocean-the-second_mvp-scene-defaults_policy_prepared-v01_20261021-231349-a83c4bae.gd"
const CITY := "res://scripts/city_hall_park_v06_scene.gd"
const V13 := "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v13_20261018-135539-63201688.gd"
const V05 := "res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-scene-opt-in-selector_unapproved-v05_20261017-234337-84862412.gd"
const LOOP_TSCN := "res://scenes/rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn"
const ANNEX := "res://scripts/survey_annex.gd"

var failures: Array[String] = []
var passed := 0


func check(name: String, ok: bool) -> void:
	if ok:
		passed += 1
		print("PASS ", name)
	else:
		failures.append(name)
		print("FAIL ", name)


func _initialize() -> void:
	var policy: GDScript = load(POLICY)
	var city: GDScript = load(CITY)
	var v13: GDScript = load(V13)
	var v05: GDScript = load(V05)
	check("no user args", OS.get_cmdline_user_args().is_empty())
	var consts := policy.get_script_constant_map()
	for bit in ["CITY_V06_DEFAULT", "RUINS_V13_DEFAULT", "RECORDS_ROOM2_DEFAULT", "CHICAGO_V05_DEFAULT"]:
		check("bit %s is false" % bit, consts.get(bit) == false)
	for key in [policy.CITY, policy.RUINS, policy.RECORDS, policy.CHICAGO]:
		check("default_on(%s) false" % key, policy.default_on(key) == false)

	check("city off by default", city.enabled() == false)
	policy.preview_override[policy.CITY] = true
	check("city preview on", city.enabled() == true)
	city.enabled_override = 0
	check("city explicit 0 beats preview", city.enabled() == false)
	city.enabled_override = -1
	policy.clear_preview()
	check("city rollback off", city.enabled() == false)

	check("ruins off by default", v13.v13_enabled() == false)
	policy.preview_override[policy.RUINS] = true
	check("ruins preview on", v13.v13_enabled() == true)
	v13.r2_override = 1
	check("ruins older v12r2 override keeps priority", v13.v13_enabled() == false)
	v13.r2_override = -1
	v13.v13_override = 0
	check("ruins explicit 0 beats preview", v13.v13_enabled() == false)
	v13.v13_override = -1
	policy.clear_preview()
	check("ruins rollback off", v13.v13_enabled() == false)

	var annex_src := FileAccess.get_file_as_string(ANNEX)
	check("records gate scoped to ruins room 2 + flag-or-policy",
		annex_src.contains("wdc_room_two_walls = room == 2 and destination_id == \"scifi.ruins\"")
		and annex_src.contains("if wdc_room_two_walls and (OS.get_cmdline_user_args().has(WDC_ROOM_TWO_FLAG) or SceneDefaults35.default_on(SceneDefaults35.RECORDS)):"))
	policy.preview_override[policy.RECORDS] = true
	check("records preview on", policy.default_on(policy.RECORDS) == true)
	policy.clear_preview()
	check("records rollback off", policy.default_on(policy.RECORDS) == false)

	check("chicago v05 explicit off by default", v05.v05_enabled() == false)
	var packed: PackedScene = load(LOOP_TSCN)
	var root := packed.instantiate()
	var script: Script = root.get_script()
	check("Loop .tscn wired to v05 selector", script != null and script.resource_path == V05)
	root.free()
	var v05_src := FileAccess.get_file_as_string(V05)
	check("chicago policy fallback after every explicit flag",
		v05_src.find("V03Selector.V03_SCENE") < v05_src.find("SceneDefaults35.default_on(SceneDefaults35.CHICAGO)"))

	print("SDEF35_PROBE passed=%d failed=%d" % [passed, failures.size()])
	if failures.is_empty():
		print("SDEF35_PROBE_OK")
		quit(0)
	else:
		quit(1)
