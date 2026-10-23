extends RefCounted

# Navigation/exploration UI skin pilot helper (scifi_exploration_area.gd, survey_annex.gd, scifi_world_map.gd): an
# UNAPPROVED technical candidate, not creator-approved art. It reuses the copied battle-skin-v01 package read-only
# (no new or altered images). Constructing it loads nothing. apply(screen) detects the screen kind from its required
# refs, validates the whole package (manifest text hash, typed fields, all 11 images, sizes, slices, raw PNG hashes,
# font colours), every ref, every existing chrome ColorRect's exact rectangle, every plate's clearance and every
# stylebox's minimum size before the first mutation. It then adds:
# - one mouse-ignoring, unfocusable, nearest-filtered NinePatchRect as the only child of each existing chrome
#   ColorRect (header/footer bands: hud-band; dialogue, investigation, field log, company and credits panels: panel),
#   exactly covering that rect, so it draws over the old flat fill and under every later sibling label and button.
#   The overlay dim ColorRects themselves, their colour, visibility and input handling are never touched;
# - StyleBoxTexture overrides on the existing stock-theme Buttons that copy each old stylebox's content margins, and
#   button font colours only (never text, font, font size, position, size, disabled state, visibility or signals).
# The world map's own native chrome is deliberately left as it is: the map frame and everything in it (terrain,
# routes, labels, markers, legend, calendar, zoom/view buttons, relief credit plate), the route card (its panel and
# _draw_route_card dressing, and its science-styled Depart/Cancel/option buttons, which are rebuilt on refresh).
# Any target Button that already has a stylebox override is refused rather than restyled.
# A post-check of every existing control's effective rectangle and combined minimum size reverts everything and
# returns false if anything moved. revert() restores the screen exactly.

const MANIFEST_NAME := "rpg-2-star-ocean-the-second_battle-ui_asset-manifest_skin-v01_20261019-171056-ca4652ec.json"
# sha256-text-lf-v1 (CRLF -> LF, UTF-8) of the manifest.
const MANIFEST_SHA256_TEXT_LF := "545c0e25368a15061ee9b1cb8fca3f4c796907d43eecbcaa0c6e35bed221a504"
const PACKAGE_ID := "20261019-171056-ca4652ec"
const PLATE_NAME := "NavigationUiSkinPilotPlate"
const VIEW_RECT := Rect2(0, 0, 640, 360)
# A label origin may sit this far into a plate's top border: Label lays text out below its line-top padding, so the
# map title at y 3 keeps its glyphs below the header band's 4 px top border. Sides and bottom get no allowance.
const LABEL_TOP_ALLOWANCE := 1.0
# key -> [size, [left, top, right, bottom] slices]
const REQUIRED := {
	"hud-band": [Vector2i(24, 24), [4, 4, 4, 4]],
	"panel": [Vector2i(24, 24), [4, 4, 4, 4]],
	"button-normal": [Vector2i(16, 16), [4, 4, 4, 4]],
	"button-hover": [Vector2i(16, 16), [4, 4, 4, 4]],
	"button-pressed": [Vector2i(16, 16), [4, 4, 4, 4]],
	"button-disabled": [Vector2i(16, 16), [4, 4, 4, 4]],
	"button-focus": [Vector2i(16, 16), [4, 4, 4, 4]],
	"bar-trough": [Vector2i(16, 16), [4, 4, 4, 4]],
	"bar-fill-health": [Vector2i(16, 16), [2, 4, 2, 4]],
	"bar-fill-energy": [Vector2i(16, 16), [2, 4, 2, 4]],
	"bar-fill-enemy": [Vector2i(16, 16), [2, 4, 2, 4]],
}
const BUTTON_STATES := {
	"normal": "button-normal",
	"hover": "button-hover",
	"pressed": "button-pressed",
	"hover_pressed": "button-pressed",
	"disabled": "button-disabled",
	"focus": "button-focus",
}
const FONT_COLOR_NAMES := ["font_color", "font_hover_color", "font_pressed_color", "font_hover_pressed_color", "font_focus_color", "font_disabled_color"]
# Existing chrome ColorRects, by exact rectangle in their parent's space (the CanvasLayer, or a full-view overlay).
const EXPLORE_HEADER_RECT := Rect2(0, 0, 640, 62)
const EXPLORE_FOOTER_RECT := Rect2(0, 318, 640, 42)
const EXPLORE_DIALOGUE_RECT := Rect2(87, 93, 466, 185)
# Optional character-ui-portraits pilot: its exact dialogue profile (panel, title, text, invite, later), entered from
# and reverted to the exact original layout above. Accepted only on the panel that installed helper owns.
const PORTRAITS_SCRIPT := "res://scripts/rpg-2-star-ocean-the-second_character-ui-portraits_helper_v01_20261019-233832-b7c4e912.gd"
const PORTRAIT_DIALOGUE_LAYOUT := [Rect2(8, 28, 624, 304), Rect2(274, 42, 344, 26), Rect2(274, 76, 344, 186), Rect2(274, 278, 160, 36), Rect2(446, 278, 160, 36)]
const ANNEX_HEADER_RECT := Rect2(0, 0, 640, 62)
const ANNEX_FOOTER_RECT := Rect2(0, 318, 640, 42)
const ANNEX_OVERLAY_RECT := Rect2(53, 41, 534, 278)
const MAP_HEADER_RECT := Rect2(0, 0, 640, 44)
const MAP_STRIP_RECT := Rect2(0, 313, 640, 47)
const MAP_FIELD_RECT := Rect2(48, 39, 544, 285)
const MAP_COMMERCE_RECT := Rect2(48, 39, 544, 285)
const MAP_CREDITS_RECT := Rect2(72, 62, 496, 236)

var asset_dir := ""
var require_raw_png := true
var applied := false
var screen_kind := ""
var last_error := ""
var _screen: Node = null
var _textures := {}
var _canvas_textures := {}
var _slices := {}
var _font_colors := {}
var _undo: Array[Callable] = []


func _init(directory: String) -> void:
	asset_dir = directory.trim_suffix("/")


func apply(screen: Node) -> bool:
	if applied:
		if screen == _screen:
			return true
		return _fail("already applied to another screen")
	last_error = ""
	screen_kind = ""
	if screen == null or not is_instance_valid(screen):
		return _fail("no screen")
	if not _load_package():
		return false
	var targets := _collect_targets(screen)
	if targets.is_empty():
		return false
	var plan := _plan(targets)
	if plan.is_empty():
		return false
	# --- Mutation starts here; everything above only reads. ---
	var before := _snapshot(targets["controls"])
	for item in plan["plates"]:
		_add_plate(item)
	for item in plan["boxes"]:
		_override_box(item[0], item[1], item[2])
	for item in plan["colors"]:
		_override_color(item[0], item[1], item[2])
	if _snapshot(targets["controls"]) != before:
		revert()
		return _fail("a skinned screen control changed rectangle or minimum size; reverted")
	_screen = screen
	screen_kind = targets["kind"]
	applied = true
	return true


# Removes every plate and restores every previous override. Safe to call when nothing was applied.
func revert() -> void:
	for index in range(_undo.size() - 1, -1, -1):
		_undo[index].call()
	_undo.clear()
	_screen = null
	applied = false


func _fail(message: String) -> bool:
	last_error = message
	return false


func _is_whole(value: Variant, minimum: int) -> bool:
	if typeof(value) != TYPE_INT and typeof(value) != TYPE_FLOAT:
		return false
	var number := float(value)
	return is_finite(number) and number == floorf(number) and number >= float(minimum)


func _number_equals(value: Variant, expected: int) -> bool:
	return _is_whole(value, -1000000) and float(value) == float(expected)


func _is_sha256(value: Variant) -> bool:
	if not value is String or value.length() != 64:
		return false
	for character in String(value):
		if not "0123456789abcdef".contains(character):
			return false
	return true


func _is_plain_name(value: Variant, extension: String) -> bool:
	if not value is String:
		return false
	var file_name: String = value
	return file_name.length() > extension.length() and file_name.ends_with(extension) and not file_name.contains("/") and not file_name.contains("\\") and not file_name.contains("..") and not file_name.contains(":")


func _text_sha256_lf(text: String) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(text.replace("\r\n", "\n").to_utf8_buffer())
	return context.finish().hex_encode()


func _load_package() -> bool:
	if not _textures.is_empty():
		return true
	var manifest_path := asset_dir + "/" + MANIFEST_NAME
	if not FileAccess.file_exists(manifest_path):
		return _fail("missing manifest " + manifest_path)
	var text := FileAccess.get_file_as_string(manifest_path)
	if _text_sha256_lf(text) != MANIFEST_SHA256_TEXT_LF:
		return _fail("manifest hash mismatch")
	var parser := JSON.new()
	if parser.parse(text) != OK:
		return _fail("invalid manifest JSON")
	var manifest: Variant = parser.data
	if not manifest is Dictionary:
		return _fail("invalid manifest")
	if not _number_equals(manifest.get("schemaVersion"), 1):
		return _fail("unsupported schemaVersion")
	if not manifest.get("packageId") is String or manifest["packageId"] != PACKAGE_ID:
		return _fail("packageId mismatch")
	if not manifest.get("filter") is String or manifest["filter"] != "nearest":
		return _fail("filter is not nearest")
	var order: Variant = manifest.get("skinOrder")
	if not order is Array or order.size() != REQUIRED.size():
		return _fail("invalid skinOrder")
	var seen := {}
	for key in order:
		if not key is String or not REQUIRED.has(key) or seen.has(key):
			return _fail("invalid skinOrder entry")
		seen[key] = true
	if not manifest.get("skins") is Dictionary:
		return _fail("manifest lacks skins")
	var skins: Dictionary = manifest["skins"]
	var textures := {}
	var slices := {}
	for key in REQUIRED:
		var entry: Variant = skins.get(key)
		if not entry is Dictionary:
			return _fail("manifest lacks skin " + key)
		var expected_size: Vector2i = REQUIRED[key][0]
		var expected_slices: Array = REQUIRED[key][1]
		var size: Variant = entry.get("size")
		if not size is Array or size.size() != 2 or not _number_equals(size[0], expected_size.x) or not _number_equals(size[1], expected_size.y):
			return _fail("manifest size mismatch for " + key)
		var s: Variant = entry.get("slices")
		if not s is Dictionary or s.size() != 4:
			return _fail("invalid slices for " + key)
		var sides := ["left", "top", "right", "bottom"]
		for side_index in sides.size():
			var value: Variant = s.get(sides[side_index])
			if not _is_whole(value, 1) or not _number_equals(value, expected_slices[side_index]):
				return _fail("manifest slice mismatch for " + key)
		if expected_slices[0] + expected_slices[2] >= expected_size.x or expected_slices[1] + expected_slices[3] >= expected_size.y:
			return _fail("slices leave no stretch centre for " + key)
		if not _is_plain_name(entry.get("png"), ".png") or not _is_plain_name(entry.get("pxo"), ".pxo") or not _is_plain_name(entry.get("ora"), ".ora"):
			return _fail("invalid file fields for " + key)
		var hashes: Variant = entry.get("sha256")
		if not hashes is Dictionary:
			return _fail("invalid sha256 field for " + key)
		for field in ["png", "pxo", "ora"]:
			if not _is_sha256(hashes.get(entry[field])):
				return _fail("invalid " + field + " hash for " + key)
		var file_name: String = entry["png"]
		var path := asset_dir + "/" + file_name
		if FileAccess.file_exists(path):
			if FileAccess.get_sha256(path) != hashes[file_name]:
				return _fail("raw PNG hash mismatch for " + key)
		elif require_raw_png:
			return _fail("missing raw PNG for " + key)
		var texture := _load_texture(path)
		if texture == null:
			return _fail("cannot load " + path)
		if Vector2i(texture.get_size()) != expected_size:
			return _fail("texture size mismatch for " + key)
		textures[key] = texture
		slices[key] = expected_slices
	var colors := {}
	var font_colors: Variant = manifest.get("fontColors")
	if not font_colors is Dictionary:
		return _fail("manifest lacks fontColors")
	for color_name in FONT_COLOR_NAMES:
		var html_value: Variant = font_colors.get(color_name)
		if not html_value is String or not String(html_value).begins_with("#") or not Color.html_is_valid(html_value):
			return _fail("invalid font colour " + color_name)
		colors[color_name] = Color.html(html_value)
	_textures = textures
	_slices = slices
	_font_colors = colors
	for key in textures:
		var canvas_texture := CanvasTexture.new()
		canvas_texture.diffuse_texture = textures[key]
		canvas_texture.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		_canvas_textures[key] = canvas_texture
	return true


func _load_texture(path: String) -> Texture2D:
	if ResourceLoader.exists(path):
		return load(path) as Texture2D
	if FileAccess.file_exists(path):
		var image := Image.load_from_file(path)
		if image != null and not image.is_empty():
			return ImageTexture.create_from_image(image)
	return null


# Kind detection from each scene's required refs (checked most specific first).
func _collect_targets(screen: Node) -> Dictionary:
	if screen.get("route_card") is Control and screen.get("commerce_overlay") is ColorRect and screen.get("credits_overlay") is ColorRect:
		return _collect_map(screen)
	if screen.get("overlay_body") is RichTextLabel and screen.get("link_buttons") is Array and screen.get("overlay") is ColorRect:
		return _collect_annex(screen)
	if screen.get("dialogue_overlay") is ColorRect and screen.get("invite_button") is Button and screen.get("later_button") is Button:
		return _collect_exploration(screen)
	_fail("screen is not scifi_exploration_area, survey_annex or scifi_world_map")
	return {}


func _ref_button(source: Object, ref: String, out: Array[Button]) -> bool:
	var button: Variant = source.get(ref)
	if not button is Button:
		return _fail("missing button " + ref)
	out.append(button)
	return true


func _ref_group(source: Object, ref: String, count: int, out: Array[Button]) -> bool:
	var group: Variant = source.get(ref)
	if not group is Array or group.is_empty() or (count >= 0 and group.size() != count):
		return _fail("missing or resized button group " + ref)
	for button in group:
		if not button is Button:
			return _fail("invalid button in " + ref)
		out.append(button)
	return true


# Labels and RichTextLabels drawn over a plate; only their origins are checked against plate borders.
func _ref_labels(source: Object, refs: Array, out: Array[Control]) -> bool:
	for ref in refs:
		var label: Variant = source.get(ref)
		if not label is Label and not label is RichTextLabel:
			return _fail("missing label " + ref)
		out.append(label)
	return true


# The exact existing chrome ColorRect child of parent; it must have no children (a plate becomes its only child).
func _chrome(parent: Node, rect: Rect2, what: String) -> ColorRect:
	var found: ColorRect = null
	for child in parent.get_children():
		if child is ColorRect and child.position == rect.position and child.size == rect.size:
			if found != null:
				_fail("ambiguous " + what)
				return null
			found = child
	if found == null:
		_fail("missing " + what + " ColorRect " + str(rect))
		return null
	if found.get_child_count() != 0:
		_fail(what + " already has children (already skinned?)")
		return null
	return found


# The exploration dialogue panel. Without the portrait pilot this is exactly _chrome(). With the installed portrait
# helper the panel and its four controls must sit exactly in either the helper's recorded original layout (which must
# be EXPLORE_DIALOGUE_RECT) or its exact portrait profile; both layouts must clear the plate border, and only that
# helper's own frame/portrait may be children. Returns [panel, follow] or [] after _fail.
func _dialogue_panel(screen: Node, overlay: Node, buttons: Array[Button], labels: Array[Control]) -> Array:
	var helper: Variant = screen.get("character_ui_portraits")
	if not helper is Control or helper.get_script() == null or helper.get_script().resource_path != PORTRAITS_SCRIPT or helper.get("_installed_dialogue") != true:
		var plain := _chrome(overlay, EXPLORE_DIALOGUE_RECT, "dialogue panel")
		return [] if plain == null else [plain, false]
	var panel: Variant = helper.get("_dialogue_panel")
	var original: Variant = helper.get("_dialogue_original")
	if not panel is ColorRect or panel.get_parent() != overlay or not original is Dictionary or helper.get("DIALOGUE_PANEL_RECT") != PORTRAIT_DIALOGUE_LAYOUT[0]:
		_fail("portrait dialogue profile not installed on the dialogue panel")
		return []
	if helper.get("_dialogue_title") != labels[0] or helper.get("_dialogue_text") != labels[1] or helper.get("_dialogue_invite") != buttons[0] or helper.get("_dialogue_later") != buttons[1]:
		_fail("portrait dialogue profile does not own the scene's dialogue controls")
		return []
	var controls: Array = [panel, labels[0], labels[1], buttons[0], buttons[1]]
	var base := []
	var live := []
	for index in controls.size():
		var key: String = ["panel", "title", "text", "invite", "later"][index]
		if not original.get(key) is Rect2:
			_fail("portrait dialogue profile has no original " + key)
			return []
		base.append(original[key])
		live.append(Rect2(controls[index].position, controls[index].size))
	if base[0] != EXPLORE_DIALOGUE_RECT or (live != base and live != PORTRAIT_DIALOGUE_LAYOUT):
		_fail("missing dialogue panel ColorRect " + str(EXPLORE_DIALOGUE_RECT) + " or exact portrait profile")
		return []
	for child in panel.get_children():
		if child != helper.get("_dialogue_frame") and child != helper.get("_dialogue_portrait"):
			_fail("dialogue panel already has children (already skinned?)")
			return []
	for layout in [base, PORTRAIT_DIALOGUE_LAYOUT]:
		var button_rects := []
		for index in [3, 4]:
			button_rects.append(Rect2(layout[index].position, layout[index].size.max(controls[index].get_combined_minimum_size())))
		if not _check_plate_rects(layout[0], "panel", buttons, button_rects, labels, [layout[1].position, layout[2].position]):
			return []
	return [panel, true]


# A full-view overlay (dim) ColorRect, as built by the scene; it stays untouched.
func _overlay(source: Object, ref: String, canvas: Node) -> ColorRect:
	var overlay: Variant = source.get(ref)
	if not overlay is ColorRect or overlay.get_parent() != canvas or overlay.position != Vector2.ZERO or overlay.size != VIEW_RECT.size:
		_fail("missing or moved overlay " + ref)
		return null
	return overlay


func _same_parent(controls: Array, parent: Node, what: String) -> bool:
	for control in controls:
		if control.get_parent() != parent:
			return _fail(what + " " + String(control.name) + " outside its layer")
	return true


# Builds one layer: plates (parent ColorRect + key) with every button and label that shares the ColorRects' space.
func _layer(chromes: Array, keys: Array, buttons: Array[Button], labels: Array[Control], parent: Node) -> Array:
	if not _same_parent(buttons, parent, "button") or not _same_parent(labels, parent, "label"):
		return []
	var plates := []
	for index in chromes.size():
		var chrome: ColorRect = chromes[index]
		var rect := Rect2(chrome.position, chrome.size)
		if not _check_plate(rect, keys[index], buttons, labels):
			return []
		plates.append({"parent": chrome, "key": keys[index], "size": chrome.size, "name": PLATE_NAME + str(keys[index]).capitalize().replace(" ", "")})
	return plates


func _canvas_of(screen: Node) -> CanvasLayer:
	var back: Variant = screen.get("back_button")
	if not back is Button or not back.get_parent() is CanvasLayer or back.get_parent().get_parent() != screen:
		_fail("back_button is not on the scene's CanvasLayer")
		return null
	return back.get_parent()


func _collect_exploration(screen: Node) -> Dictionary:
	var canvas := _canvas_of(screen)
	if canvas == null:
		return {}
	var bar_buttons: Array[Button] = []
	var bar_labels: Array[Control] = []
	var dialogue_buttons: Array[Button] = []
	var dialogue_labels: Array[Control] = []
	if not _ref_button(screen, "back_button", bar_buttons) or not _ref_button(screen, "save_button", bar_buttons):
		return {}
	if not _ref_labels(screen, ["title_label", "hint_label", "feedback_label", "help_label"], bar_labels):
		return {}
	if not _ref_button(screen, "invite_button", dialogue_buttons) or not _ref_button(screen, "later_button", dialogue_buttons):
		return {}
	if not _ref_labels(screen, ["dialogue_title", "dialogue_text"], dialogue_labels):
		return {}
	var overlay := _overlay(screen, "dialogue_overlay", canvas)
	if overlay == null:
		return {}
	var header := _chrome(canvas, EXPLORE_HEADER_RECT, "header")
	var footer := _chrome(canvas, EXPLORE_FOOTER_RECT, "footer")
	if header == null or footer == null:
		return {}
	var found := _dialogue_panel(screen, overlay, dialogue_buttons, dialogue_labels)
	if found.is_empty():
		return {}
	var panel: ColorRect = found[0]
	var plates := _layer([header, footer], ["hud-band", "hud-band"], bar_buttons, bar_labels, canvas)
	var dialogue := _layer([panel], ["panel"], dialogue_buttons, dialogue_labels, overlay)
	if plates.is_empty() or dialogue.is_empty():
		return {}
	dialogue[0]["follow"] = found[1]
	plates.append_array(dialogue)
	return _targets("exploration", plates, [bar_buttons, dialogue_buttons], [bar_labels, dialogue_labels], [header, footer, panel, overlay])


func _collect_annex(screen: Node) -> Dictionary:
	var canvas := _canvas_of(screen)
	if canvas == null:
		return {}
	var bar_buttons: Array[Button] = []
	var bar_labels: Array[Control] = []
	var overlay_buttons: Array[Button] = []
	var overlay_labels: Array[Control] = []
	if not _ref_button(screen, "save_button", bar_buttons) or not _ref_button(screen, "back_button", bar_buttons):
		return {}
	if not _ref_labels(screen, ["title_label", "progress_label", "help_label"], bar_labels):
		return {}
	if not _ref_group(screen, "option_buttons", 3, overlay_buttons) or not _ref_group(screen, "link_buttons", 6, overlay_buttons):
		return {}
	for ref in ["notes_button", "previous_note_button", "next_note_button", "close_button"]:
		if not _ref_button(screen, ref, overlay_buttons):
			return {}
	if not _ref_labels(screen, ["overlay_title", "overlay_body"], overlay_labels):
		return {}
	var overlay := _overlay(screen, "overlay", canvas)
	if overlay == null:
		return {}
	var header := _chrome(canvas, ANNEX_HEADER_RECT, "header")
	var footer := _chrome(canvas, ANNEX_FOOTER_RECT, "footer")
	var panel := _chrome(overlay, ANNEX_OVERLAY_RECT, "investigation panel")
	if header == null or footer == null or panel == null:
		return {}
	var plates := _layer([header, footer], ["hud-band", "hud-band"], bar_buttons, bar_labels, canvas)
	var investigation := _layer([panel], ["panel"], overlay_buttons, overlay_labels, overlay)
	if plates.is_empty() or investigation.is_empty():
		return {}
	plates.append_array(investigation)
	return _targets("annex", plates, [bar_buttons, overlay_buttons], [bar_labels, overlay_labels], [header, footer, panel, overlay])


func _collect_map(screen: Node) -> Dictionary:
	var canvas := _canvas_of(screen)
	if canvas == null:
		return {}
	var bar_buttons: Array[Button] = []
	var bar_labels: Array[Control] = []
	for ref in ["save_button", "growth_button", "back_button", "field_button", "commerce_button"]:
		if not _ref_button(screen, ref, bar_buttons):
			return {}
	if not _ref_labels(screen, ["title_label", "help_label", "field_status"], bar_labels):
		return {}
	var header := _chrome(canvas, MAP_HEADER_RECT, "map header")
	var strip := _chrome(canvas, MAP_STRIP_RECT, "map strip")
	if header == null or strip == null:
		return {}
	var plates := _layer([header, strip], ["hud-band", "hud-band"], bar_buttons, bar_labels, canvas)
	if plates.is_empty():
		return {}
	var button_sets: Array = [bar_buttons]
	var label_sets: Array = [bar_labels]
	var chromes: Array = [header, strip]
	# [overlay ref, panel rect, button refs, button group refs, label refs]
	var overlays := [
		["field_overlay", MAP_FIELD_RECT, ["talk_button", "field_close"], {}, ["field_title", "field_body"]],
		["commerce_overlay", MAP_COMMERCE_RECT, ["commerce_recall_button", "commerce_rest_button", "commerce_close"], {"commerce_member_buttons": -1}, ["commerce_title", "commerce_body"]],
		["credits_overlay", MAP_CREDITS_RECT, ["credits_close"], {}, ["credits_title", "credits_body"]],
	]
	for spec in overlays:
		var overlay := _overlay(screen, spec[0], canvas)
		if overlay == null:
			return {}
		var buttons: Array[Button] = []
		var labels: Array[Control] = []
		for ref in spec[2]:
			if not _ref_button(screen, ref, buttons):
				return {}
		for ref in spec[3]:
			if not _ref_group(screen, ref, spec[3][ref], buttons):
				return {}
		if not _ref_labels(screen, spec[4], labels):
			return {}
		var panel := _chrome(overlay, spec[1], String(spec[0]) + " panel")
		if panel == null:
			return {}
		var layer := _layer([panel], ["panel"], buttons, labels, overlay)
		if layer.is_empty():
			return {}
		plates.append_array(layer)
		button_sets.append(buttons)
		label_sets.append(labels)
		chromes.append_array([panel, overlay])
	return _targets("map", plates, button_sets, label_sets, chromes)


func _targets(kind: String, plates: Array, button_sets: Array, label_sets: Array, extra: Array) -> Dictionary:
	var buttons: Array[Button] = []
	var controls: Array[Control] = []
	for group_list in button_sets:
		buttons.append_array(group_list)
	for button in buttons:
		# Never replace a scene's own native button styling (e.g. the map's science buttons).
		for state in BUTTON_STATES:
			if button.has_theme_stylebox_override(state):
				_fail("button " + String(button.name) + " already has its own " + state + " style")
				return {}
	controls.append_array(buttons)
	for group_list in label_sets:
		controls.append_array(group_list)
	for control in extra:
		controls.append(control)
	return {"kind": kind, "buttons": buttons, "plates": plates, "controls": controls}


func _effective_rect(control: Control) -> Rect2:
	return Rect2(control.position, control.size.max(control.get_combined_minimum_size()))


func _check_plate(rect: Rect2, key: String, buttons: Array[Button], labels: Array[Control]) -> bool:
	var button_rects := []
	for button in buttons:
		button_rects.append(_effective_rect(button))
	var label_points := []
	for label in labels:
		label_points.append(label.position)
	return _check_plate_rects(rect, key, buttons, button_rects, labels, label_points)


func _check_plate_rects(rect: Rect2, key: String, buttons: Array[Button], button_rects: Array, labels: Array[Control], label_points: Array) -> bool:
	var s: Array = _slices[key]
	if not is_finite(rect.size.x) or not is_finite(rect.size.y) or not VIEW_RECT.encloses(rect) or rect.size.x <= s[0] + s[2] or rect.size.y <= s[1] + s[3]:
		return _fail("plate outside the 640x360 view or below its slices")
	var inner := Rect2(rect.position + Vector2(s[0], s[1]), rect.size - Vector2(s[0] + s[2], s[1] + s[3]))
	var label_inner := Rect2(inner.position - Vector2(0, LABEL_TOP_ALLOWANCE), inner.size + Vector2(0, LABEL_TOP_ALLOWANCE))
	for index in buttons.size():
		var button_rect: Rect2 = button_rects[index]
		if rect.intersects(button_rect) and not inner.encloses(button_rect):
			return _fail("plate border would crowd button " + String(buttons[index].name))
	for index in labels.size():
		var point: Vector2 = label_points[index]
		if rect.has_point(point) and not label_inner.has_point(point):
			return _fail("plate border would crowd label " + String(labels[index].name))
	return true


# Builds every stylebox and checks it keeps the old minimum size, still without touching the screen.
func _plan(targets: Dictionary) -> Dictionary:
	var boxes := []
	var colors := []
	for target in targets["buttons"]:
		var button: Button = target
		for state in BUTTON_STATES:
			var box := _make_box(BUTTON_STATES[state], button.get_theme_stylebox(state))
			if box == null:
				return {}
			boxes.append([button, state, box])
		for color_name in FONT_COLOR_NAMES:
			colors.append([button, color_name, _font_colors[color_name]])
	return {"plates": targets["plates"], "boxes": boxes, "colors": colors}


func _make_box(key: String, old: StyleBox) -> StyleBoxTexture:
	if old == null:
		_fail("no existing stylebox for " + key)
		return null
	var s: Array = _slices[key]
	var box := StyleBoxTexture.new()
	box.texture = _canvas_textures[key]
	box.texture_margin_left = s[0]
	box.texture_margin_top = s[1]
	box.texture_margin_right = s[2]
	box.texture_margin_bottom = s[3]
	box.content_margin_left = old.get_margin(SIDE_LEFT)
	box.content_margin_top = old.get_margin(SIDE_TOP)
	box.content_margin_right = old.get_margin(SIDE_RIGHT)
	box.content_margin_bottom = old.get_margin(SIDE_BOTTOM)
	if box.get_minimum_size() != old.get_minimum_size():
		_fail("minimum size would change for " + key)
		return null
	return box


func _add_plate(item: Dictionary) -> void:
	var parent: ColorRect = item["parent"]
	var key: String = item["key"]
	var plate := NinePatchRect.new()
	plate.name = item["name"]
	plate.texture = _textures[key]
	plate.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	plate.draw_center = true
	plate.patch_margin_left = _slices[key][0]
	plate.patch_margin_top = _slices[key][1]
	plate.patch_margin_right = _slices[key][2]
	plate.patch_margin_bottom = _slices[key][3]
	plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
	plate.focus_mode = Control.FOCUS_NONE
	parent.add_child(plate)
	plate.position = Vector2.ZERO
	plate.size = item["size"]
	if item.get("follow", false):
		# Portrait profile: draw under the helper's own frame/portrait and track the panel's exact rect both ways.
		parent.move_child(plate, 0)
		plate.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_undo.append(func():
		if is_instance_valid(plate):
			if plate.get_parent() != null:
				plate.get_parent().remove_child(plate)
			plate.free())


func _override_box(control: Control, item: String, box: StyleBox) -> void:
	var previous: StyleBox = control.get_theme_stylebox(item) if control.has_theme_stylebox_override(item) else null
	control.add_theme_stylebox_override(item, box)
	_undo.append(func():
		if not is_instance_valid(control):
			return
		if previous != null:
			control.add_theme_stylebox_override(item, previous)
		else:
			control.remove_theme_stylebox_override(item))


func _override_color(control: Control, item: String, color: Color) -> void:
	var had := control.has_theme_color_override(item)
	var previous := control.get_theme_color(item)
	control.add_theme_color_override(item, color)
	_undo.append(func():
		if not is_instance_valid(control):
			return
		if had:
			control.add_theme_color_override(item, previous)
		else:
			control.remove_theme_color_override(item))


func _snapshot(controls: Array[Control]) -> Array:
	var out := []
	for control in controls:
		# Hidden controls can retain an initial below-minimum rect until their first theme/show; compare the
		# effective settled rectangle. Root separately compares every visible context ON vs OFF.
		var minimum := control.get_combined_minimum_size()
		out.append([control.position, control.size.max(minimum), minimum, control.visible])
	return out
