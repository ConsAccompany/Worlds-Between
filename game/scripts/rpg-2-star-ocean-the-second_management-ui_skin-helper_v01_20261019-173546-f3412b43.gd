extends RefCounted

# Management UI skin pilot helper (growth_screen.gd + save_screen.gd): an UNAPPROVED technical candidate, not
# creator-approved art. It reuses the copied battle-skin-v01 package read-only (no new or altered images).
# Constructing it loads nothing. apply(screen) validates the whole package (manifest text hash, typed fields, all 11
# images, sizes, slices, raw PNG hashes, font colours), every screen ref, every plate's clearance and every
# stylebox's minimum size before the first mutation. It then adds:
# - mouse-ignoring, unfocusable NinePatchRect plates directly above the existing background/shade/row ColorRect and
#   below every existing label and button (growth: header band + two group panels, node overlay: header band;
#   save: header band + a frame-only cell behind each row's text);
# - StyleBoxTexture overrides on every existing Button that copy each old stylebox's content margins, and button font
#   colours only (never text, font, font size, disabled state, visibility or signals).
# A post-check of every existing control's effective rectangle and combined minimum size reverts everything and
# returns false if anything moved. revert() restores the screen exactly.

const MANIFEST_NAME := "rpg-2-star-ocean-the-second_battle-ui_asset-manifest_skin-v01_20261019-171056-ca4652ec.json"
# sha256-text-lf-v1 (CRLF -> LF, UTF-8) of the manifest.
const MANIFEST_SHA256_TEXT_LF := "545c0e25368a15061ee9b1cb8fca3f4c796907d43eecbcaa0c6e35bed221a504"
const PACKAGE_ID := "20261019-171056-ca4652ec"
const PLATE_NAME := "ManagementUiSkinPilotPlate"
const VIEW_RECT := Rect2(0, 0, 640, 360)
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
# Plate rectangles in the parent's local space (the screen and the node overlay are full 640x360 rects).
const GROWTH_HEADER_RECT := Rect2(0, 0, 640, 44)
const GROWTH_GROUP_RECTS := [Rect2(10, 82, 620, 180), Rect2(10, 270, 620, 88)]
const NODE_HEADER_RECT := Rect2(0, 0, 640, 44)
const SAVE_HEADER_RECT := Rect2(0, 0, 640, 42)
# save_screen rows: ColorRect at (16, label.y + offset) sized 608 x height.
const SAVE_ROW_X := 16.0
const SAVE_ROW_WIDTH := 608.0
const SAVE_MANUAL_ROW := [-7.0, 34.0]
const SAVE_AUTO_ROW := [-6.0, 29.0]
const CELL_GAP := 4.0
const GROWTH_BUTTON_REFS := ["back_button", "personal_upgrade_button", "stay_button", "promote_button", "nodes_button"]
# ref -> exact count (-1 = at least one)
const GROWTH_BUTTON_GROUPS := {"member_buttons": -1, "upgrade_buttons": 2, "series_buttons": 5}
const NODE_BUTTON_GROUPS := {"career_node_buttons": 10, "personal_node_buttons": 10}
const GROWTH_LABEL_REFS := ["title_label", "info_label", "aptitude_label", "job_label", "skill_label", "pending_label"]
const NODE_LABEL_REFS := ["node_title_label", "node_career_label", "node_personal_label", "node_summary_label"]
const SAVE_LABEL_REFS := ["title_label", "auto_title", "feedback_label"]

var asset_dir := ""
var require_raw_png := true
var applied := false
var screen_kind := ""
var last_error := ""
var _screen: Control = null
var _textures := {}
var _canvas_textures := {}
var _slices := {}
var _font_colors := {}
var _undo: Array[Callable] = []


func _init(directory: String) -> void:
	asset_dir = directory.trim_suffix("/")


func apply(screen: Control) -> bool:
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


func _collect_targets(screen: Control) -> Dictionary:
	if screen.get("member_buttons") is Array and screen.get("node_panel") is Control:
		return _collect_growth(screen)
	if screen.get("manual_load_buttons") is Array and screen.get("auto_load_buttons") is Array:
		return _collect_save(screen)
	_fail("screen is neither growth_screen nor save_screen")
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


func _ref_labels(source: Object, refs: Array, out: Array[Control]) -> bool:
	for ref in refs:
		var label: Variant = source.get(ref)
		if not label is Label:
			return _fail("missing label " + ref)
		out.append(label)
	return true


# The existing full-rect background/shade must be the first child; plates are inserted right after it.
func _background(parent: Control) -> ColorRect:
	if parent.get_child_count() == 0:
		return null
	var first := parent.get_child(0)
	if first is ColorRect and first.anchor_left == 0.0 and first.anchor_top == 0.0 and first.anchor_right == 1.0 and first.anchor_bottom == 1.0:
		return first
	return null


func _has_plate(parent: Node) -> bool:
	for child in parent.get_children():
		if String(child.name).begins_with(PLATE_NAME):
			return true
	return false


func _collect_growth(screen: Control) -> Dictionary:
	var node_panel: Control = screen.get("node_panel")
	if node_panel.get_parent() != screen:
		_fail("node_panel is not a child of the screen")
		return {}
	var main_buttons: Array[Button] = []
	var node_buttons: Array[Button] = []
	for ref in GROWTH_BUTTON_REFS:
		if not _ref_button(screen, ref, main_buttons):
			return {}
	for ref in GROWTH_BUTTON_GROUPS:
		if not _ref_group(screen, ref, GROWTH_BUTTON_GROUPS[ref], main_buttons):
			return {}
	if not _ref_button(screen, "node_close_button", node_buttons):
		return {}
	for ref in NODE_BUTTON_GROUPS:
		if not _ref_group(screen, ref, NODE_BUTTON_GROUPS[ref], node_buttons):
			return {}
	var main_labels: Array[Control] = []
	var node_labels: Array[Control] = []
	if not _ref_labels(screen, GROWTH_LABEL_REFS, main_labels) or not _ref_labels(screen, NODE_LABEL_REFS, node_labels):
		return {}
	for button in main_buttons:
		if button.get_parent() != screen:
			_fail("growth button outside the screen layer")
			return {}
	for button in node_buttons:
		if button.get_parent() != node_panel:
			_fail("node button outside the node overlay")
			return {}
	if _background(screen) == null or _background(node_panel) == null:
		_fail("missing growth background or node shade")
		return {}
	if _has_plate(screen) or _has_plate(node_panel):
		_fail("already skinned")
		return {}
	var plates := []
	plates.append({"parent": screen, "index": 1, "rect": GROWTH_HEADER_RECT, "key": "hud-band", "center": true, "name": PLATE_NAME + "Header"})
	for index in GROWTH_GROUP_RECTS.size():
		plates.append({"parent": screen, "index": 2 + index, "rect": GROWTH_GROUP_RECTS[index], "key": "panel", "center": true, "name": PLATE_NAME + "Group" + str(index)})
	plates.append({"parent": node_panel, "index": 1, "rect": NODE_HEADER_RECT, "key": "hud-band", "center": true, "name": PLATE_NAME + "NodeHeader"})
	if not _check_layer(plates.slice(0, 3), main_buttons, main_labels, screen) or not _check_layer(plates.slice(3), node_buttons, node_labels, node_panel):
		return {}
	var buttons: Array[Button] = []
	buttons.append_array(main_buttons)
	buttons.append_array(node_buttons)
	var controls: Array[Control] = []
	controls.append_array(buttons)
	controls.append_array(main_labels)
	controls.append_array(node_labels)
	controls.append(node_panel)
	return {"kind": "growth", "buttons": buttons, "plates": plates, "controls": controls}


func _collect_save(screen: Control) -> Dictionary:
	var buttons: Array[Button] = []
	var labels: Array[Control] = []
	if not _ref_button(screen, "back_button", buttons) or not _ref_labels(screen, SAVE_LABEL_REFS, labels):
		return {}
	var manual_labels: Variant = screen.get("manual_labels")
	var auto_labels: Variant = screen.get("auto_labels")
	var manual_save: Array[Button] = []
	var manual_load: Array[Button] = []
	var auto_load: Array[Button] = []
	if not manual_labels is Array or not auto_labels is Array or manual_labels.is_empty() or auto_labels.is_empty():
		_fail("missing save row labels")
		return {}
	if not _ref_group(screen, "manual_save_buttons", manual_labels.size(), manual_save) or not _ref_group(screen, "manual_load_buttons", manual_labels.size(), manual_load) or not _ref_group(screen, "auto_load_buttons", auto_labels.size(), auto_load):
		return {}
	buttons.append_array(manual_save)
	buttons.append_array(manual_load)
	buttons.append_array(auto_load)
	for button in buttons:
		if button.get_parent() != screen:
			_fail("save button outside the screen layer")
			return {}
	if _background(screen) == null:
		_fail("missing save background")
		return {}
	if _has_plate(screen):
		_fail("already skinned")
		return {}
	var header := {"parent": screen, "index": 1, "rect": SAVE_HEADER_RECT, "key": "hud-band", "center": true, "name": PLATE_NAME + "Header"}
	var rows: Array[Control] = []
	var cells := []
	for index in manual_labels.size() + auto_labels.size():
		var manual: bool = index < manual_labels.size()
		var row_index: int = index if manual else index - manual_labels.size()
		var label: Variant = manual_labels[row_index] if manual else auto_labels[row_index]
		if not label is Label:
			_fail("invalid save row label")
			return {}
		labels.append(label)
		var geometry: Array = SAVE_MANUAL_ROW if manual else SAVE_AUTO_ROW
		var row := _find_row(screen, Rect2(SAVE_ROW_X, label.position.y + geometry[0], SAVE_ROW_WIDTH, geometry[1]))
		if row == null:
			_fail("missing save row ColorRect " + str(index))
			return {}
		if row.get_child_count() != 0:
			_fail("save row already has children")
			return {}
		rows.append(row)
		# Frame-only cell behind the row text, ending CELL_GAP before the row's first visible button.
		var row_buttons: Array = [manual_save[row_index], manual_load[row_index]] if manual else [auto_load[row_index]]
		var right := row.position.x + row.size.x
		for button in row_buttons:
			if button.visible:
				right = minf(right, button.position.x - CELL_GAP)
		var cell := Rect2(0, 0, right - row.position.x, row.size.y)
		cells.append({"parent": row, "index": 0, "rect": cell, "key": "panel", "center": false, "name": PLATE_NAME + "Cell", "screen_rect": Rect2(row.position, cell.size)})
	var plates := [header]
	if not _check_layer(plates, buttons, labels, screen):
		return {}
	# The manual Save buttons are hidden for the whole visit in load mode; the cells only need to clear visible ones.
	var visible_buttons: Array[Button] = []
	for button in buttons:
		if button.visible:
			visible_buttons.append(button)
	for cell in cells:
		if not _check_plate(cell["screen_rect"], cell["key"], visible_buttons, labels):
			return {}
	plates.append_array(cells)
	var controls: Array[Control] = []
	controls.append_array(buttons)
	controls.append_array(labels)
	controls.append_array(rows)
	return {"kind": "save", "buttons": buttons, "plates": plates, "controls": controls}


func _find_row(parent: Node, rect: Rect2) -> ColorRect:
	for child in parent.get_children():
		if child is ColorRect and child.position == rect.position and child.size == rect.size:
			return child
	return null


func _effective_rect(control: Control) -> Rect2:
	return Rect2(control.position, control.size.max(control.get_combined_minimum_size()))


# Layer plates must stay on screen, clear the layer's other ColorRects, and keep borders off buttons and label origins.
func _check_layer(plates: Array, buttons: Array[Button], labels: Array[Control], parent: Control) -> bool:
	for plate in plates:
		var rect: Rect2 = plate["rect"]
		for child in parent.get_children():
			if child is ColorRect and child != parent.get_child(0) and rect.intersects(Rect2(child.position, child.size)):
				return _fail("plate overlaps an existing panel")
		if not _check_plate(rect, plate["key"], buttons, labels):
			return false
	return true


func _check_plate(rect: Rect2, key: String, buttons: Array[Button], labels: Array[Control]) -> bool:
	var s: Array = _slices[key]
	if not VIEW_RECT.encloses(rect) or rect.size.x <= s[0] + s[2] or rect.size.y <= s[1] + s[3]:
		return _fail("plate outside the 640x360 view or below its slices")
	var inner := Rect2(rect.position + Vector2(s[0], s[1]), rect.size - Vector2(s[0] + s[2], s[1] + s[3]))
	for button in buttons:
		var button_rect := _effective_rect(button)
		if rect.intersects(button_rect) and not inner.encloses(button_rect):
			return _fail("plate border would crowd button " + String(button.name))
	for label in labels:
		if rect.has_point(label.position) and not inner.has_point(label.position):
			return _fail("plate border would crowd label " + String(label.name))
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
	var parent: Control = item["parent"]
	var key: String = item["key"]
	var rect: Rect2 = item["rect"]
	var plate := NinePatchRect.new()
	plate.name = item["name"]
	plate.texture = _textures[key]
	plate.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	plate.draw_center = item["center"]
	plate.patch_margin_left = _slices[key][0]
	plate.patch_margin_top = _slices[key][1]
	plate.patch_margin_right = _slices[key][2]
	plate.patch_margin_bottom = _slices[key][3]
	plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
	plate.focus_mode = Control.FOCUS_NONE
	parent.add_child(plate)
	parent.move_child(plate, item["index"])
	plate.position = rect.position
	plate.size = rect.size
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
