extends Node

# Isolated visual QA: the two unapproved quantized female south-idle candidates (boxquant,
# lanczosquant) at 48 logical pixels beside the current 32x48 female gameplay placeholder,
# in the outskirts and ruins exploration areas. Review only — not art approval.
# Ground/bounds logic mirrors the city pilot QA script, which is not modified or loaded.
# No runtime script, scene, asset, or save is edited; saves are redirected to a test path.
# Run windowed (headless render capture can hang):
# Godot_v4.7.2-stable_win64_console.exe --path game res://tests/<this-scene>.tscn
# One run writes four standalone 1280x720 captures and one JSON report to outputs/.
const PILOT_DIR := "res://assets/characters/pixelorama-pilots/"
const PILOT_PATHS := {
	"boxquant": PILOT_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-boxquant-pilot_m8-v01_20261014-212322-7c30d48c.png",
	"lanczosquant": PILOT_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-lanczosquant-pilot_m8-v01_20261014-212322-b9fd58f7.png",
}
const AREAS := {"outskirts": "scifi.outskirts", "ruins": "scifi.ruins"}
const AREA_SCENE := "res://scenes/scifi_exploration_area.tscn"
const OUTPUT_DIR := "res://../outputs"
const TARGET_HEIGHT := 48
# Left of the placeholder: +36 (the city offset) would overlap the field-trace marker
# drawn at (125, 240) in outskirts and (115, 245) in ruins.
const PILOT_GAP := -36.0
const ALPHA_THRESHOLD := 128
const RUN_ID := "20261014-220500-d41f7a2c"


func _ready() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("M8_QUANT_PILOT_OUTSKIRTS_RUINS_QA: " + reason)
	get_tree().quit(1)


func _alpha_bounds(image: Image) -> Rect2i:
	var left := image.get_width()
	var top := image.get_height()
	var right := -1
	var bottom := -1
	for y in image.get_height():
		for x in image.get_width():
			if image.get_pixel(x, y).a8 >= ALPHA_THRESHOLD:
				left = mini(left, x)
				top = mini(top, y)
				right = maxi(right, x)
				bottom = maxi(bottom, y)
	if right < 0:
		return Rect2i()
	return Rect2i(left, top, right - left + 1, bottom - top + 1)


# Window-pixel bounds of every pixel that differs between two same-size captures.
func _diff_bounds(a: Image, b: Image) -> Rect2i:
	var left := a.get_width()
	var top := a.get_height()
	var right := -1
	var bottom := -1
	for y in a.get_height():
		for x in a.get_width():
			if a.get_pixel(x, y) != b.get_pixel(x, y):
				left = mini(left, x)
				top = mini(top, y)
				right = maxi(right, x)
				bottom = maxi(bottom, y)
	if right < 0:
		return Rect2i()
	return Rect2i(left, top, right - left + 1, bottom - top + 1)


func _rect_json(rect: Rect2i) -> Dictionary:
	return {"x": rect.position.x, "y": rect.position.y, "w": rect.size.x, "h": rect.size.y}


func _capture() -> Image:
	await get_tree().process_frame
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	return get_tree().root.get_viewport().get_texture().get_image()


func _run() -> void:
	var window := get_tree().root
	window.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	window.content_scale_size = Vector2i(640, 360)
	window.size = Vector2i(1280, 720)
	var output_path := ProjectSettings.globalize_path(OUTPUT_DIR)
	if DirAccess.make_dir_recursive_absolute(output_path) != OK:
		_fail("cannot make output directory")
		return
	var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var unique_id := "%08x" % (randi() & 0xffffffff)
	SaveStore.root_path = "user://test-saves/m8-quant-pilot-outskirts-ruins-qa"
	var app: Node = get_node("/root/AppState")
	var captures: Array = []
	for area_key in AREAS.keys():
		for variant in PILOT_PATHS.keys():
			# Load from disk so the candidate does not need a Godot import entry.
			var pilot_abs := ProjectSettings.globalize_path(PILOT_PATHS[variant])
			var pilot_image := Image.new()
			if pilot_image.load(pilot_abs) != OK:
				_fail("cannot load pilot PNG " + pilot_abs)
				return
			pilot_image.convert(Image.FORMAT_RGBA8)
			var pilot_bounds := _alpha_bounds(pilot_image)
			if pilot_bounds.size.y <= 0:
				_fail("pilot has no visible pixels: " + variant)
				return
			# Fresh run state per capture so each area renders its default first-visit layout.
			app.begin_new_run()
			app.hero_appearance = "female"
			if not app.select_destination(AREAS[area_key]):
				_fail("destination rejected: " + AREAS[area_key])
				return
			var area: Node2D = (load(AREA_SCENE) as PackedScene).instantiate()
			add_child(area)
			await get_tree().process_frame
			await get_tree().process_frame
			area.set_process(false)
			if String(area.get("destination_id")) != AREAS[area_key]:
				_fail("area fell back to %s instead of %s" % [area.get("destination_id"), AREAS[area_key]])
				return
			var hero: Sprite2D = area.get("hero")
			var placeholder_image := hero.texture.get_image()
			placeholder_image.convert(Image.FORMAT_RGBA8)
			var placeholder_bounds := _alpha_bounds(placeholder_image)
			# Ground row of the placeholder's lowest opaque pixel, in area logical pixels.
			var texture_top := hero.position.y + hero.offset.y - placeholder_image.get_height() * 0.5
			var ground_y := texture_top + placeholder_bounds.end.y
			var baseline := await _capture()
			var scale_factor := float(TARGET_HEIGHT) / float(pilot_bounds.size.y)
			var pilot_foot_x := pilot_bounds.position.x + pilot_bounds.size.x * 0.5
			var pilot := Sprite2D.new()
			pilot.texture = ImageTexture.create_from_image(pilot_image)
			pilot.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
			pilot.centered = false
			pilot.offset = Vector2(-pilot_foot_x, -pilot_bounds.end.y)
			pilot.scale = Vector2.ONE * scale_factor
			pilot.position = Vector2(hero.position.x + PILOT_GAP, ground_y)
			pilot.z_index = int(ground_y)
			area.add_child(pilot)
			var capture := await _capture()
			if capture == null or capture.get_size() != Vector2i(1280, 720):
				_fail("unexpected capture size: " + str(capture.get_size() if capture != null else Vector2i.ZERO))
				return
			var window_scale := float(capture.get_height()) / 360.0
			var pilot_window_diff := _diff_bounds(baseline, capture)
			var stem := "rpg-2-star-ocean-the-second_scifi-%s_protagonist-female-quantized-south-%s-pilot-h48-beside-placeholder_m8-v01_%s-%s" % [area_key, variant, stamp, unique_id]
			var capture_path := output_path.path_join(stem + ".png")
			if capture.save_png(capture_path) != OK:
				_fail("cannot save capture")
				return
			var entry := {
				"area": AREAS[area_key],
				"variant": variant,
				"capture": capture_path,
				"capture_sha256": FileAccess.get_sha256(capture_path),
				"capture_size": [capture.get_width(), capture.get_height()],
				"pilot_source": PILOT_PATHS[variant],
				"pilot_source_sha256": FileAccess.get_sha256(pilot_abs),
				"pilot_source_size": [pilot_image.get_width(), pilot_image.get_height()],
				"pilot_visible_bounds_source": _rect_json(pilot_bounds),
				"pilot_scale": scale_factor,
				"pilot_visible_logical": [pilot_bounds.size.x * scale_factor, pilot_bounds.size.y * scale_factor],
				"pilot_visible_window_expected": [pilot_bounds.size.x * scale_factor * window_scale, pilot_bounds.size.y * scale_factor * window_scale],
				"pilot_window_diff_bounds_measured": _rect_json(pilot_window_diff),
				"pilot_position_logical": [pilot.position.x, pilot.position.y],
				"placeholder_texture_path": hero.texture.resource_path,
				"placeholder_texture_size": [placeholder_image.get_width(), placeholder_image.get_height()],
				"placeholder_visible_bounds": _rect_json(placeholder_bounds),
				"placeholder_visible_window": [placeholder_bounds.size.x * window_scale, placeholder_bounds.size.y * window_scale],
				"placeholder_position_logical": [hero.position.x, hero.position.y],
				"ground_y_logical": ground_y,
			}
			captures.append(entry)
			print("CAPTURE %s %s  src %dx%d  bounds %s  scale %.4f  logical %.1fx%.1f  diff %s  sha %s  %s" % [
				AREAS[area_key], variant, pilot_image.get_width(), pilot_image.get_height(), str(pilot_bounds),
				scale_factor, pilot_bounds.size.x * scale_factor, pilot_bounds.size.y * scale_factor,
				str(pilot_window_diff), entry["capture_sha256"], capture_path])
			area.queue_free()
			await get_tree().process_frame
			await get_tree().process_frame
	var report := {
		"project": "Worlds Between",
		"milestone": "M8",
		"purpose": "Readability check of boxquant and lanczosquant female south-idle candidates at 48 logical px in the outskirts and ruins exploration areas, beside the current 32x48 female placeholder.",
		"status": "technical visual QA only; unapproved candidates; not integrated",
		"art_approved": false,
		"human_reviewed": false,
		"acceptance_counters_unchanged": {"runtime_exploration_sprites_accepted": "0/52", "scene_quality_gates_passed": "0/11"},
		"qa_script": "game/tests/rpg-2-star-ocean-the-second_protagonist-female_quantized-south-idle-outskirts-ruins-visual-qa_m8-v01_%s.gd" % RUN_ID,
		"renderer": "Godot %s windowed, viewport texture capture" % Engine.get_version_info()["string"],
		"canvas": [640, 360],
		"window": [1280, 720],
		"camera": "none; area scene draws a fixed 640x360 canvas",
		"hero_start": "runtime first-visit SPAWN; area _process disabled after two frames so no input moves it",
		"pilot_placement": "feet on placeholder ground row, %+.0f logical px from placeholder x" % PILOT_GAP,
		"pilot_loading": "Image.load from disk (no import); ImageTexture; nearest filtering",
		"captures": captures,
		"limitations": [
			"Static south idle only; no walk frames or other facings.",
			"Pilot sits left of the placeholder (city QA used the right) to avoid the field-trace marker; this is a placement choice, not runtime behaviour.",
			"Only first-visit default state captured (enemy visible, no relay/records/survey progress).",
			"Measured diff bounds are window pixels that changed when the pilot was added; they include nothing else only if the area is otherwise static between captures.",
			"Readability judgement in this report is automated measurement only; human review is still required.",
		],
	}
	var report_path := output_path.path_join("rpg-2-star-ocean-the-second_scifi-outskirts-ruins_protagonist-female-quantized-south-pilot-visual-qa-report_m8-v01_%s-%s.json" % [stamp, unique_id])
	var file := FileAccess.open(report_path, FileAccess.WRITE)
	if file == null:
		_fail("cannot write report")
		return
	file.store_string(JSON.stringify(report, "\t") + "\n")
	file.close()
	print("STATUS unapproved candidates; technical visual QA only")
	print("REPORT " + report_path)
	get_tree().quit(0)
