extends SceneTree
# Probe for the standalone Jiang Lan display preview. Args after --: --lang=en|zh --out=<abs dir>
# Prints JDISPLAY40_PROBE_OK only when every check passes; capture is attempted only with a rendering display.

const SCENE := "res://scenes/jdisplay40/rpg-2-star-ocean-the-second_jiang-lan_display-preview_standalone-v01_20261022-155956-1414792c.tscn"
const MANIFEST := "res://assets/portraits/jiang-display40/rpg-2-star-ocean-the-second_jiang-lan_display-portrait-manifest_v01_20261022-155956-1414792c.json"
const CROP_RAW_SHA := "e65dd229668bba6ec07a38e3a1d64e478ed49b6008c457b40fa12c35b664f1f3"
const SOURCE_SHA := "bbddf46f3c1370742c86d1934e36adf7969e5f43a4e6d67ddbf9ba8d44902e4a"

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
	var man = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
	ok(typeof(man) == TYPE_DICTIONARY, "manifest parses")
	if typeof(man) == TYPE_DICTIONARY:
		ok(man["source"]["sha256"] == SOURCE_SHA, "manifest source pin")
		var c: Dictionary = man["crop"]
		ok([int(c["left"]), int(c["top"]), int(c["right"]), int(c["bottom"])] == [0, 0, 480, 630], "crop rect 0,0,480,630")
		ok(man["output"]["raw_rgba_sha256"] == CROP_RAW_SHA, "manifest raw hash pin")
		ok(String(man["status"]).begins_with("UNAPPROVED"), "status UNAPPROVED")
	var scene: Control = (load(SCENE) as PackedScene).instantiate()
	root.add_child(scene)
	await process_frame
	await process_frame
	var st: Dictionary = scene.state()
	print("STATE ", st)
	ok(st["lang"] == lang, "lang from --lang")
	ok(Vector2i(st["portrait_size"]) == Vector2i(480, 630), "portrait texture 480x630")
	var img: Image = scene.portrait.texture.get_image()
	img.convert(Image.FORMAT_RGBA8)
	ok(img.get_data().hex_encode() != "" and _sha(img.get_data()) == CROP_RAW_SHA, "portrait pixels == crop raw hash")
	ok(scene.portrait.stretch_mode == TextureRect.STRETCH_KEEP_ASPECT_CENTERED, "keep aspect")
	ok(scene.portrait.texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST, "nearest")
	var pbox: Rect2 = scene.portrait.get_rect()
	ok(pbox.size == Vector2(180, 250), "portrait box 180x250")
	for key in ["title", "pending", "hint"]:
		ok(not pbox.intersects(scene.labels[key].get_rect()), "portrait clear of " + key)
	for key in ["name", "career", "identity"]:
		ok(not scene.STAGE.intersects(scene.labels[key].get_rect()), "identity clear of actor stage: " + key)
	for b in scene.card.get_children():
		if b is Button:
			ok(not pbox.intersects(b.get_rect()), "portrait clear of button " + b.name)
	ok(st["binding"] in ["pilot", "manual-viewer"], "actor bound (%s)" % st["binding"])
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
			if out != "" and DisplayServer.get_name() != "headless":
				await process_frame
				var cap := root.get_texture().get_image()
				var path := out.path_join("rpg-2-star-ocean-the-second_jiang-lan_display-preview-capture_standalone-%s-%s-%s_20261022-155956-1414792c.png" % [lang, dir, act])
				ok(cap != null and cap.save_png(path) == OK, "capture " + path.get_file())
	ok(seen.size() == 4 and seen.values()[0] != seen.values()[1], "four directions show distinct textures")
	ok(scene.labels["pending"].text == ("美术待定" if lang == "zh" else "Art pending"), "art pending label " + lang)
	print("JDISPLAY40_CHECKS ", checks, " FAILS ", fails.size(), " BINDING ", st["binding"])
	if fails.is_empty():
		print("JDISPLAY40_PROBE_OK")
	quit(0 if fails.is_empty() else 1)


static func _sha(data: PackedByteArray) -> String:
	var c := HashingContext.new()
	c.start(HashingContext.HASH_SHA256)
	c.update(data)
	return c.finish().hex_encode()
