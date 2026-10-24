extends SceneTree
# Probe for the standalone Muxiu display preview (derived from the Lin Que ldisplay64 probe).
# Args after --: --lang=en|zh --out=<abs dir>
# Prints MDISPLAY91_PROBE_OK only when every check passes; capture is attempted only with a rendering display.
# Besides the normal scene it instantiates one fallback copy with a missing portrait path.

const SCENE := "res://scenes/mdisplay91/rpg-2-star-ocean-the-second_muxiu_display-preview_standalone-v01_20261024-083014-7c4a91d2.tscn"
const MANIFEST := "res://assets/portraits/mdisplay91/rpg-2-star-ocean-the-second_muxiu_display-portrait-manifest_v01_20261024-083014-7c4a91d2.json"
const SOURCE := "res://assets/characters/muxiu-native-v01/south/rpg-2-star-ocean-the-second_muxiu_south-static_unapproved-v01_20261024-071500-ca23fad5.png"
const RUN := "20261024-083014-7c4a91d2"
const BG := Color(0.09, 0.11, 0.15)
const STAGE_COL := Color(0.16, 0.19, 0.24)
const SOURCE_SHA := "e14d5c50890d7fcd0c75eb362d2b08fd1d4ac02c9c33e04fc4861b5a7d7a26fe"
const SOURCE_RAW := "02cbb1d00a22eb4268bc40eddbfb5179b106f703645150c8f096bd06f50b5faa"
const CROP_RAW := "c5de9401f9f10901061082e342bd1130dddd22e0c8f453f66aae0fcd165663b0"
const EXPECTED_OPAQUE := 11952

var fails: Array[String] = []
var checks := 0


func ok(cond: bool, what: String) -> void:
	checks += 1
	if not cond:
		fails.append(what)
		print("FAIL ", what)


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var lang := "en"
	var out := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--lang="):
			lang = a.substr(7)
		elif a.begins_with("--out="):
			out = a.substr(6)
	var capturing := out != "" and DisplayServer.get_name() != "headless"
	var man = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
	ok(typeof(man) == TYPE_DICTIONARY, "manifest parses")
	if typeof(man) == TYPE_DICTIONARY:
		ok(man["subject"] == "muxiu", "manifest subject muxiu")
		ok(man["source"]["sha256"] == SOURCE_SHA, "manifest source pin")
		ok(man["source"]["width"] == 80 and man["source"]["height"] == 112, "manifest source size 80x112")
		ok(man["source_manifest"]["sha256"] == "24c751575fe02a4857628dbfb8b379cd1d42344167062ae8ddbb033024e114de", "source manifest pin")
		var tr: Dictionary = man["transform"]
		ok(tr["method"] == "nearest-neighbor-integer-upscale" and int(tr["factor"]) == 2, "transform 2x integer replication")
		ok(tr["resampled"] == true and tr["pixel_replication_only"] == true, "transform declared resampled/replication")
		ok(tr["repainted"] == false and tr["ai_generated_new_pixels"] == false, "no repaint/new generative pixels")
		ok(man["output"]["width"] == 160 and man["output"]["height"] == 224, "manifest output 160x224")
		ok(man["output"]["raw_rgba_sha256"] == CROP_RAW, "manifest display raw hash pin")
		ok(String(man["status"]).begins_with("UNAPPROVED"), "status UNAPPROVED")
	var scene: Control = (load(SCENE) as PackedScene).instantiate()
	root.add_child(scene)
	await process_frame
	await process_frame
	var st: Dictionary = scene.state()
	print("STATE ", st)
	ok(st["lang"] == lang, "lang from --lang")
	ok(st["portrait_loaded"] and not scene.labels.has("no_portrait"), "portrait loaded, no fallback label")
	ok(Vector2i(st["portrait_size"]) == Vector2i(160, 224), "portrait texture 160x224")
	var img: Image = scene.portrait.texture.get_image()
	img.convert(Image.FORMAT_RGBA8)
	print("UI_TEXTURE_SHA ", _sha(img.get_data()))
	ok(scene.portrait.stretch_mode == TextureRect.STRETCH_KEEP_ASPECT_CENTERED, "keep aspect")
	ok(scene.portrait.texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST, "nearest")
	var pbox: Rect2 = scene.portrait.get_rect()
	ok(pbox == Rect2(26, 69, 160, 224), "portrait image rect 26,69,160,224")
	ok(scene.PORTRAIT_BOX.encloses(pbox), "portrait image inside 180x250 frame")
	for key in ["title", "pending", "hint", "name", "career", "identity", "source_note"]:
		ok(not pbox.intersects(scene.labels[key].get_rect()), "portrait clear of " + key)
	for key in ["name", "career", "identity"]:
		var r: Rect2 = scene.labels[key].get_rect()
		ok(not scene.STAGE.intersects(r), "identity clear of actor stage: " + key)
		ok(Rect2(Vector2.ZERO, scene.CARD).encloses(r), "inside card: " + key)
	ok(scene.labels["name"].text == ("牧修" if lang == "zh" else "Muxiu"), "name " + lang)
	ok(scene.labels["career"].text == ("动物照护者 · 24岁" if lang == "zh" else "Animal carer · 24"), "career " + lang)
	ok(scene.labels["pending"].text == ("美术待定" if lang == "zh" else "Art pending"), "art pending label " + lang)
	ok(scene.labels["source_note"].text == ("南向静止帧 · 原生 80×112 · 0.5 倍" if lang == "zh" else "South static · native 80x112 · 0.5 scale"), "source note " + lang)
	ok(st["binding"] == "static-source", "actor bound to static source (%s)" % st["binding"])
	ok(st["actor_scale"] == Vector2(0.5, 0.5), "actor scale 0.5")
	ok(Vector2i(st["actor_texture_size"]) == Vector2i(80, 112), "actor frame 80x112 unscaled")
	var simg: Image = scene.actor.texture.get_image()
	simg.convert(Image.FORMAT_RGBA8)
	ok(_sha(simg.get_data()) == SOURCE_RAW, "actor pixels == native south raw hash")
	# The committed display PNG bytes are validated independently of Godot's importer, which may sanitize RGB
	# values under fully transparent texels. Visible (alpha>0) texels must match the committed file exactly.
	var raw_display := Image.load_from_file(ProjectSettings.globalize_path("res://assets/portraits/mdisplay91/rpg-2-star-ocean-the-second_muxiu_display-portrait_v01_20261024-083014-7c4a91d2.png"))
	ok(raw_display != null, "committed display file loads from disk")
	if raw_display != null:
		raw_display.convert(Image.FORMAT_RGBA8)
		ok(_sha(raw_display.get_data()) == CROP_RAW, "committed display file raw hash")
		ok(_exact_2x(simg, raw_display), "committed display file is exact 2x replication of the native south static")
		ok(_visible_equal(raw_display, img), "UI texture matches committed display on visible pixels")
	if capturing:
		await process_frame
		var cap := root.get_texture().get_image()
		var path := out.path_join("rpg-2-star-ocean-the-second_muxiu_display-preview-capture_standalone-%s-south-static_%s.png" % [lang, RUN])
		ok(cap != null and cap.get_size() == Vector2i(640, 360), "capture 640x360 " + path.get_file())
		var pe := _portrait_evidence(cap, Rect2(scene.card.get_global_transform_with_canvas() * pbox))
		print("PORTRAIT_EVIDENCE ", pe)
		ok(pe["expected"] == EXPECTED_OPAQUE, "display opaque texels 11952")
		ok(pe["differing"] * 100 >= pe["expected"] * 95, "capture shows display pixels")
		ok(pe["corner_transparent"], "transparent display corner shows card background")
		var ab := _actor_evidence(scene, cap)
		print("ACTOR_EVIDENCE ", ab)
		ok(ab["inside_stage"], "actor bounds inside stage")
		ok(ab["expected"] >= 100 and ab["differing"] * 2 >= ab["expected"], "capture shows actor pixels vs stage color")
		ok(ab["control_differing"] == 0, "empty stage corner is solid stage color")
		ok(cap.save_png(path) == OK, "capture saved " + path.get_file())
	scene.queue_free()
	await process_frame

	# Fallback: missing portrait shows the localized text label, no engine error, the static source still binds.
	var missing: Control = (load(SCENE) as PackedScene).instantiate()
	missing.portrait_path = "res://assets/portraits/mdisplay91/absent-probe-only.png"
	root.add_child(missing)
	await process_frame
	await process_frame
	var ms: Dictionary = missing.state()
	ok(not ms["portrait_loaded"], "fallback: missing portrait not loaded")
	ok(missing.labels.has("no_portrait") and missing.labels["no_portrait"].text == ("展示图缺失" if lang == "zh" else "Portrait unavailable"), "fallback: localized missing-portrait label")
	ok(ms["binding"] == "static-source", "fallback: static source still bound with missing portrait")
	if capturing:
		await process_frame
		var mcap := root.get_texture().get_image()
		ok(mcap.save_png(out.path_join("rpg-2-star-ocean-the-second_muxiu_display-preview-capture_fallback-missing-portrait-%s_%s.png" % [lang, RUN])) == OK, "fallback capture saved")
	missing.queue_free()
	await process_frame

	print("MDISPLAY91_CHECKS ", checks, " FAILS ", fails.size(), " BINDING ", st["binding"], " CAPTURES ", capturing)
	if fails.is_empty():
		print("MDISPLAY91_PROBE_OK")
	quit(0 if fails.is_empty() else 1)


static func _visible_equal(a: Image, b: Image) -> bool:
	if a.get_size() != b.get_size():
		return false
	for y in a.get_height():
		for x in a.get_width():
			var pa := a.get_pixel(x, y)
			if pa.a == 0.0:
				if b.get_pixel(x, y).a != 0.0:
					return false
			elif b.get_pixel(x, y) != pa:
				return false
	return true


static func _exact_2x(src: Image, dst: Image) -> bool:
	if src.get_width() * 2 != dst.get_width() or src.get_height() * 2 != dst.get_height():
		return false
	for y in src.get_height():
		for x in src.get_width():
			var p := src.get_pixel(x, y)
			for dy in 2:
				for dx in 2:
					if dst.get_pixel(x * 2 + dx, y * 2 + dy) != p:
						return false
	return true


# A region counts as shown when at least 95% of the display texture's opaque texels differ from the card background.
static func _portrait_evidence(img: Image, r: Rect2) -> Dictionary:
	var differing := 0
	for y in range(int(r.position.y), int(r.end.y)):
		for x in range(int(r.position.x), int(r.end.x)):
			if _differs(img.get_pixel(x, y), BG):
				differing += 1
	return {"differing": differing, "expected": EXPECTED_OPAQUE,
		"corner_transparent": not _differs(img.get_pixel(int(r.position.x) + 1, int(r.position.y) + 1), BG)}


# Actor evidence: inside the sprite's on-screen bounds, captured pixels must differ from the stage color for at
# least half of the texture's opaque pixels (scaled); an empty stage corner must remain the exact stage color.
static func _actor_evidence(scene: Control, img: Image) -> Dictionary:
	var xf: Transform2D = scene.actor.get_global_transform_with_canvas()
	var bounds := Rect2i((xf * scene.actor.get_rect()).abs())
	var stage_screen := Rect2i(scene.card.get_global_transform_with_canvas() * scene.STAGE)
	var tex_img: Image = scene.actor.texture.get_image()
	tex_img.convert(Image.FORMAT_RGBA8)
	var opaque := 0
	for y in tex_img.get_height():
		for x in tex_img.get_width():
			if tex_img.get_pixel(x, y).a > 0.5:
				opaque += 1
	var differing := 0
	var b := bounds.intersection(Rect2i(Vector2i.ZERO, img.get_size()))
	for y in range(b.position.y, b.end.y):
		for x in range(b.position.x, b.end.x):
			if _differs(img.get_pixel(x, y), STAGE_COL):
				differing += 1
	var control := Rect2i(stage_screen.position + Vector2i(2, 2), Vector2i(24, 24))
	var control_differing := 0
	for y in range(control.position.y, control.end.y):
		for x in range(control.position.x, control.end.x):
			if _differs(img.get_pixel(x, y), STAGE_COL):
				control_differing += 1
	return {"bounds": bounds, "inside_stage": stage_screen.encloses(bounds) and not control.intersects(bounds),
		"expected": int(opaque * absf(xf.get_scale().x * xf.get_scale().y)), "differing": differing,
		"control_differing": control_differing}


static func _differs(p: Color, c: Color) -> bool:
	return absf(p.r - c.r) + absf(p.g - c.g) + absf(p.b - c.b) > 0.06


static func _sha(data: PackedByteArray) -> String:
	var c := HashingContext.new()
	c.start(HashingContext.HASH_SHA256)
	c.update(data)
	return c.finish().hex_encode()
