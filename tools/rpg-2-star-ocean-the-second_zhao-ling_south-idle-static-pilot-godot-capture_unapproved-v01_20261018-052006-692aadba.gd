extends SceneTree

# Test-only, real-Godot 1280x720 review captures for the UNAPPROVED, NONRUNTIME Zhao Ling (赵铃) south idle STATIC
# pilot v01 at exactly 48 logical px (640x360 canvas, canvas_items, sprite scale 0.5: 96 texels -> 48 logical px,
# 1 texel = 1 window px). Scenes: science city (bright, default first-visit layout) and city survey annex room 2 (dark
# interior), at the spot used for the Liang Xu pilot and the approved female v8 review (hero placeholder x + 36),
# hero_appearance "female" as in those runs. Zhao is placed by her foot pin (cell x 40, sole row 103).
# Per scene, one run writes two separate 1280x720 PNGs (no collage):
#   1. Zhao Ling alone (the only Zhao in the frame; the scenes' old runtime NPCs are not Zhao);
#   2. an explicit comparison frame: the same plus the approved female v8 static beside the placeholder.
# Gates (exit 1, no report on failure): source SHA-256 locks (Zhao, v8); 1280x720 captures; Zhao diff window exactly
# 46x96 and v8 exactly 43x96 (1:1); 100% texel fidelity for both; the v8 window does not touch Zhao's.
# Contrast (reported, not gated): CIELAB dE76 per region vs an 8 px ring median, the +/-6-row local ring median and
# the occluded pixel, as in the v8, Liang and male pilot QA.
# Lives in tools/ (outside res://), so no game/ file is added or edited. Run windowed from the repository root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path of this file>
const ZHAO_PATH := "res://assets/characters/zhao-ling/south-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot_unapproved-v01_20261018-052006-73f1d603.png"
const ZHAO_SHA256 := "069acee4ba3c25c55cd381e19ab3a7453bb9ddd7fe27ff69eca7068c038859f7"
const ZHAO_PIN_X := 40
const ZHAO_WINDOW := Vector2i(46, 96)
const ZHAO_OPAQUE := 2491
const V8_PATH := "res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png"
const V8_SHA256 := "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"
const V8_WINDOW := Vector2i(43, 96)
const V8_OPAQUE := 2419
const AREA_SCENE := "res://scenes/scifi_exploration_area.tscn"
const ANNEX_SCENE := "res://scenes/survey_annex.tscn"
# scene key -> [kind, destination, Zhao x offset from placeholder, v8 x offset, note]
const SCENES := {
	"city-bright": ["area", "scifi.city", 36.0, -36.0, "science city, default first-visit layout (bright)"],
	"annex-room2-dark": ["annex", "scifi.city", 36.0, 80.0, "city survey annex room 2 (dark interior)"],
}
const TARGET_HEIGHT := 48
const ALPHA_THRESHOLD := 128
const RING := 8
const ROW_BAND := 6
const OUTPUT_DIR := "res://../outputs"
# Region colour sets (tool RAMPS) + cell limits.
const HAIR_HEX := ["525b76", "2f3348", "151722"]
const BLUE_HEX := ["8fd3e6", "4f9dbf", "2c6585"]
const STEEL_HEX := ["d7dce2", "8f98a8", "535b6b"]
const SKIN_HEX := ["f4d8c6", "dcb09c", "b3806f"]
const JACKET_HEX := ["666a7d", "424556", "272935"]
const LINING_HEX := ["dfe0e5", "abaeb9", "777b8c"]
const SHIRT_HEX := ["f6f4ee"]
const TROUSER_HEX := ["74767f", "54565f"]
const BOOT_HEX := ["5a5d6b", "2a2c36"]
const BRASS_HEX := ["e8c780", "b48c4d", "6c5133"]

var app: Node


func _initialize() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("ZHAO_PILOT_CAPTURE FAIL: " + reason)
	print("ZHAO_PILOT_CAPTURE FAIL: " + reason)
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


func _ring(baseline: Image, window: Rect2i, row_from: int = -RING, row_to: int = 1 << 20) -> Array:
	var outer := window.grow(RING).intersection(Rect2i(Vector2i.ZERO, baseline.get_size()))
	var out := []
	for y in range(maxi(outer.position.y, window.position.y + row_from), mini(outer.end.y, window.position.y + row_to)):
		for x in range(outer.position.x, outer.end.x):
			if not window.has_point(Vector2i(x, y)):
				out.append(baseline.get_pixel(x, y))
	return out


func _stats(values: Array) -> Dictionary:
	var s := values.duplicate()
	s.sort()
	var total := 0.0
	for v in s:
		total += v
	return {"texels": s.size(), "mean_dE76": snappedf(total / s.size(), 0.01),
		"p10_dE76": snappedf(s[int(floor(0.1 * (s.size() - 1)))], 0.01), "min_dE76": snappedf(s[0], 0.01)}


func _contrast(capture: Image, baseline: Image, window: Rect2i, offsets: Array) -> Dictionary:
	var ring_lab := _lab(_median(_ring(baseline, window)))
	var row_lab := []
	for wy in window.size.y:
		row_lab.append(_lab(_median(_ring(baseline, window, wy - ROW_BAND, wy + ROW_BAND + 1))))
	var ring := []
	var rowl := []
	var occl := []
	for off in offsets:
		var shown := _lab(capture.get_pixelv(window.position + off))
		ring.append(shown.distance_to(ring_lab))
		rowl.append(shown.distance_to(row_lab[off.y]))
		occl.append(shown.distance_to(_lab(baseline.get_pixelv(window.position + off))))
	return {"ring_median": _stats(ring), "row_local_ring": _stats(rowl), "occluded_backdrop": _stats(occl)}


func _regions(image: Image, b: Rect2i) -> Dictionary:
	# cell coordinates: x = b.position.x + offset.x, y = b.position.y + offset.y
	var r := {"whole_figure": [], "hair": [], "blue_hair_tips": [], "earcup_band": [], "antenna": [], "face_skin": [],
		"jacket": [], "collar_cuffs_lining": [], "shirt": [], "trousers": [], "boots": [], "hip_radio": [],
		"coiled_cable": [], "tablet": [], "thigh_strap": []}
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
			if cx == 48 and cy <= 20 and (hx == "1f2029" or BRASS_HEX.has(hx)):
				r["antenna"].append(off)
			elif cx <= 23 and cy >= 46 and cy <= 59 and hx != "0c0d12":
				r["tablet"].append(off)
			elif cx >= 47 and cy >= 57 and cy <= 66 and hx != "0c0d12":
				r["hip_radio"].append(off)
			elif BLUE_HEX.has(hx) and cy >= 67 and cx >= 52:
				r["coiled_cable"].append(off)
			elif BLUE_HEX.has(hx) and cy <= 34 and cx <= 36:
				r["blue_hair_tips"].append(off)
			elif (BLUE_HEX.has(hx) or STEEL_HEX.has(hx)) and cy <= 29 and cx >= 40:
				r["earcup_band"].append(off)
			elif HAIR_HEX.has(hx):
				r["hair"].append(off)
			elif SKIN_HEX.has(hx) and cy <= 35:
				r["face_skin"].append(off)
			elif (BLUE_HEX.has(hx) or STEEL_HEX.has(hx)) and cx >= 33 and cx <= 34 and cy >= 56 and cy <= 75:
				r["thigh_strap"].append(off)
			elif JACKET_HEX.has(hx) and cy <= 61:
				r["jacket"].append(off)
			elif LINING_HEX.has(hx):
				r["collar_cuffs_lining"].append(off)
			elif SHIRT_HEX.has(hx):
				r["shirt"].append(off)
			elif TROUSER_HEX.has(hx) or (JACKET_HEX.has(hx) and cy >= 62):
				r["trousers"].append(off)
			elif BOOT_HEX.has(hx) and cy >= 90:
				r["boots"].append(off)
	return r


func _whole(image: Image, b: Rect2i) -> Array:
	var out := []
	for y in b.size.y:
		for x in b.size.x:
			if image.get_pixel(b.position.x + x, b.position.y + y).a8 >= ALPHA_THRESHOLD:
				out.append(Vector2i(x, y))
	return out


func _sprite(image: Image, bounds: Rect2i, x: float, ground_y: float, pin_x: float = -1.0) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = ImageTexture.create_from_image(image)
	s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	s.centered = false
	var ax := pin_x if pin_x >= 0.0 else bounds.position.x + bounds.size.x * 0.5
	s.offset = Vector2(-ax, -bounds.end.y)
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


func _run() -> void:
	if DisplayServer.get_name() == "headless":
		_fail("windowed run required")
		return
	var sources := {}
	for pair in [["zhao-ling-pilot-v01", ZHAO_PATH, ZHAO_SHA256], ["female-v8-benchmark", V8_PATH, V8_SHA256]]:
		var digest := FileAccess.get_sha256(ProjectSettings.globalize_path(pair[1]))
		if digest != pair[2]:
			_fail("%s SHA-256 %s != %s" % [pair[0], digest, pair[2]])
			return
		sources[pair[0]] = {"path": pair[1], "sha256": digest}
	var zhao := _load_rgba(ZHAO_PATH)
	var v8 := _load_rgba(V8_PATH)
	if zhao == null or v8 == null:
		_fail("cannot load source PNGs")
		return
	var zb := _alpha_bounds(zhao)
	var vb := _alpha_bounds(v8)
	if zb.size != ZHAO_WINDOW or vb.size != V8_WINDOW:
		_fail("visible bounds %s / %s" % [str(zb), str(vb)])
		return
	var regions := _regions(zhao, zb)
	var region_sizes := {}
	for k in regions.keys():
		region_sizes[k] = regions[k].size()
	var v8_offsets := _whole(v8, vb)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(1280, 720)
	var out_dir := ProjectSettings.globalize_path(OUTPUT_DIR)
	var stamp := Time.get_datetime_string_from_system(false).replace("-", "").replace(":", "").replace("T", "-")
	var uid := "%08x" % (randi() & 0xffffffff)
	SaveStore.root_path = "user://test-saves/zhao-ling-south-idle-static-pilot-v01"
	app = root.get_node("AppState")
	var captures := []
	var contrast_table := {}
	for key in SCENES.keys():
		var spec: Array = SCENES[key]
		app.begin_new_run()
		app.hero_appearance = "female"
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
		var ground_y := hero.position.y + hero.offset.y - ph.get_height() * 0.5 + pb.end.y
		var baseline := await _grab()
		var zs := _sprite(zhao, zb, hero.position.x + float(spec[2]), ground_y, float(ZHAO_PIN_X))
		host.add_child(zs)
		var solo := await _grab()
		if solo.get_size() != Vector2i(1280, 720):
			_fail("capture size " + str(solo.get_size()))
			return
		var zw := _diff_bounds(baseline, solo)
		if zw.size != ZHAO_WINDOW:
			_fail("%s: Zhao window %s is not 1:1 %s" % [key, str(zw), str(ZHAO_WINDOW)])
			return
		var zf := _fidelity(zhao, zb, solo, zw)
		if zf["exact_rgb_matches"] != zf["opaque_texels"] or zf["opaque_texels"] != ZHAO_OPAQUE:
			_fail("%s: Zhao fidelity %s" % [key, str(zf)])
			return
		var vs := _sprite(v8, vb, hero.position.x + float(spec[3]), ground_y)
		host.add_child(vs)
		var bench := await _grab()
		var vw := _diff_bounds(solo, bench)
		if vw.size != V8_WINDOW or vw.intersects(zw):
			_fail("%s: v8 window %s (Zhao %s)" % [key, str(vw), str(zw)])
			return
		var vf := _fidelity(v8, vb, bench, vw)
		if vf["exact_rgb_matches"] != vf["opaque_texels"] or vf["opaque_texels"] != V8_OPAQUE:
			_fail("%s: v8 fidelity %s" % [key, str(vf)])
			return
		var contrast := {}
		for k in regions.keys():
			if regions[k].size() > 0:
				contrast[k] = _contrast(solo, baseline, zw, regions[k])
		contrast["v8_benchmark_whole_figure"] = _contrast(bench, solo, vw, v8_offsets)
		contrast_table[key] = contrast
		var ring_bg := _median(_ring(baseline, zw))
		for item in [["south-idle-static-pilot", solo], ["south-idle-static-pilot-vs-female-v8", bench]]:
			var name: String = "rpg-2-star-ocean-the-second_zhao-ling_%s-%s-h48_unapproved-v01_%s-%s.png" % [item[0], key, stamp, uid]
			var path := out_dir.path_join(name)
			if (item[1] as Image).save_png(path) != OK:
				_fail("cannot save " + path)
				return
			captures.append({"scene": key, "scene_note": spec[4], "content": "Zhao Ling alone" if item[1] == solo else "comparison: Zhao Ling + approved female v8 benchmark",
				"capture": "outputs/" + name, "capture_sha256": FileAccess.get_sha256(path), "capture_size": [1280, 720],
				"zhao_window": _rect_json(zw), "zhao_texel_fidelity": zf,
				"v8_window": _rect_json(vw) if item[1] == bench else null,
				"v8_texel_fidelity": vf if item[1] == bench else null,
				"zhao_position_logical": [zs.position.x, zs.position.y], "v8_position_logical": [vs.position.x, vs.position.y] if item[1] == bench else null,
				"ground_y_logical": ground_y, "placeholder_position_logical": [hero.position.x, hero.position.y],
				"placeholder_texture": hero.texture.resource_path, "background_ring_median_rgb8": [ring_bg.r8, ring_bg.g8, ring_bg.b8]})
			print("CAPTURE %s %s %s" % [key, item[0], path])
		for k in contrast.keys():
			var c: Dictionary = contrast[k]
			print("   %-26s ring %6.2f/%6.2f  rowlocal mean %6.2f p10 %6.2f min %6.2f  occluded mean %6.2f p10 %6.2f min %6.2f" % [
				k, c["ring_median"]["mean_dE76"], c["ring_median"]["min_dE76"], c["row_local_ring"]["mean_dE76"],
				c["row_local_ring"]["p10_dE76"], c["row_local_ring"]["min_dE76"], c["occluded_backdrop"]["mean_dE76"],
				c["occluded_backdrop"]["p10_dE76"], c["occluded_backdrop"]["min_dE76"]])
		host.queue_free()
		await process_frame
		await process_frame
	var report := {
		"project": "Worlds Between", "milestone": "M8",
		"purpose": "Test-only real Godot 1280x720 review captures of the UNAPPROVED, NONRUNTIME Zhao Ling south idle static pilot v01 at exactly 48 logical px in the bright science city and the dark city survey annex room 2; one solo frame per scene and one separate comparison frame per scene with the approved female selout v8 static beside the placeholder.",
		"status": "technical visual QA only; UNAPPROVED; NONRUNTIME; not integrated", "art_approved": false, "human_reviewed": false,
		"acceptance_counters_unchanged": {"runtime_sprites_accepted": "0/52"},
		"capture_tool": "tools/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-godot-capture_unapproved-v01_20261018-052006-692aadba.gd",
		"placement": "Zhao by foot pin (cell x 40, sole row 103) at hero placeholder x + 36 (the Liang / v8 review spot); v8 bounds-centred as in its reviewed captures",
		"renderer": "Godot %s windowed, viewport texture capture" % Engine.get_version_info()["string"],
		"canvas": [640, 360], "window": [1280, 720], "sprite_scale": 0.5, "display_logical_height": 48, "filter": "nearest", "shadow": "none",
		"hero_appearance": "female",
		"sources": sources,
		"gates_passed": ["source SHA-256 locks (Zhao, v8)", "1280x720 captures", "Zhao window 46x96 (1:1)", "v8 window 43x96 (1:1)",
			"Zhao texel fidelity 2491/2491", "v8 texel fidelity 2419/2419", "v8 window does not touch Zhao window"],
		"regions": {"definition": "colour-set + cell-position regions of the Zhao pilot (tool RAMPS); see _regions in the capture tool", "texels": region_sizes},
		"contrast_dE76_by_scene": contrast_table,
		"captures": captures,
		"limitations": [
			"Static south idle only; one position per scene; first-visit default state; scene _process disabled.",
			"The science city shows the old runtime Liang Xu NPC and the old female hero placeholder; neither is Zhao Ling and both are unchanged.",
			"Runs against the shared working tree, whose runtime scripts carry other sessions' uncommitted hunks; they were only read.",
			"1920x1080 / fullscreen sampling (1.5 px per texel) not captured.",
			"dE76 is a proxy; visual judgement is for Codex and the creator.",
		],
	}
	var rpath := out_dir.path_join("rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-capture-report_unapproved-v01_%s-%s.json" % [stamp, uid])
	var f := FileAccess.open(rpath, FileAccess.WRITE)
	if f == null:
		_fail("cannot write report")
		return
	f.store_string(JSON.stringify(report, "\t") + "\n")
	f.close()
	print("REPORT " + rpath)
	print("STATUS unapproved nonruntime pilot; technical visual QA only")
	quit(0)
