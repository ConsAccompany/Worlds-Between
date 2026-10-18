extends SceneTree

# Real-Godot review captures for the UNAPPROVED, NONRUNTIME Ji Cheng (纪澄) south idle static pilot (v01, run 04cd6a26)
# at exactly 48 logical px: the project's own display settings (640x360 canvas, canvas_items, 1280x720 window), sprite
# scale 0.5 (96 texels -> 48 logical px, 1 texel = 1 window px), nearest filter, no shadow.
# Test-harness override only: the runtime's old placeholder hero is hidden (visible = false) and the pilot is drawn
# at the hero spot by its foot pin (cell (40,104)). No game/ file is added or edited; runtime stays unchanged.
# Scenes: science city (bright, default first-visit layout) and city survey annex room 2 (dark interior), each in the
# Chinese and English UI (AppState.language), as the female v8 / Liang / male pilot captures.
# Per scene x language: one 1280x720 PNG of the pilot alone (1x: what the default window shows), a 2x nearest review
# crop of it, and one NATIVE 640x360 window capture (window resized to the canvas size: 1 logical px = 1 window px, so
# the 96-texel sprite is nearest-subsampled 2:1 to 48 px, as a 640x360 window would show it). Per scene (English UI)
# one extra 1280x720 frame with the approved female v8 standing beside the pilot as density/scale pair, plus its 2x
# crop. Each is a separate PNG; no collage.
# Gates (exit 1, no report on failure): source SHA-256 locks (pilot, v8); 1280x720 captures; pilot diff window exactly
# 42x96 (96 window px = 48 logical px) and v8 exactly 43x96; 100% exact-RGB texel match for both; pivot: the pilot
# window's left/bottom edges equal 2*spot_x - 24 / 2*ground_y (pin column 40 lands on the hero spot, sole row 103 is
# the last row above the ground line); v8 window does not touch the pilot window; native 640 capture is 640x360 and
# the pilot's diff window there is exactly 48 px tall with its bottom on ground_y.
# Contrast (reported, not gated): CIELAB dE76 per region vs an 8 px ring median, as in the earlier pilot QA.
# Lives in tools/ (outside res://). Run windowed from the worktree root after one `--headless --path game --import`:
#   <Godot 4.7.2 console exe> --path game -s <absolute path of this file>
const JI_PATH := "res://assets/characters/ji-cheng-hd/rpg-2-star-ocean-the-second_ji-cheng_south-idle-static_unapproved-v01_20261018-132812-1920ff13.png"
const JI_SHA256 := "58c92f51959aa7b34dfc9d37c953665579fe75b5629e6d8c807180cba4a32a1d"
const JI_PIN := Vector2i(40, 104)
const JI_WINDOW := Vector2i(42, 96)
const JI_OPAQUE := 2820
const V8_PATH := "res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png"
const V8_SHA256 := "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"
const V8_WINDOW := Vector2i(43, 96)
const V8_OPAQUE := 2419
const AREA_SCENE := "res://scenes/scifi_exploration_area.tscn"
const ANNEX_SCENE := "res://scenes/survey_annex.tscn"
# scene key -> [kind, destination, v8 x offset from the hero spot (logical px), note]
const SCENES := {
	"city-bright": ["area", "scifi.city", 40.0, "science city, default first-visit layout (bright)"],
	"annex-room2-dark": ["annex", "scifi.city", 80.0, "city survey annex room 2 (dark interior)"],
}
const LANGS := ["zh", "en"]
const PAIR_LANG := "en"
const TARGET_HEIGHT := 48
const ALPHA_THRESHOLD := 128
const RING := 8
const CROP := Vector2i(120, 128)
const OUTPUT_DIR := "res://../outputs"
const TAG := "south-idle-static"
# Region colour sets (tool RAMPS) + cell-row limits.
const HAIR_HEX := ["6c7482", "434852", "292c34", "111216"]
const SILVER_HEX := ["e2e4e6", "b2b8c0", "7e848e"]
const SHAVED_HEX := ["c4aca2", "927e84"]
const SKIN_HEX := ["f0d0bc", "d8aa94", "b47e6c"]
const COAT_HEX := ["5a7450", "3c5338", "223524", "0f1a11"]
const LENS_HEX := ["d2e4e8", "7c98a2"]
const BRASS_HEX := ["e2c272", "a8844a", "6c5432"]
const CLOTH_HEX := ["dcd0b2", "a89c84"]
const DARK_HEX := ["3c3c46", "1f1f26", "504e58", "32313a", "19181e"]
const BOOT_HEX := ["54494a", "2e2629"]

var app: Node


func _initialize() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("JI_CHENG_STATIC_CAPTURE FAIL: " + reason)
	print("JI_CHENG_STATIC_CAPTURE FAIL: " + reason)
	quit(1)


func _load_rgba(path: String) -> Image:
	var image := Image.load_from_file(ProjectSettings.globalize_path(path))
	if image == null:
		return null
	image.convert(Image.FORMAT_RGBA8)
	return image


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
	return Rect2i(left, top, right - left + 1, bottom - top + 1) if right >= 0 else Rect2i()


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
	return Rect2i(left, top, right - left + 1, bottom - top + 1) if right >= 0 else Rect2i()


func _fidelity(pilot: Image, bounds: Rect2i, capture: Image, window: Rect2i) -> Dictionary:
	var total := 0
	var exact := 0
	for y in bounds.size.y:
		for x in bounds.size.x:
			var t := pilot.get_pixel(bounds.position.x + x, bounds.position.y + y)
			if t.a8 < ALPHA_THRESHOLD:
				continue
			total += 1
			var s := capture.get_pixel(window.position.x + x, window.position.y + y)
			if s.r8 == t.r8 and s.g8 == t.g8 and s.b8 == t.b8:
				exact += 1
	return {"opaque_texels": total, "exact_rgb_matches": exact}


func _palette_share(pilot: Image, bounds: Rect2i, before: Image, capture: Image, window: Rect2i) -> Dictionary:
	# native 640 view: every changed window pixel must be one of the pilot's own colours (nearest sampling, no blend)
	var colours := {}
	for y in bounds.size.y:
		for x in bounds.size.x:
			var t := pilot.get_pixel(bounds.position.x + x, bounds.position.y + y)
			if t.a8 >= ALPHA_THRESHOLD:
				colours[t.to_html(false)] = true
	var changed := 0
	var in_palette := 0
	for y in range(window.position.y, window.end.y):
		for x in range(window.position.x, window.end.x):
			var c := capture.get_pixel(x, y)
			if c == before.get_pixel(x, y):
				continue
			if colours.has(c.to_html(false)):
				in_palette += 1
			changed += 1
	return {"changed_pixels": changed, "changed_pixels_in_pilot_palette": in_palette}


func _lab(c: Color) -> Vector3:
	var lin := []
	for v in [c.r, c.g, c.b]:
		lin.append(v / 12.92 if v <= 0.04045 else pow((v + 0.055) / 1.055, 2.4))
	var x: float = (0.4124 * lin[0] + 0.3576 * lin[1] + 0.1805 * lin[2]) / 0.95047
	var y: float = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
	var z: float = (0.0193 * lin[0] + 0.1192 * lin[1] + 0.9505 * lin[2]) / 1.08883
	var f := func(t: float) -> float: return pow(t, 1.0 / 3.0) if t > 0.008856 else 7.787 * t + 16.0 / 116.0
	return Vector3(116.0 * f.call(y) - 16.0, 500.0 * (f.call(x) - f.call(y)), 200.0 * (f.call(y) - f.call(z)))


func _median(pixels: Array) -> Color:
	var ch := [[], [], []]
	for c in pixels:
		ch[0].append(c.r)
		ch[1].append(c.g)
		ch[2].append(c.b)
	for a in ch:
		a.sort()
	var mid: int = ch[0].size() / 2
	return Color(ch[0][mid], ch[1][mid], ch[2][mid])


func _ring(baseline: Image, window: Rect2i) -> Array:
	var outer := window.grow(RING).intersection(Rect2i(Vector2i.ZERO, baseline.get_size()))
	var out := []
	for y in range(outer.position.y, outer.end.y):
		for x in range(outer.position.x, outer.end.x):
			if not window.has_point(Vector2i(x, y)):
				out.append(baseline.get_pixel(x, y))
	return out


func _contrast(capture: Image, baseline: Image, window: Rect2i, offsets: Array) -> Dictionary:
	var ring_lab := _lab(_median(_ring(baseline, window)))
	var vals := []
	for off in offsets:
		vals.append(_lab(capture.get_pixelv(window.position + off)).distance_to(ring_lab))
	vals.sort()
	var total := 0.0
	for v in vals:
		total += v
	return {"texels": vals.size(), "mean_dE76": snappedf(total / vals.size(), 0.01),
		"p10_dE76": snappedf(vals[int(floor(0.1 * (vals.size() - 1)))], 0.01), "min_dE76": snappedf(vals[0], 0.01)}


func _regions(image: Image, b: Rect2i) -> Dictionary:
	var r := {"whole_figure": [], "hair_black": [], "silver_tips": [], "shaved_temple": [], "face_skin": [], "coat": [],
		"magnifier": [], "cloth_panels": [], "dark_clothes": [], "boots": []}
	for y in b.size.y:
		for x in b.size.x:
			var cx := b.position.x + x
			var cy := b.position.y + y
			var t := image.get_pixel(cx, cy)
			if t.a8 < ALPHA_THRESHOLD:
				continue
			var off := Vector2i(x, y)
			var hx := t.to_html(false)
			r["whole_figure"].append(off)
			if HAIR_HEX.has(hx) and cy <= 41:
				r["hair_black"].append(off)
			elif SILVER_HEX.has(hx) and cy <= 42 and cx >= 26:
				r["silver_tips"].append(off)
			elif SHAVED_HEX.has(hx):
				r["shaved_temple"].append(off)
			elif SKIN_HEX.has(hx) and cy <= 33:
				r["face_skin"].append(off)
			elif COAT_HEX.has(hx):
				r["coat"].append(off)
			elif (LENS_HEX.has(hx) or BRASS_HEX.has(hx)) and cy <= 33 and cx <= 24:
				r["magnifier"].append(off)
			elif CLOTH_HEX.has(hx) and cy >= 56:
				r["cloth_panels"].append(off)
			elif DARK_HEX.has(hx):
				r["dark_clothes"].append(off)
			elif BOOT_HEX.has(hx) and cy >= 88:
				r["boots"].append(off)
	return r


func _whole(image: Image, b: Rect2i) -> Array:
	var out := []
	for y in b.size.y:
		for x in b.size.x:
			if image.get_pixel(b.position.x + x, b.position.y + y).a8 >= ALPHA_THRESHOLD:
				out.append(Vector2i(x, y))
	return out


func _sprite(image: Image, anchor: Vector2, x: float, ground_y: float) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = ImageTexture.create_from_image(image)
	s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	s.centered = false
	s.offset = -anchor
	s.scale = Vector2.ONE * (float(TARGET_HEIGHT) / 96.0)
	s.position = Vector2(x, ground_y)
	s.z_index = int(ground_y)
	return s


func _grab() -> Image:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var img := root.get_viewport().get_texture().get_image()
	img.convert(Image.FORMAT_RGBA8)
	return img


func _resize_window(size: Vector2i) -> void:
	root.size = size
	for i in 4:
		await process_frame


func _rect_json(r: Rect2i) -> Dictionary:
	return {"x": r.position.x, "y": r.position.y, "w": r.size.x, "h": r.size.y}


func _save(img: Image, name: String) -> String:
	var path := ProjectSettings.globalize_path(OUTPUT_DIR).path_join(name)
	if img.save_png(path) != OK:
		return ""
	return path


func _crop2x(img: Image, around: Rect2i) -> Image:
	var size := Vector2i(maxi(CROP.x, around.size.x + 24), maxi(CROP.y, around.size.y + 32))
	var r := Rect2i(around.get_center() - size / 2, size).intersection(Rect2i(Vector2i.ZERO, img.get_size()))
	var out := img.get_region(r)
	out.resize(r.size.x * 2, r.size.y * 2, Image.INTERPOLATE_NEAREST)
	return out


func _run() -> void:
	if DisplayServer.get_name() == "headless":
		_fail("windowed run required")
		return
	var sources := {}
	for pair in [["ji-cheng-pilot", JI_PATH, JI_SHA256], ["female-v8-approved", V8_PATH, V8_SHA256]]:
		var digest := FileAccess.get_sha256(ProjectSettings.globalize_path(pair[1]))
		if digest != pair[2]:
			_fail("%s SHA-256 %s != %s" % [pair[0], digest, pair[2]])
			return
		sources[pair[0]] = {"path": pair[1], "sha256": digest}
	var ji := _load_rgba(JI_PATH)
	var v8 := _load_rgba(V8_PATH)
	if ji == null or v8 == null:
		_fail("cannot load source PNGs")
		return
	var jb := _alpha_bounds(ji)
	var vb := _alpha_bounds(v8)
	if jb.size != JI_WINDOW or vb.size != V8_WINDOW or jb.end.y != JI_PIN.y:
		_fail("visible bounds %s / %s" % [str(jb), str(vb)])
		return
	var regions := _regions(ji, jb)
	var region_sizes := {}
	for k in regions.keys():
		region_sizes[k] = regions[k].size()
	var v8_offsets := _whole(v8, vb)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	await _resize_window(Vector2i(1280, 720))
	var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var uid := "%08x" % (randi() & 0xffffffff)
	SaveStore.root_path = "user://test-saves/ji-cheng-south-idle-static-v01"
	app = root.get_node("AppState")
	var captures := []
	var contrast_table := {}
	for key in SCENES.keys():
		for lang in LANGS:
			var spec: Array = SCENES[key]
			app.begin_new_run()
			app.hero_appearance = "female"
			app.language = lang
			if not app.select_destination(spec[1]):
				_fail("destination rejected: " + spec[1])
				return
			if spec[0] == "annex":
				app.current_annex_room = 2
			var host: Node2D = (load(AREA_SCENE if spec[0] == "area" else ANNEX_SCENE) as PackedScene).instantiate()
			root.add_child(host)
			current_scene = host
			await process_frame
			await process_frame
			host.set_process(false)
			if String(host.get("destination_id")) != spec[1]:
				_fail("scene fell back to " + String(host.get("destination_id")))
				return
			var hero: Sprite2D = host.get("hero")
			var ph := hero.texture.get_image()
			ph.convert(Image.FORMAT_RGBA8)
			var pb := _alpha_bounds(ph)
			# test-harness override: hide the old placeholder, stand the pilot on its ground point
			var ground_y := snappedf(hero.position.y + hero.offset.y - ph.get_height() * 0.5 + pb.end.y, 0.5)
			var spot_x := snappedf(hero.position.x, 0.5)
			hero.visible = false
			var baseline := await _grab()
			var js := _sprite(ji, Vector2(JI_PIN), spot_x, ground_y)
			host.add_child(js)
			var solo := await _grab()
			if solo.get_size() != Vector2i(1280, 720):
				_fail("capture size " + str(solo.get_size()))
				return
			var jw := _diff_bounds(baseline, solo)
			if jw.size != JI_WINDOW:
				_fail("%s/%s: pilot window %s is not 1:1 %s" % [key, lang, str(jw), str(JI_WINDOW)])
				return
			var pivot := {"pin_cell": [JI_PIN.x, JI_PIN.y], "spot_logical": [spot_x, ground_y],
				"expected_window_left": int(round(2.0 * spot_x)) - (JI_PIN.x - jb.position.x),
				"expected_window_bottom_exclusive": int(round(2.0 * ground_y)),
				"window_left": jw.position.x, "window_bottom_exclusive": jw.end.y,
				"window_height_px": jw.size.y, "logical_height_px": jw.size.y / 2.0}
			if jw.position.x != pivot["expected_window_left"] or jw.end.y != pivot["expected_window_bottom_exclusive"]:
				_fail("%s/%s: pivot %s" % [key, lang, str(pivot)])
				return
			var jf := _fidelity(ji, jb, solo, jw)
			if jf["exact_rgb_matches"] != jf["opaque_texels"] or jf["opaque_texels"] != JI_OPAQUE:
				_fail("%s/%s: pilot fidelity %s" % [key, lang, str(jf)])
				return
			var contrast := {}
			for k in regions.keys():
				contrast[k] = _contrast(solo, baseline, jw, regions[k])
			var ring_bg := _median(_ring(baseline, jw))
			var base := "rpg-2-star-ocean-the-second_ji-cheng_%s-%s-%s" % [TAG, key, lang]
			var items := [["solo-1280-1x", solo, jw], ["solo-1280-2x-crop", _crop2x(solo, jw), jw]]
			var vw := Rect2i()
			var vf := {}
			if lang == PAIR_LANG:
				var vs := _sprite(v8, Vector2(vb.position.x + vb.size.x * 0.5, vb.end.y), spot_x + float(spec[2]), ground_y)
				host.add_child(vs)
				var bench := await _grab()
				vw = _diff_bounds(solo, bench)
				if vw.size != V8_WINDOW or vw.intersects(jw) or vw.end.y != jw.end.y:
					_fail("%s: v8 window %s (pilot %s)" % [key, str(vw), str(jw)])
					return
				vf = _fidelity(v8, vb, bench, vw)
				if vf["exact_rgb_matches"] != vf["opaque_texels"] or vf["opaque_texels"] != V8_OPAQUE:
					_fail("%s: v8 fidelity %s" % [key, str(vf)])
					return
				contrast["v8_benchmark_whole_figure"] = _contrast(bench, solo, vw, v8_offsets)
				items.append(["with-female-v8-1280-1x", bench, jw])
				items.append(["with-female-v8-1280-2x-crop", _crop2x(bench, jw.merge(vw)), jw])
				vs.queue_free()
				await process_frame
			# native 640x360 window: same scene, same placement, 1 logical px = 1 window px
			js.visible = false
			await _resize_window(Vector2i(640, 360))
			var nbase := await _grab()
			js.visible = true
			var native := await _grab()
			if native.get_size() != Vector2i(640, 360):
				_fail("%s/%s: native capture size %s" % [key, lang, str(native.get_size())])
				return
			var nw := _diff_bounds(nbase, native)
			var native_info := {"window": _rect_json(nw), "expected_height_px": TARGET_HEIGHT,
				"expected_bottom_exclusive": int(round(ground_y)),
				"palette_share": _palette_share(ji, jb, nbase, native, nw)}
			if nw.size.y != TARGET_HEIGHT or nw.end.y != int(round(ground_y)):
				_fail("%s/%s: native window %s" % [key, lang, str(native_info)])
				return
			items.append(["native-640-1x", native, nw])
			await _resize_window(Vector2i(1280, 720))
			contrast_table["%s-%s" % [key, lang]] = contrast
			for item in items:
				var name: String = "%s-%s_unapproved-v01_%s-%s.png" % [base, item[0], stamp, uid]
				var path := _save(item[1], name)
				if path == "":
					_fail("cannot save " + name)
					return
				var is_native: bool = item[0].begins_with("native")
				captures.append({"scene": key, "language": lang, "scene_note": spec[3], "content": item[0],
					"scale_label": "640x360 window, 1 logical px = 1 window px, 96 texels nearest-subsampled to 48 px" if is_native else ("1280x720 window, 1 texel = 1 window px = 0.5 logical px" if item[0].ends_with("1x") else "1280x720 window crop, nearest x2 for review only (2 screen px per window px)"),
					"capture": "outputs/" + name, "capture_sha256": FileAccess.get_sha256(path),
					"capture_size": [(item[1] as Image).get_width(), (item[1] as Image).get_height()],
					"pilot_window": _rect_json(item[2]),
					"pilot_texel_fidelity": null if is_native else jf, "pivot": null if is_native else pivot,
					"native_640": native_info if is_native else null,
					"v8_window": _rect_json(vw) if item[0].begins_with("with") else null,
					"v8_texel_fidelity": vf if item[0].begins_with("with") else null,
					"placeholder_hidden": not hero.visible, "placeholder_texture": hero.texture.resource_path,
					"background_ring_median_rgb8": [ring_bg.r8, ring_bg.g8, ring_bg.b8]})
				print("CAPTURE %s %s %s %s" % [key, lang, item[0], path])
			for k in contrast.keys():
				print("   %-26s mean %6.2f p10 %6.2f min %6.2f" % [k, contrast[k]["mean_dE76"], contrast[k]["p10_dE76"], contrast[k]["min_dE76"]])
			host.queue_free()
			await process_frame
			await process_frame
	var report := {
		"project": "Worlds Between", "milestone": "M8",
		"purpose": "Real Godot captures of the UNAPPROVED, NONRUNTIME Ji Cheng (纪澄) south idle static pilot at exactly 48 logical px in the bright science city and the dark survey annex room 2, Chinese and English UI; old placeholder hidden by the test harness; pilot alone (1280 window 1x + 2x crop + native 640x360 window) and, in English, beside the approved female v8 (1280 window 1x + 2x crop).",
		"status": "technical visual QA only; UNAPPROVED; NONRUNTIME; not integrated", "art_approved": false, "human_reviewed": false,
		"acceptance_counters_unchanged": {"runtime_sprites_accepted": "0/52", "scene_visual_gates": "3/12", "overall_meter": "40.8%", "plays": "0/2"},
		"capture_tool": "tools/rpg-2-star-ocean-the-second_ji-cheng_south-idle-static-pilot-godot-capture_unapproved-v01_20261018-132812-81f87641.gd",
		"placement": "pilot by its foot pin (cell 40,104) at the hidden placeholder hero's spot (snapped to 0.5 logical px); v8 bounds-centred at the earlier reviewed pair spots (city hero x + 40, annex hero x + 80 logical px)",
		"renderer": "Godot %s windowed, viewport texture capture" % Engine.get_version_info()["string"],
		"canvas": [640, 360], "window": [1280, 720], "native_window": [640, 360], "sprite_scale": 0.5, "display_logical_height": 48, "filter": "nearest", "shadow": "none",
		"review_scales": {"solo-1280-1x": "1280x720 window capture as displayed by default (1 texel = 1 window px = 0.5 logical px)",
			"solo-1280-2x-crop": "window-px crop around the figure(s) (at least 120x128, figures + 12 px margin), nearest x2; review aid only",
			"native-640-1x": "window resized to 640x360 (canvas size): 1 logical px = 1 window px; the 96-texel sprite is nearest-subsampled 2:1 to 48 px, so about half the texels are not shown"},
		"hero_appearance": "female (placeholder hidden; irrelevant to the pilot)", "placeholder": "hidden (visible = false) in every frame; runtime files unchanged",
		"sources": sources,
		"gates_passed": ["source SHA-256 locks (pilot, v8)", "1280x720 captures", "pilot window 42x96 = 48 logical px (1:1)",
			"pilot texel match 2820/2820 exact RGB", "pivot: window left = 2*spot_x - 24, window bottom = 2*ground_y",
			"v8 window 43x96 (1:1), texel match 2419/2419, same ground row, no overlap with the pilot",
			"native 640x360 capture, pilot window 48 px tall, bottom on ground_y"],
		"regions": {"definition": "colour-set regions of the pilot (tool RAMPS); hair_black rows <= 41; silver_tips rows <= 42, x >= 26 (excludes the hip vials); magnifier rows <= 33, x <= 24; cloth_panels rows >= 56; boots rows >= 88; v8_benchmark_whole_figure = v8's opaque texels in the pair frame vs the pilot-only frame", "texels": region_sizes},
		"contrast_dE76_vs_8px_ring_median_by_scene_language": contrast_table,
		"captures": captures,
		"limitations": [
			"Static south idle only; one position per scene; first-visit default state; scene _process disabled.",
			"The placeholder is hidden by this test harness only; the game still shows the old placeholder hero and the old 32x48 Ji Cheng.",
			"Native 640x360 drops every other texel row/column (nearest), so thin details (razor lines, toggles, strap buckles) can vanish there.",
			"1920x1080 / fullscreen sampling (1.5 px per texel) not captured.",
			"dE76 is a proxy only; visual judgement is for Codex and the creator.",
		],
	}
	var rpath := ProjectSettings.globalize_path(OUTPUT_DIR).path_join("rpg-2-star-ocean-the-second_ji-cheng_%s-godot-capture-report_unapproved-v01_%s-%s.json" % [TAG, stamp, uid])
	var f := FileAccess.open(rpath, FileAccess.WRITE)
	if f == null:
		_fail("cannot write report")
		return
	f.store_string(JSON.stringify(report, "\t") + "\n")
	f.close()
	print("REPORT " + rpath)
	print("STATUS unapproved nonruntime pilot; technical visual QA only")
	quit(0)
