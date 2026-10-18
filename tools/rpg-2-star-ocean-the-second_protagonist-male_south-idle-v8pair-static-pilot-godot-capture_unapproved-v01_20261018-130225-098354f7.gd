extends SceneTree

# Real-Godot review captures for the UNAPPROVED, NONRUNTIME male protagonist south idle static pilot paired to the
# approved female selout v8 (v01, run 3617dbe6), at exactly 48 logical px: the project's own display settings
# (640x360 canvas, canvas_items, 1280x720 window), sprite scale 0.5 (96 texels -> 48 logical px, 1 texel = 1 window
# px), nearest filter, no shadow.
# Test-harness override only: the runtime's old placeholder hero is hidden (visible = false) and the pilot is drawn
# at the hero spot by its foot pin (cell (40,104)). No game/ file is added or edited; runtime stays unchanged.
# Scenes: science city (bright, default first-visit layout) and city survey annex room 2 (dark interior), each in the
# Chinese and English UI (AppState.language), as the female v8 / Liang / male v02 captures.
# Per scene x language one separate 1280x720 PNG of the pilot alone (native 1x: what the game window shows) plus a
# 2x nearest review crop of it; per scene (English UI) one extra frame with the approved female v8 standing beside
# the pilot as density/scale pair, plus its 2x crop. No collage of separate requests.
# Gates (exit 1, no report on failure): source SHA-256 locks (pilot, v8); 1280x720 captures; pilot diff window exactly
# 39x96 (96 window px = 48 logical px) and v8 exactly 43x96; 100% exact-RGB texel match for both; pivot: the pilot
# window's left/bottom edges equal 2*pin_x - 18 / 2*ground_y (pin column 40 lands on the hero spot, sole row 103 is
# the last row above the ground line); v8 window does not touch the pilot window.
# Contrast (reported, not gated): CIELAB dE76 per region vs an 8 px ring median, as in the earlier pilot QA.
# Lives in tools/ (outside res://). Run windowed from the worktree root after one `--headless --path game --import`:
#   <Godot 4.7.2 console exe> --path game -s <absolute path of this file>
const MALE_PATH := "res://assets/characters/protagonist-male-v8pair/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair_unapproved-v01_20261018-130225-79ed5d37.png"
const MALE_SHA256 := "e4b2db368f65e158724dff4c8844fe2dcabf9f9b7f7a9aa3807d76bd72409af2"
const MALE_PIN := Vector2i(40, 104)
const MALE_WINDOW := Vector2i(39, 96)
const MALE_OPAQUE := 2488
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
const TAG := "south-idle-v8pair"
# Region colour sets (tool RAMPS) + cell-row limits.
const HAIR_HEX := ["735442", "4b362b", "30231d", "1f1614"]
const SKIN_HEX := ["f0c090", "d49868", "a86a48", "7a4234"]
const SCARF_HEX := ["82c8b8", "46988c", "2a6660"]
const BEDROLL_HEX := ["5e9c9c", "3c7678", "28505a"]
const COAT_HEX := ["8c7664", "6a5b4e", "4a3e36", "2b2422"]
const SHIRT_HEX := ["efe6d2", "c9bea6", "978a76"]
const TROUSER_HEX := ["7e7a62", "5c5a4a", "3c3b30"]
const BOOT_HEX := ["8c5a3a", "623d2a", "3a2520"]

var app: Node


func _initialize() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("MALE_V8PAIR_CAPTURE FAIL: " + reason)
	print("MALE_V8PAIR_CAPTURE FAIL: " + reason)
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
	var r := {"whole_figure": [], "hair": [], "face_skin": [], "scarf": [], "bedroll": [], "coat": [], "shirt": [],
		"trousers": [], "boots": []}
	for y in b.size.y:
		for x in b.size.x:
			var cy := b.position.y + y
			var t := image.get_pixel(b.position.x + x, cy)
			if t.a8 < ALPHA_THRESHOLD:
				continue
			var off := Vector2i(x, y)
			var hx := t.to_html(false)
			r["whole_figure"].append(off)
			if HAIR_HEX.has(hx):
				r["hair"].append(off)
			elif SKIN_HEX.has(hx) and cy <= 33:
				r["face_skin"].append(off)
			elif SCARF_HEX.has(hx) and cy <= 39:
				r["scarf"].append(off)
			elif BEDROLL_HEX.has(hx):
				r["bedroll"].append(off)
			elif COAT_HEX.has(hx):
				r["coat"].append(off)
			elif SHIRT_HEX.has(hx):
				r["shirt"].append(off)
			elif TROUSER_HEX.has(hx):
				r["trousers"].append(off)
			elif BOOT_HEX.has(hx) and cy >= 86:
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
	for pair in [["male-pilot", MALE_PATH, MALE_SHA256], ["female-v8-approved", V8_PATH, V8_SHA256]]:
		var digest := FileAccess.get_sha256(ProjectSettings.globalize_path(pair[1]))
		if digest != pair[2]:
			_fail("%s SHA-256 %s != %s" % [pair[0], digest, pair[2]])
			return
		sources[pair[0]] = {"path": pair[1], "sha256": digest}
	var male := _load_rgba(MALE_PATH)
	var v8 := _load_rgba(V8_PATH)
	if male == null or v8 == null:
		_fail("cannot load source PNGs")
		return
	var mb := _alpha_bounds(male)
	var vb := _alpha_bounds(v8)
	if mb.size != MALE_WINDOW or vb.size != V8_WINDOW or mb.end.y != MALE_PIN.y:
		_fail("visible bounds %s / %s" % [str(mb), str(vb)])
		return
	var regions := _regions(male, mb)
	var region_sizes := {}
	for k in regions.keys():
		region_sizes[k] = regions[k].size()
	var v8_offsets := _whole(v8, vb)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(1280, 720)
	var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var uid := "%08x" % (randi() & 0xffffffff)
	SaveStore.root_path = "user://test-saves/protagonist-male-south-idle-v8pair-v01"
	app = root.get_node("AppState")
	var captures := []
	var contrast_table := {}
	for key in SCENES.keys():
		for lang in LANGS:
			var spec: Array = SCENES[key]
			app.begin_new_run()
			app.hero_appearance = "male"
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
			var ms := _sprite(male, Vector2(MALE_PIN), spot_x, ground_y)
			host.add_child(ms)
			var solo := await _grab()
			if solo.get_size() != Vector2i(1280, 720):
				_fail("capture size " + str(solo.get_size()))
				return
			var mw := _diff_bounds(baseline, solo)
			if mw.size != MALE_WINDOW:
				_fail("%s/%s: male window %s is not 1:1 %s" % [key, lang, str(mw), str(MALE_WINDOW)])
				return
			var pivot := {"pin_cell": [MALE_PIN.x, MALE_PIN.y], "spot_logical": [spot_x, ground_y],
				"expected_window_left": int(round(2.0 * spot_x)) - (MALE_PIN.x - mb.position.x),
				"expected_window_bottom_exclusive": int(round(2.0 * ground_y)),
				"window_left": mw.position.x, "window_bottom_exclusive": mw.end.y,
				"window_height_px": mw.size.y, "logical_height_px": mw.size.y / 2.0}
			if mw.position.x != pivot["expected_window_left"] or mw.end.y != pivot["expected_window_bottom_exclusive"]:
				_fail("%s/%s: pivot %s" % [key, lang, str(pivot)])
				return
			var mf := _fidelity(male, mb, solo, mw)
			if mf["exact_rgb_matches"] != mf["opaque_texels"] or mf["opaque_texels"] != MALE_OPAQUE:
				_fail("%s/%s: male fidelity %s" % [key, lang, str(mf)])
				return
			var contrast := {}
			for k in regions.keys():
				contrast[k] = _contrast(solo, baseline, mw, regions[k])
			var ring_bg := _median(_ring(baseline, mw))
			var base := "rpg-2-star-ocean-the-second_protagonist-male_%s-%s-%s" % [TAG, key, lang]
			var items := [["solo-1x", solo], ["solo-2x-crop", _crop2x(solo, mw)]]
			var vw := Rect2i()
			var vf := {}
			if lang == PAIR_LANG:
				var vs := _sprite(v8, Vector2(vb.position.x + vb.size.x * 0.5, vb.end.y), spot_x + float(spec[2]), ground_y)
				host.add_child(vs)
				var bench := await _grab()
				vw = _diff_bounds(solo, bench)
				if vw.size != V8_WINDOW or vw.intersects(mw) or vw.end.y != mw.end.y:
					_fail("%s: v8 window %s (male %s)" % [key, str(vw), str(mw)])
					return
				vf = _fidelity(v8, vb, bench, vw)
				if vf["exact_rgb_matches"] != vf["opaque_texels"] or vf["opaque_texels"] != V8_OPAQUE:
					_fail("%s: v8 fidelity %s" % [key, str(vf)])
					return
				contrast["v8_benchmark_whole_figure"] = _contrast(bench, solo, vw, v8_offsets)
				items.append(["with-female-v8-1x", bench])
				items.append(["with-female-v8-2x-crop", _crop2x(bench, mw.merge(vw))])
			contrast_table["%s-%s" % [key, lang]] = contrast
			for item in items:
				var name: String = "%s-%s_unapproved-v01_%s-%s.png" % [base, item[0], stamp, uid]
				var path := _save(item[1], name)
				if path == "":
					_fail("cannot save " + name)
					return
				captures.append({"scene": key, "language": lang, "scene_note": spec[3], "content": item[0],
					"capture": "outputs/" + name, "capture_sha256": FileAccess.get_sha256(path),
					"capture_size": [(item[1] as Image).get_width(), (item[1] as Image).get_height()],
					"male_window": _rect_json(mw), "male_texel_fidelity": mf, "pivot": pivot,
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
		"purpose": "Real Godot captures of the UNAPPROVED, NONRUNTIME male protagonist south idle static pilot paired to the approved female selout v8, at exactly 48 logical px in the bright science city and the dark survey annex room 2, Chinese and English UI; old placeholder hidden by the test harness; pilot alone (1x + 2x crop) and, in English, beside the approved female v8 (1x + 2x crop).",
		"status": "technical visual QA only; UNAPPROVED; NONRUNTIME; not integrated", "art_approved": false, "human_reviewed": false,
		"acceptance_counters_unchanged": {"runtime_sprites_accepted": "0/52", "scene_visual_gates": "3/12", "overall_meter": "40.8%", "plays": "0/2"},
		"capture_tool": "tools/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair-static-pilot-godot-capture_unapproved-v01_20261018-130225-098354f7.gd",
		"placement": "pilot by its foot pin (cell 40,104) at the hidden placeholder's spot (snapped to 0.5 logical px); v8 bounds-centred at its earlier reviewed pair spots (city hero x + 40, annex hero x + 80 logical px; the English district label covers the city x - 36 spot)",
		"renderer": "Godot %s windowed, viewport texture capture" % Engine.get_version_info()["string"],
		"canvas": [640, 360], "window": [1280, 720], "sprite_scale": 0.5, "display_logical_height": 48, "filter": "nearest", "shadow": "none",
		"review_scales": {"1x": "1280x720 window capture as displayed (1 texel = 1 window px = 0.5 logical px)", "2x-crop": "window-px crop around the figure(s) (at least 120x128, figures + 12 px margin), nearest x2"},
		"hero_appearance": "male", "placeholder": "hidden (visible = false) in every frame; runtime files unchanged",
		"sources": sources,
		"gates_passed": ["source SHA-256 locks (pilot, v8)", "1280x720 captures", "pilot window 39x96 = 48 logical px (1:1)",
			"pilot texel match 2488/2488 exact RGB", "pivot: window left = 2*spot_x - 18, window bottom = 2*ground_y",
			"v8 window 43x96 (1:1), texel match 2419/2419, same ground row, no overlap with the pilot"],
		"regions": {"definition": "colour-set regions of the pilot (tool RAMPS); face_skin rows <= 33, scarf rows <= 39 (excludes emblem and sash), boots rows >= 86; v8_benchmark_whole_figure = v8's opaque texels in the pair frame vs the pilot-only frame", "texels": region_sizes},
		"contrast_dE76_vs_8px_ring_median_by_scene_language": contrast_table,
		"captures": captures,
		"limitations": [
			"Static south idle only; one position per scene; first-visit default state; scene _process disabled.",
			"The placeholder is hidden by this test harness only; the game still shows the old placeholder.",
			"1920x1080 / fullscreen sampling (1.5 px per texel) not captured.",
			"dE76 is a proxy only; visual judgement is for Codex and the creator.",
		],
	}
	var rpath := ProjectSettings.globalize_path(OUTPUT_DIR).path_join("rpg-2-star-ocean-the-second_protagonist-male_%s-godot-capture-report_unapproved-v01_%s-%s.json" % [TAG, stamp, uid])
	var f := FileAccess.open(rpath, FileAccess.WRITE)
	if f == null:
		_fail("cannot write report")
		return
	f.store_string(JSON.stringify(report, "\t") + "\n")
	f.close()
	print("REPORT " + rpath)
	print("STATUS unapproved nonruntime pilot; technical visual QA only")
	quit(0)
