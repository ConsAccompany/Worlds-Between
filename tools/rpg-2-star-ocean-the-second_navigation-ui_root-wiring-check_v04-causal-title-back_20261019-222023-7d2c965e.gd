extends SceneTree

# Bounded windowed check of the opt-in `--navigation-ui-skin-pilot` wiring in scifi_exploration_area.gd,
# survey_annex.gd and scifi_world_map.gd (UNAPPROVED technical candidate, no art approval).
# Root v04: source-bound causal Save pixel mask replaces the incorrect all-Save-pixels-identical expectation.
# Root v03: retains v02 predicates; declares the additional NYC English room1 title repair.
# Producer v02 source is frozen/hash-bound by the root run manifest.
# v02-backfix: v01's 259 predicates plus the NYC annex Back layout repair. The original refusal fixture now runs on
# the pre-repair wired copy of survey_annex.gd (it must still refuse); the repaired source is compared with it and
# with the pre-wiring copy, and the only declared default change is the NYC English Back font step and rect.
# Run: Godot --path game --resolution 640x360 --audio-driver Dummy -s res://tests/<this>.gd --
#      --capture-dir=<abs dir> --frozen-dir=<abs dir holding the pre-wiring copies of the three scripts>
#      --prerepair-dir=<abs dir holding the wired, pre-repair copy of survey_annex.gd>
# Fixture states (labelled, not a human playtest): dialogue/clue/credits/route card are opened by calling the
# scene's own open function; closes, field log/company open+close and route option/cancel use real mouse events.

# Capture names use this run's actual UTC start time plus the task id.
const TASK_ID := "7d2c965e"
var stamp := ""
const PLATE_PREFIX := "NavigationUiSkinPilotPlate"
const HELPER := "res://scripts/rpg-2-star-ocean-the-second_navigation-ui_skin-helper_v01_20261019-174604-f7b34a81.gd"
const SKIN_DIR := "res://assets/ui/battle-skin-v01"
const SCRIPTS := {
	"exploration": "res://scripts/scifi_exploration_area.gd",
	"annex": "res://scripts/survey_annex.gd",
	"map": "res://scripts/scifi_world_map.gd",
}
const SCENES := {
	"exploration": "res://scenes/scifi_exploration_area.tscn",
	"annex": "res://scenes/survey_annex.tscn",
	"map": "res://scenes/scifi_world_map.tscn",
}
const EXPECTED_PLATES := {"exploration": 3, "annex": 3, "map": 5}
# Annex captures use Yonkers room 1 (its English Back is widened to fit). NYC room 1 English is a refusal fixture on
# the pre-repair source: its "Return outside" Back grows to 123 px at x 525 and ends at x 648, past the 640 view.
const YONKERS := "scifi.outskirts"
const ANNEX_PLACES := ["scifi.city", "scifi.outskirts", "scifi.ruins"]
# The NYC Back keeps x 525 and the 98x38 button of every other annex; only its font steps down when the label is wider.
const REPAIRED_BACK := Rect2(525, 12, 98, 38)
const HEADER := Rect2(0, 0, 640, 62)

var app: Node
var checks := 0
var fails := 0
var capture_dir := ""
var frozen_dir := ""
var prerepair_dir := ""
var current: Node = null


func _initialize() -> void:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--capture-dir="):
			capture_dir = argument.trim_prefix("--capture-dir=")
		elif argument.begins_with("--frozen-dir="):
			frozen_dir = argument.trim_prefix("--frozen-dir=")
		elif argument.begins_with("--prerepair-dir="):
			prerepair_dir = argument.trim_prefix("--prerepair-dir=")
	_run.call_deferred()


func _check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		fails += 1
		print("NAVUI_FAIL ", label)


func _run() -> void:
	app = root.get_node("AppState")
	stamp = Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-") + "-" + TASK_ID
	_check(capture_dir != "" and DirAccess.dir_exists_absolute(capture_dir), "capture dir exists")
	_check(frozen_dir != "" and FileAccess.file_exists(frozen_dir.path_join("scifi_world_map.gd")), "frozen dir exists")
	_check(prerepair_dir != "" and FileAccess.file_exists(prerepair_dir.path_join("survey_annex.gd")), "pre-repair dir exists")
	_check(root.get_visible_rect().size == Vector2(640, 360), "viewport 640x360 " + str(root.get_visible_rect().size))
	for kind in SCRIPTS:
		var script: GDScript = load(SCRIPTS[kind])
		_check(script.navigation_ui_skin_override == -1, kind + " override default -1")
		_check(not script.call("navigation_ui_skin_enabled"), kind + " pilot off by default")
	await _helper_unit_checks()
	for language in ["en", "zh"]:
		for context in ["explore", "annex", "map", "field", "company", "credits", "route"]:
			await _context_checks(context, language)
	await _interaction_checks()
	await _real_scene_checks()
	await _nyc_annex_fallback_checks()
	await _annex_header_repair_checks()
	await _nyc_language_refresh_checks()
	await _nyc_header_mouse_checks()
	for kind in SCRIPTS:
		load(SCRIPTS[kind]).navigation_ui_skin_override = -1
	load(prerepair_dir.path_join("survey_annex.gd")).navigation_ui_skin_override = -1
	print("NAVUI_WIRING checks %d fails %d %s" % [checks, fails, "NAVUI_WIRING_ALL_OK" if fails == 0 else "FAILED"])
	quit(0 if fails == 0 else 1)


func _reset_state(language: String, destination := "scifi.city") -> void:
	app.language = language
	app.current_destination_id = destination
	app.current_annex_room = 1
	app.show_initial_guide = false
	app.recruited_members.erase("liang-xu")
	app.returning_from_battle = false
	app.resume_area_pending = false
	app.resume_annex_pending = false


func _kind_of(context: String) -> String:
	if context == "explore":
		return "exploration"
	if context == "annex":
		return "annex"
	return "map"


# variant: "frozen" (pre-wiring copy), "off" or "on" (wired, repaired script, static override 0/1),
# "prerepair-off" / "prerepair-on" (annex only: the wired copy before the NYC Back repair).
func _spawn(kind: String, variant: String) -> Node:
	var wired: GDScript = load(SCRIPTS[kind])
	wired.navigation_ui_skin_override = 1 if variant == "on" else 0
	var script: GDScript = wired
	if variant == "frozen":
		script = load(frozen_dir.path_join(SCRIPTS[kind].get_file()))
	elif variant.begins_with("prerepair-"):
		script = load(prerepair_dir.path_join(SCRIPTS[kind].get_file()))
		script.navigation_ui_skin_override = 1 if variant == "prerepair-on" else 0
	var node := Node2D.new()
	node.set_script(script)
	root.add_child(node)
	current = node
	return node


func _despawn() -> void:
	if current != null:
		root.remove_child(current)
		current.free()
		current = null
	await process_frame


func _settle() -> void:
	for i in 4:
		await process_frame
	await RenderingServer.frame_post_draw


# Opens one visual context with the scene's own functions (fixture) on an already spawned scene.
func _open_context(node: Node, context: String) -> void:
	match context:
		"explore":
			node._open_dialogue()
		"annex":
			app.survey_clues[node._clue_key(0)] = true
			node._inspect_clue(0)
		"field":
			node._open_field_log()
		"company":
			node.open_commerce()
		"credits":
			node.open_map_credits()
		"route":
			node.select_place(_other_place(node))


func _other_place(node: Node) -> String:
	var here: String = node.route_adapter.current_place_id()
	for place in node.places:
		if String(place["id"]) != here:
			return String(place["id"])
	return ""


func _plates(node: Node) -> Array:
	var out := []
	var stack: Array = [node]
	while not stack.is_empty():
		var item: Node = stack.pop_back()
		if String(item.name).begins_with(PLATE_PREFIX):
			out.append(item)
		stack.append_array(item.get_children())
	return out


# Every visible Control except the pilot's own plates: index path, rect, minimum, text, font size, disabled,
# focus mode, visibility and signal connection counts.
func _controls(node: Node, path := "") -> Array:
	var out := []
	for index in node.get_child_count():
		var child := node.get_child(index)
		if String(child.name).begins_with(PLATE_PREFIX):
			continue
		var child_path := path + "/" + str(index)
		if child is Control and child.is_visible_in_tree():
			var entry := [child_path, child.get_class(), child.get_global_rect(), child.get_combined_minimum_size(), child.focus_mode, child.mouse_filter]
			if child.get("text") != null:
				entry.append(child.text)
			entry.append(child.get_theme_font_size("font_size"))
			entry.append(child.get_theme_font("font"))
			if child is BaseButton:
				entry.append(child.disabled)
			var connections := []
			for signal_info in child.get_signal_list():
				# Godot itself connects a parent Control's child_order_changed/item_rect_changed to each added Control
				# child; connections whose target is a pilot plate are excluded, every other connection is compared.
				var count := 0
				for connection in child.get_signal_connection_list(signal_info["name"]):
					var target: Object = connection["callable"].get_object()
					# Likewise the engine's own Viewport::canvas_parent_mark_dirty hook on a CanvasItem that gained a child.
					var engine_hook: bool = target is Viewport and str(connection["callable"]) == "Viewport::canvas_parent_mark_dirty"
					if not engine_hook and not (target is Node and String(target.name).begins_with(PLATE_PREFIX)):
						count += 1
				if count > 0:
					connections.append([signal_info["name"], count])
			entry.append(connections)
			out.append(entry)
		out.append_array(_controls(child, child_path))
	return out


func _capture(context: String, language: String, variant: String) -> Image:
	var image := root.get_texture().get_image()
	if variant == "on":
		var file := "rpg-2-star-ocean-the-second_navigation-ui_wired-capture-%s-%s_pilot-on_%s.png" % [context, language, stamp]
		_check(image.save_png(capture_dir.path_join(file)) == OK, "saved " + file)
	return image


func _diff_box(a: Image, b: Image) -> Array:
	if a.get_size() != b.get_size():
		return [-1, Rect2i()]
	var count := 0
	var box := Rect2i()
	for y in a.get_height():
		for x in a.get_width():
			if a.get_pixel(x, y) != b.get_pixel(x, y):
				count += 1
				box = Rect2i(x, y, 1, 1) if count == 1 else box.merge(Rect2i(x, y, 1, 1))
	return [count, box]


func _context_checks(context: String, language: String) -> void:
	var kind: String = _kind_of(context)
	var label: String = context + "/" + language
	var images := {}
	var controls := {}
	for variant in ["frozen", "off", "on"]:
		_reset_state(language, YONKERS if kind == "annex" else "scifi.city")
		var node := _spawn(kind, variant)
		await process_frame
		_open_context(node, context)
		await _settle()
		images[variant] = _capture(context, language, variant)
		controls[variant] = _controls(node)
		var plates := _plates(node)
		if variant == "on":
			_check(node.navigation_ui_skin != null and node.navigation_ui_skin.applied, label + " helper applied")
			_check(node.navigation_ui_skin != null and node.navigation_ui_skin.screen_kind == kind, label + " screen kind")
			_check(plates.size() == EXPECTED_PLATES[kind], label + " plate count %d" % plates.size())
		else:
			_check(plates.is_empty(), label + " " + variant + " has no plates")
			if variant == "off":
				_check(node.navigation_ui_skin == null, label + " off constructs no helper")
		await _despawn()
	var frozen_diff := _diff_box(images["frozen"], images["off"])
	_check(frozen_diff[0] == 0, label + " OFF vs frozen pre-wiring pixels %s" % str(frozen_diff))
	_check(controls["frozen"] == controls["off"], label + " OFF vs frozen controls")
	_check(controls["on"].size() > 0 and controls["on"] == controls["off"], label + " ON vs OFF visible controls (%d)" % controls["on"].size())
	if controls["on"] != controls["off"]:
		for i in mini(controls["on"].size(), controls["off"].size()):
			if controls["on"][i] != controls["off"][i]:
				print("NAVUI_CONTROL_DIFF ", label, "\n  on  ", controls["on"][i], "\n  off ", controls["off"][i])
				break
	var on_diff := _diff_box(images["on"], images["off"])
	_check(on_diff[0] > 0, label + " pilot visibly changes pixels")
	print("NAVUI_DIFF ", label, " on_vs_off ", on_diff)
	if kind == "map":
		# The map frame (y 44..311) and the travel route card stay pixel-identical.
		var frame_box := Rect2i(0, 44, 640, 268)
		_check(not on_diff[1].intersects(frame_box) or _region_equal(images["on"], images["off"], frame_box, context), label + " map frame untouched")


func _root_button_contract(button: Button) -> Array:
	var calls := []
	for signal_info in button.get_signal_list():
		for connection in button.get_signal_connection_list(signal_info.name):calls.append([String(signal_info.name), connection.callable, connection.flags])
	var styles := []
	for state in ["normal", "hover", "pressed", "hover_pressed", "disabled", "focus"]:styles.append(button.get_theme_stylebox(state))
	var colors := []
	for state in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color", "font_disabled_color"]:colors.append(button.get_theme_color(state))
	return [button.get_instance_id(), button.get_global_rect(), button.get_combined_minimum_size(), button.text, button.get_theme_font("font"), button.get_theme_font_size("font_size"), button.disabled, button.visible, button.focus_mode, button.mouse_filter, styles, colors, calls]


func _root_diff_only(a: Image, b: Image, allowed: Array, protected_save: Rect2i, old_title_hidden: Image = null) -> bool:
	for y in a.get_height():
		for x in a.get_width():
			if a.get_pixel(x, y) == b.get_pixel(x, y):continue
			var point := Vector2i(x, y)
			if protected_save.has_point(point):
				# Save control/theme is unchanged; only the proven old Title glyph mask may disappear.
				if old_title_hidden == null or b.get_pixel(x, y) == old_title_hidden.get_pixel(x, y) or a.get_pixel(x, y) != old_title_hidden.get_pixel(x, y):return false
			var contained := false
			for box: Rect2i in allowed:
				if box.has_point(point):contained = true;break
			if not contained:return false
	return true


func _region_equal(a: Image, b: Image, box: Rect2i, context: String) -> bool:
	# Field log/company/credits panels sit over the frame by design; only their panel rects may differ there.
	var allowed := Rect2i()
	if context in ["field", "company"]:
		allowed = Rect2i(48, 39, 544, 285)
	elif context == "credits":
		allowed = Rect2i(72, 62, 496, 236)
	for y in range(box.position.y, box.end.y):
		for x in range(box.position.x, box.end.x):
			if allowed.has_point(Vector2i(x, y)):
				continue
			if a.get_pixel(x, y) != b.get_pixel(x, y):
				print("NAVUI_FRAME_PIXEL ", context, " ", x, ",", y)
				return false
	return true


func _click(control: Control) -> void:
	var at := control.get_global_rect().get_center()
	var motion := InputEventMouseMotion.new()
	motion.position = at
	motion.global_position = at
	Input.parse_input_event(motion)
	await process_frame
	for pressed in [true, false]:
		var event := InputEventMouseButton.new()
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = pressed
		event.position = at
		event.global_position = at
		Input.parse_input_event(event)
		await process_frame
	await process_frame


func _interaction_checks() -> void:
	for variant in ["off", "on"]:
		var tag: String = "interact/" + variant
		_reset_state("en")
		var explore := _spawn("exploration", variant)
		await _settle()
		var recruited: Dictionary = app.recruited_members.duplicate(true)
		explore._open_dialogue()
		await _settle()
		_check(explore.dialogue_overlay.visible and explore.dialogue_open, tag + " dialogue open")
		_check(explore.get_viewport().gui_get_focus_owner() == explore.invite_button, tag + " invite focused")
		await _click(explore.later_button)
		_check(not explore.dialogue_overlay.visible and not explore.dialogue_open, tag + " dialogue closed by mouse")
		_check(app.recruited_members == recruited, tag + " recruit state unchanged")
		await _despawn()

		_reset_state("en", YONKERS)
		var annex := _spawn("annex", variant)
		await _settle()
		app.survey_clues[annex._clue_key(0)] = true
		var clues: Dictionary = app.survey_clues.duplicate(true)
		annex._inspect_clue(0)
		await _settle()
		_check(annex.overlay.visible and annex.overlay_mode == "clue", tag + " clue panel open")
		_check(annex.get_viewport().gui_get_focus_owner() == annex.close_button, tag + " close focused")
		await _click(annex.close_button)
		_check(not annex.overlay.visible, tag + " clue panel closed by mouse")
		_check(app.survey_clues == clues, tag + " clue state unchanged")
		await _despawn()

		_reset_state("en")
		var map := _spawn("map", variant)
		await _settle()
		var minutes: int = app.calendar_minutes
		var destination: String = app.current_destination_id
		await _click(map.field_button)
		_check(map.field_overlay.visible, tag + " field log opened by mouse")
		await _click(map.field_close)
		_check(not map.field_overlay.visible, tag + " field log closed by mouse")
		await _click(map.commerce_button)
		_check(map.commerce_overlay.visible, tag + " company opened by mouse")
		await _click(map.commerce_close)
		_check(not map.commerce_overlay.visible, tag + " company closed by mouse")
		map.open_map_credits()
		await _settle()
		_check(map.credits_overlay.visible, tag + " credits open")
		await _click(map.credits_close)
		_check(not map.credits_overlay.visible, tag + " credits closed by mouse")
		map.select_place(_other_place(map))
		await _settle()
		_check(map.route_card.visible, tag + " route card visible")
		var options: Array = map.card_options.get_children().filter(func(c): return c is Button and c.visible and not c.disabled)
		# Choose the last listed trip option (NYC -> Yonkers lists one) by mouse; the card stays open on it.
		_check(options.size() >= 1, tag + " route card lists a trip option")
		if options.size() >= 1:
			var expected_option: String = map.selected_option_id
			await _click(options[-1])
			print("NAVUI_ROUTE ", tag, " options ", options.size(), " selected ", map.selected_option_id)
			_check(map.route_card.visible and map.selected_option_id != "", tag + " route option chosen, card still open")
			_check(options.size() > 1 or map.selected_option_id == expected_option, tag + " single option stays selected")
		await _click(map.cancel_button)
		_check(not map.route_card.visible, tag + " route card cancelled by mouse")
		_check(app.calendar_minutes == minutes and app.current_destination_id == destination, tag + " no time travel")
		_check(current == map and map.is_inside_tree(), tag + " still on the map")
		await _despawn()


# Original refusal fixture, kept on the PRE-REPAIR wired source: NYC annex room 1 English refuses (existing Back ends
# at x 648) and must leave the screen pixel- and control-identical; Chinese (98 px Back) applies.
func _nyc_annex_fallback_checks() -> void:
	for language in ["en", "zh"]:
		var images := {}
		var controls := {}
		for variant in ["prerepair-off", "prerepair-on"]:
			_reset_state(language, "scifi.city")
			var node := _spawn("annex", variant)
			await process_frame
			_open_context(node, "annex")
			await _settle()
			images[variant] = root.get_texture().get_image()
			controls[variant] = _controls(node)
			if variant == "prerepair-on":
				var back: Button = node.back_button
				print("NAVUI_NYC_BACK pre-repair ", language, " ", Rect2(back.position, back.size), " min ", back.get_combined_minimum_size())
				if language == "en":
					_check(node.navigation_ui_skin == null and _plates(node).is_empty(), "pre-repair nyc annex en refused safely")
					_check(back.position.x + back.size.x > 640.0, "pre-repair nyc annex en Back really exceeds the view")
				else:
					_check(node.navigation_ui_skin != null and _plates(node).size() == 3, "pre-repair nyc annex zh applied")
			await _despawn()
		if language == "en":
			_check(_diff_box(images["prerepair-on"], images["prerepair-off"])[0] == 0, "pre-repair nyc annex en refused pilot leaves pixels identical")
			_check(controls["prerepair-on"] == controls["prerepair-off"], "pre-repair nyc annex en refused pilot leaves controls identical")
		else:
			_check(controls["prerepair-on"] == controls["prerepair-off"], "pre-repair nyc annex zh ON vs OFF controls")


func _annex_spawn(variant: String, language: String, destination: String, annex_room: int) -> Node:
	_reset_state(language, destination)
	app.current_annex_room = annex_room
	var node := _spawn("annex", variant)
	await _settle()
	return node


func _header_fits(node: Node, tag: String) -> void:
	var back: Button = node.back_button
	var save: Button = node.save_button
	var back_rect := back.get_global_rect()
	var save_rect := save.get_global_rect()
	_check(back.get_combined_minimum_size().x <= back.size.x and back.get_combined_minimum_size().y <= back.size.y, tag + " Back label fits its button %s min %s" % [back_rect, back.get_combined_minimum_size()])
	_check(save.get_combined_minimum_size().x <= save.size.x and save.get_combined_minimum_size().y <= save.size.y, tag + " Save label fits its button")
	_check(HEADER.encloses(back_rect) and HEADER.encloses(save_rect), tag + " Back and Save inside the 640 header band")
	_check(save_rect.end.x <= back_rect.position.x and not save_rect.intersects(back_rect), tag + " Save and Back do not overlap")
	_check(node.title_label.get_global_rect().end.x <= save_rect.position.x, tag + " title ends before Save")


# All six annex rooms (NYC, Yonkers, Washington x room 1/2) in both languages, default OFF and opt-in ON, on the
# repaired source. The repaired OFF is compared with the pre-wiring copy and the pre-repair copy: only the two NYC English
# rooms may differ, and only in the declared Back font size, rect and minimum, inside the old Back footprint.
# Declared: room 1 "Return outside" was 123 px (ends x 648), room 2 "Outer room" was 100 px; both become 98x38 at x 525.
const DECLARED_OLD_BACK_WIDTH := {1: 123.0, 2: 100.0}


func _annex_header_repair_checks() -> void:
	for destination in ANNEX_PLACES:
		for annex_room in [1, 2]:
			for language in ["en", "zh"]:
				var tag := "header %s room%d %s" % [destination, annex_room, language]
				var declared: bool = destination == "scifi.city" and language == "en"
				var images := {}
				var controls := {}
				var rows := {}
				var title_rows := {}
				for variant in ["frozen", "prerepair-off", "off", "on"]:
					var node: Node = await _annex_spawn(variant, language, destination, annex_room)
					images[variant] = root.get_texture().get_image()
					controls[variant] = _controls(node)
					var back: Button = node.back_button
					rows[variant] = [back.get_global_rect(), back.get_theme_font_size("font_size"), back.get_combined_minimum_size(), back.text]
					title_rows[variant] = [node.title_label.get_global_rect(), node.title_label.get_theme_font_size("font_size"), node.title_label.get_combined_minimum_size(), node.title_label.text, node.save_button.get_global_rect()]
					if variant in ["off", "on"]:
						_header_fits(node, tag + " " + variant)
					if variant == "on":
						_check(node.navigation_ui_skin != null and node.navigation_ui_skin.applied and _plates(node).size() == 3, tag + " pilot applies (helper success)")
					if destination == "scifi.city":
						var file := "rpg-2-star-ocean-the-second_navigation-ui_nyc-back-repair-capture-room%d-%s_%s_%s.png" % [annex_room, language, "pilot-on" if variant == "on" else "default-" + variant, stamp]
						if variant in ["off", "on"]:
							_check(images[variant].save_png(capture_dir.path_join(file)) == OK, "saved " + file)
					if declared and annex_room == 1 and variant == "frozen":
						var save_contract := _root_button_contract(node.save_button)
						var back_contract := _root_button_contract(node.back_button)
						node.title_label.visible = false
						await _settle()
						images["frozen-title-hidden"] = root.get_texture().get_image()
						_check(_root_button_contract(node.save_button) == save_contract, tag + " old Title hide keeps SAME Save instance rect/text/font/styles/exact Callables")
						_check(_root_button_contract(node.back_button) == back_contract, tag + " old Title hide keeps SAME Back instance rect/text/font/styles/exact Callables")
						node.title_label.visible = true
						await _settle()
						_check(root.get_texture().get_image().get_data() == images["frozen"].get_data(), tag + " old Title visibility restores full old pixels exactly")
					await _despawn()
				print("NAVUI_BACK ", tag, " frozen ", rows["frozen"], " repaired ", rows["off"])
				_check(controls["on"].size() > 0 and controls["on"] == controls["off"], tag + " ON vs repaired OFF controls")
				_check(_diff_box(images["on"], images["off"])[0] > 0, tag + " pilot visibly changes pixels")
				_check(controls["prerepair-off"] == controls["frozen"] and _diff_box(images["prerepair-off"], images["frozen"])[0] == 0, tag + " pre-repair OFF equals pre-wiring")
				var diff := _diff_box(images["off"], images["frozen"])
				if not declared:
					_check(diff[0] == 0, tag + " repaired OFF vs pre-wiring pixels %s" % str(diff))
					_check(controls["off"] == controls["frozen"], tag + " repaired OFF vs pre-wiring controls")
					continue
				# Root-declared exception: Back in both NYC English rooms; title ONLY room1.
				# Pointwise union of the original control footprints, never a broad header rectangle.
				var allowed := [Rect2i(525, 12, 115, 38)]
				if annex_room == 1:allowed.append(Rect2i(title_rows["frozen"][0]))
				_check(diff[0] > 0 and _root_diff_only(images["off"], images["frozen"], allowed, Rect2i(title_rows["frozen"][4]), images.get("frozen-title-hidden")), tag + " repaired diff only original Back plus declared room1 Title and causal old-glyph Save mask " + str(diff))
				if annex_room == 1:
					var save_rect := Rect2i(title_rows["frozen"][4])
					var old_crop: Image = images["frozen"].get_region(save_rect)
					var hidden_crop: Image = images["frozen-title-hidden"].get_region(save_rect)
					var repaired_crop: Image = images["off"].get_region(save_rect)
					_check(old_crop.get_data() != hidden_crop.get_data(), tag + " original Title glyphs really overlap Save pixels")
					_check(repaired_crop.get_data() == hidden_crop.get_data(), tag + " repaired Save crop EXACT to old Title-hidden counterfactual")
					print("NAVUI_ROOT_SAVE_CAUSAL ", tag, " oldGlyphMaskPixels=", _diff_box(old_crop, hidden_crop)[0], " repairedEqualsHidden=", repaired_crop.get_data() == hidden_crop.get_data())
					for role in ["old-title-visible", "old-title-hidden", "repaired-title14"]:
						var crop: Image = old_crop if role == "old-title-visible" else (hidden_crop if role == "old-title-hidden" else repaired_crop)
						crop.save_png(capture_dir.path_join("rpg-2-star-ocean-the-second_navigation-ui_save-causal-root-v04-%s_unscored_%s.png" % [role, stamp]))
				var changed := []
				_check(controls["off"].size() == controls["frozen"].size(), tag + " same control count")
				for i in mini(controls["off"].size(), controls["frozen"].size()):
					if controls["off"][i] != controls["frozen"][i]:changed.append(i)
				_check(changed.size() == (2 if annex_room == 1 else 1), tag + " exact declared changed-control set " + str(changed))
				var changed_back := 0
				var changed_title := 0
				for index in changed:
					var before: Array = controls["frozen"][index]
					var after: Array = controls["off"][index]
					if after[1] == "Button":
						changed_back += 1
						_check(after[6] == rows["frozen"][3] and after[6] == rows["off"][3], tag + " changed Button is Back, text unchanged")
						_check(after[0] == before[0] and after.slice(4, 6) == before.slice(4, 6) and after.slice(8) == before.slice(8), tag + " Back keeps path, focus, filter, font and connections")
					elif after[1] == "Label" and annex_room == 1:
						changed_title += 1
						_check(after[6] == title_rows["frozen"][3] and after[6] == title_rows["off"][3], tag + " changed Label is Title, exact text unchanged")
						_check(after[0] == before[0] and after.slice(4, 6) == before.slice(4, 6) and after.slice(8) == before.slice(8), tag + " Title keeps path, focus, filter, font and connections")
					else:_check(false, tag + " undeclared control changed")
				_check(changed_back == 1 and changed_title == (1 if annex_room == 1 else 0), tag + " only named Back/Title controls changed")
				if annex_room == 1:
					_check(title_rows["frozen"][0].end.x > title_rows["frozen"][4].position.x and title_rows["frozen"][1] == 18, tag + " original Title overlap reproduced")
					_check(title_rows["off"][0].end.x <= title_rows["off"][4].position.x and title_rows["off"][1] == 14, tag + " repaired Title14 ends before Save")
					print("NAVUI_ROOT_TITLE ", tag, " old ", title_rows["frozen"], " repaired ", title_rows["off"])

				_check(rows["frozen"][0] == Rect2(525, 12, DECLARED_OLD_BACK_WIDTH[annex_room], 38), tag + " pre-wiring Back really was %d px (bug reproduced)" % DECLARED_OLD_BACK_WIDTH[annex_room])
				_check(rows["off"][0] == REPAIRED_BACK and rows["off"][1] < rows["frozen"][1] and rows["off"][1] >= 11, tag + " repaired Back 98x38 at x 525 with a stepped font %d <- %d" % [rows["off"][1], rows["frozen"][1]])


# Language refresh on a live, skinned NYC annex: EN -> ZH -> EN keeps the helper applied, the plates, and the Back/Save
# header identical to a fresh scene in that language.
func _nyc_language_refresh_checks() -> void:
	for annex_room in [1, 2]:
		var fresh := {}
		for language in ["en", "zh"]:
			var node: Node = await _annex_spawn("on", language, "scifi.city", annex_room)
			fresh[language] = [_controls(node), root.get_texture().get_image().get_region(Rect2i(HEADER))]
			await _despawn()
		var live: Node = await _annex_spawn("on", "en", "scifi.city", annex_room)
		for language in ["zh", "en"]:
			app.toggle_language()
			await _settle()
			var tag := "language refresh room%d -> %s" % [annex_room, language]
			_check(app.language == language, tag + " language set")
			_check(live.navigation_ui_skin != null and live.navigation_ui_skin.applied and _plates(live).size() == 3, tag + " helper still applied")
			_check(_controls(live) == fresh[language][0], tag + " controls equal a fresh scene")
			_check(_diff_box(root.get_texture().get_image().get_region(Rect2i(HEADER)), fresh[language][1])[0] == 0, tag + " header pixels equal a fresh scene")
			_header_fits(live, tag)
		await _despawn()


# Real mouse clicks on the NYC header. Back must do the same intended action on the pre-repair source (its button
# still had a clickable centre on screen), on the repaired default and with the pilot on; Save likewise.
func _nyc_header_mouse_checks() -> void:
	load(SCRIPTS["exploration"]).navigation_ui_skin_override = 0
	for annex_room in [1, 2]:
		var outcomes := {}
		for variant in ["prerepair-off", "off", "on"]:
			for button_name in ["back", "save"]:
				var node: Node = await _annex_spawn(variant, "en", "scifi.city", annex_room)
				# The opened scene would apply the annex override again; keep it off for the follow-up scene.
				load(SCRIPTS["annex"]).navigation_ui_skin_override = 0
				app.annex_surface_return_position = Vector2(558, 143)
				app.resume_area_position = Vector2.ZERO
				app.save_screen_mode = "load"
				app.save_return_scene = ""
				var button: Button = node.back_button if button_name == "back" else node.save_button
				await _click(button)
				for i in 3:
					await process_frame
				var scene: Node = current_scene
				var result := [scene.scene_file_path if scene != null else "", app.current_annex_room, app.resume_annex_pending, app.resume_area_pending, app.resume_area_position, app.save_screen_mode, app.save_return_scene]
				outcomes[variant + "/" + button_name] = result
				print("NAVUI_CLICK room%d %s %s %s" % [annex_room, variant, button_name, str(result)])
				if scene != null:
					root.remove_child(scene)
					scene.free()
				await _despawn()
		var back_expected: String = "res://scenes/survey_annex.tscn" if annex_room == 2 else "res://scenes/scifi_exploration_area.tscn"
		_check(outcomes["off/back"][0] == back_expected, "room%d repaired Back click opens %s" % [annex_room, back_expected])
		_check(outcomes["off/back"] == outcomes["prerepair-off/back"] and outcomes["on/back"] == outcomes["prerepair-off/back"], "room%d Back click same action pre-repair/repaired/pilot" % annex_room)
		_check(outcomes["off/save"][0] == "res://scenes/save_screen.tscn" and outcomes["off/save"][5] == "save" and outcomes["off/save"][6] == "res://scenes/survey_annex.tscn", "room%d Save click opens the save screen" % annex_room)
		_check(outcomes["off/save"] == outcomes["prerepair-off/save"] and outcomes["on/save"] == outcomes["prerepair-off/save"], "room%d Save click same action pre-repair/repaired/pilot" % annex_room)


func _real_scene_checks() -> void:
	# Real .tscn instances (exploration uses its opt-in selector subclass): ON applies, OFF does nothing.
	for kind in SCENES:
		for variant in ["off", "on"]:
			_reset_state("en", YONKERS if kind == "annex" else "scifi.city")
			load(SCRIPTS[kind]).navigation_ui_skin_override = 1 if variant == "on" else 0
			var node: Node = load(SCENES[kind]).instantiate()
			root.add_child(node)
			current = node
			await _settle()
			var expected: int = EXPECTED_PLATES[kind] if variant == "on" else 0
			_check(_plates(node).size() == expected, kind + " tscn " + variant + " plates")
			await _despawn()


func _helper_unit_checks() -> void:
	var Helper: GDScript = load(HELPER)
	# Constructor loads nothing.
	var fresh = Helper.new(SKIN_DIR)
	_check(fresh._textures.is_empty() and not fresh.applied, "constructor loads nothing")
	# Missing package: apply refuses, scene unchanged.
	for kind in SCRIPTS:
		_reset_state("en", YONKERS if kind == "annex" else "scifi.city")
		var node := _spawn(kind, "off")
		await _settle()
		var before := _controls(node)
		var bad = Helper.new("res://assets/ui/navui-missing-package")
		_check(not bad.apply(node) and bad.last_error != "", kind + " missing package refused: " + bad.last_error)
		_check(_plates(node).is_empty() and _controls(node) == before, kind + " missing package changes nothing")
		# Valid package: apply, idempotent, foreign second helper refused, revert restores exactly.
		var skin = Helper.new(SKIN_DIR)
		_check(skin.apply(node), kind + " apply " + skin.last_error)
		if not skin.applied:
			for button in _all_buttons(node):
				if button.is_visible_in_tree() or kind == "annex":
					print("NAVUI_BUTTON ", kind, " ", button.name, " ", button.text, " rect ", Rect2(button.position, button.size), " min ", button.get_combined_minimum_size(), " parent ", button.get_parent().name)
		var count := _plates(node).size()
		_check(count == EXPECTED_PLATES[kind], kind + " plates %d" % count)
		_check(skin.apply(node) and _plates(node).size() == count, kind + " apply idempotent")
		var other = Helper.new(SKIN_DIR)
		_check(not other.apply(node), kind + " second helper refused: " + other.last_error)
		var stranger := Node2D.new()
		_check(not skin.apply(stranger), kind + " applied helper refuses another screen")
		stranger.free()
		skin.revert()
		await _settle()
		_check(_plates(node).is_empty() and _controls(node) == before, kind + " revert restores controls")
		var overrides := 0
		for control in _all_buttons(node):
			for state in ["normal", "hover", "pressed", "focus", "disabled"]:
				if control.has_theme_stylebox_override(state) and control.get_theme_stylebox(state) is StyleBoxTexture:
					overrides += 1
		_check(overrides == 0, kind + " revert leaves no skin styleboxes")
		await _despawn()
	# Missing refs: a non-scene node and a scene with a nulled required ref are refused safely.
	var plain := Node2D.new()
	root.add_child(plain)
	var refused = Helper.new(SKIN_DIR)
	_check(not refused.apply(plain) and refused.last_error != "", "plain node refused")
	plain.free()
	_reset_state("en", YONKERS)
	var annex := _spawn("annex", "off")
	await _settle()
	var keep: Button = annex.notes_button
	annex.notes_button = null
	var partial = Helper.new(SKIN_DIR)
	_check(not partial.apply(annex) and _plates(annex).is_empty(), "annex with missing notes_button refused: " + partial.last_error)
	annex.notes_button = keep
	await _despawn()
	# Exit-tree revert: removing an ON scene reverts the skin without errors.
	_reset_state("en")
	var map := _spawn("map", "on")
	await _settle()
	var helper = map.navigation_ui_skin
	_check(helper != null and helper.applied, "map ON applied before exit")
	root.remove_child(map)
	_check(helper != null and not helper.applied and _plates(map).is_empty(), "exit_tree reverted the skin")
	map.free()
	current = null
	await process_frame


func _all_buttons(node: Node) -> Array:
	var out := []
	for child in node.get_children():
		if child is Button:
			out.append(child)
		out.append_array(_all_buttons(child))
	return out
