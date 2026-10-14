extends Node

# Isolated visual QA: the two unapproved female south-idle refinement candidates (inkline,
# selout) at 48 logical pixels in the science city (beside the current 32x48 female gameplay
# placeholder), in the sunlit outskirts (bright) and in the dark teal prototype room (dark).
# Review only — not art approval. No shadow is drawn under the candidates.
# Ground/bounds logic mirrors the existing city and outskirts/ruins pilot QA scripts, which
# are not modified or loaded. No runtime script, scene, asset, or save is edited; saves are
# redirected to a test path.
# Run windowed (headless render capture can hang):
# Godot_v4.7.2-stable_win64_console.exe --path game res://tests/<this-scene>.tscn
# One run writes six standalone 1280x720 captures and one JSON report to outputs/.
const PILOT_DIR := "res://assets/characters/pixelorama-pilots/"
const PILOT_PATHS := {
	"inkline": PILOT_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-refine-inkline-candidate_m8-v01_20261014-231100-fb830d80.png",
	"selout": PILOT_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-refine-selout-candidate_m8-v01_20261014-231100-4d141ad5.png",
}
const AREA_SCENE := "res://scenes/scifi_exploration_area.tscn"
const ROOM_SCENE := "res://scenes/prototype_room.tscn"
# scene key -> [kind, destination id, x offset from placeholder or absolute foot x, lighting note]
const SCENES := {
	"city": ["area", "scifi.city", 36.0, "science city, default first-visit layout"],
	"outskirts-bright": ["area", "scifi.outskirts", -36.0, "sunlit outskirts paving (bright scene)"],
	"prototype-room-dark": ["room", "", 320.0, "dark teal prototype room floor #28434a (dark scene); room hero hidden"],
}
const ROOM_FOOT_Y := 270.0
const OUTPUT_DIR := "res://../outputs"
const TARGET_HEIGHT := 48
const ALPHA_THRESHOLD := 128
const RUN_ID := "20261014-231100-68425d09"


func _ready() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("M8_REFINE_CANDIDATES_QA: " + reason)
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


# Opaque candidate texels whose RGB8 equals the captured window pixel at the 1:1 mapped spot
# (texel bounds origin -> diff bounds origin). Only meaningful when the diff is texel-sized.
func _texel_fidelity(pilot: Image, bounds: Rect2i, capture: Image, diff: Rect2i) -> Dictionary:
	var total := 0
	var exact := 0
	for y in bounds.size.y:
		for x in bounds.size.x:
			var texel := pilot.get_pixel(bounds.position.x + x, bounds.position.y + y)
			if texel.a8 < ALPHA_THRESHOLD:
				continue
			total += 1
			var shown := capture.get_pixel(diff.position.x + x, diff.position.y + y)
			if shown.r8 == texel.r8 and shown.g8 == texel.g8 and shown.b8 == texel.b8:
				exact += 1
	return {"opaque_texels": total, "exact_rgb_matches": exact}


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
	SaveStore.root_path = "user://test-saves/m8-refine-candidates-qa"
	var app: Node = get_node("/root/AppState")
	var captures: Array = []
	for scene_key in SCENES.keys():
		var spec: Array = SCENES[scene_key]
		for variant in PILOT_PATHS.keys():
			# Load from disk so the candidate does not need a Godot import entry.
			var pilot_abs := ProjectSettings.globalize_path(PILOT_PATHS[variant])
			var pilot_image := Image.new()
			if pilot_image.load(pilot_abs) != OK:
				_fail("cannot load candidate PNG " + pilot_abs)
				return
			pilot_image.convert(Image.FORMAT_RGBA8)
			var pilot_bounds := _alpha_bounds(pilot_image)
			if pilot_bounds.size.y <= 0:
				_fail("candidate has no visible pixels: " + variant)
				return
			app.begin_new_run()
			app.hero_appearance = "female"
			var host: Node2D
			var ground_y := 0.0
			var pilot_x := 0.0
			var placeholder_info := {}
			if spec[0] == "area":
				if not app.select_destination(spec[1]):
					_fail("destination rejected: " + spec[1])
					return
				host = (load(AREA_SCENE) as PackedScene).instantiate()
				add_child(host)
				await get_tree().process_frame
				await get_tree().process_frame
				host.set_process(false)
				if String(host.get("destination_id")) != spec[1]:
					_fail("area fell back to %s instead of %s" % [host.get("destination_id"), spec[1]])
					return
				var hero: Sprite2D = host.get("hero")
				var placeholder_image := hero.texture.get_image()
				placeholder_image.convert(Image.FORMAT_RGBA8)
				var placeholder_bounds := _alpha_bounds(placeholder_image)
				# Ground row of the placeholder's lowest opaque pixel, in area logical pixels.
				var texture_top := hero.position.y + hero.offset.y - placeholder_image.get_height() * 0.5
				ground_y = texture_top + placeholder_bounds.end.y
				pilot_x = hero.position.x + float(spec[2])
				placeholder_info = {
					"placeholder_texture_path": hero.texture.resource_path,
					"placeholder_texture_size": [placeholder_image.get_width(), placeholder_image.get_height()],
					"placeholder_visible_bounds": _rect_json(placeholder_bounds),
					"placeholder_position_logical": [hero.position.x, hero.position.y],
				}
			else:
				host = (load(ROOM_SCENE) as PackedScene).instantiate()
				add_child(host)
				await get_tree().process_frame
				await get_tree().process_frame
				host.set_process(false)
				(host.get("hero") as Sprite2D).visible = false
				ground_y = ROOM_FOOT_Y
				pilot_x = float(spec[2])
				placeholder_info = {"placeholder": "none (prototype-room temp hero hidden)"}
			var baseline := await _capture()
			var scale_factor := float(TARGET_HEIGHT) / float(pilot_bounds.size.y)
			var pilot_foot_x := pilot_bounds.position.x + pilot_bounds.size.x * 0.5
			var pilot := Sprite2D.new()
			pilot.texture = ImageTexture.create_from_image(pilot_image)
			pilot.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
			pilot.centered = false
			pilot.offset = Vector2(-pilot_foot_x, -pilot_bounds.end.y)
			pilot.scale = Vector2.ONE * scale_factor
			pilot.position = Vector2(pilot_x, ground_y)
			pilot.z_index = int(ground_y)
			host.add_child(pilot)
			var capture := await _capture()
			if capture == null or capture.get_size() != Vector2i(1280, 720):
				_fail("unexpected capture size: " + str(capture.get_size() if capture != null else Vector2i.ZERO))
				return
			var window_scale := float(capture.get_height()) / 360.0
			var diff := _diff_bounds(baseline, capture)
			var fidelity := _texel_fidelity(pilot_image, pilot_bounds, capture, diff)
			var stem := "rpg-2-star-ocean-the-second_%s_protagonist-female-south-idle-refine-%s-candidate-h48_m8-v01_%s-%s" % [scene_key, variant, stamp, unique_id]
			var capture_path := output_path.path_join(stem + ".png")
			if capture.save_png(capture_path) != OK:
				_fail("cannot save capture")
				return
			var entry := {
				"scene": scene_key,
				"scene_note": spec[3],
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
				"pilot_window_diff_bounds_measured": _rect_json(diff),
				"pilot_texel_fidelity": fidelity,
				"pilot_position_logical": [pilot.position.x, pilot.position.y],
				"ground_y_logical": ground_y,
				"shadow": "none",
			}
			entry.merge(placeholder_info)
			captures.append(entry)
			print("CAPTURE %s %s  src %dx%d  bounds %s  scale %.4f  logical %.1fx%.1f  diff %s  fidelity %d/%d  sha %s  %s" % [
				scene_key, variant, pilot_image.get_width(), pilot_image.get_height(), str(pilot_bounds),
				scale_factor, pilot_bounds.size.x * scale_factor, pilot_bounds.size.y * scale_factor,
				str(diff), fidelity["exact_rgb_matches"], fidelity["opaque_texels"], entry["capture_sha256"], capture_path])
			host.queue_free()
			await get_tree().process_frame
			await get_tree().process_frame
	var report := {
		"project": "Worlds Between",
		"milestone": "M8",
		"purpose": "In-engine readability captures of the inkline and selout female south-idle refinement candidates at 48 logical px: science city beside the 32x48 placeholder, bright outskirts, dark prototype room.",
		"status": "technical visual QA only; unapproved candidates; not integrated",
		"art_approved": false,
		"human_reviewed": false,
		"acceptance_counters_unchanged": {"runtime_exploration_sprites_accepted": "0/52", "scene_quality_gates_passed": "0/11"},
		"qa_script": "game/tests/rpg-2-star-ocean-the-second_protagonist-female_south-idle-refinement-candidates-visual-qa_m8-v01_%s.gd" % RUN_ID,
		"renderer": "Godot %s windowed, viewport texture capture" % Engine.get_version_info()["string"],
		"canvas": [640, 360],
		"window": [1280, 720],
		"camera": "none; scenes draw a fixed 640x360 canvas",
		"pilot_loading": "Image.load from disk (no import); ImageTexture; nearest filtering; no shadow",
		"captures": captures,
		"limitations": [
			"Static south idle only; no walk frames or other facings.",
			"Only first-visit default area state captured; area _process disabled after two frames.",
			"Prototype room is the project's existing dark test room, not a gameplay area; its temp hero is hidden.",
			"Texel fidelity compares RGB8 at a 1:1 mapping anchored on the measured diff bounds; it assumes the diff equals the candidate's visible bounds.",
			"Readability judgement in this report is automated measurement only; visual review is still required.",
		],
	}
	var report_path := output_path.path_join("rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-refine-candidates-visual-qa-report_m8-v01_%s-%s.json" % [stamp, unique_id])
	var file := FileAccess.open(report_path, FileAccess.WRITE)
	if file == null:
		_fail("cannot write report")
		return
	file.store_string(JSON.stringify(report, "\t") + "\n")
	file.close()
	print("STATUS unapproved candidates; technical visual QA only")
	print("REPORT " + report_path)
	get_tree().quit(0)
