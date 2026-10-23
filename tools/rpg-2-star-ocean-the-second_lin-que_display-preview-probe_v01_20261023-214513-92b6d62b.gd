extends SceneTree
# Probe for the standalone Lin Que display preview (derived from the Jiang display40 probe).
# Args after --: --lang=en|zh --out=<abs dir>
# Prints LDISPLAY64_PROBE_OK only when every check passes; capture is attempted only with a rendering display.
# Besides the normal scene it instantiates two fallback copies: a missing portrait path and a forced manual viewer.

const SCENE := "res://scenes/ldisplay64/rpg-2-star-ocean-the-second_lin-que_display-preview_standalone-v01_20261023-214513-92b6d62b.tscn"
const MANIFEST := "res://assets/portraits/ldisplay64/rpg-2-star-ocean-the-second_lin-que_display-portrait-manifest_v01_20261023-214513-92b6d62b.json"
const CROP_RAW_SHA := "7d8bbb214bb6e8780e26622a0acda37b8d35dd30c0c2dfadd561ab07ba3ab333"
const SOURCE_SHA := "24007e147c9dd67b330af4a84ac13054f65989cddb9bdf2702dc5c80de7fb352"
const RUN := "20261023-214513-92b6d62b"
const BG := Color(0.09, 0.11, 0.15)
const Pilot := preload("res://scripts/exploration_sprite_set_pilot.gd")

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
		ok(man["source"]["sha256"] == SOURCE_SHA, "manifest source pin")
		ok(man["subject"] == "lin-que", "manifest subject lin-que")
		var c: Dictionary = man["crop"]
		ok([int(c["left"]), int(c["top"]), int(c["right"]), int(c["bottom"])] == [16, 0, 592, 800], "crop rect 16,0,592,800")
		ok(c["resampled"] == false and c["repainted"] == false and c["ai_generated_new_pixels"] == false, "crop is an exact slice")
		ok(man["output"]["raw_rgba_sha256"] == CROP_RAW_SHA, "manifest raw hash pin")
		ok(String(man["status"]).begins_with("UNAPPROVED"), "status UNAPPROVED")
	var scene: Control = (load(SCENE) as PackedScene).instantiate()
	root.add_child(scene)
	await process_frame
	await process_frame
	var st: Dictionary = scene.state()
	print("STATE ", st)
	ok(st["lang"] == lang, "lang from --lang")
	ok(st["portrait_loaded"] and not scene.labels.has("no_portrait"), "portrait loaded, no fallback label")
	ok(Vector2i(st["portrait_size"]) == Vector2i(576, 800), "portrait texture 576x800")
	var img: Image = scene.portrait.texture.get_image()
	img.convert(Image.FORMAT_RGBA8)
	ok(_sha(img.get_data()) == CROP_RAW_SHA, "portrait pixels == crop raw hash")
	ok(scene.portrait.stretch_mode == TextureRect.STRETCH_KEEP_ASPECT_CENTERED, "keep aspect")
	ok(scene.portrait.texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST, "nearest")
	var pbox: Rect2 = scene.portrait.get_rect()
	ok(pbox.size == Vector2(180, 250), "portrait box 180x250")
	for key in ["title", "pending", "hint", "name", "career", "identity"]:
		ok(not pbox.intersects(scene.labels[key].get_rect()), "portrait clear of " + key)
	for key in ["name", "career", "identity"]:
		var r: Rect2 = scene.labels[key].get_rect()
		ok(not scene.STAGE.intersects(r), "identity clear of actor stage: " + key)
		ok(Rect2(Vector2.ZERO, scene.CARD).encloses(r), "inside card: " + key)
	for b in scene.card.get_children():
		if b is Button:
			ok(not pbox.intersects(b.get_rect()), "portrait clear of button " + b.name)
	ok(scene.labels["name"].text == ("林阙" if lang == "zh" else "Lin Que"), "name " + lang)
	ok(scene.labels["career"].text == ("精确射手 · 22岁" if lang == "zh" else "Precision shooter · 22"), "career " + lang)
	ok(st["binding"] == "pilot", "actor bound through pilot (%s)" % st["binding"])
	ok(st["actor_scale"] == Vector2(0.5, 0.5), "actor scale 0.5")
	ok(Vector2i(st["actor_texture_size"]) == Vector2i(80, 112), "actor frame 80x112 unscaled")
	var seen := {}
	for dir in ["west", "north", "east", "south"]:
		scene.card.get_node("Face_" + dir).pressed.emit()
		await process_frame
		ok(scene.facing == dir, "arrow button faces " + dir)
		seen[dir] = scene.actor.texture
		for act in ["walk", "idle"]:
			scene.toggle_action()
			await process_frame
			ok(scene.action == act, "toggle -> %s (%s)" % [act, dir])
			if capturing:
				await process_frame
				var cap := root.get_texture().get_image()
				var path := out.path_join("rpg-2-star-ocean-the-second_lin-que_display-preview-capture_standalone-%s-%s-%s_%s.png" % [lang, dir, act, RUN])
				ok(cap != null and cap.get_size() == Vector2i(640, 360), "capture 640x360 " + path.get_file())
				ok(_rendered(cap, Rect2i(16, 56, 180, 250)), "capture shows portrait pixels " + dir + act)
				var ab := _actor_evidence(scene, cap)
				print("ACTOR_EVIDENCE %s %s %s" % [dir, act, ab])
				ok(ab["inside_stage"], "actor bounds inside stage " + dir + act)
				ok(ab["expected"] >= 100 and ab["differing"] * 2 >= ab["expected"], "capture shows actor pixels vs stage color " + dir + act)
				ok(ab["control_differing"] == 0, "empty stage corner is solid stage color " + dir + act)
				ok(cap.save_png(path) == OK, "capture saved " + path.get_file())
	var distinct := {}
	for t in seen.values():
		distinct[t] = true
	ok(distinct.size() == 4, "four directions show distinct textures")
	ok(scene.labels["pending"].text == ("美术待定" if lang == "zh" else "Art pending"), "art pending label " + lang)
	scene.queue_free()
	await process_frame

	# Fallback 1: missing portrait shows the localized text label, no engine error, the rest still binds.
	var missing: Control = (load(SCENE) as PackedScene).instantiate()
	missing.portrait_path = "res://assets/portraits/ldisplay64/absent-probe-only.png"
	root.add_child(missing)
	await process_frame
	await process_frame
	var ms: Dictionary = missing.state()
	ok(not ms["portrait_loaded"], "fallback: missing portrait not loaded")
	ok(missing.labels.has("no_portrait") and missing.labels["no_portrait"].text == ("展示图缺失" if lang == "zh" else "Portrait unavailable"), "fallback: localized missing-portrait label")
	ok(ms["binding"] == "pilot", "fallback: actor still bound with missing portrait")
	if capturing:
		await process_frame
		var mcap := root.get_texture().get_image()
		ok(mcap.save_png(out.path_join("rpg-2-star-ocean-the-second_lin-que_display-preview-capture_fallback-missing-portrait-%s_%s.png" % [lang, RUN])) == OK, "fallback capture saved")
	missing.queue_free()
	await process_frame

	# Fallback 2: forced bounded manual viewer of the same registry: same frame size/scale, directions and time advance.
	var manual: Control = (load(SCENE) as PackedScene).instantiate()
	manual.force_manual = true
	root.add_child(manual)
	await process_frame
	var mv: Dictionary = manual.state()
	ok(mv["binding"] == "manual-viewer", "fallback: manual viewer bound (%s)" % mv["binding"])
	ok(mv["actor_scale"] == Vector2(0.5, 0.5), "fallback: manual scale 0.5")
	ok(Vector2i(mv["actor_texture_size"]) == Vector2i(80, 112), "fallback: manual frame 80x112")
	var mseen := {}
	for dir in ["west", "north", "east", "south"]:
		manual.set_facing(dir)
		mseen[manual.actor.texture] = true
	ok(mseen.size() == 4, "fallback: manual four distinct facings")
	manual.set_action("walk")
	var f0: Texture2D = manual.actor.texture
	var walk_clip: Dictionary = manual.manual["clips"]["walk"]["south"]
	ok(walk_clip["textures"].size() == 12, "fallback: manual south walk has 12 frames")
	manual.manual_clock_us = int(walk_clip["ends_us"][0])
	manual._apply_manual()
	ok(manual.actor.texture != f0 and manual.actor.texture == walk_clip["textures"][1], "fallback: frame advances exactly at first boundary")
	manual.manual_clock_us = int(walk_clip["ends_us"][0]) - 1
	manual._apply_manual()
	ok(manual.actor.texture == f0, "fallback: frame holds 1us before boundary")
	# Exact frame_at boundaries: last frame 1us before cycle end, wrap to frame 0 at cycle end.
	var cyc := int(walk_clip["cycle_us"])
	var last: int = walk_clip["textures"].size() - 1
	ok(cyc == int(walk_clip["ends_us"][last]), "fallback: cycle equals last frame end")
	ok(Pilot.frame_at(walk_clip, 0) == 0, "frame_at(0) == 0")
	ok(Pilot.frame_at(walk_clip, int(walk_clip["ends_us"][0]) - 1) == 0, "frame_at(end0-1) == 0")
	ok(Pilot.frame_at(walk_clip, int(walk_clip["ends_us"][0])) == 1, "frame_at(end0) == 1")
	ok(Pilot.frame_at(walk_clip, cyc - 1) == last, "frame_at(cycle-1) == last")
	ok(Pilot.frame_at(walk_clip, cyc) == 0, "frame_at(cycle) wraps to 0")
	manual.manual_clock_us = cyc - 1
	manual._apply_manual()
	ok(manual.actor.texture == walk_clip["textures"][last], "fallback: last frame shown 1us before cycle end")
	manual.manual_clock_us = cyc
	manual._apply_manual()
	ok(manual.actor.texture == walk_clip["textures"][0], "fallback: wraps to first frame at cycle end")
	manual.queue_free()
	await process_frame

	print("LDISPLAY64_CHECKS ", checks, " FAILS ", fails.size(), " BINDING ", st["binding"], " CAPTURES ", capturing)
	if fails.is_empty():
		print("LDISPLAY64_PROBE_OK")
	quit(0 if fails.is_empty() else 1)


# A region counts as rendered when a meaningful share of its pixels differ from the card background.
static func _rendered(img: Image, r: Rect2i) -> bool:
	var differing := 0
	var total := 0
	for y in range(r.position.y, r.end.y, 4):
		for x in range(r.position.x, r.end.x, 4):
			total += 1
			var p := img.get_pixel(x, y)
			if absf(p.r - BG.r) + absf(p.g - BG.g) + absf(p.b - BG.b) > 0.06:
				differing += 1
	return total > 0 and differing * 4 >= total


# Actor evidence: inside the sprite's on-screen bounds, captured pixels must differ from the stage color for at
# least half of the texture's opaque pixels (scaled); an empty stage corner must remain the exact stage color.
static func _actor_evidence(scene: Control, img: Image) -> Dictionary:
	var stage_col: Color = Color(0.16, 0.19, 0.24)
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
			if _differs(img.get_pixel(x, y), stage_col):
				differing += 1
	var control := Rect2i(stage_screen.position + Vector2i(2, 2), Vector2i(24, 24))
	var control_differing := 0
	for y in range(control.position.y, control.end.y):
		for x in range(control.position.x, control.end.x):
			if _differs(img.get_pixel(x, y), stage_col):
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
