extends SceneTree

const TAG := "20261019-180100-fd60b5a8"
var checks: Array = []
var app: Node
var output: String

func _initialize() -> void:
	call_deferred("run")

func check(label: String, okay: bool) -> void:
	checks.append({"key": label, "pass": okay})

func setup(kind: String, mode: int, language: String, frozen: bool = false) -> Control:
	app.begin_new_run()
	app.language = language
	app.save_screen_mode = "save"
	SaveStore.root_path = "user://management-ui-root/" + kind + "-" + language
	app.recruit_member("liang-xu")
	app.recruit_member("zhao-ling")
	app.ji_records_checked = true
	app.recruit_member("ji-cheng")
	var path := "res://scripts/" + kind + "_screen.gd"
	if frozen:
		path = output.path_join("rpg-2-star-ocean-the-second_management-" + kind + "_frozen-before-wiring_v01_" + TAG + ".gd")
	var script: Script = load(path)
	if not frozen:
		script.management_ui_skin_override = mode
	var screen: Control = script.new()
	screen.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.add_child(screen)
	current_scene = screen
	await process_frame
	return screen

func dispose(screen: Control) -> void:
	screen.queue_free()
	await process_frame

func control_state(screen: Control) -> Array:
	var rows: Array = []
	for node in screen.find_children("*", "Control", true, false):
		if String(node.name).begins_with("ManagementUiSkinPilotPlate") or not node.is_visible_in_tree():
			continue
		var text := String(node.text) if node is Label or node is Button else ""
		var row: Array = [node.get_class(), node.get_global_rect(), node.get_combined_minimum_size(), text, node.get_theme_font_size("font_size")]
		if node is Button:
			var connections: Array = []
			for item in node.pressed.get_connections():
				connections.append(String(item.callable.get_method()))
			row.append([node.disabled, node.focus_mode, connections])
		rows.append(row)
	return rows

func capture(label: String) -> Image:
	await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	image.convert(Image.FORMAT_RGBA8)
	check("capture-" + label, image.save_png(output.path_join("rpg-2-star-ocean-the-second_management-ui_" + label + "_actual-640_v01_" + TAG + ".png")) == OK)
	return image

func click_at(point: Vector2) -> void:
	var motion := InputEventMouseMotion.new()
	motion.position = point
	root.push_input(motion, true)
	for pressed in [true, false]:
		var event := InputEventMouseButton.new()
		event.position = point
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = pressed
		root.push_input(event, true)

func run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 1:
		push_error("Expected absolute output directory")
		quit(2)
		return
	output = args[0]
	root.size = Vector2i(640, 360)
	root.content_scale_size = Vector2i(640, 360)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	await process_frame
	app = root.get_node("AppState")
	SaveStore.root_path = "user://management-ui-root"
	for kind in ["growth", "save"]:
		for language in ["en", "zh"]:
			var old := await setup(kind, 0, language, true)
			var baseline_controls := control_state(old)
			var baseline_image := await capture(kind + "-" + language + "-baseline")
			await dispose(old)
			var off := await setup(kind, 0, language)
			var off_image := await capture(kind + "-" + language + "-off")
			check(kind + language + "-default-zero-pixel-diff", baseline_image.get_data() == off_image.get_data())
			check(kind + language + "-default-controls", baseline_controls == control_state(off))
			var contexts: Dictionary = {"main": control_state(off)}
			if kind == "growth":
				off._show_nodes(true)
				await process_frame
				await RenderingServer.frame_post_draw
				contexts["nodes"] = control_state(off)
			await dispose(off)
			var on := await setup(kind, 1, language)
			check(kind + language + "-applied", on.management_ui_skin_status == "applied")
			check(kind + language + "-main-exact", contexts.main == control_state(on))
			await capture(kind + "-" + language + "-main-skin")
			check(kind + language + "-expected-plate-count", on.find_children("ManagementUiSkinPilotPlate*", "NinePatchRect", true, false).size() == (4 if kind == "growth" else 9))
			for plate in on.find_children("ManagementUiSkinPilotPlate*", "NinePatchRect", true, false):
				check(kind + language + "-plate-input-clear", plate.mouse_filter == Control.MOUSE_FILTER_IGNORE and plate.focus_mode == Control.FOCUS_NONE)
			if kind == "growth":
				click_at(on.member_buttons[1].get_global_rect().get_center())
				await process_frame
				check(language + "-real-party-click", on.selected_id == "liang-xu")
				on._select(0)
				click_at(on.nodes_button.get_global_rect().get_center())
				await process_frame
				await RenderingServer.frame_post_draw
				check(language + "-real-nodes-open", on.node_panel.visible)
				check(language + "-nodes-controls-exact", contexts.nodes == control_state(on))
				if contexts.nodes != control_state(on):
					var actual_nodes := control_state(on)
					print("NODE_GEOMETRY_DIAGNOSTIC " + JSON.stringify({"lang": language, "expected": contexts.nodes, "actual": actual_nodes}))
				await capture("growth-" + language + "-nodes-skin")
				click_at(on.node_close_button.get_global_rect().get_center())
				await process_frame
				check(language + "-real-nodes-close", not on.node_panel.visible)
			else:
				click_at(on.manual_save_buttons[0].get_global_rect().get_center())
				await process_frame
				check(language + "-real-save-click", SaveStore.list_entries().any(func(entry): return entry.get("kind") == "manual" and entry.get("slot") == 1))
			var helper = on.management_ui_skin
			check(kind + language + "-same-instance-idempotent", helper.apply(on))
			helper.revert()
			await process_frame
			check(kind + language + "-revert-no-plates", on.find_children("ManagementUiSkinPilotPlate*", "NinePatchRect", true, false).is_empty())
			await dispose(on)
	for kind in ["growth", "save"]:
		var script: Script = load("res://scripts/" + kind + "_screen.gd")
		script.management_ui_skin_override = -1
	var helper_script: Script = load("res://scripts/rpg-2-star-ocean-the-second_management-ui_skin-helper_v01_20261019-173546-f3412b43.gd")
	var valid_dir := "res://assets/ui/battle-skin-v01"
	var blank := Control.new()
	root.add_child(blank)
	var invalid_target = helper_script.new(valid_dir)
	check("missing-target-refs-safe-reject", not invalid_target.apply(blank) and blank.get_child_count() == 0)
	blank.queue_free()
	await process_frame
	var target := await setup("growth", 0, "en")
	var before := control_state(target)
	var child_count := target.get_child_count()
	var bad_dir := "user://management-ui-bad-fixtures"
	DirAccess.make_dir_recursive_absolute(bad_dir)
	for text in ["{", "null", "{}", "[]", "{\"skins\":false}"]:
		var fixture := FileAccess.open(bad_dir.path_join(helper_script.MANIFEST_NAME), FileAccess.WRITE)
		fixture.store_string(text)
		fixture.close()
		var bad = helper_script.new(bad_dir)
		check("invalid-package-safe-reject-" + text, not bad.apply(target) and control_state(target) == before and target.get_child_count() == child_count)
	var missing = helper_script.new("user://management-ui-missing-package")
	check("missing-package-safe-reject", not missing.apply(target) and control_state(target) == before and target.get_child_count() == child_count)
	await dispose(target)
	var failed := checks.filter(func(item): return not item.pass)
	var report := {"passed": checks.size() - failed.size(), "failed": failed.size(), "failures": failed, "checks": checks, "artApproved": false, "sourceHashMode": "raw"}
	var file := FileAccess.open(output.path_join("rpg-2-star-ocean-the-second_management-ui_root-runtime-report_v01_" + TAG + ".json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, " ") + "\n")
	file.close()
	print(JSON.stringify({"passed": report.passed, "failed": report.failed, "failures": failed}))
	print("MANAGEMENT_UI_ROOT_DONE")
	quit(0 if failed.is_empty() else 1)
