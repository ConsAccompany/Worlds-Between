class_name MvpDisplayPortraitsPilot
extends Control

## One bounded, non-mutating display portrait helper for five MVP variants:
## the existing protagonist-female crop plus four new exact-crop variants.
## OFF by default. The constructor performs no file/texture/metadata I/O.
## It never writes AppState, never moves/hides/relabels/clips original controls,
## and never falls back to another character or a placeholder.
##
## Root wiring (root-owned, after review):
##   const Pilot := preload("res://scripts/mvp_display_portraits_pilot.gd")
##   var pilot := Pilot.new()
##   add_child(pilot)
##   pilot.install(self, node_panel)
##   pilot.update(AppState.hero_appearance, selected_id, not node_panel.visible)
##   # call update after the original _refresh()/selection/panel changes, and
##   # revert() on leaving the screen. Prefer --mvp-display-portraits-pilot over
##   # the old female flag when both are set.

const PILOT_FLAG := "--mvp-display-portraits-pilot"
const RECT := Rect2(522, 88, 96, 124)
const STRETCH_MODE := TextureRect.STRETCH_KEEP_ASPECT_CENTERED

# Literal expected path, raw PNG SHA-256 and native size per variant.
const VARIANTS := {
	"protagonist-female": {
		"image_path": "res://assets/portraits/female-display-v01/rpg-2-star-ocean-the-second_protagonist-female_display-portrait-crop_v01_20261019-221307-97f0236e.png",
		"raw_sha256": "481182891a0bf9b110a2ba05ca69c9c902b9d208255cf76bddd1aeb6c15868f6",
		"size": Vector2i(239, 311),
	},
	"protagonist-male": {
		"image_path": "res://assets/portraits/mvp-display-v01/rpg-2-star-ocean-the-second_protagonist-male_display-portrait-crop_v01_20261019-224538-744e4841.png",
		"raw_sha256": "8b47f7a8d4f7aa7e205573de6c62ff24190e638a61cbba6e4a67ffa6e65bdefe",
		"size": Vector2i(239, 311),
	},
	"liang-xu": {
		"image_path": "res://assets/portraits/mvp-display-v01/rpg-2-star-ocean-the-second_liang-xu_display-portrait-crop_v01_20261019-224538-dc29d7d2.png",
		"raw_sha256": "9872b534d040c05f1721a8fe385ff75f13cdb943537b16773a686a41a1ac5ab9",
		"size": Vector2i(305, 368),
	},
	"ji-cheng": {
		"image_path": "res://assets/portraits/mvp-display-v01/rpg-2-star-ocean-the-second_ji-cheng_display-portrait-crop_v02_20261019-225614-54ca9249.png",
		"raw_sha256": "764f7615d5eb6b2ed49eac7f8fe05bfb32645e3dcaa4bd8a2f6186946143b761",
		"size": Vector2i(360, 410),
	},
	"zhao-ling": {
		"image_path": "res://assets/portraits/mvp-display-v01/rpg-2-star-ocean-the-second_zhao-ling_display-portrait-crop_v01_20261019-224538-7203e81d.png",
		"raw_sha256": "1d37761501402043fb471d5b9f8843d84b5bc515eb2eb54ecabd73426a0eac53",
		"size": Vector2i(380, 345),
	},
}
const COMPANION_WHITELIST := ["liang-xu", "ji-cheng", "zhao-ling"]

var status := "off"
var refusal_reason := ""
var _host: Control = null
var _overlay: Control = null
var _installed := false
var _texture_rect: TextureRect = null
var _textures: Dictionary = {}
var _active_variant := ""
var _overlaps: Array[String] = []


func _init() -> void:
	name = "MvpDisplayPortraitsPilot"
	position = RECT.position
	size = RECT.size
	visible = false
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	set_process(false)


static func pilot_requested(user_args: PackedStringArray) -> bool:
	return user_args.has(PILOT_FLAG)


func install(host: Control, node_overlay: Control) -> bool:
	if host == null or node_overlay == null or node_overlay.get_parent() != host:
		_refuse("install-needs-host-and-child-overlay")
		return false
	if get_parent() != host:
		if get_parent() != null:
			get_parent().remove_child(self)
		host.add_child(self)
	if get_index() + 1 != node_overlay.get_index():
		var target := node_overlay.get_index()
		if get_index() < target:
			target -= 1
		host.move_child(self, target)
	_host = host
	_overlay = node_overlay
	_installed = true
	visible = false
	status = "installed-off"
	return true


## Re-evaluates the whole display from explicit identity values plus the host's
## actual selected_id. Uses a verified cached texture; never reloads on selection.
func update(appearance: Variant, selected_id: Variant, panel_hidden: Variant) -> bool:
	if not _installed:
		return _refuse("helper-not-installed")
	if not (appearance is String) or not (selected_id is String) or not (panel_hidden is bool):
		return _refuse("bad-argument-type")
	if not panel_hidden or (_overlay != null and _overlay.visible):
		_hide("node-panel-visible")
		return false
	var host_selected: Variant = _host.get("selected_id")
	if host_selected == null or not (host_selected is String) or String(host_selected) != selected_id:
		_hide("host-selected-id-mismatch")
		return false
	var variant := _variant_for(String(appearance), String(selected_id))
	if variant.is_empty():
		_hide("unknown-or-missing-selected-id")
		return false
	var texture := _texture_for(variant)
	if texture == null:
		return false
	_ensure_texture_rect()
	_texture_rect.texture = texture
	_active_variant = variant
	_overlaps = _find_overlaps()
	if not _overlaps.is_empty():
		_hide("visible-text-or-interactive-control-overlap: " + ", ".join(_overlaps))
		return false
	visible = true
	status = "shown:" + variant
	refusal_reason = ""
	return true


func refresh(appearance: Variant, selected_id: Variant, panel_hidden: Variant) -> bool:
	return update(appearance, selected_id, panel_hidden)


func revert() -> void:
	visible = false
	_installed = false
	_host = null
	_overlay = null
	if _texture_rect != null:
		_texture_rect.texture = null
	_textures.clear()
	_active_variant = ""
	_overlaps.clear()
	status = "reverted"
	refusal_reason = ""


func is_showing() -> bool:
	return visible


func get_status() -> String:
	return status


func get_refusal_reason() -> String:
	return refusal_reason


func get_overlap_details() -> Array[String]:
	var copy: Array[String] = []
	copy.assign(_overlaps)
	return copy


func get_active_variant() -> String:
	return _active_variant


func get_expected_rect() -> Rect2:
	return RECT


func get_texture_size() -> Vector2i:
	if _texture_rect == null or _texture_rect.texture == null:
		return Vector2i.ZERO
	return _texture_rect.texture.get_size()


func get_debug_state() -> Dictionary:
	return {
		"status": status,
		"refusal_reason": refusal_reason,
		"installed": _installed,
		"visible": visible,
		"variant": _active_variant,
		"texture_size": get_texture_size(),
		"rect": RECT,
		"cached": _textures.keys(),
		"overlaps": _overlaps.duplicate(),
	}


func _variant_for(appearance: String, selected_id: String) -> String:
	if selected_id == "hero":
		if appearance == "male":
			return "protagonist-male"
		if appearance == "female":
			return "protagonist-female"
		return ""
	if COMPANION_WHITELIST.has(selected_id):
		# Companion identity wins regardless of the hero's appearance.
		return selected_id
	return ""


func _texture_for(variant: String) -> ImageTexture:
	if _textures.has(variant):
		return _textures[variant] as ImageTexture
	var spec: Dictionary = VARIANTS[variant]
	var path := String(spec["image_path"])
	if not FileAccess.file_exists(path):
		_refuse("image-missing: " + path)
		return null
	var bytes := FileAccess.get_file_as_bytes(path)
	if bytes.is_empty():
		_refuse("image-unreadable: " + path)
		return null
	if _sha256_hex(bytes) != String(spec["raw_sha256"]):
		_refuse("image-sha256-mismatch: " + variant)
		return null
	var image := Image.new()
	if image.load_png_from_buffer(bytes) != OK or image.is_empty():
		_refuse("image-decode-failed: " + variant)
		return null
	if image.get_size() != Vector2i(spec["size"]):
		_refuse("image-size-mismatch: " + variant)
		return null
	var texture := ImageTexture.create_from_image(image)
	_textures[variant] = texture
	return texture


func _ensure_texture_rect() -> void:
	if _texture_rect != null:
		return
	_texture_rect = TextureRect.new()
	_texture_rect.name = "PortraitTexture"
	_texture_rect.position = Vector2.ZERO
	_texture_rect.size = RECT.size
	_texture_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_texture_rect.stretch_mode = STRETCH_MODE
	_texture_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_texture_rect.focus_mode = Control.FOCUS_NONE
	add_child(_texture_rect)


func _find_overlaps() -> Array[String]:
	var result: Array[String] = []
	if _host == null or not is_inside_tree():
		return result
	var target := get_global_rect()
	_collect_overlaps(_host, target, result)
	return result


func _collect_overlaps(node: Node, target: Rect2, result: Array[String]) -> void:
	for child in node.get_children():
		if child == self or (_overlay != null and (child == _overlay or _overlay.is_ancestor_of(child))):
			continue
		if child is Control:
			var control := child as Control
			# Passive decoration (ColorRect/TextureRect/NinePatchRect) is not an
			# obstruction; actual text and interactive controls are.
			if control.is_visible_in_tree() and _is_obstacle(control):
				var bounds := control.get_global_rect()
				var minimum := control.get_combined_minimum_size()
				bounds.size = Vector2(maxf(bounds.size.x, minimum.x), maxf(bounds.size.y, minimum.y))
				if bounds.size.x > 0.0 and bounds.size.y > 0.0 and bounds.intersects(target):
					result.append(String(control.get_path()))
		if child.get_child_count() > 0:
			_collect_overlaps(child, target, result)


func _is_obstacle(control: Control) -> bool:
	if control is Label:
		return not control.text.is_empty()
	if control is BaseButton or control is LineEdit or control is TextEdit or control is RichTextLabel or control is Range:
		return true
	return control.mouse_filter != Control.MOUSE_FILTER_IGNORE and not (control is ColorRect or control is TextureRect or control is NinePatchRect)


func _hide(reason: String) -> void:
	visible = false
	status = "hidden"
	refusal_reason = reason
	_overlaps.clear()


func _refuse(reason: String) -> bool:
	visible = false
	status = "refused"
	refusal_reason = reason
	_overlaps.clear()
	return false


func _sha256_hex(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	if context.start(HashingContext.HASH_SHA256) != OK:
		return ""
	context.update(bytes)
	return context.finish().hex_encode().to_lower()
