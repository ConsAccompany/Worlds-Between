extends RefCounted
# Presentation-only common combat VFX layer for content.vfx.common.
# The authored package is loaded only when this loader is explicitly constructed
# with an asset directory.  If the package is absent, malformed, or only partly
# valid, the matching effect keeps the copied transient-layer procedural fallback.
# No timers, random generators, input, game-state references or resource writes.

const DURATIONS: Dictionary = {
	"attack": 0.22,
	"dodge": 0.27,
	"guard": 0.30,
	"hit": 0.20,
	"heal": 0.55,
}
const MAX_EVENTS: int = 24
const FRAME_COUNT: int = 8
const CELL_SIZE: Vector2 = Vector2(64.0, 64.0)
const PIVOT: Vector2 = Vector2(32.0, 32.0)
const NATIVE_FPS: int = 12
const DURATION_EPSILON: float = 0.000001
const ASSET_PREFIX: String = "rpg-2-star-ocean-the-second_common_"
const ASSET_VARIANT: String = "common-v01_20261019-164451-e82135a0"
const MANIFEST_NAME: String = ASSET_PREFIX + "asset-manifest_" + ASSET_VARIANT + ".json"

var events: Array[Dictionary] = []
var emitted: int = 0
var _asset_dir: String = ""
var _frames_by_kind: Dictionary = {}

func _init(asset_dir: String = "") -> void:
	_asset_dir = asset_dir
	for kind in DURATIONS:
		_frames_by_kind[kind] = []
	if not _asset_dir.is_empty():
		_load_assets()

func _matches_pair(value: Variant, expected_x: int, expected_y: int) -> bool:
	if typeof(value) != TYPE_ARRAY:
		return false
	var pair: Array = value
	if pair.size() != 2:
		return false
	for item in pair:
		if typeof(item) != TYPE_INT and typeof(item) != TYPE_FLOAT:
			return false
	return is_equal_approx(float(pair[0]), float(expected_x)) and is_equal_approx(float(pair[1]), float(expected_y))

func _load_assets() -> void:
	var manifest_path: String = _asset_dir.path_join(MANIFEST_NAME)
	if not FileAccess.file_exists(manifest_path):
		return
	var manifest_text: String = FileAccess.get_file_as_string(manifest_path)
	if manifest_text.is_empty():
		return
	var json: JSON = JSON.new()
	if json.parse(manifest_text) != OK:
		return
	var parsed: Variant = json.data
	if typeof(parsed) != TYPE_DICTIONARY:
		return
	var manifest: Dictionary = parsed
	if int(manifest.get("fps", 0)) != NATIVE_FPS:
		return
	if not _matches_pair(manifest.get("cell"), 64, 64):
		return
	if not _matches_pair(manifest.get("pivot"), 32, 32):
		return
	var events_value: Variant = manifest.get("events", {})
	if typeof(events_value) != TYPE_DICTIONARY:
		return
	var event_entries: Dictionary = events_value
	for kind in DURATIONS:
		_load_kind(kind, event_entries)

func _load_kind(kind: String, event_entries: Dictionary) -> void:
	# Invalid/partial kinds stay empty so draw() uses the whole procedural effect;
	# a half-decoded timeline is never installed.
	_frames_by_kind[kind] = []
	var entry_value: Variant = event_entries.get(kind)
	if typeof(entry_value) != TYPE_DICTIONARY:
		return
	var entry: Dictionary = entry_value
	if not _matches_pair(entry.get("cell"), 64, 64):
		return
	if not _matches_pair(entry.get("pivot"), 32, 32):
		return
	if int(entry.get("frameCount", 0)) != FRAME_COUNT:
		return
	var duration_value: Variant = entry.get("durationSeconds")
	if typeof(duration_value) != TYPE_FLOAT and typeof(duration_value) != TYPE_INT:
		return
	if not is_equal_approx(float(duration_value), float(DURATIONS[kind])):
		return
	var native_value: Variant = entry.get("nativeFrameDurations")
	if typeof(native_value) != TYPE_ARRAY:
		return
	var native_durations: Array = native_value
	if native_durations.size() != FRAME_COUNT:
		return
	var native_total: float = 0.0
	for duration_item in native_durations:
		if typeof(duration_item) != TYPE_FLOAT and typeof(duration_item) != TYPE_INT:
			return
		var native_duration: float = float(duration_item)
		if not is_finite(native_duration) or native_duration <= 0.0:
			return
		native_total += native_duration
	if absf(native_total / float(NATIVE_FPS) - float(DURATIONS[kind])) > DURATION_EPSILON:
		return
	var names_value: Variant = entry.get("frames")
	if typeof(names_value) != TYPE_ARRAY:
		return
	var frame_names: Array = names_value
	if frame_names.size() != FRAME_COUNT:
		return
	# Validate every name and path before decoding any image.
	var frame_paths: Array[String] = []
	for name_value in frame_names:
		if typeof(name_value) != TYPE_STRING:
			return
		var frame_name: String = str(name_value)
		if frame_name.is_empty():
			return
		if frame_name.get_file() != frame_name or frame_name.contains("..") or frame_name.contains("\\"):
			return
		var frame_path: String = _asset_dir.path_join(frame_name)
		if not FileAccess.file_exists(frame_path):
			return
		frame_paths.append(frame_path)
	if frame_paths.size() != FRAME_COUNT:
		return
	# Decode into a local array and install it only after all eight cels pass.
	var textures: Array = []
	for frame_path in frame_paths:
		var image: Image = Image.load_from_file(frame_path)
		if image == null or image.is_empty():
			return
		if image.get_width() != int(CELL_SIZE.x) or image.get_height() != int(CELL_SIZE.y):
			return
		if image.get_format() != Image.FORMAT_RGBA8:
			image.convert(Image.FORMAT_RGBA8)
		var texture: ImageTexture = ImageTexture.create_from_image(image)
		if texture == null:
			return
		textures.append(texture)
	if textures.size() != FRAME_COUNT:
		return
	_frames_by_kind[kind] = textures

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
		if float(events[index]["age"]) + DURATION_EPSILON >= float(events[index]["duration"]):
			events.remove_at(index)

func draw(canvas: CanvasItem) -> void:
	if canvas == null:
		return
	var previous_filter: int = int(canvas.texture_filter)
	canvas.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	for event in events:
		if typeof(event) != TYPE_DICTIONARY:
			continue
		var kind: String = str(event.get("kind", ""))
		if not DURATIONS.has(kind):
			continue
		var age: float = float(event.get("age", 0.0))
		var duration: float = float(event.get("duration", DURATIONS[kind]))
		if not is_finite(age) or not is_finite(duration) or duration <= 0.0:
			continue
		var origin: Vector2 = event.get("origin", Vector2.ZERO)
		var direction: float = -1.0 if float(event.get("facing", 1.0)) < 0.0 else 1.0
		var progress: float = clampf(age / duration, 0.0, 1.0)
		var frames_value: Variant = _frames_by_kind.get(kind, [])
		if typeof(frames_value) == TYPE_ARRAY:
			var frames: Array = frames_value
			if frames.size() == FRAME_COUNT:
				var frame_index: int = clampi(int(floor(progress * float(FRAME_COUNT))), 0, FRAME_COUNT - 1)
				var texture_value: Variant = frames[frame_index]
				if texture_value is Texture2D:
					canvas.draw_set_transform(origin.round(), 0.0, Vector2(direction, 1.0))
					canvas.draw_texture(texture_value as Texture2D, -PIVOT)
					canvas.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
					continue
		_draw_procedural(canvas, kind, origin, direction, progress)
	canvas.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	canvas.texture_filter = previous_filter

func _draw_procedural(canvas: CanvasItem, kind: String, origin: Vector2, facing: float, progress: float) -> void:
	var fade: float = (1.0 - progress) * 0.68
	match kind:
		"attack", "hit":
			var contact_color := Color("#e6b66a") if kind == "attack" else Color("#cf8b7f")
			contact_color.a = fade
			# Small contact spokes; no solid flash covering the body or screen.
			for offset in [Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1)]:
				var inner: float = 4.0 + progress * 4.0
				var outer: float = 8.0 + progress * 7.0
				canvas.draw_line((origin + offset * inner).round(), (origin + offset * outer).round(), contact_color, 1.0, false)
		"dodge":
			var dodge_color := Color(0.44, 0.69, 0.75, fade * 0.8)
			for line in 3:
				var at: Vector2 = origin + Vector2(-facing * (4.0 + progress * 12.0), line * 3.0 - 3.0)
				canvas.draw_line(at.round(), (at + Vector2(-facing * (8.0 - progress * 4.0), 0)).round(), dodge_color, 1.0, false)
		"guard":
			var guard_color := Color(0.49, 0.75, 0.81, fade)
			var points := PackedVector2Array()
			for step in 7:
				var angle: float = -PI * 0.40 + step * PI * 0.80 / 6.0
				points.append((origin + Vector2(cos(angle) * facing, sin(angle)) * (12.0 + progress * 3.0)).round())
			canvas.draw_polyline(points, guard_color, 1.0, false)
		"heal":
			var heal_color := Color(0.49, 0.79, 0.66, fade)
			for side in [-1.0, 1.0]:
				var at: Vector2 = (origin + Vector2(side * 12.0, -progress * 14.0)).round()
				canvas.draw_line(at - Vector2(2, 0), at + Vector2(2, 0), heal_color, 1.0, false)
				canvas.draw_line(at - Vector2(0, 2), at + Vector2(0, 2), heal_color, 1.0, false)
