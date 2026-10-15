extends Node

# Isolated review capture: female protagonist SOUTH walk pilot w01 (8 frames built from the approved
# static selout v8 idle) at 48 logical px in the real science city (bright) and sunlit outskirts.
# Review only - not art approval, not wired into the runtime. No runtime script, scene, asset or
# save is edited; saves are redirected to a test path; area _process is disabled after two frames.
# Placement is the v8 QA harness's (placeholder hero x +36 city / -36 outskirts, its ground row),
# but with ONE fixed cell pin (40,104) for every frame, so the ground anchor never moves per frame.
# Frames are read from res://assets/characters/walk-pilots/ (a .gdignore folder: no import entry).
# Run windowed from the repository root (headless render capture can hang):
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game res://tests/<this>.tscn -- --motion-dir=<abs scratch dir>
# Writes to outputs/: per scene 8 frame stills + 1 v8 idle reference (separate 1280x720 PNGs),
# 3 motion sample PNGs, and one JSON receipt. Every motion tick is written to --motion-dir (scratch,
# outside the repo) for GIF/MP4 encoding. Exits 1 on any failed gate:
#   frame SHA-256 locks; 1280x720 captures; every opaque texel shown 1:1 with exact RGB at the
#   expected window position (stills and every 12th motion tick); identical pin for all frames.
const DIR := "res://assets/characters/walk-pilots/"
const STEM := "rpg-2-star-ocean-the-second_protagonist-female_south-walk-pilot-"
const FRAMES := [
	["f01-contact-vr", "6f8a0aba", "6441a66441ab28fae0edfe7117938b8cf51c7324464b55d5075688eec32122db", "vr"],
	["f02-down-vr", "dd9c8254", "b33621219f8973aa736340b911cd814a84e52ec57401a7c25f5313707010b7fc", "vr"],
	["f03-passing-vr", "946d8b8b", "cbdbe78f3fdf7e99a11a97b679ab3fec282589c8c182631c7549f6e3de414f9c", "vr"],
	["f04-up-vr", "609ca364", "24589520271620c3d89f9c0de6ff16ec79193521532928a23031a90ff0240d67", "vr"],
	["f05-contact-vl", "81795ce8", "cb7aaf5e715aa3d5b8ec0257e47f5ea53b5d4b1f6c5cc542abb4e445987df974", "vl"],
	["f06-down-vl", "556ea1f8", "77b6a7d5cde3e6d466474369e35d200915adab5e75d59749201fe74465bc722b", "vl"],
	["f07-passing-vl", "918cf8be", "088b0fa683901e3010b825d38c9028864b05d1dc15abbcc4aea478129fee1342", "vl"],
	["f08-up-vl", "00984cc2", "de181f69ff07445f8facd38dec15da135cbd7ad9ae51fea49aaf4eca8f7a164e", "vl"],
]
const V8_PATH := "res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png"
const V8_SHA256 := "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"
const PIN := Vector2i(40, 104)
const AREA_SCENE := "res://scenes/scifi_exploration_area.tscn"
const SCENES := {
	"city-bright": ["scifi.city", 36.0, "science city, default first-visit layout (bright)"],
	"outskirts-bright": ["scifi.outskirts", -36.0, "sunlit outskirts warm beige paving (bright)"],
}
# Motion: straight south, distance-driven frames (6 logical px per frame = 48 px cycle, 24 px step),
# 1 logical px per rendered tick = 60 logical px/s at 60 fps -> 10 frames/s, 2.5 steps/s.
const START_ABOVE := 40.0
const TICKS := 97
const SPEED_PER_TICK := 1.0
const PX_PER_FRAME := 6.0
const SAMPLE_EVERY := 12
const OUTPUT_DIR := "res://../outputs"
const ALPHA_THRESHOLD := 128


func _ready() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("M8_SOUTH_WALK_PILOT: " + reason)
	get_tree().quit(1)


func _capture() -> Image:
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	return get_tree().root.get_viewport().get_texture().get_image()


func _load_rgba(path: String) -> Image:
	var image := Image.new()
	if image.load(ProjectSettings.globalize_path(path)) != OK:
		return null
	image.convert(Image.FORMAT_RGBA8)
	return image


# Every opaque texel must appear with exact RGB at window = 2 * logical position + (texel - PIN).
func _fidelity(img: Image, pos: Vector2, cap: Image) -> Dictionary:
	var origin := Vector2i(int(round(pos.x * 2.0)), int(round(pos.y * 2.0))) - PIN
	var total := 0
	var exact := 0
	for y in img.get_height():
		for x in img.get_width():
			var t := img.get_pixel(x, y)
			if t.a8 < ALPHA_THRESHOLD:
				continue
			total += 1
			var s := cap.get_pixel(origin.x + x, origin.y + y)
			if s.r8 == t.r8 and s.g8 == t.g8 and s.b8 == t.b8:
				exact += 1
	return {"opaque_texels": total, "exact_rgb_matches": exact, "window_origin_of_cell": [origin.x, origin.y]}


func _user_arg(name: String) -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return ""


func _run() -> void:
	var motion_dir := _user_arg("motion-dir")
	if motion_dir == "" or DirAccess.make_dir_recursive_absolute(motion_dir) != OK:
		_fail("pass -- --motion-dir=<absolute scratch dir>")
		return
	var frames: Array = []
	var sources := []
	for f in FRAMES:
		var path: String = DIR + STEM + f[0] + "_m8-w01_20261015-024345-" + f[1] + ".png"
		var digest := FileAccess.get_sha256(ProjectSettings.globalize_path(path))
		if digest != f[2]:
			_fail("%s SHA-256 %s != %s" % [f[0], digest, f[2]])
			return
		var img := _load_rgba(path)
		if img == null or img.get_size() != Vector2i(80, 112):
			_fail("cannot load 80x112 frame " + path)
			return
		frames.append({"key": f[0], "image": img, "texture": ImageTexture.create_from_image(img), "stance": f[3]})
		sources.append({"key": f[0], "path": path, "sha256": digest})
	if FileAccess.get_sha256(ProjectSettings.globalize_path(V8_PATH)) != V8_SHA256:
		_fail("v8 SHA-256 mismatch")
		return
	var v8_image := _load_rgba(V8_PATH)
	var window := get_tree().root
	window.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	window.content_scale_size = Vector2i(640, 360)
	window.size = Vector2i(1280, 720)
	var out_abs := ProjectSettings.globalize_path(OUTPUT_DIR)
	var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var uid := "%08x" % (randi() & 0xffffffff)
	SaveStore.root_path = "user://test-saves/m8-south-walk-pilot-w01"
	var app: Node = get_node("/root/AppState")
	var report_scenes := {}
	for scene_key in SCENES.keys():
		var spec: Array = SCENES[scene_key]
		app.begin_new_run()
		app.hero_appearance = "female"
		if not app.select_destination(spec[0]):
			_fail("destination rejected: " + spec[0])
			return
		var host: Node2D = (load(AREA_SCENE) as PackedScene).instantiate()
		add_child(host)
		await get_tree().process_frame
		await get_tree().process_frame
		host.set_process(false)
		if String(host.get("destination_id")) != spec[0]:
			_fail("scene fell back to " + String(host.get("destination_id")))
			return
		var hero: Sprite2D = host.get("hero")
		var ph := hero.texture.get_image()
		ph.convert(Image.FORMAT_RGBA8)
		var ph_bottom := 0
		for y in ph.get_height():
			for x in ph.get_width():
				if ph.get_pixel(x, y).a8 >= ALPHA_THRESHOLD:
					ph_bottom = y + 1
		var ground_y := floorf(hero.position.y + hero.offset.y - ph.get_height() * 0.5 + ph_bottom)
		var pin_x := floorf(hero.position.x + float(spec[1]))
		var pilot := Sprite2D.new()
		pilot.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		pilot.centered = false
		pilot.offset = -Vector2(PIN)
		pilot.scale = Vector2(0.5, 0.5)
		host.add_child(pilot)
		var stills := []
		# --- stills: each frame (and the v8 idle reference) at the identical pin
		var still_list: Array = frames.duplicate()
		still_list.append({"key": "v8-idle-reference", "image": v8_image, "texture": ImageTexture.create_from_image(v8_image), "stance": "-"})
		for fr in still_list:
			pilot.texture = fr["texture"]
			pilot.position = Vector2(pin_x, ground_y)
			pilot.z_index = int(ground_y)
			var cap := await _capture()
			if cap.get_size() != Vector2i(1280, 720):
				_fail("capture size " + str(cap.get_size()))
				return
			var fid := _fidelity(fr["image"], pilot.position, cap)
			if fid["exact_rgb_matches"] != fid["opaque_texels"]:
				_fail("%s %s fidelity %d/%d" % [scene_key, fr["key"], fid["exact_rgb_matches"], fid["opaque_texels"]])
				return
			var name := "rpg-2-star-ocean-the-second_%s_protagonist-female-south-walk-pilot-%s-h48_m8-w01_%s-%s.png" % [scene_key, fr["key"], stamp, uid]
			cap.save_png(out_abs.path_join(name))
			stills.append({"frame": fr["key"], "capture": name, "sha256": FileAccess.get_sha256(out_abs.path_join(name)), "pin_logical": [pin_x, ground_y], "fidelity": fid})
			print("STILL %s %s %d/%d" % [scene_key, fr["key"], fid["exact_rgb_matches"], fid["opaque_texels"]])
		# --- motion: walk south, distance-driven frame selection
		var ticks := []
		var samples := []
		for tick in TICKS:
			var dist := tick * SPEED_PER_TICK
			var fi := int(floor(dist / PX_PER_FRAME)) % frames.size()
			var fr: Dictionary = frames[fi]
			pilot.texture = fr["texture"]
			pilot.position = Vector2(pin_x, ground_y - START_ABOVE + dist)
			pilot.z_index = int(pilot.position.y)
			var cap := await _capture()
			cap.save_png(motion_dir.path_join("%s_tick-%03d.png" % [scene_key, tick]))
			var entry := {"tick": tick, "distance_logical": dist, "frame": fr["key"], "stance_leg": fr["stance"], "pin_logical": [pilot.position.x, pilot.position.y]}
			if tick % SAMPLE_EVERY == 0:
				var fid := _fidelity(fr["image"], pilot.position, cap)
				entry["fidelity"] = fid
				if fid["exact_rgb_matches"] != fid["opaque_texels"]:
					_fail("%s motion tick %d fidelity %d/%d" % [scene_key, tick, fid["exact_rgb_matches"], fid["opaque_texels"]])
					return
				if tick in [24, 48, 72]:
					var sname := "rpg-2-star-ocean-the-second_%s_protagonist-female-south-walk-pilot-motion-tick-%03d-%s_m8-w01_%s-%s.png" % [scene_key, tick, fr["key"], stamp, uid]
					cap.save_png(out_abs.path_join(sname))
					samples.append({"tick": tick, "frame": fr["key"], "capture": sname, "sha256": FileAccess.get_sha256(out_abs.path_join(sname))})
			ticks.append(entry)
		print("MOTION %s %d ticks" % [scene_key, ticks.size()])
		report_scenes[scene_key] = {"note": spec[2], "pin_x_logical": pin_x, "ground_y_logical": ground_y,
			"placeholder_position_logical": [hero.position.x, hero.position.y], "stills": stills,
			"motion_samples": samples, "motion_ticks": ticks}
		host.queue_free()
		await get_tree().process_frame
		await get_tree().process_frame
	var report := {
		"project": "Worlds Between", "milestone": "M8", "variant": "m8-w01",
		"purpose": "Isolated in-engine review captures of the female south walk pilot w01 (8 frames from approved static selout v8).",
		"status": "technical review evidence only; unapproved; not runtime-integrated",
		"art_approved": false, "human_reviewed": false,
		"renderer": "Godot %s windowed, viewport texture capture" % Engine.get_version_info()["string"],
		"canvas": [640, 360], "window": [1280, 720], "scale": 0.5, "filter": "nearest", "shadow": "none",
		"cell_pin": [PIN.x, PIN.y],
		"motion_model": {"direction": "south (+y)", "logical_px_per_tick": SPEED_PER_TICK, "assumed_fps": 60,
			"logical_px_per_s": SPEED_PER_TICK * 60.0, "frame_selection": "distance-driven: floor(distance / %d) mod 8" % int(PX_PER_FRAME),
			"cycle_logical_px": PX_PER_FRAME * 8.0, "ticks": TICKS, "start_above_ground_logical": START_ABOVE,
			"runtime_note": "runtime uses 140 logical px/s with time-driven 0.12 s phases; this pilot does not change it"},
		"sources": sources, "v8_reference_sha256": V8_SHA256,
		"gates_passed": ["frame SHA-256 locks", "1280x720 captures", "100% texel fidelity at the fixed pin on all stills and every 12th motion tick"],
		"scenes": report_scenes,
	}
	var rpath := out_abs.path_join("rpg-2-star-ocean-the-second_city-outskirts_protagonist-female-south-walk-pilot-capture-receipt_m8-w01_%s-%s.json" % [stamp, uid])
	var f := FileAccess.open(rpath, FileAccess.WRITE)
	f.store_string(JSON.stringify(report, "\t") + "\n")
	f.close()
	print("REPORT " + rpath)
	get_tree().quit(0)
