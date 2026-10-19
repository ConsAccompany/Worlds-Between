extends RefCounted

# Battle HUD skin pilot helper: an UNAPPROVED technical candidate (not creator-approved art).
# Constructing it loads nothing. apply(arena) reads the package from the asset directory, prevalidates every
# required image, size, slice, hash and arena node, and only then skins the existing UI:
# - a mouse-ignoring NinePatchRect plate as the first child of the header, footer, pause panel and result panel
#   ColorRects (drawn above the rect's own colour, below every later label/button sibling; the pause/result veils are
#   untouched);
# - StyleBoxTexture overrides on the existing Buttons and ProgressBars, copying each old stylebox's effective content
#   margins so minimum sizes, text placement and every rectangle stay the same;
# - button font colour overrides only (never text, font or font size).
# Any missing or invalid input returns false before the first mutation. A post-check of every touched control's
# rectangle and combined minimum size reverts everything and returns false if anything moved.

const MANIFEST_NAME := "rpg-2-star-ocean-the-second_battle-ui_asset-manifest_skin-v01_20261019-171056-ca4652ec.json"
const PLATE_NAME := "BattleUiSkinPilotPlate"
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
const BAR_FILLS := {"hp_bar": "bar-fill-health", "energy_bar": "bar-fill-energy", "enemy_bar": "bar-fill-enemy"}
const HEADER_RECT := Rect2(0, 0, 640, 90)
const FOOTER_RECT := Rect2(0, 302, 640, 58)
const PAUSE_PANEL_RECT := Rect2(55, 43, 530, 265)
const RESULT_PANEL_RECT := Rect2(112, 99, 416, 171)

var asset_dir := ""
var applied := false
var last_error := ""
var _textures := {}
var _canvas_textures := {}
var _slices := {}
var _font_colors := {}
var _undo: Array[Callable] = []


func _init(directory: String) -> void:
	asset_dir = directory.trim_suffix("/")


func apply(arena: Node2D) -> bool:
	if applied:
		return true
	last_error = ""
	if arena == null or not _load_package():
		if last_error == "":
			last_error = "no arena"
		return false
	var targets := _collect_targets(arena)
	if targets.is_empty():
		return false
	var plan := _plan(targets)
	if plan.is_empty():
		return false
	# --- Mutation starts here; everything above only reads. ---
	var before := _snapshot(targets["controls"])
	for item in plan["plates"]:
		_add_plate(item[0], item[1])
	for item in plan["boxes"]:
		_override_box(item[0], item[1], item[2])
	for item in plan["colors"]:
		_override_color(item[0], item[1], item[2])
	if _snapshot(targets["controls"]) != before:
		revert()
		last_error = "a skinned control changed rectangle or minimum size; reverted"
		return false
	applied = true
	return true


# Removes every plate and restores every previous override. Safe to call when nothing was applied.
func revert() -> void:
	for index in range(_undo.size() - 1, -1, -1):
		_undo[index].call()
	_undo.clear()
	applied = false


func _fail(message: String) -> bool:
	last_error = message
	return false


func _number_equals(value: Variant, expected: int) -> bool:
	return (typeof(value) == TYPE_INT or typeof(value) == TYPE_FLOAT) and is_finite(float(value)) and float(value) == float(expected)

func _load_package() -> bool:
	if not _textures.is_empty():
		return true
	var manifest_path := asset_dir + "/" + MANIFEST_NAME
	if not FileAccess.file_exists(manifest_path):
		return _fail("missing manifest " + manifest_path)
	var parser := JSON.new()
	if parser.parse(FileAccess.get_file_as_string(manifest_path)) != OK:
		return _fail("invalid manifest JSON")
	var manifest: Variant = parser.data
	if not manifest is Dictionary or not manifest.get("skins") is Dictionary:
		return _fail("invalid manifest")
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
		if not s is Dictionary or not _number_equals(s.get("left"), expected_slices[0]) or not _number_equals(s.get("top"), expected_slices[1]) or not _number_equals(s.get("right"), expected_slices[2]) or not _number_equals(s.get("bottom"), expected_slices[3]):
			return _fail("manifest slice mismatch for " + key)
		var file_value: Variant = entry.get("png")
		if not file_value is String:
			return _fail("invalid png field for " + key)
		var file_name: String = file_value
		if file_name == "" or file_name.contains("/") or file_name.contains("\\") or not file_name.ends_with(".png"):
			return _fail("invalid png name for " + key)
		var path := asset_dir + "/" + file_name
		if FileAccess.file_exists(path):
			var hashes: Variant = entry.get("sha256")
			if not hashes is Dictionary:
				return _fail("invalid hash map for " + key)
			var digest: Variant = hashes.get(file_name)
			if not digest is String or FileAccess.get_sha256(path) != digest:
				return _fail("hash mismatch for " + key)
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
		if not html_value is String:
			return _fail("invalid font colour type " + color_name)
		var html: String = html_value
		if not Color.html_is_valid(html):
			return _fail("invalid font colour " + color_name)
		colors[color_name] = Color.html(html)
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


func _collect_targets(arena: Node2D) -> Dictionary:
	var buttons: Array[Button] = []
	for ref in ["quick_skill_button", "auto_button", "pause_skill_button", "pause_policy_button", "pause_resume_button", "result_button"]:
		var button: Variant = arena.get(ref)
		if not button is Button:
			_fail("missing button " + ref)
			return {}
		buttons.append(button)
	for ref in ["party_buttons", "pause_job_skill_buttons", "pause_target_buttons"]:
		var group: Variant = arena.get(ref)
		if not group is Array or group.is_empty():
			_fail("missing button group " + ref)
			return {}
		for button in group:
			if not button is Button:
				_fail("invalid button in " + ref)
				return {}
			buttons.append(button)
	var orders: Variant = arena.get("pause_order_buttons")
	if not orders is Dictionary or orders.is_empty():
		_fail("missing pause_order_buttons")
		return {}
	for command in orders:
		if not orders[command] is Button:
			_fail("invalid order button " + String(command))
			return {}
		buttons.append(orders[command])
	var bars := {}
	for ref in BAR_FILLS:
		var bar: Variant = arena.get(ref)
		if not bar is ProgressBar:
			_fail("missing bar " + ref)
			return {}
		bars[ref] = bar
	var canvas: Node = bars["hp_bar"].get_parent()
	var header := _find_rect(canvas, HEADER_RECT)
	var footer := _find_rect(canvas, FOOTER_RECT)
	var pause_overlay: Variant = arena.get("pause_overlay")
	var result_overlay: Variant = arena.get("result_overlay")
	if not pause_overlay is ColorRect or not result_overlay is ColorRect:
		_fail("missing pause/result overlay")
		return {}
	var pause_panel := _find_rect(pause_overlay, PAUSE_PANEL_RECT)
	var result_panel := _find_rect(result_overlay, RESULT_PANEL_RECT)
	if header == null or footer == null or pause_panel == null or result_panel == null:
		_fail("missing header/footer/panel ColorRect")
		return {}
	for plate_parent in [header, footer, pause_panel, result_panel]:
		if plate_parent.has_node(PLATE_NAME):
			_fail("already skinned")
			return {}
	var controls: Array[Control] = []
	controls.append_array(buttons)
	for ref in bars:
		controls.append(bars[ref])
	return {"buttons": buttons, "bars": bars, "plates": [[header, "hud-band"], [footer, "hud-band"], [pause_panel, "panel"], [result_panel, "panel"]], "controls": controls}


func _find_rect(parent: Node, rect: Rect2) -> ColorRect:
	for child in parent.get_children():
		if child is ColorRect and child.position == rect.position and child.size == rect.size:
			return child
	return null


# Builds every stylebox and checks it keeps the old minimum size, still without touching the arena.
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
	for ref in targets["bars"]:
		var bar: ProgressBar = targets["bars"][ref]
		var background := _make_box("bar-trough", bar.get_theme_stylebox("background"))
		var fill := _make_box(BAR_FILLS[ref], bar.get_theme_stylebox("fill"))
		if background == null or fill == null:
			return {}
		boxes.append([bar, "background", background])
		boxes.append([bar, "fill", fill])
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


func _add_plate(parent: ColorRect, key: String) -> void:
	var plate := NinePatchRect.new()
	plate.name = PLATE_NAME
	plate.texture = _textures[key]
	plate.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	plate.patch_margin_left = _slices[key][0]
	plate.patch_margin_top = _slices[key][1]
	plate.patch_margin_right = _slices[key][2]
	plate.patch_margin_bottom = _slices[key][3]
	plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
	plate.focus_mode = Control.FOCUS_NONE
	parent.add_child(plate)
	parent.move_child(plate, 0)
	plate.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_undo.append(func():
		if is_instance_valid(plate):
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
		# Hidden controls can retain an initial below-minimum rect until their first theme/show.
		# Compare the effective post-layout rectangle; root separately compares every visible context.
		var minimum := control.get_combined_minimum_size()
		out.append([control.position, control.size.max(minimum), minimum])
	return out
