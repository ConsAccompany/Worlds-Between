extends Node

# Isolated visual QA: the unapproved female south-idle selout v8 cloth/leather candidate (storm
# slate coat, spruce-grey trousers, boots one step deeper on the warm leather ramp) at 48 logical
# pixels beside the current 32x48 female gameplay placeholder in the science city (bright), the
# sunlit outskirts (bright) and the city survey annex room 2 (darkest gameplay room). The selout
# v7 PNG is captured in the same run, at the identical position, as an A/B reference. Each
# capture is a separate PNG (no collage). Review only - not art approval. No shadow is drawn.
# Adapted from the v7 harness (rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-
# v7-slate-coat-visual-qa_m8-v07_20261015-015010-a4ea0661.gd), which is not modified or loaded.
# No runtime script, scene, asset, or save is edited; saves are redirected to a test path.
# Gates (the run exits 1 and writes no report if any fails): both source PNGs match their
# expected SHA-256; both visible bounds and every diff window are exactly 43x96 at 1 texel =
# 1 window px; every capture is 1280x720; texel fidelity is 100%; opaque texels are exactly
# 2419 for both; v8 and v7 land on the identical window rect in each scene; and, because v8
# changes no alpha (recolour only), the v8-vs-v7 changed window pixels in every scene must
# equal the manifest's 793 changed texels exactly.
# Measurement (reported, not gated), CIELAB dE76 (sRGB D65), for v8 and for v7 at the same
# texel positions, per region (coat = texels that are v7 slate roles 1/2/3; trousers and boots =
# texels v8 changes in rows 57-84 and 85+; whole figure = every opaque texel):
#   ring_median        vs the per-channel median of an 8 px background ring (v7 note's method);
#   row_local_ring     vs the median of the ring pixels within +/-6 rows of the texel, so the
#                      upper body is compared with the upper background and the legs with the
#                      paving beside the legs;
#   occluded_backdrop  vs the pilot-free baseline pixel at the same window position (what the
#                      texel covers).
# Each gives mean, 10th percentile and minimum over the region's texels.
# Run windowed from the repository root (headless render capture can hang):
# work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game res://tests/<this-scene>.tscn
# One run writes six standalone 1280x720 captures (3 scenes x {v8, v7}) and one JSON report.
const PILOT_DIR := "res://assets/characters/pixelorama-pilots/"
const PILOT_PATHS := {
	"selout-v8": PILOT_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png",
	"selout-v7-reference": PILOT_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v7-slate-coat-candidate_m8-v07_20261015-015010-05615df5.png",
}
const EXPECTED_SHA256 := {
	"selout-v8": "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd",
	"selout-v7-reference": "4ada7df785a2a6fd19dea74b199f28d9d2101bfe75f306529412d17a4d5bb295",
}
const EXPECTED_OPAQUE := {"selout-v8": 2419, "selout-v7-reference": 2419}
const EXPECTED_WINDOW := Vector2i(43, 96)
const EXPECTED_CHANGED_TEXELS := 793
# v7 coat slate roles P1 lit, P2 base, P3 shadow (v7 manifest new_colours 1-3).
const V7_COAT_RGB8 := [Color8(0x62, 0x5c, 0x61), Color8(0x46, 0x42, 0x4a), Color8(0x2d, 0x2c, 0x34)]
const TROUSER_ROWS := Vector2i(57, 85)
const BOOT_ROWS := Vector2i(85, 112)
const RING := 8
const ROW_BAND := 6
const AREA_SCENE := "res://scenes/scifi_exploration_area.tscn"
const ANNEX_SCENE := "res://scenes/survey_annex.tscn"
# scene key -> [kind, destination id, x offset from placeholder, lighting note] (same as v7)
const SCENES := {
	"city-bright": ["area", "scifi.city", 36.0, "science city, default first-visit layout (bright)"],
	"outskirts-bright": ["area", "scifi.outskirts", -36.0, "sunlit outskirts warm beige paving (bright)"],
	"survey-annex-room2-dark": ["annex", "scifi.city", 36.0, "city survey annex room 2 (darkest gameplay room)"],
}
const OUTPUT_DIR := "res://../outputs"
const TARGET_HEIGHT := 48
const ALPHA_THRESHOLD := 128
const RUN_ID := "20261015-021600-97a4fea2"


func _ready() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("M8_SELOUT_V8_QA: " + reason)
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


# sRGB (D65) -> CIELAB.
func _lab(c: Color) -> Vector3:
	var lin := []
	for v in [c.r, c.g, c.b]:
		lin.append(v / 12.92 if v <= 0.04045 else pow((v + 0.055) / 1.055, 2.4))
	var x: float = (0.4124 * lin[0] + 0.3576 * lin[1] + 0.1805 * lin[2]) / 0.95047
	var y: float = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
	var z: float = (0.0193 * lin[0] + 0.1192 * lin[1] + 0.9505 * lin[2]) / 1.08883
	var f := func(t: float) -> float: return pow(t, 1.0 / 3.0) if t > 0.008856 else 7.787 * t + 16.0 / 116.0
	return Vector3(116.0 * f.call(y) - 16.0, 500.0 * (f.call(x) - f.call(y)), 200.0 * (f.call(y) - f.call(z)))


func _median_color(pixels: Array) -> Color:
	var channels := [[], [], []]
	for c in pixels:
		channels[0].append(c.r)
		channels[1].append(c.g)
		channels[2].append(c.b)
	for ch in channels:
		ch.sort()
	var mid: int = channels[0].size() / 2
	return Color(channels[0][mid], channels[1][mid], channels[2][mid])


# Baseline pixels in a RING-px band around the pilot window, optionally limited to window rows
# [row_from, row_to) (window-relative; the band's own top/bottom rows count as rows -RING.. and
# h..h+RING).
func _ring_pixels(baseline: Image, window: Rect2i, row_from: int = -RING, row_to: int = 1 << 20) -> Array:
	var outer := window.grow(RING).intersection(Rect2i(Vector2i.ZERO, baseline.get_size()))
	var out := []
	for y in range(maxi(outer.position.y, window.position.y + row_from), mini(outer.end.y, window.position.y + row_to)):
		for x in range(outer.position.x, outer.end.x):
			if window.has_point(Vector2i(x, y)):
				continue
			out.append(baseline.get_pixel(x, y))
	return out


func _stats(values: Array) -> Dictionary:
	var sorted := values.duplicate()
	sorted.sort()
	var total := 0.0
	for v in sorted:
		total += v
	return {"texels": sorted.size(), "mean_dE76": snappedf(total / sorted.size(), 0.01),
		"p10_dE76": snappedf(sorted[int(floor(0.1 * (sorted.size() - 1)))], 0.01),
		"min_dE76": snappedf(sorted[0], 0.01)}


# Three contrast measures for the captured pixels at `offsets` (window-relative).
func _region_contrast(capture: Image, baseline: Image, window: Rect2i, offsets: Array, ring_lab: Vector3, row_lab: Array) -> Dictionary:
	var ring := []
	var rowl := []
	var occl := []
	for off in offsets:
		var shown := _lab(capture.get_pixelv(window.position + off))
		ring.append(shown.distance_to(ring_lab))
		rowl.append(shown.distance_to(row_lab[off.y]))
		occl.append(shown.distance_to(_lab(baseline.get_pixelv(window.position + off))))
	return {"ring_median": _stats(ring), "row_local_ring": _stats(rowl), "occluded_backdrop": _stats(occl)}


func _rect_json(rect: Rect2i) -> Dictionary:
	return {"x": rect.position.x, "y": rect.position.y, "w": rect.size.x, "h": rect.size.y}


func _capture() -> Image:
	await get_tree().process_frame
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	return get_tree().root.get_viewport().get_texture().get_image()


func _load_rgba(path: String) -> Image:
	var image := Image.new()
	if image.load(ProjectSettings.globalize_path(path)) != OK:
		return null
	image.convert(Image.FORMAT_RGBA8)
	return image


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
	# Region texel offsets, relative to the visible bounds, from the two source PNGs.
	var v8_image := _load_rgba(PILOT_PATHS["selout-v8"])
	var v7_image := _load_rgba(PILOT_PATHS["selout-v7-reference"])
	if v8_image == null or v7_image == null:
		_fail("cannot load source PNGs")
		return
	var vb := _alpha_bounds(v7_image)
	var regions := {"coat": [], "trousers": [], "boots": [], "whole_figure": []}
	for y in vb.size.y:
		for x in vb.size.x:
			var t7 := v7_image.get_pixel(vb.position.x + x, vb.position.y + y)
			if t7.a8 != 255:
				continue
			var off := Vector2i(x, y)
			var cell_y := vb.position.y + y
			regions["whole_figure"].append(off)
			var is_coat := false
			for slate in V7_COAT_RGB8:
				if t7.r8 == slate.r8 and t7.g8 == slate.g8 and t7.b8 == slate.b8:
					is_coat = true
			if is_coat:
				regions["coat"].append(off)
				continue
			var t8 := v8_image.get_pixel(vb.position.x + x, vb.position.y + y)
			if t8 == t7:
				continue
			if cell_y >= TROUSER_ROWS.x and cell_y < TROUSER_ROWS.y:
				regions["trousers"].append(off)
			elif cell_y >= BOOT_ROWS.x and cell_y < BOOT_ROWS.y:
				regions["boots"].append(off)
	var region_sizes := {}
	for k in regions.keys():
		region_sizes[k] = regions[k].size()
	print("REGIONS ", region_sizes)
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
	SaveStore.root_path = "user://test-saves/m8-selout-v8-qa"
	var app: Node = get_node("/root/AppState")
	var captures: Array = []
	var v8_vs_v7 := {}
	var contrast_table := {}
	for scene_key in SCENES.keys():
		var spec: Array = SCENES[scene_key]
		var scene_captures := {}
		var scene_windows := {}
		contrast_table[scene_key] = {}
		for variant in PILOT_PATHS.keys():
			# Load from disk so the candidate does not need a Godot import entry.
			var pilot_abs := ProjectSettings.globalize_path(PILOT_PATHS[variant])
			var pilot_image := _load_rgba(PILOT_PATHS[variant])
			if pilot_image == null:
				_fail("cannot load candidate PNG " + pilot_abs)
				return
			var pilot_bounds := _alpha_bounds(pilot_image)
			if pilot_bounds.size != EXPECTED_WINDOW or pilot_bounds != vb:
				_fail("%s visible bounds %s, expected %s at %s" % [variant, str(pilot_bounds.size), str(EXPECTED_WINDOW), str(vb.position)])
				return
			app.begin_new_run()
			app.hero_appearance = "female"
			if not app.select_destination(spec[1]):
				_fail("destination rejected: " + spec[1])
				return
			if spec[0] == "annex":
				app.current_annex_room = 2
			var scene_path: String = {"area": AREA_SCENE, "annex": ANNEX_SCENE}[spec[0]]
			var host: Node2D = (load(scene_path) as PackedScene).instantiate()
			add_child(host)
			await get_tree().process_frame
			await get_tree().process_frame
			host.set_process(false)
			if String(host.get("destination_id")) != spec[1]:
				_fail("scene fell back to %s instead of %s" % [host.get("destination_id"), spec[1]])
				return
			var hero: Sprite2D = host.get("hero")
			var placeholder_image := hero.texture.get_image()
			placeholder_image.convert(Image.FORMAT_RGBA8)
			var placeholder_bounds := _alpha_bounds(placeholder_image)
			# Ground row of the placeholder's lowest opaque pixel, in scene logical pixels.
			var texture_top := hero.position.y + hero.offset.y - placeholder_image.get_height() * 0.5
			var ground_y := texture_top + placeholder_bounds.end.y
			var pilot_x := hero.position.x + float(spec[2])
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
			if diff.size != EXPECTED_WINDOW:
				_fail("%s %s: diff window %s is not the 1:1 visible bounds %s" % [scene_key, variant, str(diff.size), str(EXPECTED_WINDOW)])
				return
			var fidelity := _texel_fidelity(pilot_image, pilot_bounds, capture, diff)
			if fidelity["exact_rgb_matches"] != fidelity["opaque_texels"]:
				_fail("%s %s: texel fidelity %d/%d" % [scene_key, variant, fidelity["exact_rgb_matches"], fidelity["opaque_texels"]])
				return
			if fidelity["opaque_texels"] != EXPECTED_OPAQUE[variant]:
				_fail("%s opaque texels %d, expected %d" % [variant, fidelity["opaque_texels"], EXPECTED_OPAQUE[variant]])
				return
			var ring_bg := _median_color(_ring_pixels(baseline, diff))
			var row_lab := []
			for wy in diff.size.y:
				row_lab.append(_lab(_median_color(_ring_pixels(baseline, diff, wy - ROW_BAND, wy + ROW_BAND + 1))))
			var contrast := {}
			for k in regions.keys():
				contrast[k] = _region_contrast(capture, baseline, diff, regions[k], _lab(ring_bg), row_lab)
			contrast_table[scene_key][variant] = contrast
			var stem := "rpg-2-star-ocean-the-second_%s_protagonist-female-south-idle-%s-h48_m8-v08_%s-%s" % [scene_key, variant, stamp, unique_id]
			var capture_path := output_path.path_join(stem + ".png")
			if capture.save_png(capture_path) != OK:
				_fail("cannot save capture")
				return
			scene_captures[variant] = capture
			scene_windows[variant] = diff
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
				"background_ring_median_rgb8": [ring_bg.r8, ring_bg.g8, ring_bg.b8],
				"contrast_dE76": contrast,
				"shadow": "none",
				"placeholder_texture_path": hero.texture.resource_path,
				"placeholder_texture_size": [placeholder_image.get_width(), placeholder_image.get_height()],
				"placeholder_visible_bounds": _rect_json(placeholder_bounds),
				"placeholder_position_logical": [hero.position.x, hero.position.y],
			}
			captures.append(entry)
			print("CAPTURE %s %s  diff %s  fidelity %d/%d  ring_bg %s  sha %s  %s" % [
				scene_key, variant, str(diff), fidelity["exact_rgb_matches"], fidelity["opaque_texels"],
				str(entry["background_ring_median_rgb8"]), entry["capture_sha256"], capture_path])
			for k in contrast.keys():
				var c: Dictionary = contrast[k]
				print("   %-12s ring %6.2f/%6.2f  rowlocal mean %6.2f p10 %6.2f min %6.2f  occluded mean %6.2f p10 %6.2f min %6.2f" % [
					k, c["ring_median"]["mean_dE76"], c["ring_median"]["min_dE76"],
					c["row_local_ring"]["mean_dE76"], c["row_local_ring"]["p10_dE76"], c["row_local_ring"]["min_dE76"],
					c["occluded_backdrop"]["mean_dE76"], c["occluded_backdrop"]["p10_dE76"], c["occluded_backdrop"]["min_dE76"]])
			host.queue_free()
			await get_tree().process_frame
			await get_tree().process_frame
		if scene_windows["selout-v8"] != scene_windows["selout-v7-reference"]:
			_fail("%s: v8 and v7 windows differ (%s vs %s); positions must be identical" % [scene_key, str(scene_windows["selout-v8"]), str(scene_windows["selout-v7-reference"])])
			return
		# Same scene, same placement, identical alpha: exactly the recoloured texels must differ.
		var changed := _diff_count(scene_captures["selout-v8"], scene_captures["selout-v7-reference"])
		v8_vs_v7[scene_key] = {"changed_window_pixels": changed,
			"expected_changed_texels": EXPECTED_CHANGED_TEXELS,
			"matches_expected": changed == EXPECTED_CHANGED_TEXELS,
			"identical_window": _rect_json(scene_windows["selout-v8"]),
			"changed_bounds": _rect_json(_diff_bounds(scene_captures["selout-v8"], scene_captures["selout-v7-reference"]))}
		print("V8_VS_V7 %s changed_window_pixels %d (expected %d)" % [scene_key, changed, EXPECTED_CHANGED_TEXELS])
		if changed != EXPECTED_CHANGED_TEXELS:
			_fail("%s: v8 vs v7 changed window pixels %d, expected exactly %d (v8 is recolour-only)" % [scene_key, changed, EXPECTED_CHANGED_TEXELS])
			return
	var report := {
		"project": "Worlds Between",
		"milestone": "M8",
		"purpose": "In-engine readability captures of the female south-idle selout v8 cloth/leather candidate (storm-slate coat, spruce-grey trousers, deeper warm boots) at 48 logical px beside the 32x48 placeholder: bright science city, bright outskirts, dark city survey annex room 2; selout v7 captured in the same run at the identical position as A/B reference.",
		"status": "technical visual QA only; unapproved candidate; not integrated",
		"art_approved": false,
		"human_reviewed": false,
		"acceptance_counters_unchanged": {"runtime_exploration_sprites_accepted": "0/52", "scene_quality_gates_passed": "0/11"},
		"qa_script": "game/tests/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-visual-qa_m8-v08_%s.gd" % RUN_ID,
		"renderer": "Godot %s windowed, viewport texture capture" % Engine.get_version_info()["string"],
		"canvas": [640, 360],
		"window": [1280, 720],
		"camera": "none; scenes draw a fixed 640x360 canvas",
		"pilot_loading": "Image.load from disk (no import); ImageTexture; nearest filtering; no shadow",
		"sources": sources,
		"gates_passed": ["source SHA-256 lock", "1280x720 captures", "visible bounds and diff window 43x96 (1:1)", "100% texel fidelity per candidate", "opaque texels 2419 for v8 and v7", "v8 and v7 identical window rect per scene", "v8 vs v7 changed window pixels = 793 in every scene"],
		"regions": {"definition": "coat = opaque texels whose v7 colour is v7 slate P1/P2/P3; trousers = texels v8 changes in cell rows 57-84 that are not coat; boots = texels v8 changes in rows 85-111; whole_figure = all opaque texels. Same window-relative positions for v8 and v7.", "texels": region_sizes},
		"contrast_measures": {
			"ring_median": "dE76 vs the per-channel median of the baseline in an %d px ring around the window (the v7 note's method)" % RING,
			"row_local_ring": "dE76 vs the per-channel median of the ring pixels within +/-%d window rows of the texel" % ROW_BAND,
			"occluded_backdrop": "dE76 vs the pilot-free baseline pixel at the same window position",
			"stats": "mean, 10th percentile and minimum over the region's texels",
		},
		"contrast_dE76_by_scene": contrast_table,
		"v8_vs_v7_same_scene": v8_vs_v7,
		"captures": captures,
		"limitations": [
			"Static south idle only; no walk frames or other facings.",
			"Only first-visit default area state captured; area _process disabled after two frames.",
			"Survey annex is captured in room 2 of the city annex (current_annex_room set to 2 for the test only) with default state.",
			"dE76 is a colour-difference proxy; it does not model the 1-texel ink outline, which both variants share unchanged.",
			"selout-v7-reference captures exist only for same-run A/B comparison; v7 is not modified.",
			"human_reviewed is false at capture time; any later user review is recorded elsewhere, not by rewriting this report.",
			"Readability judgement in this report is automated measurement only; visual review is still required.",
		],
	}
	var report_path := output_path.path_join("rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v8-visual-qa-report_m8-v08_%s-%s.json" % [stamp, unique_id])
	var file := FileAccess.open(report_path, FileAccess.WRITE)
	if file == null:
		_fail("cannot write report")
		return
	file.store_string(JSON.stringify(report, "\t") + "\n")
	file.close()
	print("STATUS unapproved candidate; technical visual QA only")
	print("REPORT " + report_path)
	get_tree().quit(0)
