class_name CharacterUiPortraitsPilot
extends Control

## One generic, default-off helper for the fixed known MVP five-variant kit:
## explicit whole-head nearest downsample to28px in a32px bronze/teal party frame, and the
## same committed full display crops shown with keep-aspect nearest filtering in
## dialogue.  The constructor performs no file/texture/metadata I/O; every read
## is counted and only happens after an explicit enabled apply call.
##
## It never writes AppState, never changes dialogue strings, never moves/hides/
## relabels original text, never reconnects button callbacks and never falls back
## to another character.  Unknown members, unknown speakers, trace/system text
## and malformed packages hide the affected visual and keep the original UI.

const PILOT_FLAG := "--character-ui-portraits-pilot"
const KIT_MANIFEST := "res://assets/portraits/ui-kit-v02/rpg-2-star-ocean-the-second_character-ui-kit_manifest_v02_20261020-001030-9be4a34f.json"
const SCHEMA_ID := "ds-character-ui/portrait-kit/v1"
const ICON_FACE_SIZE := 28
const ICON_TRANSFORM := "whole-head-roi-nearest-neighbor-downscale-to-28x28"
const ICON_FRAME_SIZE := 32
const PARTY_BUTTON_Y := 45.0
const PARTY_BUTTON_HEIGHT := 34.0
const DIALOGUE_PANEL_RECT := Rect2(8, 28, 624, 304)
const DIALOGUE_TITLE_POS := Vector2(274, 42)
const DIALOGUE_TITLE_SIZE := Vector2(344, 26)
const DIALOGUE_TEXT_RECT := Rect2(274, 76, 344, 186)
const DIALOGUE_INVITE_RECT := Rect2(274, 278, 160, 36)
const DIALOGUE_LATER_RECT := Rect2(446, 278, 160, 36)
const DIALOGUE_PORTRAIT_POS := Vector2(12, 14)
const DIALOGUE_PORTRAIT_SIZE := Vector2(238, 272)
const DIALOGUE_FRAME_POS := Vector2(9, 11)
const DIALOGUE_FRAME_SIZE := Vector2(244, 278)
const DIALOGUE_TRANSFORM := "nearest-neighbor-keep-aspect-centered-downscale-only"
const EXPECTED_SUBJECTS := ["protagonist-female", "protagonist-male", "liang-xu", "zhao-ling", "ji-cheng"]
const COMPANION_IDS := ["liang-xu", "zhao-ling", "ji-cheng"]
const BRONZE := Color("#b08d57")
const TEAL := Color("#69bbce")
const NAVY := Color(0.070588, 0.141176, 0.192157, 1.0)


var status := "off"
var refusal_reason := ""
var io_read_count := 0
var last_text_fit := false

var _installed_party := false
var _installed_dialogue := false
var _manifest_loaded := false
var _manifest_error := ""
var _manifest: Dictionary = {}
var _variants: Dictionary = {}
var _icon_textures: Dictionary = {}
var _portrait_textures: Dictionary = {}
var _party_buttons: Array[Button] = []
var _party_original: Array[Dictionary] = []
var _party_subjects: Array[String] = []
var _party_applied := false
var _dialogue_overlay: Control = null
var _dialogue_panel: Control = null
var _dialogue_title: Label = null
var _dialogue_text: Label = null
var _dialogue_invite: Button = null
var _dialogue_later: Button = null
var _dialogue_original: Dictionary = {}
var _dialogue_portrait: TextureRect = null
var _dialogue_frame: Control = null
var _dialogue_subject := ""
var _dialogue_applied := false


func _init() -> void:
	name = "CharacterUiPortraitsPilot"
	visible = false
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	set_process(false)


static func pilot_requested(user_args: PackedStringArray) -> bool:
	return user_args.has(PILOT_FLAG)


## Stores button references and their original geometry.  No file or texture I/O.
func install_party(host: Control, buttons: Array) -> bool:
	if host == null:
		return _refuse("party-install-needs-host")
	if _installed_party:
		return true
	if get_parent() != host:
		if get_parent() != null:
			get_parent().remove_child(self)
		host.add_child(self)
	_party_buttons.clear()
	_party_original.clear()
	for candidate in buttons:
		if not (candidate is Button):
			return _refuse("party-install-needs-buttons")
		var button := candidate as Button
		_party_buttons.append(button)
		_party_original.append({
			"position": button.position,
			"size": button.size,
			"texture_filter": button.texture_filter,
			"clip_text": button.clip_text,
			"icon": button.icon,
			"expand_icon": button.expand_icon,
			"icon_alignment": button.icon_alignment,
		})
	_installed_party = true
	status = "installed-party-off"
	return true


## Stores dialogue controls and their original geometry.  No file/texture I/O.
func install_dialogue(
		host: Node,
		overlay: Control,
		panel: Control,
		title: Label,
		text: Label,
		invite: Button,
		later: Button) -> bool:
	if host == null or overlay == null or panel == null or title == null or text == null or invite == null or later == null:
		return _refuse("dialogue-install-needs-controls")
	if panel.get_parent() != overlay or title.get_parent() != overlay or text.get_parent() != overlay:
		return _refuse("dialogue-controls-not-children-of-overlay")
	if invite.get_parent() != overlay or later.get_parent() != overlay:
		return _refuse("dialogue-buttons-not-children-of-overlay")
	if _installed_dialogue:
		return true
	if get_parent() != host:
		if get_parent() != null:
			get_parent().remove_child(self)
		host.add_child(self)
	_dialogue_overlay = overlay
	_dialogue_panel = panel
	_dialogue_title = title
	_dialogue_text = text
	_dialogue_invite = invite
	_dialogue_later = later
	_dialogue_original = {
		"panel": Rect2(panel.position, panel.size),
		"title": Rect2(title.position, title.size),
		"text": Rect2(text.position, text.size),
		"invite": Rect2(invite.position, invite.size),
		"later": Rect2(later.position, later.size),
	}
	_installed_dialogue = true
	status = "installed-dialogue-off"
	return true


## Applies exactly the actual active-party ids plus the actual hero appearance.
## Unknown members keep a readable name but get no icon; no other character is
## substituted.  Returns true only when every actual visible member resolved.
func apply_party(party_ids: Array, appearance: String, enabled: bool) -> bool:
	if not enabled:
		_revert_party_visuals()
		status = "party-off"
		refusal_reason = ""
		return false
	if not _installed_party:
		return _refuse("party-helper-not-installed")
	if not (party_ids is Array):
		return _refuse("party-ids-not-array")
	if not _ensure_manifest():
		_revert_party_visuals()
		return _refuse("package-invalid: " + _manifest_error)
	var resolved: Array[String] = []
	var unknown := ""
	for index in _party_buttons.size():
		var button := _party_buttons[index]
		button.icon = null
		if index >= party_ids.size():
			continue
		var value: Variant = party_ids[index]
		if not (value is String):
			unknown = "non-string-member-id"
			continue
		var member_id := String(value)
		var subject := _subject_for_member(member_id, appearance)
		if subject.is_empty():
			unknown = member_id
			continue
		var texture: Texture2D = _icon_textures.get(subject) as Texture2D
		if texture == null:
			unknown = subject
			continue
		button.icon = texture
		button.expand_icon = false
		button.icon_alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.clip_text = false
		button.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		button.position.y = PARTY_BUTTON_Y
		button.size.y = PARTY_BUTTON_HEIGHT
		resolved.append(subject)
	_party_subjects = resolved
	_party_applied = true
	status = "party-shown:%d" % resolved.size()
	if not unknown.is_empty():
		refusal_reason = "unknown-member-no-icon: " + unknown
		return false
	refusal_reason = ""
	return resolved.size() == party_ids.size()


## Shows only a known recruit/assist speaker.  Trace/system/unknown speakers hide
## the portrait while preserving the same readable text column and all strings.
func apply_dialogue(mode: String, speaker_id: String, enabled: bool) -> bool:
	if not enabled:
		_revert_dialogue_visuals()
		status = "dialogue-off"
		refusal_reason = ""
		return false
	if not _installed_dialogue:
		return _refuse("dialogue-helper-not-installed")
	if not _ensure_manifest():
		_revert_dialogue_visuals()
		return _refuse("package-invalid: " + _manifest_error)
	_apply_dialogue_layout()
	if not _dialogue_text_fits():
		_revert_dialogue_visuals()
		return _refuse("dialogue-text-overflow")
	var subject := ""
	if (mode == "recruit" or mode == "assist") and speaker_id != "hero" and _variants.has(speaker_id):
		subject = speaker_id
	_dialogue_subject = subject
	if subject.is_empty():
		_hide_dialogue_portrait("dialogue-hidden:" + mode)
		last_text_fit = _dialogue_text_fits()
		return false
	if not _dialogue_overlay.visible:
		_hide_dialogue_portrait("dialogue-overlay-hidden")
		last_text_fit = _dialogue_text_fits()
		return false
	var texture: Texture2D = _portrait_textures.get(subject) as Texture2D
	if texture == null:
		_hide_dialogue_portrait("portrait-texture-missing:" + subject)
		last_text_fit = _dialogue_text_fits()
		return false
	_ensure_dialogue_visuals()
	_dialogue_portrait.texture = texture
	_dialogue_portrait.visible = true
	_dialogue_frame.visible = true
	_dialogue_applied = true
	last_text_fit = _dialogue_text_fits()
	status = "dialogue-shown:" + subject
	refusal_reason = ""
	return true


func hide_dialogue() -> void:
	if not _installed_dialogue:
		return
	_hide_dialogue_portrait("dialogue-hidden:closed")


func revert() -> void:
	_revert_party_visuals()
	_revert_dialogue_visuals()
	_clear_package_cache()
	status = "reverted"
	refusal_reason = ""


func _clear_package_cache() -> void:
	_icon_textures.clear()
	_portrait_textures.clear()
	_variants.clear()
	_manifest.clear()
	_manifest_loaded = false
	_manifest_error = ""


func is_showing_party() -> bool:
	for button in _party_buttons:
		if button.icon != null:
			return true
	return false


func is_showing_dialogue() -> bool:
	return _dialogue_portrait != null and _dialogue_portrait.visible


func get_status() -> String:
	return status


func get_refusal_reason() -> String:
	return refusal_reason


func get_party_subjects() -> Array[String]:
	var copy: Array[String] = []
	copy.assign(_party_subjects)
	return copy


func get_dialogue_subject() -> String:
	return _dialogue_subject


func get_io_read_count() -> int:
	return io_read_count


func get_text_fit() -> bool:
	return last_text_fit


func get_debug_state() -> Dictionary:
	return {
		"status": status,
		"refusal_reason": refusal_reason,
		"installed_party": _installed_party,
		"installed_dialogue": _installed_dialogue,
		"manifest_loaded": _manifest_loaded,
		"manifest_error": _manifest_error,
		"io_read_count": io_read_count,
		"party_subjects": _party_subjects.duplicate(),
		"dialogue_subject": _dialogue_subject,
		"dialogue_visible": is_showing_dialogue(),
		"text_fit": last_text_fit,
		"panel_rect": Rect2(_dialogue_panel.position, _dialogue_panel.size) if _dialogue_panel != null else Rect2(),
		"text_rect": Rect2(_dialogue_text.position, _dialogue_text.size) if _dialogue_text != null else Rect2(),
	}


func _subject_for_member(member_id: String, appearance: String) -> String:
	if member_id == "hero":
		if appearance == "male":
			return "protagonist-male"
		if appearance == "female":
			return "protagonist-female"
		return ""
	if COMPANION_IDS.has(member_id):
		return member_id
	return ""


func _ensure_manifest() -> bool:
	if _manifest_loaded:
		return true
	if not _manifest_error.is_empty():
		return false
	_manifest_error = _validate_and_load_manifest()
	if not _manifest_error.is_empty():
		_icon_textures.clear()
		_portrait_textures.clear()
		_variants.clear()
		_manifest.clear()
		return false
	_manifest_loaded = true
	return true


func _validate_and_load_manifest() -> String:
	io_read_count += 1
	if not FileAccess.file_exists(KIT_MANIFEST):
		return "kit-manifest-missing"
	var file := FileAccess.open(KIT_MANIFEST, FileAccess.READ)
	if file == null:
		return "kit-manifest-unreadable"
	var text := file.get_as_text()
	file.close()
	var parser := JSON.new()
	if parser.parse(text) != OK:
		return "kit-manifest-json-malformed"
	var parsed: Variant = parser.data
	if not (parsed is Dictionary):
		return "kit-manifest-not-object"
	var meta: Dictionary = parsed
	if not _safe_manifest_types(meta):
		return "kit-manifest-field-types"
	if String(meta.get("schema", "")) != SCHEMA_ID:
		return "kit-manifest-schema-mismatch"
	if String(meta.get("content_id", "")) != "content.ui-visual.character-portraits":
		return "kit-manifest-content-id-mismatch"
	if String(meta.get("pilot_flag", "")) != PILOT_FLAG:
		return "kit-manifest-flag-mismatch"
	var provenance: Dictionary = meta.get("provenance")
	if String(provenance.get("source_status", "")) != "unapproved-derived-display-crops":
		return "kit-manifest-source-status-mismatch"
	if provenance.get("original_source_ai_generated") != true or provenance.get("new_generative_processing") != false:
		return "kit-manifest-generation-claim-mismatch"
	if provenance.get("approved_static") != false or provenance.get("full_sprite_approved") != false or provenance.get("full_display_portrait_approved") != false:
		return "kit-manifest-approval-claim-mismatch"
	if provenance.get("accepted_character_canon") != false or provenance.get("human_artist") != false or String(provenance.get("approval", "")) != "none":
		return "kit-manifest-provenance-mismatch"
	var variants_value: Variant = meta.get("variants")
	if not (variants_value is Dictionary):
		return "kit-manifest-variants-missing"
	var variants: Dictionary = variants_value
	if variants.size() != EXPECTED_SUBJECTS.size():
		return "kit-manifest-variant-count"
	for subject in EXPECTED_SUBJECTS:
		if not variants.has(subject):
			return "kit-manifest-missing-variant: " + subject
		if not (variants[subject] is Dictionary):
			return "kit-manifest-variant-not-object: " + subject
		var variant: Dictionary = variants[subject]
		if not (variant.get("party_icon") is Dictionary) or not (variant.get("dialogue") is Dictionary):
			return "kit-manifest-variant-sections: " + subject
		var icon: Dictionary = variant["party_icon"]
		var dialogue: Dictionary = variant["dialogue"]
		if _as_int(icon.get("face_size")) != ICON_FACE_SIZE or _as_int(icon.get("frame_size")) != ICON_FRAME_SIZE:
			return "kit-manifest-icon-size: " + subject
		var roi: Dictionary = icon.get("roi")
		if _as_int(roi.get("width")) <= ICON_FACE_SIZE or _as_int(roi.get("height")) != _as_int(roi.get("width")):
			return "kit-manifest-icon-roi: " + subject
		if icon.get("transform") != ICON_TRANSFORM or icon.get("resampled") != true:
			return "kit-manifest-icon-transform: " + subject
		if _as_int(roi.get("left")) < 0 or _as_int(roi.get("top")) < 0:
			return "kit-manifest-icon-roi-negative: " + subject
		if String(dialogue.get("transform", "")) != DIALOGUE_TRANSFORM:
			return "kit-manifest-dialogue-transform: " + subject
		if dialogue.get("upscale_allowed") != false or dialogue.get("keep_aspect") != true:
			return "kit-manifest-dialogue-policy: " + subject
		var width := _as_int(dialogue.get("width"))
		var height := _as_int(dialogue.get("height"))
		var display_rect: Dictionary = dialogue.get("display_rect")
		if _as_int(roi.get("right")) != _as_int(roi.get("left")) + _as_int(roi.get("width")) or _as_int(roi.get("bottom")) != _as_int(roi.get("top")) + _as_int(roi.get("height")):
			return "kit-manifest-icon-roi-extents: " + subject
		if _as_int(roi.get("right")) > width or _as_int(roi.get("bottom")) > height:
			return "kit-manifest-icon-roi-bounds: " + subject
		if width <= 0 or height <= 0:
			return "kit-manifest-dialogue-size: " + subject
		if _as_int(display_rect.get("width")) > width or _as_int(display_rect.get("height")) > height:
			return "kit-manifest-dialogue-upscale: " + subject
		if String(dialogue.get("png", "")).is_empty() or String(icon.get("png", "")).is_empty():
			return "kit-manifest-path-empty: " + subject
		if not _is_sha256(String(icon.get("png_sha256", ""))) or not _is_sha256(String(dialogue.get("png_sha256", ""))):
			return "kit-manifest-sha-format: " + subject
		var icon_image := _load_image(String(icon["png"]), String(icon["png_sha256"]), Vector2i(ICON_FACE_SIZE, ICON_FACE_SIZE))
		if icon_image == null:
			return "icon-invalid: " + subject
		_icon_textures[subject] = ImageTexture.create_from_image(_compose_icon(icon_image))
		var portrait_image := _load_image(String(dialogue["png"]), String(dialogue["png_sha256"]), Vector2i(width, height))
		if portrait_image == null:
			return "portrait-invalid: " + subject
		_portrait_textures[subject] = ImageTexture.create_from_image(portrait_image)
		_variants[subject] = variant
	return ""


func _load_image(path: String, expected_sha: String, expected_size: Vector2i) -> Image:
	if not path.begins_with("res://") or path.contains("..") or path.contains("\\"):
		return null
	io_read_count += 1
	if not FileAccess.file_exists(path):
		return null
	var bytes := FileAccess.get_file_as_bytes(path)
	if bytes.is_empty() or _sha256_hex(bytes) != expected_sha:
		return null
	var image := Image.new()
	if image.load_png_from_buffer(bytes) != OK or image.is_empty():
		return null
	if image.get_size() != expected_size:
		return null
	image.convert(Image.FORMAT_RGBA8)
	return image


func _compose_icon(face: Image) -> Image:
	var icon := Image.create(ICON_FRAME_SIZE, ICON_FRAME_SIZE, false, Image.FORMAT_RGBA8)
	icon.fill(Color(0, 0, 0, 0))
	for index in ICON_FRAME_SIZE:
		icon.set_pixel(index, 0, BRONZE)
		icon.set_pixel(index, ICON_FRAME_SIZE - 1, BRONZE)
		icon.set_pixel(0, index, BRONZE)
		icon.set_pixel(ICON_FRAME_SIZE - 1, index, BRONZE)
	for index in range(2, ICON_FRAME_SIZE - 1):
		icon.set_pixel(index, 1, TEAL)
		icon.set_pixel(index, ICON_FRAME_SIZE - 2, TEAL)
		icon.set_pixel(1, index, TEAL)
		icon.set_pixel(ICON_FRAME_SIZE - 2, index, TEAL)
	icon.blit_rect(face, Rect2i(0, 0, ICON_FACE_SIZE, ICON_FACE_SIZE), Vector2i(2, 2))
	return icon


func _ensure_dialogue_visuals() -> void:
	if _dialogue_frame == null:
		var bronze := ColorRect.new()
		bronze.name = "CharacterUiPortraitFrame"
		bronze.position = DIALOGUE_FRAME_POS
		bronze.size = DIALOGUE_FRAME_SIZE
		bronze.color = BRONZE
		bronze.mouse_filter = Control.MOUSE_FILTER_IGNORE
		bronze.focus_mode = Control.FOCUS_NONE
		_dialogue_frame = bronze
		_dialogue_panel.add_child(_dialogue_frame)
		var teal := ColorRect.new()
		teal.name = "TealInset"
		teal.position = Vector2(1, 1)
		teal.size = DIALOGUE_FRAME_SIZE - Vector2(2, 2)
		teal.color = TEAL
		teal.mouse_filter = Control.MOUSE_FILTER_IGNORE
		teal.focus_mode = Control.FOCUS_NONE
		_dialogue_frame.add_child(teal)
		var navy := ColorRect.new()
		navy.name = "NavyInset"
		navy.position = Vector2(1, 1)
		navy.size = DIALOGUE_FRAME_SIZE - Vector2(4, 4)
		navy.color = NAVY
		navy.mouse_filter = Control.MOUSE_FILTER_IGNORE
		navy.focus_mode = Control.FOCUS_NONE
		teal.add_child(navy)
	if _dialogue_portrait == null:
		_dialogue_portrait = TextureRect.new()
		_dialogue_portrait.name = "CharacterUiPortrait"
		_dialogue_portrait.position = DIALOGUE_PORTRAIT_POS
		_dialogue_portrait.size = DIALOGUE_PORTRAIT_SIZE
		_dialogue_portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		_dialogue_portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		_dialogue_portrait.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		_dialogue_portrait.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_dialogue_portrait.focus_mode = Control.FOCUS_NONE
		_dialogue_panel.add_child(_dialogue_portrait)
	_dialogue_frame.visible = false
	_dialogue_portrait.visible = false


func _apply_dialogue_layout() -> void:
	if _dialogue_panel == null:
		return
	_dialogue_panel.position = DIALOGUE_PANEL_RECT.position
	_dialogue_panel.size = DIALOGUE_PANEL_RECT.size
	_dialogue_title.position = DIALOGUE_TITLE_POS
	_dialogue_title.size = DIALOGUE_TITLE_SIZE
	_dialogue_text.position = DIALOGUE_TEXT_RECT.position
	_dialogue_text.size = DIALOGUE_TEXT_RECT.size
	_dialogue_invite.position = DIALOGUE_INVITE_RECT.position
	_dialogue_invite.size = DIALOGUE_INVITE_RECT.size
	_dialogue_later.position = DIALOGUE_LATER_RECT.position
	_dialogue_later.size = DIALOGUE_LATER_RECT.size


func _hide_dialogue_portrait(reason: String) -> void:
	if _dialogue_portrait != null:
		_dialogue_portrait.texture = null
		_dialogue_portrait.visible = false
	if _dialogue_frame != null:
		_dialogue_frame.visible = false
	_dialogue_applied = false
	status = "hidden"
	refusal_reason = reason


func _dialogue_text_fits() -> bool:
	if _dialogue_text == null:
		return false
	var font := _dialogue_text.get_theme_font("font")
	if font == null:
		return false
	var font_size := _dialogue_text.get_theme_font_size("font_size")
	var measured := font.get_multiline_string_size(
		_dialogue_text.text, HORIZONTAL_ALIGNMENT_LEFT, DIALOGUE_TEXT_RECT.size.x, font_size)
	return measured.y <= DIALOGUE_TEXT_RECT.size.y + 0.5


func _revert_party_visuals() -> void:
	for index in _party_buttons.size():
		var button := _party_buttons[index]
		button.icon = null
		if index < _party_original.size():
			var original: Dictionary = _party_original[index]
			button.position = original["position"]
			button.size = original["size"]
			button.texture_filter = original["texture_filter"]
			button.clip_text = original["clip_text"]
			button.icon = original["icon"]
			button.expand_icon = original["expand_icon"]
			button.icon_alignment = original["icon_alignment"]
	_party_applied = false
	_party_subjects.clear()


func _revert_dialogue_visuals() -> void:
	if _dialogue_portrait != null:
		_dialogue_portrait.texture = null
		_dialogue_portrait.free()
		_dialogue_portrait = null
	if _dialogue_frame != null:
		_dialogue_frame.free()
		_dialogue_frame = null
	if _dialogue_panel != null and not _dialogue_original.is_empty():
		var panel_rect: Rect2 = _dialogue_original["panel"]
		_dialogue_panel.position = panel_rect.position
		_dialogue_panel.size = panel_rect.size
		var title_rect: Rect2 = _dialogue_original["title"]
		_dialogue_title.position = title_rect.position
		_dialogue_title.size = title_rect.size
		var text_rect: Rect2 = _dialogue_original["text"]
		_dialogue_text.position = text_rect.position
		_dialogue_text.size = text_rect.size
		var invite_rect: Rect2 = _dialogue_original["invite"]
		_dialogue_invite.position = invite_rect.position
		_dialogue_invite.size = invite_rect.size
		var later_rect: Rect2 = _dialogue_original["later"]
		_dialogue_later.position = later_rect.position
		_dialogue_later.size = later_rect.size
	_dialogue_applied = false
	_dialogue_subject = ""
	last_text_fit = false


func _refuse(reason: String) -> bool:
	status = "refused"
	refusal_reason = reason
	return false


func _safe_manifest_types(meta: Dictionary) -> bool:
	for key in ["schema", "content_id", "pilot_flag"]:
		if not meta.get(key) is String:
			return false
	if not meta.get("provenance") is Dictionary or not meta.get("variants") is Dictionary:
		return false
	var provenance: Dictionary = meta["provenance"]
	for key in ["source_status", "approval"]:
		if not provenance.get(key) is String:
			return false
	for key in ["original_source_ai_generated", "new_generative_processing", "approved_static", "full_sprite_approved", "full_display_portrait_approved", "accepted_character_canon", "human_artist"]:
		if not provenance.get(key) is bool:
			return false
	for subject in meta["variants"]:
		var variant = meta["variants"][subject]
		if not subject is String or not variant is Dictionary:
			return false
		if not variant.get("party_icon") is Dictionary or not variant.get("dialogue") is Dictionary:
			return false
		var icon: Dictionary = variant["party_icon"]
		var dialogue: Dictionary = variant["dialogue"]
		if not icon.get("transform") is String or not icon.get("resampled") is bool:
			return false
		if not icon.get("roi") is Dictionary or not dialogue.get("display_rect") is Dictionary:
			return false
		for section in [icon, dialogue]:
			for key in ["png", "png_sha256"]:
				if not section.get(key) is String:
					return false
		if not dialogue.get("transform") is String or not dialogue.get("upscale_allowed") is bool or not dialogue.get("keep_aspect") is bool:
			return false
		for key in ["face_size", "frame_size"]:
			if _as_int(icon.get(key)) <= 0:
				return false
		for key in ["width", "height"]:
			if _as_int(dialogue.get(key)) <= 0 or _as_int(dialogue["display_rect"].get(key)) <= 0:
				return false
		for key in ["left", "top", "right", "bottom", "width", "height"]:
			if _as_int(icon["roi"].get(key)) < 0:
				return false
	return true


func _sha256_hex(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	if context.start(HashingContext.HASH_SHA256) != OK:
		return ""
	context.update(bytes)
	return context.finish().hex_encode().to_lower()


func _is_sha256(value: String) -> bool:
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
