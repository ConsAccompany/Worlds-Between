extends SceneTree

# TEST-ONLY real-Godot review captures for the UNAPPROVED, NONRUNTIME female protagonist NORTH idle static pilot v01,
# at exactly 48 logical px in the game's native 640x360 canvas (canvas_items, integer scale, default 1280x720 window,
# sprite scale 0.5: 96 texels -> 48 logical px, 1 texel = 1 window px). Nothing in game/ is added or edited; the pilot
# is never wired into a scene file. Run windowed from the repository root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path of this file>
# Scenes: science city (bright, default first-visit layout) and city survey annex room 2 (dark interior), each in zh
# and en. Per scene x language, two SEPARATE 1280x720 PNGs with identical framing (no collage):
#   1. the north pilot alone at the hero spot (the runtime placeholder hero is hidden, so one character stands there);
#   2. the approved south selout v8 alone at the same pin spot, with an on-screen label marking it as the comparison
#      reference (the label sits at the top-left of the play area, added after the v8 window is measured, away from the figure and HUD text).
# Both are placed by the foot pin (cell x 40, sole row 103). No outline, glow, shadow or filter is added.
# Gates (exit 1, no report on failure): source SHA-256 locks; 1280x720 captures; language applied; placeholder hidden;
# north diff window exactly 40x96 and v8 exactly 43x96 (1:1); 100% texel fidelity for both; both share the same
# ground row and pin x. Contrast (reported, not gated): whole-figure CIELAB dE76 vs the 8 px ring median and the
# occluded backdrop pixel, north vs v8 at the same spot.
const NORTH_PATH := "res://assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot_unapproved-v01_20261018-090713-6ed8d8dd.png"
const NORTH_SHA256 := "bd5c81661e52ed2ff4fb3c41940cf96de8390c6cec14129f78d691b613cb8e82"
const V8_PATH := "res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png"
const V8_SHA256 := "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"
const PIN_X := 40
const NORTH_WINDOW := Vector2i(40, 96)
const V8_WINDOW := Vector2i(43, 96)
const NORTH_OPAQUE := 2471
const V8_OPAQUE := 2419
const AREA_SCENE := "res://scenes/scifi_exploration_area.tscn"
const ANNEX_SCENE := "res://scenes/survey_annex.tscn"
const SCENES := {
	"city-bright": ["area", "scifi.city", "science city, default first-visit layout (bright)"],
	"annex-room2-dark": ["annex", "scifi.city", "city survey annex room 2 (dark interior)"],
}
const LANGS := ["zh", "en"]
const REF_LABEL := {"zh": "对照参考：已批准南向 v8（非候选）", "en": "Reference: approved south v8 (not the candidate)"}
const TARGET_HEIGHT := 48
const ALPHA_THRESHOLD := 128
const RING := 8
const OUTPUT_DIR := "res://../outputs"
const TOOL := "tools/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-godot-capture_unapproved-v01_20261018-090713-d3f837ab.gd"

var app: Node


func _initialize() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("FEMALE_NORTH_CAPTURE FAIL: " + reason)
	print("FEMALE_NORTH_CAPTURE FAIL: " + reason)
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


func _fidelity(src: Image, bounds: Rect2i, capture: Image, window: Rect2i) -> Dictionary:
	var total := 0
	var exact := 0
	for y in bounds.size.y:
		for x in bounds.size.x:
			var t := src.get_pixel(bounds.position.x + x, bounds.position.y + y)
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


func _stats(values: Array) -> Dictionary:
	var s := values.duplicate()
	s.sort()
	var total := 0.0
	for v in s:
		total += v
	return {"texels": s.size(), "mean_dE76": snappedf(total / s.size(), 0.01),
		"p10_dE76": snappedf(s[int(floor(0.1 * (s.size() - 1)))], 0.01), "min_dE76": snappedf(s[0], 0.01)}


func _contrast(capture: Image, baseline: Image, window: Rect2i, src: Image, bounds: Rect2i) -> Dictionary:
	var outer := window.grow(RING).intersection(Rect2i(Vector2i.ZERO, baseline.get_size()))
	var ring_px := []
	for y in range(outer.position.y, outer.end.y):
		for x in range(outer.position.x, outer.end.x):
			if not window.has_point(Vector2i(x, y)):
				ring_px.append(baseline.get_pixel(x, y))
	var ring_lab := _lab(_median(ring_px))
	var ring := []
	var occl := []
	for y in bounds.size.y:
		for x in bounds.size.x:
			if src.get_pixel(bounds.position.x + x, bounds.position.y + y).a8 < ALPHA_THRESHOLD:
				continue
			var p := window.position + Vector2i(x, y)
			var shown := _lab(capture.get_pixelv(p))
			ring.append(shown.distance_to(ring_lab))
			occl.append(shown.distance_to(_lab(baseline.get_pixelv(p))))
	var med := _median(ring_px)
	return {"ring_median_rgb8": [med.r8, med.g8, med.b8], "ring_median": _stats(ring), "occluded_backdrop": _stats(occl)}


func _sprite(image: Image, bounds: Rect2i, x: float, ground_y: float) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = ImageTexture.create_from_image(image)
	s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	s.centered = false
	s.offset = Vector2(-PIN_X, -bounds.end.y)
	s.scale = Vector2.ONE * (float(TARGET_HEIGHT) / float(bounds.size.y))
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


func _save(img: Image, name: String, out_dir: String) -> String:
	var path := out_dir.path_join(name)
	if img.save_png(path) != OK:
		return ""
	return path


func _run() -> void:
	if DisplayServer.get_name() == "headless":
		_fail("windowed run required")
		return
	var sources := {}
	for pair in [["north-pilot-v01", NORTH_PATH, NORTH_SHA256], ["south-v8-approved-reference", V8_PATH, V8_SHA256]]:
		var digest := FileAccess.get_sha256(ProjectSettings.globalize_path(pair[1]))
		if digest != pair[2]:
			_fail("%s SHA-256 %s != %s" % [pair[0], digest, pair[2]])
			return
		sources[pair[0]] = {"path": pair[1], "sha256": digest}
	var north := _load_rgba(NORTH_PATH)
	var v8 := _load_rgba(V8_PATH)
	if north == null or v8 == null:
		_fail("cannot load source PNGs")
		return
	var nb := _alpha_bounds(north)
	var vb := _alpha_bounds(v8)
	if nb.size != NORTH_WINDOW or vb.size != V8_WINDOW or nb.end.y != vb.end.y:
		_fail("visible bounds %s / %s" % [str(nb), str(vb)])
		return
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(1280, 720)
	var out_dir := ProjectSettings.globalize_path(OUTPUT_DIR)
	var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var uid := "%08x" % (randi() & 0xffffffff)
	SaveStore.root_path = "user://test-saves/protagonist-female-north-idle-static-pilot-v01"
	app = root.get_node("AppState")
	var captures := []
	var contrast := {}
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
			if String(host.get("destination_id")) != spec[1] or app.language != lang:
				_fail("%s/%s: scene state %s %s" % [key, lang, String(host.get("destination_id")), app.language])
				return
			var hero: Sprite2D = host.get("hero")
			var ph := hero.texture.get_image()
			ph.convert(Image.FORMAT_RGBA8)
			var pb := _alpha_bounds(ph)
			var ground_y := hero.position.y + hero.offset.y - ph.get_height() * 0.5 + pb.end.y
			hero.visible = false
			var baseline := await _grab()
			if baseline.get_size() != Vector2i(1280, 720):
				_fail("capture size " + str(baseline.get_size()))
				return
			var tag := "%s-%s" % [key, lang]
			var results := {}
			for item in [["north-idle-pilot", north, nb, NORTH_WINDOW, NORTH_OPAQUE], ["south-v8-reference", v8, vb, V8_WINDOW, V8_OPAQUE]]:
				var s := _sprite(item[1], item[2], hero.position.x, ground_y)
				host.add_child(s)
				var frame := await _grab()
				var w := _diff_bounds(baseline, frame)
				if w.size != item[3]:
					_fail("%s %s: window %s is not 1:1 %s" % [tag, item[0], str(w), str(item[3])])
					return
				var fid := _fidelity(item[1], item[2], frame, w)
				if fid["exact_rgb_matches"] != fid["opaque_texels"] or fid["opaque_texels"] != item[4]:
					_fail("%s %s: fidelity %s" % [tag, item[0], str(fid)])
					return
				var con := _contrast(frame, baseline, w, item[1], item[2])
				var label: CanvasLayer = null
				if item[0] == "south-v8-reference":
					label = CanvasLayer.new()
					label.layer = 100
					var l := Label.new()
					l.text = REF_LABEL[lang]
					l.add_theme_font_size_override("font_size", 10)
					l.add_theme_color_override("font_color", Color(1, 1, 1))
					l.add_theme_color_override("font_outline_color", Color(0, 0, 0))
					l.add_theme_constant_override("outline_size", 3)
					l.position = Vector2(8, 66)
					label.add_child(l)
					host.add_child(label)
					var pre := frame
					frame = await _grab()
					var ld := _diff_bounds(pre, frame)
					if ld.size == Vector2i.ZERO or ld.intersects(w.grow(4)) or _fidelity(item[1], item[2], frame, w)["exact_rgb_matches"] != item[4]:
						_fail("%s: reference label missing or touching the figure (%s)" % [tag, str(ld)])
						return
				var name: String = "rpg-2-star-ocean-the-second_protagonist-female_%s-%s-h48_unapproved-v01_%s-%s.png" % [item[0], tag, stamp, uid]
				var path := _save(frame, name, out_dir)
				if path == "":
					_fail("cannot save " + name)
					return
				results[item[0]] = {"window": w, "pos": s.position}
				captures.append({"scene": key, "scene_note": spec[2], "language": lang, "content": item[0],
					"is_candidate": item[0] == "north-idle-pilot", "reference_label": REF_LABEL[lang] if label != null else null,
					"capture": "outputs/" + name, "capture_sha256": FileAccess.get_sha256(path), "capture_size": [1280, 720],
					"window": _rect_json(w), "texel_fidelity": fid, "position_logical": [s.position.x, s.position.y],
					"ground_y_logical": ground_y, "placeholder_hidden": not hero.visible,
					"placeholder_position_logical": [hero.position.x, hero.position.y]})
				contrast["%s/%s" % [tag, item[0]]] = con
				print("CAPTURE %s %s %s  ring %.2f/%.2f occl %.2f" % [tag, item[0], path, con["ring_median"]["mean_dE76"], con["ring_median"]["min_dE76"], con["occluded_backdrop"]["mean_dE76"]])
				if label != null:
					host.remove_child(label)
					label.queue_free()
				host.remove_child(s)
				s.queue_free()
			var nw: Rect2i = results["north-idle-pilot"]["window"]
			var vw: Rect2i = results["south-v8-reference"]["window"]
			if nw.end.y != vw.end.y or results["north-idle-pilot"]["pos"] != results["south-v8-reference"]["pos"]:
				_fail("%s: north and v8 framing differ (%s vs %s)" % [tag, str(nw), str(vw)])
				return
			host.queue_free()
			await process_frame
			await process_frame
	var report := {
		"project": "Worlds Between", "milestone": "M8",
		"purpose": "Test-only real Godot captures of the UNAPPROVED, NONRUNTIME female protagonist north idle static pilot v01 at 48 logical px (native 640x360 canvas), bright city and dark annex room 2, zh and en; each with a separate same-framing capture of the approved south selout v8 labelled as the comparison reference.",
		"status": "technical visual QA only; UNAPPROVED; NONRUNTIME; not integrated", "art_approved": false, "human_reviewed": false,
		"acceptance_counters_unchanged": {"exploration_sprites": "0/52"},
		"capture_tool": TOOL,
		"renderer": "Godot %s windowed, viewport texture capture" % Engine.get_version_info()["string"],
		"canvas": [640, 360], "window": [1280, 720], "sprite_scale": 0.5, "display_logical_height": 48, "filter": "nearest",
		"shadow_or_outline_added": "none",
		"placement": "both figures by foot pin (cell x 40, sole row 103) at the hidden placeholder hero's x and ground row",
		"sources": sources,
		"gates_passed": ["source SHA-256 locks", "1280x720 captures", "language applied per capture", "placeholder hidden",
			"north window 40x96 (1:1)", "v8 window 43x96 (1:1)", "north fidelity 2471/2471", "v8 fidelity 2419/2419",
			"same pin position and ground row for north and v8", "reference label clear of the v8 figure"],
		"contrast_whole_figure_dE76": contrast,
		"captures": captures,
		"limitations": [
			"Static idle only; one position per scene; first-visit default state; scene _process disabled.",
			"Runs against the shared working tree: scifi_exploration_area.gd and survey_annex.gd carry other sessions' uncommitted edits (read only here).",
			"The runtime placeholder hero is hidden for these frames only; no scene or script file is changed.",
			"1920x1080 / fullscreen sampling not captured.",
			"dE76 is a proxy; 1x readability is for the reviewer to judge on the captures.",
		],
	}
	var rpath := out_dir.path_join("rpg-2-star-ocean-the-second_protagonist-female_north-idle-pilot-capture-report_unapproved-v01_%s-%s.json" % [stamp, uid])
	var f := FileAccess.open(rpath, FileAccess.WRITE)
	if f == null:
		_fail("cannot write report")
		return
	f.store_string(JSON.stringify(report, "\t") + "\n")
	f.close()
	print("REPORT " + rpath)
	print("STATUS unapproved nonruntime pilot; test-only captures")
	quit(0)
