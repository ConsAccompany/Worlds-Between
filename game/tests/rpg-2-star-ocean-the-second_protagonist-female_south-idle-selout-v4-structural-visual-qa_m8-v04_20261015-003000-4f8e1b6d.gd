extends Node

# Isolated visual QA: the unapproved female south-idle selout v4 structural static refinement
# at 48 logical pixels beside the current 32x48 female gameplay placeholder in the science
# city, the sunlit outskirts (bright), the city survey annex room 2 (darkest gameplay room)
# and the dark teal prototype test room (darkest backdrop; no placeholder). The selout v3 PNG
# is captured in the same run as a same-condition A/B reference. Each capture is a separate
# PNG (no collage). Review only — not art approval. No shadow is drawn under the candidates.
# Adapted from the v3 harness (rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-
# v3-polish-visual-qa_m8-v03_20261015-000500-5d7e2a91.gd), which is not modified or loaded.
# No runtime script, scene, asset, or save is edited; saves are redirected to a test path.
# Gates (the run exits 1 and writes no report if any fails): both source PNGs match their
# expected SHA-256; every capture is 1280x720; each candidate's diff window is exactly its
# visible bounds at 1 texel = 1 window px; texel fidelity is 100% for each candidate (v3 must
# be 2433/2433; v4 is measured because its tuft changes the silhouette).
# The v3->v4 changed-window-pixel count per scene is measured and compared with the 358
# texels the edit manifest reports; a mismatch is recorded, not fatal.
# Run windowed from the repository root (headless render capture can hang):
# work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game res://tests/<this-scene>.tscn
# One run writes eight standalone 1280x720 captures (4 scenes x {v4, v3}) and one JSON report.
const PILOT_DIR := "res://assets/characters/pixelorama-pilots/"
const PILOT_PATHS := {
	"selout-v4": PILOT_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v4-structural-candidate_m8-v04_20261015-001500-e5b81f36.png",
	"selout-v3-reference": PILOT_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v3-polish-candidate_m8-v03_20261014-234700-3c9a5d27.png",
}
const EXPECTED_SHA256 := {
	"selout-v4": "da8a1ce11db136f7061206a3d8f5038b7d995016e36af2fc011d0a6f0dbcf4d7",
	"selout-v3-reference": "21b148cc026a70cdb173200c46cf007f83e4963cd7b7a7c71a174a7cb343cbc3",
}
const EXPECTED_V3_OPAQUE := 2433
const EXPECTED_CHANGED_TEXELS := 358
const AREA_SCENE := "res://scenes/scifi_exploration_area.tscn"
const ANNEX_SCENE := "res://scenes/survey_annex.tscn"
const ROOM_SCENE := "res://scenes/prototype_room.tscn"
const ROOM_FOOT := Vector2(320.0, 270.0)
# scene key -> [kind, destination id, x offset from placeholder or absolute foot x, lighting note]
const SCENES := {
	"city": ["area", "scifi.city", 36.0, "science city, default first-visit layout"],
	"outskirts-bright": ["area", "scifi.outskirts", -36.0, "sunlit outskirts paving (bright scene)"],
	"survey-annex-room2-dark": ["annex", "scifi.city", 36.0, "city survey annex room 2 (darkest gameplay room; background mean luma 72.5)"],
	"prototype-room-dark": ["room", "scifi.city", 0.0, "dark teal prototype test room #28434a floor (darkest backdrop); temp hero hidden"],
}
const OUTPUT_DIR := "res://../outputs"
const TARGET_HEIGHT := 48
const ALPHA_THRESHOLD := 128
const RUN_ID := "20261015-003000-4f8e1b6d"


func _ready() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("M8_SELOUT_V4_QA: " + reason)
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


# Number of window pixels that differ between two same-size captures.
func _diff_count(a: Image, b: Image) -> int:
	var count := 0
	for y in a.get_height():
		for x in a.get_width():
			if a.get_pixel(x, y) != b.get_pixel(x, y):
				count += 1
	return count


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
	# Source lock: both PNGs must be the exact bytes this harness was written for.
	var sources := {}
	for variant in PILOT_PATHS.keys():
		var abs_path := ProjectSettings.globalize_path(PILOT_PATHS[variant])
		var digest := FileAccess.get_sha256(abs_path)
		if digest != EXPECTED_SHA256[variant]:
			_fail("%s SHA-256 %s does not match expected %s" % [variant, digest, EXPECTED_SHA256[variant]])
			return
		sources[variant] = {"path": PILOT_PATHS[variant], "sha256": digest}
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
	SaveStore.root_path = "user://test-saves/m8-selout-v4-qa"
	var app: Node = get_node("/root/AppState")
	var captures: Array = []
	var v4_vs_v3 := {}
	for scene_key in SCENES.keys():
		var spec: Array = SCENES[scene_key]
		var scene_captures := {}
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
			if not app.select_destination(spec[1]):
				_fail("destination rejected: " + spec[1])
				return
			if spec[0] == "annex":
				app.current_annex_room = 2
			var scene_path: String = {"area": AREA_SCENE, "annex": ANNEX_SCENE, "room": ROOM_SCENE}[spec[0]]
			var host: Node2D = (load(scene_path) as PackedScene).instantiate()
			add_child(host)
			await get_tree().process_frame
			await get_tree().process_frame
			host.set_process(false)
			var ground_y := ROOM_FOOT.y
			var pilot_x := ROOM_FOOT.x
			var placeholder_info := {"placeholder": "none (prototype-room temp hero hidden)"}
			# The prototype room only hides its temp hero; exploration areas and the survey annex
			# both expose `hero` and `destination_id` for the placeholder ground row.
			if spec[0] == "room":
				(host.get("hero") as Sprite2D).visible = false
			elif String(host.get("destination_id")) != spec[1]:
				_fail("scene fell back to %s instead of %s" % [host.get("destination_id"), spec[1]])
				return
			else:
				var hero: Sprite2D = host.get("hero")
				var placeholder_image := hero.texture.get_image()
				placeholder_image.convert(Image.FORMAT_RGBA8)
				var placeholder_bounds := _alpha_bounds(placeholder_image)
				# Ground row of the placeholder's lowest opaque pixel, in scene logical pixels.
				var texture_top := hero.position.y + hero.offset.y - placeholder_image.get_height() * 0.5
				ground_y = texture_top + placeholder_bounds.end.y
				pilot_x = hero.position.x + float(spec[2])
				placeholder_info = {
					"placeholder_texture_path": hero.texture.resource_path,
					"placeholder_texture_size": [placeholder_image.get_width(), placeholder_image.get_height()],
					"placeholder_visible_bounds": _rect_json(placeholder_bounds),
					"placeholder_position_logical": [hero.position.x, hero.position.y],
				}
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
			if diff.size != pilot_bounds.size:
				_fail("%s %s: diff window %s is not the 1:1 visible bounds %s" % [scene_key, variant, str(diff.size), str(pilot_bounds.size)])
				return
			var fidelity := _texel_fidelity(pilot_image, pilot_bounds, capture, diff)
			if fidelity["exact_rgb_matches"] != fidelity["opaque_texels"]:
				_fail("%s %s: texel fidelity %d/%d" % [scene_key, variant, fidelity["exact_rgb_matches"], fidelity["opaque_texels"]])
				return
			if variant == "selout-v3-reference" and fidelity["opaque_texels"] != EXPECTED_V3_OPAQUE:
				_fail("v3 opaque texels %d, expected %d" % [fidelity["opaque_texels"], EXPECTED_V3_OPAQUE])
				return
			var stem := "rpg-2-star-ocean-the-second_%s_protagonist-female-south-idle-%s-h48_m8-v04_%s-%s" % [scene_key, variant, stamp, unique_id]
			var capture_path := output_path.path_join(stem + ".png")
			if capture.save_png(capture_path) != OK:
				_fail("cannot save capture")
				return
			scene_captures[variant] = capture
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
		# Same scene, same placement: only the edited texels should differ between v4 and v3.
		# A texel that v4 made transparent shows the scene background, so it still differs
		# unless the background happens to equal v3's colour exactly.
		var changed := _diff_count(scene_captures["selout-v4"], scene_captures["selout-v3-reference"])
		v4_vs_v3[scene_key] = {"changed_window_pixels": changed,
			"expected_changed_texels": EXPECTED_CHANGED_TEXELS,
			"matches_expected": changed == EXPECTED_CHANGED_TEXELS,
			"changed_bounds": _rect_json(_diff_bounds(scene_captures["selout-v4"], scene_captures["selout-v3-reference"]))}
		print("V4_VS_V3 %s changed_window_pixels %d (expected %d)" % [scene_key, changed, EXPECTED_CHANGED_TEXELS])
	var report := {
		"project": "Worlds Between",
		"milestone": "M8",
		"purpose": "In-engine readability captures of the female south-idle selout v4 structural static refinement at 48 logical px beside the 32x48 placeholder: science city, bright outskirts, dark city survey annex room 2, dark prototype test room; selout v3 captured in the same run as A/B reference.",
		"status": "technical visual QA only; unapproved candidate; not integrated",
		"art_approved": false,
		"human_reviewed": false,
		"acceptance_counters_unchanged": {"runtime_exploration_sprites_accepted": "0/52", "scene_quality_gates_passed": "0/11"},
		"qa_script": "game/tests/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v4-structural-visual-qa_m8-v04_%s.gd" % RUN_ID,
		"renderer": "Godot %s windowed, viewport texture capture" % Engine.get_version_info()["string"],
		"canvas": [640, 360],
		"window": [1280, 720],
		"camera": "none; scenes draw a fixed 640x360 canvas",
		"pilot_loading": "Image.load from disk (no import); ImageTexture; nearest filtering; no shadow",
		"sources": sources,
		"gates_passed": ["source SHA-256 lock", "1280x720 captures", "diff window = visible bounds (1:1)", "100% texel fidelity per candidate", "v3 opaque texels = 2433"],
		"v4_vs_v3_same_scene": v4_vs_v3,
		"captures": captures,
		"limitations": [
			"Static south idle only; no walk frames or other facings.",
			"Only first-visit default area state captured; area _process disabled after two frames.",
			"Survey annex is captured in room 2 of the city annex (current_annex_room set to 2 for the test only) with default state; its ambience audio plays but is irrelevant to the capture.",
			"Prototype room is the project's existing dark test room, not a gameplay area; its temp hero is hidden and no placeholder is shown.",
			"selout-v3-reference captures exist only for same-run A/B comparison; v3 is not modified.",
			"v4 changes the tuft silhouette (y8-12), so its opaque-texel count differs from v3 and is measured rather than fixed.",
			"v4_vs_v3 changed_window_pixels equals the edited-texel count only if the scene is static between captures and no transparent-in-v4 texel lands on a background pixel of identical colour.",
			"Readability judgement in this report is automated measurement only; visual review is still required.",
		],
	}
	var report_path := output_path.path_join("rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v4-visual-qa-report_m8-v04_%s-%s.json" % [stamp, unique_id])
	var file := FileAccess.open(report_path, FileAccess.WRITE)
	if file == null:
		_fail("cannot write report")
		return
	file.store_string(JSON.stringify(report, "\t") + "\n")
	file.close()
	print("STATUS unapproved candidate; technical visual QA only")
	print("REPORT " + report_path)
	get_tree().quit(0)
