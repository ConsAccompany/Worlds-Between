extends SceneTree
# Independent source-fixture compatibility check; not an artistic or human-play acceptance.
var area_script: Script
const NavSkin :=  preload("res://scripts/rpg-2-star-ocean-the-second_navigation-ui_skin-helper_v01_20261019-174604-f7b34a81.gd")
var checks: Array = []
var app: Node

func _initialize() -> void:
	call_deferred("run")

func check(label: String, okay: bool) -> void:
	checks.append({"label": label, "pass": okay})
	assert(okay, label)

func snapshot(node: Node) -> Array:
	var result: Array = []
	for child in node.get_children():
		if String(child.name).begins_with("NavigationUiSkinPilotPlate"):
			continue
		if child is Control:
			var data: Array = [child.get_instance_id(), child.position, child.size, child.get_combined_minimum_size(), child.visible, child.mouse_filter, child.focus_mode, child.get_theme_font_size("font_size"), child.get_theme_font("font")]
			if child is Button or child is Label:
				data.append(child.text)
			if child is Button:
				data.append(child.disabled)
				data.append(child.pressed.get_connections())
			result.append(data)
		result.append_array(snapshot(child))
	return result

func plates(node: Node) -> Array:
	return node.find_children("NavigationUiSkinPilotPlate*", "NinePatchRect", true, false)

func panel_plate(node: Node) -> Control:
	for child in node.dialogue_panel.get_children():
		if String(child.name).begins_with("NavigationUiSkinPilotPlate"):
			return child
	return null

func detach_audio(node: Node) -> void:
	for child in node.get_children():
		if child is AudioStreamPlayer or child is AudioStreamPlayer2D or child is AudioStreamPlayer3D:
			child.stop()
			child.stream = null
		detach_audio(child)

func run() -> void:
	root.size = Vector2i(640, 360)
	app = root.get_node("AppState")
	area_script = load("res://scripts/scifi_exploration_area.gd")
	check("isolated-settings-missing", app.settings.load_status == "missing")
	SaveStore.root_path = "user://ui52-regression-isolated"
	for language in ["en", "zh"]:
		for portrait_on in [false, true]:
			app.begin_new_run()
			app.language = language
			app.current_destination_id = "scifi.city"
			app.show_initial_guide = false
			area_script.navigation_ui_skin_override = 0
			area_script.character_ui_portraits_override = 1 if portrait_on else 0
			var node: Node = load("res://scenes/scifi_exploration_area.tscn").instantiate()
			root.add_child(node)
			for i in 3:
				await process_frame
			var key: String = language + "-portraits-" + str(portrait_on)
			check(key + "-starts-with-zero-plates", plates(node).is_empty())
			var initial := snapshot(node)
			var skin := NavSkin.new("res://assets/ui/battle-skin-v01")
			check(key + "-apply", skin.apply(node))
			check(key + "-three-plates", plates(node).size() == 3)
			check(key + "-geometry-text-font-input-callables-unchanged", snapshot(node) == initial)
			check(key + "-idempotent", skin.apply(node) and plates(node).size() == 3)
			node._open_dialogue()
			await process_frame
			if portrait_on:
				check(key + "-recruit-portrait-visible", node.character_ui_portraits.is_showing_dialogue())
				check(key + "-dialogue-plate-below-portrait", node.dialogue_panel.get_child(0) == panel_plate(node))
				for phase in ["recruit", "trace", "disabled", "restored", "closed"]:
					if phase == "trace":
						node._open_field_trace(0)
					elif phase == "disabled":
						node.character_ui_portraits.apply_dialogue("recruit", "liang-xu", false)
					elif phase == "restored":
						node._open_dialogue()
					elif phase == "closed":
						node._close_dialogue()
					await process_frame
					var plate := panel_plate(node)
					check(key + "-" + phase + "-exact-plate-follows-panel", plate != null and plate.position == Vector2.ZERO and plate.size == node.dialogue_panel.size)
					if phase in ["trace", "disabled", "closed"]:
						check(key + "-" + phase + "-portrait-hidden", not node.character_ui_portraits.is_showing_dialogue())
			skin.revert()
			check(key + "-revert-zero-plates", plates(node).is_empty())
			var restored := snapshot(node)
			check(key + "-reapply-after-transitions", skin.apply(node))
			check(key + "-reapply-preserves-all-controls", snapshot(node) == restored)
			skin.revert()
			check(key + "-revert-restores-all-controls", snapshot(node) == restored)
			var old_position: Vector2 = node.dialogue_panel.position
			node.dialogue_panel.position += Vector2(1, 0)
			var malformed := snapshot(node)
			check(key + "-moved-panel-refused", not skin.apply(node))
			check(key + "-refusal-atomic", snapshot(node) == malformed and plates(node).is_empty())
			node.dialogue_panel.position = old_position
			var missing := NavSkin.new("res://missing-ui52-package")
			var before_missing := snapshot(node)
			check(key + "-missing-package-refused", not missing.apply(node))
			check(key + "-missing-refusal-atomic", snapshot(node) == before_missing and plates(node).is_empty())
			detach_audio(node)
			root.remove_child(node)
			node.free()
			await process_frame
	area_script.navigation_ui_skin_override = -1
	area_script.character_ui_portraits_override = -1
	var path := OS.get_cmdline_user_args()[0]
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify({"checks": checks, "count": checks.size(), "fixture": "normal .tscn with test-only static override matrix and direct dialogue transitions", "skinSha256": FileAccess.get_sha256("res://scripts/rpg-2-star-ocean-the-second_navigation-ui_skin-helper_v01_20261019-174604-f7b34a81.gd")}, "  ") + "\n")
	file.close()
	call_deferred("finish")

func finish() -> void:
	var previous := AudioServer.get_time_since_last_mix()
	var mixes := 0
	var deadline := Time.get_ticks_usec() + 500000
	while mixes < 2 and Time.get_ticks_usec() < deadline:
		await process_frame
		var age := AudioServer.get_time_since_last_mix()
		if age < previous:
			mixes += 1
		previous = age
	assert(mixes == 2, "audio cleanup two real mix boundaries")
	print("UI52_COMPAT_OK checks=", checks.size())
	quit(0)
