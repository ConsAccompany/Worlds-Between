extends SceneTree
const Helper = preload("res://scripts/rpg-2-star-ocean-the-second_battle-ui_skin-helper_root-v02_20261019-172332-dc55a291.gd")
const TAG = "20261019-174000-89f5e61d"
const MANIFEST = Helper.MANIFEST_NAME
var checks: Array = []
var fixture: String
var out: String
var original: Dictionary
var arena: Node2D
func ck(key: String, pass_value: bool) -> void:
	checks.append({"key": key, "pass": pass_value})
func _initialize() -> void: call_deferred("run")
func snapshot(node: Node) -> Array:
	var rows = []
	for child in node.get_children():
		var row = [child.get_class(), str(child.get_path())]
		if child is Control:
			row.append([child.position, child.size, child.get_combined_minimum_size(), child.theme])
			for style in ["normal", "hover", "pressed", "hover_pressed", "disabled", "focus", "background", "fill"]:
				row.append([style, child.has_theme_stylebox_override(style), child.get_theme_stylebox(style).get_instance_id()])
			for color in Helper.FONT_COLOR_NAMES:
				row.append([color, child.has_theme_color_override(color), child.get_theme_color(color)])
		rows.append(row)
		rows.append_array(snapshot(child))
	return rows
func write_manifest(value: Variant) -> void:
	var file = FileAccess.open(fixture.path_join(MANIFEST), FileAccess.WRITE)
	file.store_string(JSON.stringify(value))
	file.close()
func bad_case(label: String, value: Variant, text_override: String = "") -> void:
	write_manifest(value)
	if text_override != "":
		var file = FileAccess.open(fixture.path_join(MANIFEST), FileAccess.WRITE)
		file.store_string(text_override)
		file.close()
	var before = snapshot(arena)
	var helper = Helper.new(fixture)
	ck(label + "-reject", not helper.apply(arena))
	ck(label + "-error-explained", helper.last_error != "")
	ck(label + "-no-ui-mutation", snapshot(arena) == before)
	ck(label + "-not-applied-no-undo", not helper.applied and helper._undo.is_empty())
	helper.revert()
	ck(label + "-revert-safe", snapshot(arena) == before)
func run() -> void:
	var args = OS.get_cmdline_user_args()
	fixture = args[0]
	out = args[1]
	DirAccess.make_dir_recursive_absolute(fixture)
	DirAccess.make_dir_recursive_absolute(out)
	original = JSON.parse_string(FileAccess.get_file_as_string("res://assets/ui/battle-skin-v01/" + MANIFEST))
	for key in original.skins:
		var name: String = original.skins[key].png
		ck("fixture-copy-" + key, DirAccess.copy_absolute(ProjectSettings.globalize_path("res://assets/ui/battle-skin-v01/" + name), fixture.path_join(name)) == OK)
	var app = root.get_node("AppState")
	app.begin_new_run()
	app.language = "en"
	app.select_destination("scifi.city")
	app.begin_battle("patrol", Vector2(330, 215))
	var script = load("res://scripts/battle_arena.gd")
	script.battle_ui_skin_override = 0
	script.battle_vfx_override = 0
	script.skill_vfx_override = 0
	script.sentry_v2_override = 0
	script.encounter_feedback_override = 0
	script.combat_sprite_set_override = 0
	arena = script.new()
	root.add_child(arena)
	arena.set_process(false)
	await process_frame
	write_manifest(original)
	var control = Helper.new(fixture)
	ck("valid-package-positive-control", control.apply(arena))
	ck("valid-package-idempotent", control.apply(arena))
	var second = Helper.new(fixture)
	var applied_snapshot = snapshot(arena)
	ck("second-instance-refuses-existing-plates", not second.apply(arena) and second.last_error == "already skinned")
	ck("second-instance-no-ui-mutation", snapshot(arena) == applied_snapshot)
	control.revert()
	ck("valid-package-four-plates-reverted", arena.find_children("BattleUiSkinPilotPlate", "NinePatchRect", true, false).is_empty())
	bad_case("invalid-json", {}, "{ invalid")
	bad_case("top-array", [])
	var m = original.duplicate(true)
	m.skins = []
	bad_case("skins-array", m)
	m = original.duplicate(true)
	m.skins.erase("hud-band")
	bad_case("missing-kind", m)
	for value in [null, {}, [], "24", true, 24.5, -1]:
		m = original.duplicate(true)
		m.skins["hud-band"].size = [value, 24]
		bad_case("size-x-" + str(value), m)
		m.skins["hud-band"].size = [24, value]
		bad_case("size-y-" + str(value), m)
	for value in [null, {}, [], "4", true, 4.5, -1]:
		for side in ["left", "right", "top", "bottom"]:
			m = original.duplicate(true)
			m.skins["hud-band"].slices[side] = value
			bad_case("slice-" + side + "-" + str(value), m)
	for value in [null, {}, [], "../missing.png", "..\\missing.png", "", "wrong.jpg", "missing.png"]:
		m = original.duplicate(true)
		m.skins["hud-band"].png = value
		bad_case("png-" + str(value), m)
	for value in [null, {}, [], "wrong", 3]:
		m = original.duplicate(true)
		m.skins["hud-band"].sha256 = value
		bad_case("hash-map-" + str(value), m)
	for value in [null, {}, [], "wrong", 3]:
		m = original.duplicate(true)
		m.skins["hud-band"].sha256[m.skins["hud-band"].png] = value
		bad_case("hash-value-" + str(value), m)
	for value in [null, {}, [], "bad", 3]:
		m = original.duplicate(true)
		m.fontColors = value
		bad_case("font-map-" + str(value), m)
	for value in [null, {}, [], "not-color", 3]:
		m = original.duplicate(true)
		m.fontColors.font_color = value
		bad_case("font-color-" + str(value), m)
	m = original.duplicate(true)
	m.skins["hud-band"].slices = []
	bad_case("slices-array", m)
	m = original.duplicate(true)
	m.skins["hud-band"].size = {}
	bad_case("size-map", m)
	var name: String = original.skins["hud-band"].png
	var small = Image.create(8, 8, false, Image.FORMAT_RGBA8)
	small.fill(Color.BLUE)
	ck("wrong-dimension-fixture-created", small.save_png(fixture.path_join(name)) == OK)
	m = original.duplicate(true)
	m.skins["hud-band"].sha256[name] = FileAccess.get_sha256(fixture.path_join(name))
	bad_case("hash-correct-wrong-image-size", m)
	ck("restore-fixture-image", DirAccess.copy_absolute(ProjectSettings.globalize_path("res://assets/ui/battle-skin-v01/" + name), fixture.path_join(name)) == OK)
	write_manifest(original)
	DirAccess.remove_absolute(fixture.path_join(MANIFEST))
	var before = snapshot(arena)
	var missing = Helper.new(fixture)
	ck("missing-manifest-reject", not missing.apply(arena))
	ck("missing-manifest-no-ui-mutation", snapshot(arena) == before)
	write_manifest(original)
	var empty = Node2D.new()
	var empty_helper = Helper.new(fixture)
	ck("missing-arena-targets-reject", not empty_helper.apply(empty))
	ck("missing-arena-targets-no-mutation", empty.get_child_count() == 0 and empty_helper._undo.is_empty())
	empty.free()
	var failed = checks.filter(func(row): return not row["pass"])
	var report = {"tag": TAG, "checks": checks, "count": checks.size(), "failed": failed, "helperRawSha256": FileAccess.get_sha256(ProjectSettings.globalize_path("res://scripts/rpg-2-star-ocean-the-second_battle-ui_skin-helper_root-v02_20261019-172332-dc55a291.gd")), "limitations": ["Transactional malformed metadata test; not a fullgame replay or an artistic inspection."]}
	var file = FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_battle-ui_invalid-package-report_v01_" + TAG + ".json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	arena.queue_free()
	await process_frame
	print("HUD_INVALID_PACKAGE ", checks.size() - failed.size(), "/", checks.size(), " PASS" if failed.is_empty() else " FAIL")
	quit(0 if failed.is_empty() else 1)
