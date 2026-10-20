extends SceneTree

## Bounded actual-runtime check for the default-off five-variant character UI
## kit.  It compares flag-off pixels to the frozen e600241 scripts, verifies the
## party icons and dialogue sideportraits in the normal exploration scene, checks
## malformed-package rejection, and saves representative 640/1280 captures.
## Nothing here is art approval or a claim of full character/display approval.

const Helper := preload("res://scripts/rpg-2-star-ocean-the-second_character-ui-portraits_helper_v01_20261019-233832-b7c4e912.gd")
var TAG := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-") + "-" + Crypto.new().generate_random_bytes(4).hex_encode()
const HELPER_PATH := "res://scripts/rpg-2-star-ocean-the-second_character-ui-portraits_helper_v01_20261019-233832-b7c4e912.gd"
const KIT_PATH := "res://assets/portraits/ui-kit-v02/rpg-2-star-ocean-the-second_character-ui-kit_manifest_v02_20261020-001030-9be4a34f.json"
const CAPTURE_PREFIX := "rpg-2-star-ocean-the-second_character-ui"
const BASE := "e600241b9f732e8f8db2a5e645d4947b88ac1142"

var app: Node
var output_dir: String
var checks: Array = []
var captures: Array = []
var phase_times: Dictionary = {}
var phase_started := 0
var kit: Dictionary = {}


func _initialize() -> void:
	call_deferred("run")


func ck(key: String, okay: bool, detail: String = "") -> void:
	checks.append({"key": key, "pass": okay, "detail": detail})


func settle() -> void:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw


func begin_phase(name: String) -> void:
	phase_started = Time.get_ticks_msec()
	phase_times[name] = {"started": phase_started}


func end_phase(name: String) -> void:
	var entry: Dictionary = phase_times[name]
	entry["ms"] = Time.get_ticks_msec() - int(entry["started"])
	phase_times[name] = entry


func sha256_text(value: String) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(value.to_utf8_buffer())
	return context.finish().hex_encode().to_lower()


func capture(label: String, viewport: Vector2i) -> Image:
	root.size = viewport
	root.content_scale_size = Vector2i(640, 360)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	await settle()
	var image := root.get_texture().get_image()
	image.convert(Image.FORMAT_RGBA8)
	var safe := label.to_lower().replace(" ", "-").replace("/", "-")
	var path := output_dir.path_join("%s_%s_capture_%dx%d_v01_%s.png" % [CAPTURE_PREFIX, safe, viewport.x, viewport.y, TAG])
	var saved := image.save_png(path)
	ck("capture-saved:" + label, saved == OK, path)
	var bytes := FileAccess.get_file_as_bytes(path)
	captures.append({"label": label, "path": path.get_file(), "width": image.get_width(), "height": image.get_height(), "sha256": _sha256_bytes(bytes)})
	return image


func _sha256_bytes(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(bytes)
	return context.finish().hex_encode().to_lower()


func detach_audio(node: Node) -> void:
	for child in node.get_children():
		if child is AudioStreamPlayer or child is AudioStreamPlayer2D or child is AudioStreamPlayer3D:
			child.stop()
			child.stream = null
		detach_audio(child)


func free_scene(scene: Node) -> void:
	if scene == null:
		return
	detach_audio(scene)
	var helper: Variant = scene.get("character_ui_portraits")
	if helper != null and helper.has_method("revert"):
		helper.revert()
	if current_scene == scene:
		current_scene = null
	if scene.get_parent() != null:
		scene.get_parent().remove_child(scene)
	scene.free()
	await process_frame


func setup_growth(lang: String, appearance: String, new_override: int, mvp_override: int, female_override: int, skin_override: int) -> Control:
	app.begin_new_run()
	app.language = lang
	app.hero_appearance = appearance
	app.recruit_member("liang-xu")
	app.recruit_member("zhao-ling")
	app.ji_records_checked = true
	app.recruit_member("ji-cheng")
	var script: Script = load("res://scripts/growth_screen.gd")
	script.character_ui_portraits_override = new_override
	script.mvp_display_portraits_override = mvp_override
	script.female_display_portrait_override = female_override
	script.management_ui_skin_override = skin_override
	var scene: Control = load("res://scenes/growth_screen.tscn").instantiate()
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.add_child(scene)
	current_scene = scene
	await settle()
	return scene


func setup_growth_baseline(lang: String, appearance: String) -> Control:
	app.begin_new_run()
	app.language = lang
	app.hero_appearance = appearance
	app.recruit_member("liang-xu")
	app.recruit_member("zhao-ling")
	app.ji_records_checked = true
	app.recruit_member("ji-cheng")
	var baseline_script: Script = load("res://tests/fixtures/rpg-2-star-ocean-the-second_character-ui_growth-screen-baseline_e600241_v01_20261019-233832-b7c4e912.gd")
	var scene: Control = baseline_script.new()
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.add_child(scene)
	current_scene = scene
	await settle()
	return scene


func setup_area(dest: String, lang: String, new_override: int) -> Node:
	app.begin_new_run()
	app.language = lang
	app.hero_appearance = "male"
	app.current_destination_id = dest
	var script: Script = load("res://scripts/scifi_exploration_area.gd")
	script.character_ui_portraits_override = new_override
	var area: Node = load("res://scenes/scifi_exploration_area.tscn").instantiate()
	root.add_child(area)
	current_scene = area
	await settle()
	return area


func setup_area_baseline(dest: String, lang: String) -> Node:
	app.begin_new_run()
	app.language = lang
	app.hero_appearance = "male"
	app.current_destination_id = dest
	var baseline_script: Script = load("res://tests/fixtures/rpg-2-star-ocean-the-second_character-ui_exploration-baseline_e600241_v01_20261019-233832-b7c4e912.gd")
	var area: Node = baseline_script.new()
	root.add_child(area)
	current_scene = area
	await settle()
	return area


func interact(area: Node, at: Vector2) -> void:
	area.hero.position = at
	var event := InputEventAction.new()
	event.action = "interact"
	event.pressed = true
	area._unhandled_input(event)
	await settle()


func click(control: Control) -> void:
	var point := control.get_global_rect().get_center()
	var motion := InputEventMouseMotion.new()
	motion.position = point
	root.push_input(motion, true)
	for pressed in [true, false]:
		var event := InputEventMouseButton.new()
		event.position = point
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = pressed
		root.push_input(event, true)


func label_snapshot(scene: Node) -> Array:
	var rows: Array = []
	for node in scene.find_children("*", "Label", true, false):
		rows.append([node.text, node.position, node.size, node.get_theme_font_size("font_size")])
	return rows


func label_diff(left: Array, right: Array) -> String:
	for index in mini(left.size(), right.size()):
		if left[index] != right[index]:
			return "index %d: %s != %s" % [index, str(left[index]), str(right[index])]
	return "size %d != %d" % [left.size(), right.size()]


func button_methods(button: Button) -> Array:
	var methods: Array = []
	for connection in button.pressed.get_connections():
		methods.append(String(connection.callable.get_method()))
	return methods


func kit_subjects() -> Dictionary:
	return kit.get("variants", {})


func icon_path_for(subject: String) -> String:
	return String(kit_subjects()[subject]["party_icon"]["png"])


func check_party_icons(scene: Control, lang: String, appearance: String) -> void:
	var helper: Control = scene.character_ui_portraits
	var expected := ["protagonist-" + appearance, "liang-xu", "zhao-ling", "ji-cheng"]
	ck("party-helper-present-" + lang + "-" + appearance, helper != null)
	if helper == null:
		return
	ck("party-status-" + lang + "-" + appearance, helper.get_status() == "party-shown:4", helper.get_status())
	ck("party-subjects-" + lang + "-" + appearance, helper.get_party_subjects() == expected, str(helper.get_party_subjects()))
	for index in 4:
		var button: Button = scene.member_buttons[index]
		var subject: String = expected[index]
		ck("party-icon-present-%d-%s-%s" % [index, lang, appearance], button.icon != null)
		ck("party-name-%d-%s-%s" % [index, lang, appearance], button.text == app.member_name(app.active_party_ids[index]), button.text)
		ck("party-clickable-%d-%s-%s" % [index, lang, appearance], button.disabled == (app.active_party_ids[index] == scene.selected_id) and button.mouse_filter != Control.MOUSE_FILTER_IGNORE)
		ck("party-methods-%d-%s-%s" % [index, lang, appearance], button_methods(button).has("_select"), str(button_methods(button)))
		if button.icon != null:
			var icon_image: Image = button.icon.get_image()
			ck("party-icon-size-%d-%s-%s" % [index, lang, appearance], icon_image.get_size() == Vector2i(32, 32), str(icon_image.get_size()))
			var face_bytes := FileAccess.get_file_as_bytes(icon_path_for(subject))
			var face := Image.new()
			ck("party-face-decode-%d-%s-%s" % [index, lang, appearance], face.load_png_from_buffer(face_bytes) == OK)
			var exact := true
			for y in 28:
				for x in 28:
					if icon_image.get_pixel(x + 2, y + 2) != face.get_pixel(x, y):
						exact = false
			ck("party-face-exact-%d-%s-%s" % [index, lang, appearance], exact)
			ck("party-frame-corner-%d-%s-%s" % [index, lang, appearance], icon_image.get_pixel(0, 0) == Color("#b08d57") and icon_image.get_pixel(2, 1) == Color("#69bbce"))
	ck("party-fifth-hidden-" + lang + "-" + appearance, not scene.member_buttons[4].visible and scene.member_buttons[4].icon == null)
	ck("party-no-legacy-" + lang + "-" + appearance, scene.mvp_display_portraits == null and scene.female_display_portrait == null)
	ck("party-single-helper-" + lang + "-" + appearance, scene.find_children("CharacterUiPortraitsPilot", "Control", true, false).size() == 1)


func test_growth() -> void:
	begin_phase("growth")
	var base := await setup_growth_baseline("en", "male")
	var base_image := await capture("growth-off-baseline-en-640", Vector2i(640, 360))
	var base_labels := label_snapshot(base)
	await free_scene(base)
	var current := await setup_growth("en", "male", 0, 0, 0, 0)
	var current_image := await capture("growth-off-current-en-640", Vector2i(640, 360))
	ck("growth-off-exact-0px", base_image.get_data() == current_image.get_data())
	ck("growth-off-no-helper", current.character_ui_portraits == null)
	var current_labels := label_snapshot(current)
	ck("growth-off-labels", base_labels == current_labels, label_diff(base_labels, current_labels))
	await free_scene(current)

	for lang in ["en", "zh"]:
		var scene := await setup_growth(lang, "male", 1, 1, 1, 0)
		check_party_icons(scene, lang, "male")
		var labels_before: Array = label_snapshot(scene)
		click(scene.member_buttons[1])
		await settle()
		ck("party-click-select-1-" + lang, scene.selected_id == app.active_party_ids[1], scene.selected_id)
		click(scene.member_buttons[0])
		await settle()
		ck("party-click-select-0-" + lang, scene.selected_id == app.active_party_ids[0], scene.selected_id)
		ck("party-labels-preserved-" + lang, labels_before == label_snapshot(scene))
		app.hero_appearance = "female"
		scene._refresh()
		await settle()
		check_party_icons(scene, lang, "female")
		await capture("growth-female-pilot-"+lang+"-640",Vector2i(640,360))
		app.hero_appearance = "male"
		scene._refresh()
		await settle()
		if lang == "en":
			await capture("growth-pilot-en-640", Vector2i(640, 360))
		else:
			await capture("growth-pilot-zh-640", Vector2i(640, 360))
		await free_scene(scene)

	var restore := await setup_growth("en", "male", 0, 0, 0, 0)
	var button: Button = restore.member_buttons[0]
	button.expand_icon = true
	button.icon_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	var icon_before: Texture2D = ImageTexture.create_from_image(Image.create(2,2,false,Image.FORMAT_RGBA8))
	button.icon = icon_before
	var icon_helper: Control = Helper.new()
	ck("icon-restore-install", icon_helper.install_party(restore,restore.member_buttons))
	ck("icon-restore-apply", icon_helper.apply_party(app.active_party_ids,"male",true))
	icon_helper.revert()
	ck("icon-properties-restored",button.expand_icon and button.icon_alignment == HORIZONTAL_ALIGNMENT_RIGHT and button.icon == icon_before)
	await free_scene(restore)
	var legacy := await setup_growth("en", "male", 0, 1, 0, 0)
	ck("legacy-only-mvp-created", legacy.character_ui_portraits == null and legacy.mvp_display_portraits != null)
	await free_scene(legacy)

	var wide := await setup_growth("en", "male", 1, 0, 0, 0)
	await capture("growth-pilot-en-1280", Vector2i(1280, 720))
	await free_scene(wide)
	end_phase("growth")


func test_five_buttons_and_unknown() -> void:
	begin_phase("five-slots")
	var host := Control.new()
	host.size = Vector2(640, 360)
	root.add_child(host)
	var buttons: Array = []
	for index in 5:
		var button := Button.new()
		button.position = Vector2(18 + index * 124, 47)
		button.size = Vector2(117, 29)
		host.add_child(button)
		buttons.append(button)
	var helper: Control = Helper.new()
	ck("five-slots-install", helper.install_party(host, buttons))
	ck("five-slots-off-no-io", not helper.apply_party(["hero"], "male", false) and helper.get_io_read_count() == 0)
	var okay: bool = helper.apply_party(["hero", "liang-xu", "zhao-ling", "ji-cheng", "unknown"], "male", true)
	ck("five-slots-known-four-icons", not okay and helper.get_party_subjects().size() == 4)
	ck("five-slots-unknown-no-icon", buttons[4].icon == null and buttons[4].text == "")
	ck("five-slots-refusal-reports-unknown", helper.get_refusal_reason().contains("unknown"))
	helper.revert()
	host.remove_child(helper)
	helper.free()
	host.free()
	await process_frame
	end_phase("five-slots")


func write_text(path: String, text: String) -> bool:
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		return false
	file.store_string(text)
	file.close()
	return true


func test_malformed_packages() -> void:
	begin_phase("malformed")
	var kit_text := FileAccess.get_file_as_string(KIT_PATH)
	var base_kit: Dictionary = JSON.parse_string(kit_text)
	var cases := [
		{"name": "missing", "manifest": "res://tests/fixtures/rpg-2-star-ocean-the-second_character-ui-missing-%s.json" % TAG},
		{"name": "json", "text": "{"},
		{"name": "types", "text": JSON.stringify({"schema": 3})},
	]
	var bad_hash: Dictionary = base_kit.duplicate(true)
	bad_hash["variants"]["protagonist-female"]["party_icon"]["png_sha256"] = "0".repeat(64)
	cases.append({"name": "hash", "text": JSON.stringify(bad_hash)})
	var upscale: Dictionary = base_kit.duplicate(true)
	upscale["variants"]["protagonist-female"]["dialogue"]["display_rect"]["width"] = int(upscale["variants"]["protagonist-female"]["dialogue"]["width"]) + 1
	cases.append({"name": "upscale", "text": JSON.stringify(upscale)})
	for field in ["roi", "display_rect", "icon-png", "icon-sha", "dialogue-transform", "dialogue-png", "dialogue-sha", "fractional-dimension"]:
		var malformed: Dictionary = base_kit.duplicate(true)
		var item: Dictionary = malformed.variants["protagonist-female"]
		match field:
			"roi": item.party_icon.roi = []
			"display_rect": item.dialogue.display_rect = 123
			"icon-png": item.party_icon.png = {}
			"icon-sha": item.party_icon.png_sha256 = []
			"dialogue-transform": item.dialogue.transform = {}
			"dialogue-png": item.dialogue.png = []
			"dialogue-sha": item.dialogue.png_sha256 = {}
			"fractional-dimension": item.dialogue.width = 12.5
		cases.append({"name": field, "text": JSON.stringify(malformed)})
	var helper_source := FileAccess.get_file_as_string(HELPER_PATH).replace("class_name CharacterUiPortraitsPilot\n", "")
	var fixture_paths: Array[String] = []
	for item in cases:
		var case_name := String(item["name"])
		var manifest_path := String(item.get("manifest", "res://tests/fixtures/rpg-2-star-ocean-the-second_character-ui-%s-%s.json" % [case_name, TAG]))
		if item.has("text"):
			ck("malformed-write-" + case_name, write_text(manifest_path, String(item["text"])))
		var script_path := "res://tests/fixtures/rpg-2-star-ocean-the-second_character-ui-%s-helper-%s.gd" % [case_name, TAG]
		ck("malformed-script-" + case_name, write_text(script_path, helper_source.replace(KIT_PATH, manifest_path)))
		fixture_paths.append(script_path)
		if item.has("text"):
			fixture_paths.append(manifest_path)
		var scene := await setup_growth("en", "male", 0, 0, 0, 0)
		var fixture: Script = load(script_path)
		ck("malformed-load-" + case_name, fixture != null)
		if fixture == null:
			await free_scene(scene)
			continue
		var helper: Control = fixture.new()
		ck("malformed-install-" + case_name, helper.install_party(scene, scene.member_buttons))
		var applied: bool = helper.apply_party(app.active_party_ids, "male", true)
		ck("malformed-reject-" + case_name, not applied and helper.get_status() == "refused", helper.get_refusal_reason())
		ck("malformed-no-icons-" + case_name, scene.member_buttons[0].icon == null and scene.member_buttons[1].icon == null)
		ck("malformed-names-intact-" + case_name, scene.member_buttons[0].text == app.member_name("hero") and scene.member_buttons[1].text == app.member_name("liang-xu"))
		ck("malformed-read-attempted-" + case_name, helper.get_io_read_count() >= 1)
		helper.revert()
		await free_scene(scene)
	for path in fixture_paths:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	end_phase("malformed")


func check_dialogue(scene: Node, mode: String, expected_subject: String, helper: Control) -> void:
	var visible: bool = helper.is_showing_dialogue()
	ck("dialogue-visible-" + mode + "-" + expected_subject, visible == (expected_subject != ""), helper.get_status())
	ck("dialogue-subject-" + mode, helper.get_dialogue_subject() == expected_subject, helper.get_dialogue_subject())
	ck("dialogue-text-fit-" + mode + "-" + expected_subject, helper.get_text_fit())
	if expected_subject == "":
		return
	var portrait: TextureRect = scene.dialogue_panel.find_child("CharacterUiPortrait", true, false)
	var frame: Control = scene.dialogue_panel.find_child("CharacterUiPortraitFrame", true, false)
	ck("dialogue-portrait-present-" + mode, portrait != null and frame != null)
	if portrait == null:
		return
	ck("dialogue-portrait-has-texture-" + mode, portrait.texture != null)
	ck("dialogue-portrait-keep-aspect-" + mode, portrait.stretch_mode == TextureRect.STRETCH_KEEP_ASPECT_CENTERED and portrait.texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST)
	for control in [scene.dialogue_title, scene.dialogue_text, scene.invite_button, scene.later_button]:
		ck("dialogue-no-overlap-" + mode + "-" + control.name, not portrait.get_global_rect().intersects(control.get_global_rect()) and not frame.get_global_rect().intersects(control.get_global_rect()))
	for control in [portrait,frame,scene.dialogue_title,scene.dialogue_text,scene.invite_button,scene.later_button]:
		ck("dialogue-native-bounds-"+mode+"-"+control.name,Rect2(Vector2.ZERO,Vector2(640,360)).encloses(control.get_global_rect()))
	ck("dialogue-invite-callback-" + mode, button_methods(scene.invite_button).has("_dialogue_primary"))
	ck("dialogue-later-callback-" + mode, button_methods(scene.later_button).has("_close_dialogue"))


func test_dialogue() -> void:
	begin_phase("dialogue")
	var base := await setup_area_baseline("scifi.city", "en")
	await interact(base, base.npc_position)
	var base_image := await capture("dialogue-off-baseline-en-640", Vector2i(640, 360))
	await free_scene(base)
	var current := await setup_area("scifi.city", "en", 0)
	await interact(current, current.npc_position)
	var current_image := await capture("dialogue-off-current-en-640", Vector2i(640, 360))
	ck("dialogue-off-exact-0px", base_image.get_data() == current_image.get_data())
	ck("dialogue-off-no-helper", current.character_ui_portraits == null)
	await free_scene(current)

	for dest in ["scifi.city", "scifi.outskirts", "scifi.ruins"]:
		for lang in ["en", "zh"]:
			var scene := await setup_area(dest, lang, 1)
			var helper: Control = scene.character_ui_portraits
			ck("dialogue-helper-" + dest + "-" + lang, helper != null)
			if helper == null:
				await free_scene(scene)
				continue
			await interact(scene, scene.npc_position)
			ck("recruit-open-" + dest + "-" + lang, scene.dialogue_open and scene.dialogue_mode == "recruit")
			var recruit_text: String = scene.dialogue_text.text
			check_dialogue(scene, "recruit", scene.recruit_id, helper)
			ck("recruit-text-known-" + dest + "-" + lang, not recruit_text.is_empty())
			helper.apply_dialogue("recruit", scene.recruit_id, true)
			ck("recruit-text-not-mutated-" + dest + "-" + lang, scene.dialogue_text.text == recruit_text)
			if dest == "scifi.city" and lang == "en":
				await capture("dialogue-recruit-en-640", Vector2i(640, 360))
			elif dest == "scifi.city" and lang == "zh":
				await capture("dialogue-recruit-zh-640", Vector2i(640, 360))
			scene._close_dialogue()
			await settle()
			await interact(scene, scene.FIELD_ASSISTS[dest]["position"])
			ck("assist-open-" + dest + "-" + lang, scene.dialogue_open and scene.dialogue_mode == "assist")
			var assist_text: String = scene.dialogue_text.text
			check_dialogue(scene, "assist", String(scene.FIELD_ASSISTS[dest]["member"]), helper)
			ck("assist-text-known-" + dest + "-" + lang, not assist_text.is_empty())
			if dest == "scifi.outskirts" and lang == "en":
				await capture("dialogue-assist-en-640", Vector2i(640, 360))
			scene._close_dialogue()
			await settle()
			await interact(scene, scene.FIELD_TRACES[dest][0])
			ck("trace-open-" + dest + "-" + lang, scene.dialogue_open and scene.dialogue_mode == "trace")
			check_dialogue(scene, "trace", "", helper)
			ck("trace-text-fit-" + dest + "-" + lang, helper.get_text_fit())
			ck("trace-invite-hidden-" + dest + "-" + lang, not scene.invite_button.visible)
			if dest == "scifi.ruins" and lang == "en":
				await capture("dialogue-trace-en-640", Vector2i(640, 360))
			helper.apply_dialogue("recruit", "unknown-speaker", true)
			ck("unknown-speaker-hidden-" + dest + "-" + lang, not helper.is_showing_dialogue())
			helper.apply_dialogue("system", "", true)
			ck("system-text-hidden-" + dest + "-" + lang, not helper.is_showing_dialogue())
			scene._close_dialogue()
			await free_scene(scene)

	var overflow := await setup_area("scifi.city", "en", 1)
	await interact(overflow, overflow.npc_position)
	var h: Control = overflow.character_ui_portraits
	var original_position: Vector2 = h._dialogue_original["text"].position
	var long_text := "Full original dialogue remains unchanged. ".repeat(300)
	overflow.dialogue_text.text = long_text
	var callbacks := button_methods(overflow.invite_button)
	ck("overflow-refused",not h.apply_dialogue("recruit","liang-xu",true) and h.get_refusal_reason() == "dialogue-text-overflow")
	ck("overflow-keeps-full-text",overflow.dialogue_text.text == long_text)
	ck("overflow-restores-layout",overflow.dialogue_text.position == original_position and not h.is_showing_dialogue())
	ck("overflow-keeps-callbacks",button_methods(overflow.invite_button) == callbacks)
	await settle()
	var restored_rect := Rect2(overflow.dialogue_text.position,overflow.dialogue_text.size)
	var equivalent := await setup_area_baseline("scifi.city","en")
	await interact(equivalent,equivalent.npc_position)
	equivalent.dialogue_text.text=long_text
	await settle()
	ck("overflow-equivalent-original-ui",restored_rect==Rect2(equivalent.dialogue_text.position,equivalent.dialogue_text.size),str(restored_rect)+" / "+str(Rect2(equivalent.dialogue_text.position,equivalent.dialogue_text.size)))
	await free_scene(equivalent)
	await free_scene(overflow)

	# Actual recruit callback, assist callback and 1280 dialogue capture.
	var recruit_scene := await setup_area("scifi.city", "en", 1)
	await interact(recruit_scene, recruit_scene.npc_position)
	recruit_scene.invite_button.pressed.emit()
	await settle()
	ck("recruit-callback-joins", app.recruited_members.has("liang-xu") and not recruit_scene.dialogue_open)
	ck("recruit-callback-hides", not recruit_scene.character_ui_portraits.is_showing_dialogue())
	await free_scene(recruit_scene)

	var assist_scene := await setup_area("scifi.outskirts", "en", 1)
	app.recruit_member("zhao-ling")
	app.discover_field_trace("scifi.outskirts", 0)
	app.discover_field_trace("scifi.outskirts", 1)
	await interact(assist_scene, assist_scene.FIELD_ASSISTS["scifi.outskirts"]["position"])
	ck("assist-callback-enabled", not assist_scene.invite_button.disabled)
	assist_scene.invite_button.pressed.emit()
	await settle()
	ck("assist-callback-records", app.field_insights.has("scifi.outskirts") and assist_scene.character_ui_portraits.is_showing_dialogue())
	assist_scene.later_button.pressed.emit()
	await settle()
	ck("assist-later-closes", not assist_scene.dialogue_open and not assist_scene.character_ui_portraits.is_showing_dialogue())
	await free_scene(assist_scene)

	var wide := await setup_area("scifi.city", "en", 1)
	await interact(wide, wide.npc_position)
	await capture("dialogue-recruit-en-1280", Vector2i(1280, 720))
	await free_scene(wide)
	end_phase("dialogue")


func test_normal_route() -> void:
	begin_phase("normal-route")
	app.begin_new_run()
	app.language = "en"
	app.hero_appearance = "male"
	app.recruit_member("liang-xu")
	app.recruit_member("zhao-ling")
	app.ji_records_checked = true
	app.recruit_member("ji-cheng")
	var growth_script: Script = load("res://scripts/growth_screen.gd")
	growth_script.character_ui_portraits_override = 1
	growth_script.mvp_display_portraits_override = 0
	growth_script.female_display_portrait_override = 0
	growth_script.management_ui_skin_override = 0
	change_scene_to_file("res://scenes/scifi_world_map.tscn")
	await settle()
	var map: Node = current_scene
	ck("normal-route-map", map != null and map.has_method("_open_growth"))
	if map != null and map.get("growth_button") != null:
		click(map.growth_button)
		await settle()
		var growth: Control = current_scene
		ck("normal-route-growth", growth != null and growth.get("character_ui_portraits") != null)
		if growth != null and growth.get("character_ui_portraits") != null:
			ck("normal-route-growth-icons", growth.character_ui_portraits.get_party_subjects().size() == 4)
		await capture("growth-normal-route-en-640", Vector2i(640, 360))
		click(growth.back_button)
		await settle()
		ck("normal-route-back", current_scene != null and current_scene.has_method("_open_growth"))
	if current_scene != null:
		await free_scene(current_scene)
	end_phase("normal-route")


func make_report() -> void:
	var failed := checks.filter(func(row): return not row.pass)
	var report := {
		"schema": "ds-character-ui/actual-runtime-check/v1",
		"project": "rpg-2-star-ocean-the-second",
		"task": "content.ui-visual.character-portraits",
		"base": BASE,
		"helper": HELPER_PATH,
		"kit": KIT_PATH,
		"passed": checks.size() - failed.size(),
		"total": checks.size(),
		"failures": failed,
		"checks": checks,
		"captures": captures,
		"phaseTimesMs": phase_times,
		"sourceHashes": {
			"game/scripts/growth_screen.gd": _sha256_bytes(FileAccess.get_file_as_bytes("res://scripts/growth_screen.gd")),
			"game/scripts/scifi_exploration_area.gd": _sha256_bytes(FileAccess.get_file_as_bytes("res://scripts/scifi_exploration_area.gd")),
			"game/scripts/rpg-2-star-ocean-the-second_character-ui-portraits_helper_v01_20261019-233832-b7c4e912.gd": _sha256_bytes(FileAccess.get_file_as_bytes(HELPER_PATH)),
			"game/assets/portraits/ui-kit-v01/rpg-2-star-ocean-the-second_character-ui-kit_manifest_v01_20261019-233832-b7c4e912.json": _sha256_bytes(FileAccess.get_file_as_bytes(KIT_PATH)),
			"game/tests/fixtures/rpg-2-star-ocean-the-second_character-ui_growth-screen-baseline_e600241_v01_20261019-233832-b7c4e912.gd": _sha256_bytes(FileAccess.get_file_as_bytes("res://tests/fixtures/rpg-2-star-ocean-the-second_character-ui_growth-screen-baseline_e600241_v01_20261019-233832-b7c4e912.gd")),
			"game/tests/fixtures/rpg-2-star-ocean-the-second_character-ui_exploration-baseline_e600241_v01_20261019-233832-b7c4e912.gd": _sha256_bytes(FileAccess.get_file_as_bytes("res://tests/fixtures/rpg-2-star-ocean-the-second_character-ui_exploration-baseline_e600241_v01_20261019-233832-b7c4e912.gd")),
		},
		"approved": false,
		"approval": "none",
		"notes": "Captures support review only; they do not approve portraits, character canon or the full display art.",
	}
	var path := output_dir.path_join("rpg-2-star-ocean-the-second_character-ui-portraits_actual-runtime-report_v01_%s.json" % TAG)
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	for row in failed:
		print("FAILED ", row.key, " :: ", row.detail)
	print("CHARACTER_UI_RUNTIME ", report.passed, "/", report.total)
	print("CHARACTER_UI_REPORT ", path)
	var previous := AudioServer.get_time_since_last_mix()
	var mixes := 0
	var deadline := Time.get_ticks_usec() + 300000
	while mixes < 2 and Time.get_ticks_usec() < deadline:
		await process_frame
		var age := AudioServer.get_time_since_last_mix()
		if age < previous:
			mixes += 1
		previous = age
	print("CHARACTER_UI_AUDIO_MIX_BOUNDARIES ",mixes)
	quit(0 if failed.is_empty() and mixes == 2 else 1)


func run() -> void:
	var args := OS.get_cmdline_user_args()
	output_dir = args[0] if args.size() > 0 else "user://character-ui-portraits"
	DirAccess.make_dir_recursive_absolute(output_dir)
	app = root.get_node("AppState")
	kit = JSON.parse_string(FileAccess.get_file_as_string(KIT_PATH))
	begin_phase("total")
	await test_growth()
	await test_five_buttons_and_unknown()
	await test_malformed_packages()
	await test_dialogue()
	await test_normal_route()
	end_phase("total")
	make_report()

