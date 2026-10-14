extends Node2D

# Isolated E8/E9 test for the source-locked segmented south walk feasibility bake (M8 it1).
# Technical evidence only: not art approval and not a runtime decision. No runtime script, scene,
# asset or save is touched; frame PNGs are read straight from the outputs folder (no import entry).
# 90 logical px/s is the isolated pilot speed only (memo R2 is still open).
# Run windowed (headless render capture can hang):
#   Godot_v4.7.2-stable_win64_console.exe --path game res://tests/<this-scene>.tscn -- --mode=stills
#   Godot_v4.7.2-stable_win64_console.exe --path game --write-movie <abs .avi> --fixed-fps 60 res://tests/<this-scene>.tscn -- --mode=motion
const EXPERIMENT_DIR := "res://../outputs/rpg-2-star-ocean-the-second_segwalk-e1e9_m8_20261014-215052-5ab7af12"
const MANIFEST := "rpg-2-star-ocean-the-second_protagonist-female_south-bake-manifest_m8-it1_20261014-215052-1da0df14.json"
const NAME_PREFIX := "rpg-2-star-ocean-the-second_protagonist-female_"
const STAMP := "20261014-215052"
const VARIANT := "m8-it1"
const GROUNDS := {"light": Color8(185, 165, 136), "dark": Color8(35, 38, 44)}
const SPEED := 90.0
const PHYSICS_HZ := 60
const PHASE_ADVANCE := 5.0
const STILL_POS := Vector2(320, 200)
const MOTION_START := Vector2(320, 40)
const MOTION_TICKS := 160
const MOTION_SAMPLE_TICKS := [37, 80, 123]

var _dir := ""
var _manifest: Dictionary = {}
var _textures: Array[ImageTexture] = []
var _images: Array[Image] = []
var _pin := Vector2.ZERO
var _scale := 0.5
var _sprite: Sprite2D
var _ground: ColorRect
var _tick := 0
var _motion_log: Array = []
var _motion_samples: Array = []
var _running := false


func _ready() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("M8_SEGWALK_E8E9: " + reason)
	get_tree().quit(1)


func _mode() -> String:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--mode="):
			return arg.trim_prefix("--mode=")
	return "stills"


func _out_name(purpose: String, ext: String) -> String:
	var short := ("%s|%s|%s" % [STAMP, VARIANT, purpose]).sha1_text().substr(0, 8)
	return "%s%s_%s_%s-%s.%s" % [NAME_PREFIX, purpose, VARIANT, STAMP, short, ext]


func _run() -> void:
	_dir = ProjectSettings.globalize_path(EXPERIMENT_DIR)
	var text := FileAccess.get_file_as_string(_dir.path_join(MANIFEST))
	var parsed: Variant = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		_fail("cannot parse bake manifest")
		return
	_manifest = parsed
	var once: Dictionary = _manifest["declared_once"]
	_pin = Vector2(once["ground_pin"][0], once["ground_pin"][1])
	_scale = float(once["sprite2d_scale"])
	for frame in _manifest["frames"]:
		var path := _dir.path_join(frame["png"]["file"])
		if FileAccess.get_sha256(path) != frame["png"]["sha256"]:
			_fail("frame hash mismatch: " + path)
			return
		var image := Image.new()
		if image.load(path) != OK:
			_fail("cannot load " + path)
			return
		image.convert(Image.FORMAT_RGBA8)
		_images.append(image)
		_textures.append(ImageTexture.create_from_image(image))
	_ground = ColorRect.new()
	_ground.size = Vector2(640, 360)
	add_child(_ground)
	_sprite = Sprite2D.new()
	_sprite.centered = false
	_sprite.offset = -_pin
	_sprite.scale = Vector2.ONE * _scale
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_sprite)
	if _mode() == "motion":
		_ground.color = GROUNDS["light"]
		_sprite.position = MOTION_START
		_running = true
	else:
		await _stills()


func _screen_transform() -> Transform2D:
	return get_viewport().get_final_transform() * _sprite.get_global_transform_with_canvas()


# Compares every texel of frame `index` against the capture; 1 texel must equal exactly 1 screen px.
func _pixel_check(capture: Image, index: int, ground: Color) -> Dictionary:
	var image := _images[index]
	var origin := _screen_transform() * (-_pin)
	var ox := int(round(origin.x))
	var oy := int(round(origin.y))
	var mismatches := 0
	var opaque := 0
	for y in image.get_height():
		for x in image.get_width():
			var texel := image.get_pixel(x, y)
			var want := texel if texel.a8 == 255 else ground
			var got := capture.get_pixel(ox + x, oy + y)
			if texel.a8 == 255:
				opaque += 1
			if got.r8 != want.r8 or got.g8 != want.g8 or got.b8 != want.b8:
				mismatches += 1
	return {"cell_top_left_screen_px": [origin.x, origin.y], "fractional": origin.x != round(origin.x) or origin.y != round(origin.y),
		"opaque_texels": opaque, "texels_compared": image.get_width() * image.get_height(), "mismatches": mismatches}


func _stills() -> void:
	_sprite.position = STILL_POS
	var results: Array = []
	var frames: Array = _manifest["frames"]
	for ground_name in GROUNDS:
		_ground.color = GROUNDS[ground_name]
		for i in frames.size():
			_sprite.texture = _textures[i]
			await get_tree().process_frame
			await get_tree().process_frame
			await RenderingServer.frame_post_draw
			var capture := get_viewport().get_texture().get_image()
			if capture.get_size() != Vector2i(1280, 720):
				_fail("unexpected capture size " + str(capture.get_size()))
				return
			var check := _pixel_check(capture, i, GROUNDS[ground_name])
			var purpose := "south-cap-%02d-%s-%s" % [int(frames[i]["phase"]), frames[i]["name"], ground_name]
			var path := _dir.path_join(_out_name(purpose, "png"))
			if capture.save_png(path) != OK:
				_fail("cannot save " + path)
				return
			check["file"] = path.get_file()
			check["sha256"] = FileAccess.get_sha256(path)
			check["phase"] = frames[i]["phase"]
			check["ground"] = ground_name
			results.append(check)
	var texel_scale := _screen_transform().get_scale()
	var receipt := {
		"schema": "segwalk-godot-stills-receipt/1", "variant": VARIANT,
		"status": "technical evidence only; not art approval",
		"godot": Engine.get_version_info()["string"], "renderer": RenderingServer.get_current_rendering_driver_name(),
		"window": [1280, 720], "canvas": [640, 360], "stretch": "canvas_items",
		"sprite2d_scale": _scale, "screen_px_per_texel": [texel_scale.x, texel_scale.y],
		"captures": results,
	}
	_write_receipt("south-godot-stills-receipt", receipt)
	get_tree().quit(0)


func _physics_process(_delta: float) -> void:
	if not _running:
		return
	# Deterministic fixed step: exactly SPEED / PHYSICS_HZ logical px per tick (no wall-clock delta).
	var distance := _tick * SPEED / PHYSICS_HZ
	var phase := int(floor(distance / PHASE_ADVANCE)) % 8 + 1
	_sprite.position = MOTION_START + Vector2(0, distance)
	_sprite.texture = _textures[phase]
	var frame: Dictionary = _manifest["frames"][phase]
	var stance: String = frame["stance"]
	var foot: Array = frame["contact_points"][stance]
	# Contact point = bottom edge of the stance foot's lowest row, at its span midpoint.
	var foot_screen := _screen_transform() * (Vector2(foot[0], foot[1] + 1) - _pin)
	var origin := _screen_transform() * Vector2.ZERO
	_motion_log.append({"tick": _tick, "distance": distance, "phase": phase, "stance": stance,
		"origin_screen": [origin.x, origin.y], "foot_screen": [foot_screen.x, foot_screen.y]})
	if _tick in MOTION_SAMPLE_TICKS:
		_sample_after_draw.call_deferred(phase)
	_tick += 1
	if _tick > MOTION_TICKS:
		_running = false
		_finish_motion.call_deferred()


func _sample_after_draw(phase: int) -> void:
	await RenderingServer.frame_post_draw
	var capture := get_viewport().get_texture().get_image()
	var check := _pixel_check(capture, phase, GROUNDS["light"])
	check["phase"] = phase
	_motion_samples.append(check)


func _finish_motion() -> void:
	await RenderingServer.frame_post_draw
	var drifts: Array = []
	var over := 0
	var fractional := 0
	var driven_ok := true
	for i in _motion_log.size():
		var e: Dictionary = _motion_log[i]
		var o: Array = e["origin_screen"]
		if o[0] != round(o[0]) or o[1] != round(o[1]):
			fractional += 1
		if int(e["phase"]) != int(floor(float(e["distance"]) / PHASE_ADVANCE)) % 8 + 1:
			driven_ok = false
		if i == 0 or _motion_log[i - 1]["stance"] != e["stance"]:
			continue
		var a: Array = _motion_log[i - 1]["foot_screen"]
		var b: Array = e["foot_screen"]
		var d := maxf(absf(b[0] - a[0]), absf(b[1] - a[1]))
		drifts.append(d)
		if d > 1.0:
			over += 1
	var max_drift := 0.0
	var total := 0.0
	for d in drifts:
		max_drift = maxf(max_drift, d)
		total += d
	var texel_scale := _screen_transform().get_scale()
	var mismatches := 0
	for s in _motion_samples:
		mismatches += int(s["mismatches"])
	var receipt := {
		"schema": "segwalk-godot-motion-receipt/1", "variant": VARIANT,
		"status": "technical evidence only; 90 logical px/s is an isolated pilot value, not a runtime decision",
		"godot": Engine.get_version_info()["string"], "renderer": RenderingServer.get_current_rendering_driver_name(),
		"speed_logical_px_per_s": SPEED, "physics_hz": PHYSICS_HZ, "phase_advance_logical_px": PHASE_ADVANCE,
		"ticks": _motion_log.size(), "path": "straight south",
		"e8": {"ticks_compared": drifts.size(), "max_stance_foot_drift_screen_px_per_tick": max_drift,
			"mean_stance_foot_drift_screen_px_per_tick": total / maxf(1.0, drifts.size()),
			"ticks_over_1px": over, "limit": "<= 1 screen px per tick", "pass": max_drift <= 1.0},
		"e9": {"screen_px_per_texel": [texel_scale.x, texel_scale.y], "fractional_origin_ticks": fractional,
			"distance_driven_stepping": driven_ok, "rendered_samples": _motion_samples,
			"rendered_sample_mismatches": mismatches,
			"pass": texel_scale == Vector2.ONE and fractional == 0 and driven_ok and mismatches == 0 and _motion_samples.size() == MOTION_SAMPLE_TICKS.size()},
		"tick_log": _motion_log,
	}
	_write_receipt("south-godot-motion-receipt", receipt)
	get_tree().quit(0)


func _write_receipt(purpose: String, data: Dictionary) -> void:
	var path := _dir.path_join(_out_name(purpose, "json"))
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		_fail("cannot write " + path)
		return
	file.store_string(JSON.stringify(data, "  ") + "\n")
	file.close()
