extends RefCounted
# Test-only presentation module for the four encounter feedback effects.
# Reads the authored frame PNGs at runtime; no timers, RNG, input or game state.
# ASSET_* name the timing-v02 build that stores native PXO durations at fps 12.

const DURATIONS: Dictionary = {
	"encounter": 0.50,
	"victory": 0.80,
	"defeat": 0.65,
	"recovery": 0.60,
}
const MAX_EVENTS: int = 8
const FRAME_COUNT: int = 8
const CELL_SIZE: Vector2 = Vector2(128.0, 80.0)
const PIVOT: Vector2 = Vector2(64.0, 48.0)
const ASSET_PREFIX: String = "rpg-2-star-ocean-the-second_encounter_"
const ASSET_VARIANT: String = "timing-v02_20261019-001519-69291ffd"
const MANIFEST_NAME: String = ASSET_PREFIX + "asset-manifest_" + ASSET_VARIANT + ".json"

var events: Array[Dictionary] = []
var emitted: int = 0
var _asset_dir: String = ""
var _frames_by_kind: Dictionary = {}

func _init(asset_dir: String) -> void:
	_asset_dir = asset_dir
	_load_assets()

func _load_assets() -> void:
	var manifest_path: String = _asset_dir.path_join(MANIFEST_NAME)
	if not FileAccess.file_exists(manifest_path):
		return
	var manifest_text: String = FileAccess.get_file_as_string(manifest_path)
	var json: JSON = JSON.new()
	var parse_error: Error = json.parse(manifest_text)
	if parse_error != OK:
		return
	var parsed: Variant = json.data
	if typeof(parsed) != TYPE_DICTIONARY:
		return
	var manifest: Dictionary = parsed
	var events_value: Variant = manifest.get("events", {})
	if typeof(events_value) != TYPE_DICTIONARY:
		return
	var event_entries: Dictionary = events_value
	for kind in DURATIONS:
		var textures: Array = []
		var entry_value: Variant = event_entries.get(kind)
		if typeof(entry_value) != TYPE_DICTIONARY:
			_frames_by_kind[kind] = textures
			continue
		var entry: Dictionary = entry_value
		var frame_names_value: Variant = entry.get("frames", [])
		if typeof(frame_names_value) != TYPE_ARRAY:
			_frames_by_kind[kind] = textures
			continue
		var frame_names: Array = frame_names_value
		if frame_names.size() != FRAME_COUNT:
			_frames_by_kind[kind] = textures
			continue
		# Validate every name and path before any image decode, so a partial
		# timeline is skipped whole instead of being drawn or re-timed.
		var frame_paths: Array = []
		var names_valid: bool = true
		for frame_name_value in frame_names:
			if typeof(frame_name_value) != TYPE_STRING:
				names_valid = false
				break
			var frame_name: String = str(frame_name_value)
			if frame_name.is_empty():
				names_valid = false
				break
			var frame_path: String = _asset_dir.path_join(frame_name)
			if not FileAccess.file_exists(frame_path):
				names_valid = false
				break
			frame_paths.append(frame_path)
		if not names_valid or frame_paths.size() != FRAME_COUNT:
			_frames_by_kind[kind] = textures
			continue
		var frames_valid: bool = true
		for frame_path_value in frame_paths:
			var frame_path: String = str(frame_path_value)
			var image: Image = Image.load_from_file(frame_path)
			if image == null or image.is_empty() or image.get_width() != int(CELL_SIZE.x) or image.get_height() != int(CELL_SIZE.y):
				frames_valid = false
				break
			var texture: ImageTexture = ImageTexture.create_from_image(image)
			if texture == null:
				frames_valid = false
				break
			textures.append(texture)
		_frames_by_kind[kind] = textures if frames_valid else []

func emit(kind: String, origin: Vector2, facing: float = 1.0) -> bool:
	if not DURATIONS.has(kind):
		return false
	if not is_finite(origin.x) or not is_finite(origin.y) or not is_finite(facing):
		return false
	var direction: float = -1.0 if facing < 0.0 else 1.0
	if events.size() >= MAX_EVENTS:
		events.pop_front()
	events.append({
		"kind": kind,
		"origin": origin.round(),
		"facing": direction,
		"age": 0.0,
		"duration": float(DURATIONS[kind]),
	})
	emitted += 1
	return true

func advance(delta: float) -> void:
	if not is_finite(delta) or delta < 0.0:
		return
	for index in range(events.size() - 1, -1, -1):
		events[index]["age"] = float(events[index]["age"]) + delta
		if float(events[index]["age"]) >= float(events[index]["duration"]):
			events.remove_at(index)

func draw(canvas: CanvasItem) -> void:
	for event in events:
		if typeof(event) != TYPE_DICTIONARY:
			continue
		var kind: String = str(event.get("kind", ""))
		var frames_value: Variant = _frames_by_kind.get(kind, [])
		if typeof(frames_value) != TYPE_ARRAY:
			continue
		var frames: Array = frames_value
		if frames.is_empty():
			continue
		var age: float = float(event.get("age", 0.0))
		var duration: float = float(event.get("duration", 1.0))
		if duration <= 0.0:
			continue
		var frame_index: int = clampi(int(floor(age / duration * float(FRAME_COUNT))), 0, FRAME_COUNT - 1)
		if frame_index >= frames.size():
			continue
		var texture_value: Variant = frames[frame_index]
		if not (texture_value is Texture2D):
			continue
		var texture: Texture2D = texture_value
		var origin: Vector2 = event.get("origin", Vector2.ZERO)
		var direction: float = -1.0 if float(event.get("facing", 1.0)) < 0.0 else 1.0
		canvas.draw_set_transform(origin.round(), 0.0, Vector2(direction, 1.0))
		canvas.draw_texture(texture, -PIVOT)
		canvas.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	canvas.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
