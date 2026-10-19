class_name FemaleDisplayPortraitPilot
extends Control

## Bounded, non-mutating display helper for content.char.protagonist-female.display.
##
## This helper is OFF unless the caller explicitly passes the pilot flag and
## explicit identity values.  It never writes AppState, never emits or wires
## gameplay signals, never moves/hides/relabels/clips original controls, and
## never falls back to another character or to the masculine variant.
##
## Required root wiring (root owns this; growth_screen.gd is not edited):
##   const Portrait := preload("res://scripts/female_display_portrait_pilot.gd")
##   const PORTRAIT_MANIFEST := "res://assets/portraits/<run>.manifest.json"
##   var portrait := Portrait.new()          # constructor loads nothing
##   add_child(portrait)
##   portrait.install(self, node_panel)      # inserts below node_panel
##   portrait.apply_appstate(
##       PORTRAIT_MANIFEST, AppState, "hero", selected_id,
##       not node_panel.visible,
##       Portrait.pilot_requested(OS.get_cmdline_user_args()))
## and call portrait.refresh(...) wherever selected_id / node_panel visibility
## may change, and portrait.revert() on leaving the screen.
##
## The display rectangle is fixed at Rect2(522, 88, 96, 124).  The helper
## refuses (hides and reports) rather than moving that rectangle or touching an
## overlapping visible text/control.

const CONTENT_ID := "content.char.protagonist-female.display"
const PILOT_FLAG := "--female-display-portrait-pilot"
const SCHEMA_ID := "ds-portrait/display-image-manifest/v1"
const SOURCE_SHA256 := "3d876c4f666913d6110fe8a058b79a55ce82ac225577d87f1f02624affeea58d"
const SOURCE_WIDTH := 1916
const SOURCE_HEIGHT := 821
const CROP_LEFT := 952
const CROP_TOP := 42
const CROP_RIGHT := 1191
const CROP_BOTTOM := 353
const CROP_WIDTH := 239
const CROP_HEIGHT := 311
const PORTRAIT_RECT := Rect2(522, 88, 96, 124)
const REQUIRED_APPEARANCE := "female"
const REQUIRED_MEMBER_ID := "hero"

const NAVY := Color(0.070588, 0.141176, 0.192157, 1.0)
const BRONZE := Color(0.690196, 0.552941, 0.341176, 1.0)

var status := "off"
var refusal_reason := ""

var _host: Control = null
var _overlay: Control = null
var _installed := false
var _applied := false
var _last_signature := ""
var _metadata_path := ""
var _metadata: Dictionary = {}
var _texture: ImageTexture = null
var _texture_rect: TextureRect = null
var _frame: Control = null
var _last_overlaps: Array[String] = []


class NavyBronzeFrame:
	extends Control

	func _init() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE
		focus_mode = Control.FOCUS_NONE

	func _draw() -> void:
		# Existing navy/bronze management UI concept; no new frame art asset.
		draw_rect(Rect2(0.5, 0.5, size.x - 1.0, size.y - 1.0), Color("#b08d57"), false, 1.0)


func _init() -> void:
	name = "FemaleDisplayPortraitPilot"
	position = PORTRAIT_RECT.position
	size = PORTRAIT_RECT.size
	visible = false
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	set_process(false)


static func pilot_requested(user_args: PackedStringArray) -> bool:
	return user_args.has(PILOT_FLAG)


func install(host: Control, node_overlay: Control) -> bool:
	if host == null or node_overlay == null:
		status = "refused-not-installed"
		refusal_reason = "install-needs-host-and-node-overlay"
		return false
	if node_overlay.get_parent() != host:
		status = "refused-not-installed"
		refusal_reason = "node-overlay-is-not-a-child-of-host"
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
	position = PORTRAIT_RECT.position
	size = PORTRAIT_RECT.size
	visible = false
	status = "installed-off"
	return true


## Explicit-identity entry point.  appearance must be the caller's actual
## AppState.hero_appearance value; no default is read here.
func apply(
		metadata_path: String,
		appearance: String,
		member_id: String,
		selected_id: String,
		panel_hidden: bool,
		pilot_enabled: bool) -> bool:
	var signature := "%s|%s|%s|%s|%s|%s" % [
		metadata_path, appearance, member_id, selected_id, str(panel_hidden), str(pilot_enabled)
	]
	if _applied and signature == _last_signature and _texture_rect != null and _texture_rect.texture != null:
		_update_visibility(appearance, member_id, selected_id, panel_hidden)
		return _applied and status != "refused-overlap"
	_applied = false
	_last_signature = ""
	_clear_texture()
	if not pilot_enabled:
		return _refuse("pilot-flag-off")
	if not _installed:
		return _refuse("helper-not-installed")
	if not _validate_and_load(metadata_path):
		return false
	_ensure_visuals()
	_texture_rect.texture = _texture
	_metadata_path = metadata_path
	_applied = true
	_last_signature = signature
	_update_visibility(appearance, member_id, selected_id, panel_hidden)
	# False means a refusal (bad package or visible overlap).  An applied but
	# ineligible portrait returns true with status "hidden-eligibility".
	return _applied and status != "refused-overlap"


## Convenience wiring that reads the real property from an explicitly supplied
## AppState object.  Missing property is a refusal, never a fallback.
func apply_appstate(
		metadata_path: String,
		app_state: Object,
		member_id: String,
		selected_id: String,
		panel_hidden: bool,
		pilot_enabled: bool) -> bool:
	if app_state == null:
		return _refuse("appstate-missing")
	var appearance_value: Variant = app_state.get("hero_appearance")
	if appearance_value == null or not (appearance_value is String):
		return _refuse("appstate-hero_appearance-missing")
	return apply(metadata_path, String(appearance_value), member_id, selected_id, panel_hidden, pilot_enabled)


## Re-evaluates visibility only; never reloads the PNG and never duplicates
## children.  Returns true only when the portrait is actually visible.
func refresh(appearance: String, member_id: String, selected_id: String, panel_hidden: bool) -> bool:
	if not _applied or _texture_rect == null or _texture_rect.texture == null:
		visible = false
		status = "not-applied"
		return false
	return _update_visibility(appearance, member_id, selected_id, panel_hidden)


## Hides and releases the texture.  Leaves original controls untouched.
func revert() -> void:
	visible = false
	_applied = false
	_last_signature = ""
	_clear_texture()
	_metadata.clear()
	_metadata_path = ""
	_last_overlaps.clear()
	status = "reverted"
	refusal_reason = ""


func is_applied() -> bool:
	return _applied


func is_showing() -> bool:
	return visible


func get_status() -> String:
	return status


func get_refusal_reason() -> String:
	return refusal_reason


func get_overlap_details() -> Array[String]:
	var copy: Array[String] = []
	copy.assign(_last_overlaps)
	return copy


func get_texture_size() -> Vector2i:
	if _texture == null:
		return Vector2i.ZERO
	return _texture.get_size()


func get_expected_rect() -> Rect2:
	return PORTRAIT_RECT


func get_debug_state() -> Dictionary:
	return {
		"status": status,
		"refusal_reason": refusal_reason,
		"installed": _installed,
		"applied": _applied,
		"visible": visible,
		"metadata_path": _metadata_path,
		"texture_size": get_texture_size(),
		"portrait_rect": PORTRAIT_RECT,
		"overlaps": _last_overlaps.duplicate(),
	}


func _update_visibility(
		appearance: String,
		member_id: String,
		selected_id: String,
		panel_hidden: bool) -> bool:
	if not _applied:
		visible = false
		status = "not-applied"
		return false
	if not _eligible(appearance, member_id, selected_id, panel_hidden):
		visible = false
		status = "hidden-eligibility"
		refusal_reason = _eligibility_reason(appearance, member_id, selected_id, panel_hidden)
		_last_overlaps.clear()
		return false
	_last_overlaps = _find_visible_overlaps()
	if not _last_overlaps.is_empty():
		visible = false
		status = "refused-overlap"
		refusal_reason = "visible-text-or-control-overlaps-portrait: " + ", ".join(_last_overlaps)
		return false
	visible = true
	status = "shown"
	refusal_reason = ""
	return true


func _eligibility_reason(
		appearance: String,
		member_id: String,
		selected_id: String,
		panel_hidden: bool) -> String:
	if appearance != REQUIRED_APPEARANCE:
		return "appearance-is-not-female"
	if member_id != REQUIRED_MEMBER_ID:
		return "member-id-is-not-hero"
	if selected_id != REQUIRED_MEMBER_ID:
		return "selected-id-is-not-hero"
	if member_id != selected_id:
		return "member-and-selected-id-differ"
	if not panel_hidden:
		return "node-panel-visible"
	if _overlay != null and _overlay.visible:
		return "node-overlay-visible"
	if _host != null:
		var host_selected: Variant = _host.get("selected_id")
		if host_selected != null and String(host_selected) != REQUIRED_MEMBER_ID:
			return "host-selected-id-is-not-hero"
	return "ineligible"


func _eligible(
		appearance: String,
		member_id: String,
		selected_id: String,
		panel_hidden: bool) -> bool:
	if appearance != REQUIRED_APPEARANCE:
		return false
	if member_id != REQUIRED_MEMBER_ID or selected_id != REQUIRED_MEMBER_ID:
		return false
	if member_id != selected_id:
		return false
	if not panel_hidden:
		return false
	if _overlay != null and _overlay.visible:
		return false
	if _host != null:
		var host_selected: Variant = _host.get("selected_id")
		if host_selected != null and String(host_selected) != REQUIRED_MEMBER_ID:
			return false
	return true


func _ensure_visuals() -> void:
	if _texture_rect == null:
		_texture_rect = TextureRect.new()
		_texture_rect.name = "PortraitTexture"
		_texture_rect.position = Vector2.ZERO
		_texture_rect.size = PORTRAIT_RECT.size
		_texture_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		_texture_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		_texture_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_texture_rect.focus_mode = Control.FOCUS_NONE
		add_child(_texture_rect)
	if _frame == null:
		_frame = NavyBronzeFrame.new()
		_frame.name = "NavyBronzeFrame"
		_frame.position = Vector2.ZERO
		_frame.size = PORTRAIT_RECT.size
		_frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_frame.focus_mode = Control.FOCUS_NONE
		add_child(_frame)


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, PORTRAIT_RECT.size), NAVY, true)
	draw_rect(Rect2(0.5, 0.5, PORTRAIT_RECT.size.x - 1.0, PORTRAIT_RECT.size.y - 1.0), BRONZE, false, 1.0)


func _clear_texture() -> void:
	if _texture_rect != null:
		_texture_rect.texture = null
	_texture = null


func _refuse(reason: String) -> bool:
	visible = false
	_applied = false
	_last_signature = ""
	_clear_texture()
	_metadata.clear()
	_metadata_path = ""
	status = "refused"
	refusal_reason = reason
	return false


func _validate_and_load(metadata_path: String) -> bool:
	_metadata.clear()
	_last_overlaps.clear()
	if metadata_path.is_empty():
		return _refuse("metadata-path-empty")
	if not FileAccess.file_exists(metadata_path):
		return _refuse("metadata-missing: " + metadata_path)
	var file := FileAccess.open(metadata_path, FileAccess.READ)
	if file == null:
		return _refuse("metadata-unreadable: " + metadata_path)
	var text := file.get_as_text()
	file.close()
	var parser := JSON.new()
	var parse_error := parser.parse(text)
	if parse_error != OK:
		return _refuse("metadata-json-malformed: %s" % parser.get_error_message())
	var parsed: Variant = parser.data
	if not (parsed is Dictionary):
		return _refuse("metadata-not-an-object")
	var meta: Dictionary = parsed
	if not _safe_types(meta):
		return _refuse("metadata-field-types")

	if String(meta.get("schema", "")) != SCHEMA_ID:
		return _refuse("metadata-schema-mismatch")
	if String(meta.get("content_id", "")) != CONTENT_ID:
		return _refuse("metadata-content-id-mismatch")

	var source_value: Variant = meta.get("source")
	if not (source_value is Dictionary):
		return _refuse("metadata-source-missing")
	var source: Dictionary = source_value
	if String(source.get("sha256", "")).to_lower() != SOURCE_SHA256:
		return _refuse("metadata-source-sha256-mismatch")
	if _as_int(source.get("width")) != SOURCE_WIDTH or _as_int(source.get("height")) != SOURCE_HEIGHT:
		return _refuse("metadata-source-dimensions-mismatch")

	var crop_value: Variant = meta.get("crop")
	if not (crop_value is Dictionary):
		return _refuse("metadata-crop-missing")
	var crop: Dictionary = crop_value
	if _as_int(crop.get("left")) != CROP_LEFT or _as_int(crop.get("top")) != CROP_TOP:
		return _refuse("metadata-crop-origin-mismatch")
	if _as_int(crop.get("right")) != CROP_RIGHT or _as_int(crop.get("bottom")) != CROP_BOTTOM:
		return _refuse("metadata-crop-extent-mismatch")
	if _as_int(crop.get("width")) != CROP_WIDTH or _as_int(crop.get("height")) != CROP_HEIGHT:
		return _refuse("metadata-crop-dimensions-mismatch")
	if String(crop.get("method", "")) != "exact-pixel-rectangle-slice":
		return _refuse("metadata-crop-method-not-exact")
	if crop.get("resampled", true) != false or crop.get("repainted", true) != false:
		return _refuse("metadata-crop-resample-or-repaint-claim")
	if crop.get("ai_generated", true) != false or crop.get("background_removed", true) != false:
		return _refuse("metadata-crop-ai-or-background-claim")
	if crop.get("invented_pixels", true) != false:
		return _refuse("metadata-crop-invented-pixels-claim")

	var display_value: Variant = meta.get("display")
	if not (display_value is Dictionary):
		return _refuse("metadata-display-missing")
	var display: Dictionary = display_value
	if String(display.get("content_id", "")) != CONTENT_ID:
		return _refuse("metadata-display-content-id-mismatch")
	if String(display.get("appearance_required", "")) != REQUIRED_APPEARANCE:
		return _refuse("metadata-appearance-contract-mismatch")
	if String(display.get("member_id_required", "")) != REQUIRED_MEMBER_ID:
		return _refuse("metadata-member-contract-mismatch")
	if String(display.get("stretch_mode", "")) != "KEEP_ASPECT_CENTERED":
		return _refuse("metadata-stretch-contract-mismatch")
	var rect_value: Variant = display.get("rect")
	if not (rect_value is Dictionary):
		return _refuse("metadata-display-rect-missing")
	var rect: Dictionary = rect_value
	if (_as_int(rect.get("x")) != int(PORTRAIT_RECT.position.x)
			or _as_int(rect.get("y")) != int(PORTRAIT_RECT.position.y)
			or _as_int(rect.get("width")) != int(PORTRAIT_RECT.size.x)
			or _as_int(rect.get("height")) != int(PORTRAIT_RECT.size.y)):
		return _refuse("metadata-display-rect-mismatch")

	var provenance_value: Variant = meta.get("provenance")
	if not (provenance_value is Dictionary):
		return _refuse("metadata-provenance-missing")
	var provenance: Dictionary = provenance_value
	if provenance.get("original_source_ai_generated") != true or provenance.get("new_generative_processing") != false:
		return _refuse("metadata-provenance-original-ai-scope")
	if String(provenance.get("source_status", "")) != "unapproved-concept-source":
		return _refuse("metadata-provenance-source-status-mismatch")
	if provenance.get("unapproved", false) != true:
		return _refuse("metadata-provenance-not-unapproved")
	if String(provenance.get("approval", "")) != "none":
		return _refuse("metadata-provenance-approval-not-none")
	if provenance.get("human_artist", true) != false:
		return _refuse("metadata-provenance-human-artist-claim")
	if provenance.get("accepted_character_canon", true) != false:
		return _refuse("metadata-provenance-canon-claim")
	if provenance.get("approved_static", true) != false:
		return _refuse("metadata-provenance-approved-static-claim")
	if provenance.get("full_sprite_approved", true) != false:
		return _refuse("metadata-provenance-full-sprite-claim")
	if provenance.get("semantic_anatomy_claims", true) != false:
		return _refuse("metadata-provenance-anatomy-claim")
	if provenance.get("handpainted_claims", true) != false:
		return _refuse("metadata-provenance-handpaint-claim")

	var expected_sha := String(display.get("image_sha256", "")).to_lower()
	if not _is_sha256_hex(expected_sha) or expected_sha != "481182891a0bf9b110a2ba05ca69c9c902b9d208255cf76bddd1aeb6c15868f6":
		return _refuse("metadata-image-sha256-malformed")
	var image_rel := String(display.get("image_path", ""))
	if image_rel.is_empty() or image_rel != image_rel.get_file() or image_rel.contains("..") or image_rel.contains(":") or image_rel.contains("\\") or image_rel.contains("/"):
		return _refuse("metadata-image-path-empty")
	var image_path := image_rel
	if not image_path.is_absolute_path():
		image_path = metadata_path.get_base_dir().path_join(image_rel)
	if not FileAccess.file_exists(image_path):
		return _refuse("image-png-missing: " + image_path)
	var png_bytes := FileAccess.get_file_as_bytes(image_path)
	if png_bytes.is_empty():
		return _refuse("image-png-unreadable: " + image_path)
	var actual_sha := _sha256_hex(png_bytes)
	if actual_sha != expected_sha:
		return _refuse("image-png-sha256-mismatch")
	var image := Image.new()
	var load_error := image.load_png_from_buffer(png_bytes)
	if load_error != OK:
		return _refuse("image-png-decode-failed: %d" % load_error)
	if image.is_empty():
		return _refuse("image-png-empty")
	if image.get_width() != CROP_WIDTH or image.get_height() != CROP_HEIGHT:
		return _refuse("image-png-dimensions-mismatch")
	if (_as_int(display.get("image_width")) != CROP_WIDTH
			or _as_int(display.get("image_height")) != CROP_HEIGHT):
		return _refuse("metadata-image-dimensions-mismatch")

	# All checks passed; only now replace the texture and metadata.
	_texture = ImageTexture.create_from_image(image)
	_metadata = meta
	return true


func _find_visible_overlaps() -> Array[String]:
	var result: Array[String] = []
	if _host == null or not is_inside_tree():
		return result
	var target := get_global_rect()
	_collect_overlaps(_host, target, result)
	return result


func _collect_overlaps(node: Node, target: Rect2, result: Array[String]) -> void:
	for child in node.get_children():
		if child == self:
			continue
		if _overlay != null and (child == _overlay or _overlay.is_ancestor_of(child)):
			continue
		if child is Control:
			var control := child as Control
			if control.is_visible_in_tree() and _is_bounds_candidate(control):
				var bounds := _control_bounds(control)
				if bounds.size.x > 0.0 and bounds.size.y > 0.0 and bounds.intersects(target):
					result.append(String(control.get_path()))
		if child.get_child_count() > 0:
			_collect_overlaps(child, target, result)


func _is_bounds_candidate(control: Control) -> bool:
	# Only actual text and interactive controls obstruct. Passive decoration is ignored.
	if control is Label:
		return not control.text.is_empty()
	if control is BaseButton or control is LineEdit or control is TextEdit or control is RichTextLabel:
		return true
	return control.mouse_filter != Control.MOUSE_FILTER_IGNORE and not (control is ColorRect or control is TextureRect or control is NinePatchRect)


func _control_bounds(control: Control) -> Rect2:
	var bounds := control.get_global_rect()
	var minimum := control.get_combined_minimum_size()
	bounds.size = Vector2(maxf(bounds.size.x, minimum.x), maxf(bounds.size.y, minimum.y))
	return bounds


func _sha256_hex(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	if context.start(HashingContext.HASH_SHA256) != OK:
		return ""
	context.update(bytes)
	return context.finish().hex_encode().to_lower()


func _is_sha256_hex(value: String) -> bool:
	if value.length() != 64:
		return false
	for index in value.length():
		if not "0123456789abcdef".contains(value[index]):
			return false
	return true


func _as_int(value: Variant) -> int:
	if value is int:
		return int(value)
	if value is float and is_finite(float(value)) and float(value) == roundf(float(value)):
		return int(roundf(float(value)))
	return -2147483648


func _safe_types(meta: Dictionary) -> bool:
	# Reject wrong types before any typed String conversion or numeric coercion.
	for key in ["schema", "content_id"]:
		if not meta.get(key) is String: return false
	for section in ["source", "crop", "display", "provenance"]:
		if not meta.get(section) is Dictionary: return false
	var fields := {"source": ["sha256"], "crop": ["method"], "display": ["content_id", "appearance_required", "member_id_required", "stretch_mode", "image_sha256", "image_path"], "provenance": ["source_status", "approval"]}
	for section in fields:
		for key in fields[section]:
			if not meta[section].get(key) is String: return false
	for key in ["resampled", "repainted", "ai_generated", "background_removed", "invented_pixels"]:
		if not meta.crop.get(key) is bool: return false
	for key in ["unapproved", "human_artist", "accepted_character_canon", "approved_static", "full_sprite_approved", "semantic_anatomy_claims", "handpainted_claims", "original_source_ai_generated", "new_generative_processing"]:
		if not meta.provenance.get(key) is bool: return false
	return true
