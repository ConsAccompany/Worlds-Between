extends Node

# Isolated review capture: female protagonist SOUTH locomotion v2 (m8-w02) at 48 logical px in the
# real science city (bright) and sunlit outskirts.  Review only - not art approval, not wired into
# the runtime.  No runtime script, scene, asset or save is edited; saves go to a test path.
#
# Movement is the REAL runtime code: the area scene's own _process(delta) is called once per tick
# with delta = 1/60 while the "move_down" action is held, so the (hidden) hero moves at the area
# script's own const MOVE_SPEED (asserted == 140).  The v2 sprite is drawn at the hero's position
# with the manifest's distance-keyed frame table and root lock (bounded draw offset that pins the
# planted sole in world space).  Modes per scene:
#   run-140         v2 run, real movement (140 px/s), root lock ON      <- alternative A
#   run-140-30fps   same, but the area _process is fed delta = 1/30 (frame-rate robustness)
#   run-140-nolock  same frames and pacing, root lock OFF (ablation: what the lock buys)
#   run-140-144fps[-nolock]  delta = 1/144: stance frames now span ~2.4 ticks (lock on / off)
#   walk-16         v2 planted walk; the hero is moved 16/60 px per tick by this harness because the
#                   runtime has no slower speed (const MOVE_SPEED is not edited)   <- alternative B
#   w01-140         walk v1 frames (read-only, hash-locked), real movement, v1 distance pacing
#                   6 px/frame, no lock (baseline at the real game speed)
# Run windowed from the repository root (headless render capture can hang):
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game res://tests/<this>.tscn -- --motion-dir=<abs scratch dir>
# Writes to outputs/: per scene one still per v2 frame + v8 reference at a fixed pin (separate
# 1280x720 PNGs), a few motion sample PNGs, and one JSON receipt.  Every tick of every mode, plus one
# sprite-free background per scene, is written to --motion-dir for slip measurement and video.
# Exits 1 on any failed gate: manifest/frame/v1/v8 SHA-256 locks, MOVE_SPEED == 140, 1280x720
# captures, exact-RGB texel fidelity on every still and every 5th motion tick.
const V2_DIR := "res://assets/characters/walk-pilots-v2/"
const MANIFEST := "rpg-2-star-ocean-the-second_protagonist-female_south-locomotion-v2-manifest_m8-w02_20261015-030458-eb352ac8.json"
const MANIFEST_SHA256 := "fd85f6437db7f72cebdfd2f335565a192315b67a3e0a3fc9f0a9a057efdc8b88"
const V1_DIR := "res://assets/characters/walk-pilots/"
const V1_STEM := "rpg-2-star-ocean-the-second_protagonist-female_south-walk-pilot-"
const V1_FRAMES := [
	["f01-contact-vr", "6f8a0aba", "6441a66441ab28fae0edfe7117938b8cf51c7324464b55d5075688eec32122db", ["vr"]],
	["f02-down-vr", "dd9c8254", "b33621219f8973aa736340b911cd814a84e52ec57401a7c25f5313707010b7fc", ["vr"]],
	["f03-passing-vr", "946d8b8b", "cbdbe78f3fdf7e99a11a97b679ab3fec282589c8c182631c7549f6e3de414f9c", ["vr"]],
	["f04-up-vr", "609ca364", "24589520271620c3d89f9c0de6ff16ec79193521532928a23031a90ff0240d67", ["vr"]],
	["f05-contact-vl", "81795ce8", "cb7aaf5e715aa3d5b8ec0257e47f5ea53b5d4b1f6c5cc542abb4e445987df974", ["vl"]],
	["f06-down-vl", "556ea1f8", "77b6a7d5cde3e6d466474369e35d200915adab5e75d59749201fe74465bc722b", ["vl"]],
	["f07-passing-vl", "918cf8be", "088b0fa683901e3010b825d38c9028864b05d1dc15abbcc4aea478129fee1342", ["vl"]],
	["f08-up-vl", "00984cc2", "de181f69ff07445f8facd38dec15da135cbd7ad9ae51fea49aaf4eca8f7a164e", ["vl"]],
]
const V1_PX_PER_FRAME := 6.0
const V8_PATH := "res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png"
const V8_SHA256 := "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"
const PIN := Vector2i(40, 104)
const AREA_SCENE := "res://scenes/scifi_exploration_area.tscn"
const AREA_SCRIPT := "res://scripts/scifi_exploration_area.gd"
# scene key -> [destination, start position of the hero (clear straight south corridor), note]
const SCENES := {
	"city-bright": ["scifi.city", Vector2(340, 165), "science city, default first-visit layout (bright)"],
	"outskirts-bright": ["scifi.outskirts", Vector2(250, 150), "sunlit outskirts warm beige paving (bright)"],
}
# mode -> [frame set, ticks, root lock, movement, tick delta s]
const MODES := {
	"run-140": ["run", 61, true, "runtime", 1.0 / 60.0],
	"run-140-30fps": ["run", 31, true, "runtime", 1.0 / 30.0],
	"run-140-nolock": ["run", 61, false, "runtime", 1.0 / 60.0],
	"run-140-144fps": ["run", 145, true, "runtime", 1.0 / 144.0],
	"run-140-144fps-nolock": ["run", 145, false, "runtime", 1.0 / 144.0],
	"walk-16": ["walk", 121, true, "harness-16", 1.0 / 60.0],
	"w01-140": ["w01", 61, false, "runtime", 1.0 / 60.0],
}
# Loop phase at the first tick (logical px).  The run's stance frames are one 60 fps tick long, so a
# start exactly on a frame boundary would make frame choice depend on float rounding; 1 px avoids it.
const PHASE_PX := 1.0
const FIDELITY_EVERY := 5
const SAMPLE_TICKS := [0, 4, 8, 20, 32]
const OUTPUT_DIR := "res://../outputs"
const ALPHA_THRESHOLD := 128


func _ready() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("M8_SOUTH_LOCOMOTION_V2: " + reason)
	Input.action_release("move_down")
	get_tree().quit(1)


func _capture() -> Image:
	await RenderingServer.frame_post_draw
	return get_tree().root.get_viewport().get_texture().get_image()


func _load_rgba(path: String) -> Image:
	var image := Image.new()
	if image.load(ProjectSettings.globalize_path(path)) != OK:
		return null
	image.convert(Image.FORMAT_RGBA8)
	return image


func _fidelity(img: Image, origin: Vector2i, cap: Image) -> Dictionary:
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
	return {"opaque_texels": total, "exact_rgb_matches": exact}


func _user_arg(name: String) -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return ""


# Frame table entry for distance s along a loop: index, distance into the frame, frame start distance.
func _locate(table: Array, s: float) -> Array:
	var cycle: float = table[table.size() - 1]["end"]
	var c := fposmod(s, cycle)
	for i in table.size():
		if c < table[i]["end"] - 1e-9:
			return [i, c - table[i]["start"]]
	return [table.size() - 1, c - table[table.size() - 1]["start"]]


func _run() -> void:
	var motion_dir := _user_arg("motion-dir")
	if motion_dir == "" or DirAccess.make_dir_recursive_absolute(motion_dir) != OK:
		_fail("pass -- --motion-dir=<absolute scratch dir>")
		return
	var mpath := ProjectSettings.globalize_path(V2_DIR + MANIFEST)
	# sha256-text-lf-v1: the manifest is text, so hash it with CRLF normalised to LF (autocrlf-proof)
	var mtext := FileAccess.get_file_as_string(mpath).replace("\r\n", "\n")
	var hasher := HashingContext.new()
	hasher.start(HashingContext.HASH_SHA256)
	hasher.update(mtext.to_utf8_buffer())
	var mdigest := hasher.finish().hex_encode()
	if mdigest != MANIFEST_SHA256:
		_fail("manifest sha256-text-lf-v1 %s != %s" % [mdigest, MANIFEST_SHA256])
		return
	var manifest: Dictionary = JSON.parse_string(mtext)
	var sets := {}
	var sources := []
	for alt in ["run", "walk"]:
		var table := []
		var acc := 0.0
		for f in manifest["alternatives"][alt]["frames"]:
			var path: String = V2_DIR + String(f["file"])
			var digest := FileAccess.get_sha256(ProjectSettings.globalize_path(path))
			if digest != String(f["sha256"]):
				_fail("%s SHA-256 %s != manifest" % [f["key"], digest])
				return
			var img := _load_rgba(path)
			if img == null or img.get_size() != Vector2i(80, 112):
				_fail("cannot load 80x112 frame " + path)
				return
			var hold: float = f["hold_px"]
			table.append({"key": f["key"], "image": img, "texture": ImageTexture.create_from_image(img),
				"planted": f["planted"], "sole": f["sole"], "start": acc, "end": acc + hold,
				"r_start": float(f["root_lock"]["r_start_px"]), "slope": float(f["root_lock"]["slope"])})
			acc += hold
			sources.append({"set": alt, "key": f["key"], "path": path, "sha256": digest})
		sets[alt] = table
	var v1_table := []
	var acc1 := 0.0
	for f in V1_FRAMES:
		var path: String = V1_DIR + V1_STEM + f[0] + "_m8-w01_20261015-024345-" + f[1] + ".png"
		var digest := FileAccess.get_sha256(ProjectSettings.globalize_path(path))
		if digest != f[2]:
			_fail("w01 %s SHA-256 %s != %s" % [f[0], digest, f[2]])
			return
		var img := _load_rgba(path)
		v1_table.append({"key": "w01-" + f[0], "image": img, "texture": ImageTexture.create_from_image(img),
			"planted": f[3], "sole": {}, "start": acc1, "end": acc1 + V1_PX_PER_FRAME, "r_start": 0.0, "slope": 0.0})
		acc1 += V1_PX_PER_FRAME
		sources.append({"set": "w01", "key": f[0], "path": path, "sha256": digest})
	sets["w01"] = v1_table
	if FileAccess.get_sha256(ProjectSettings.globalize_path(V8_PATH)) != V8_SHA256:
		_fail("v8 SHA-256 mismatch")
		return
	var v8_image := _load_rgba(V8_PATH)
	var move_speed: float = (load(AREA_SCRIPT) as GDScript).get_script_constant_map().get("MOVE_SPEED", -1.0)
	if move_speed != 140.0:
		_fail("runtime MOVE_SPEED is %s, expected 140" % str(move_speed))
		return
	var window := get_tree().root
	window.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	window.content_scale_size = Vector2i(640, 360)
	window.size = Vector2i(1280, 720)
	var out_abs := ProjectSettings.globalize_path(OUTPUT_DIR)
	var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var uid := "%08x" % (randi() & 0xffffffff)
	SaveStore.root_path = "user://test-saves/m8-south-locomotion-v2"
	var app: Node = get_node("/root/AppState")
	var report_scenes := {}
	for scene_key in SCENES.keys():
		var spec: Array = SCENES[scene_key]
		var scene_report := {"note": spec[2], "modes": {}}
		for mode in MODES.keys():
			var mspec: Array = MODES[mode]
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
			hero.position = spec[1]
			var ph := hero.texture.get_image()
			ph.convert(Image.FORMAT_RGBA8)
			var ph_bottom := 0
			for y in ph.get_height():
				for x in ph.get_width():
					if ph.get_pixel(x, y).a8 >= ALPHA_THRESHOLD:
						ph_bottom = y + 1
			# ground row of the runtime hero relative to hero.position (same rule as the v8 / w01 harnesses)
			var ground_off := floorf(hero.offset.y - ph.get_height() * 0.5 + ph_bottom)
			hero.visible = false
			var pilot := Sprite2D.new()
			pilot.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
			pilot.centered = false
			pilot.offset = -Vector2(PIN)
			pilot.scale = Vector2(0.5, 0.5)
			pilot.visible = false
			host.add_child(pilot)
			var mode_report := {"frame_set": mspec[0], "root_lock": mspec[2], "movement": mspec[3], "tick_delta_s": mspec[4]}
			# sprite-free background (first mode only) for pixel-diff slip measurement
			if mode == "run-140":
				await get_tree().process_frame
				var bg := await _capture()
				bg.save_png(motion_dir.path_join("%s_background.png" % scene_key))
				# stills: every v2 frame + v8 at one fixed pin
				var stills := []
				var still_list: Array = sets["run"] + sets["walk"]
				still_list = still_list.duplicate()
				still_list.append({"key": "v8-idle-reference", "image": v8_image, "texture": ImageTexture.create_from_image(v8_image)})
				var pin_still := Vector2(spec[1].x, spec[1].y + ground_off + 40.0)
				pilot.visible = true
				for fr in still_list:
					pilot.texture = fr["texture"]
					pilot.position = pin_still
					pilot.z_index = int(pin_still.y)
					await get_tree().process_frame
					var cap := await _capture()
					if cap.get_size() != Vector2i(1280, 720):
						_fail("capture size " + str(cap.get_size()))
						return
					var origin := Vector2i(int(round(pin_still.x * 2.0)), int(round(pin_still.y * 2.0))) - PIN
					var fid := _fidelity(fr["image"], origin, cap)
					if fid["exact_rgb_matches"] != fid["opaque_texels"]:
						_fail("%s still %s fidelity %d/%d" % [scene_key, fr["key"], fid["exact_rgb_matches"], fid["opaque_texels"]])
						return
					var name := "rpg-2-star-ocean-the-second_%s_protagonist-female-south-locomotion-v2-still-%s-h48_m8-w02_%s-%s.png" % [scene_key, fr["key"], stamp, uid]
					cap.save_png(out_abs.path_join(name))
					stills.append({"frame": fr["key"], "capture": name, "sha256": FileAccess.get_sha256(out_abs.path_join(name)), "fidelity": fid})
				scene_report["stills"] = stills
				scene_report["background_capture"] = "%s_background.png (motion dir)" % scene_key
			pilot.visible = true
			var table: Array = sets[mspec[0]]
			var start_y: float = hero.position.y
			var ticks := []
			var samples := []
			if mspec[3] == "runtime":
				Input.action_press("move_down")
			for tick in mspec[1]:
				if tick > 0:
					var before := hero.position
					if mspec[3] == "runtime":
						host.call("_process", float(mspec[4]))   # the area's real movement code
					else:
						hero.position.y += 16.0 * float(mspec[4])   # alternative B speed (runtime has no slow speed)
					if hero.position.x != before.x or hero.position.y <= before.y:
						_fail("%s %s tick %d: hero did not move straight south (%s -> %s)" % [scene_key, mode, tick, str(before), str(hero.position)])
						return
				var s := hero.position.y - start_y + PHASE_PX
				var loc := _locate(table, s)
				var fr: Dictionary = table[loc[0]]
				var r := 0.0
				if mspec[2]:
					r = fr["r_start"] + fr["slope"] * float(loc[1])
				var pin_logical_y := hero.position.y + ground_off + r
				var screen_y := int(round(pin_logical_y * 2.0))
				pilot.texture = fr["texture"]
				pilot.position = Vector2(hero.position.x, screen_y * 0.5)
				pilot.z_index = int(hero.position.y)
				await get_tree().process_frame
				var cap := await _capture()
				cap.save_png(motion_dir.path_join("%s_%s_tick-%03d.png" % [scene_key, mode, tick]))
				var origin := Vector2i(int(round(hero.position.x * 2.0)), screen_y) - PIN
				var entry := {"tick": tick, "hero_logical": [hero.position.x, hero.position.y], "distance_logical": s,
					"frame": fr["key"], "planted": fr["planted"], "root_offset_logical": r,
					"cell_origin_window_px": [origin.x, origin.y]}
				if tick % FIDELITY_EVERY == 0:
					var fid := _fidelity(fr["image"], origin, cap)
					entry["fidelity"] = fid
					if fid["exact_rgb_matches"] != fid["opaque_texels"]:
						_fail("%s %s tick %d fidelity %d/%d" % [scene_key, mode, tick, fid["exact_rgb_matches"], fid["opaque_texels"]])
						return
				if tick in SAMPLE_TICKS and mode in ["run-140", "walk-16"]:
					var sname := "rpg-2-star-ocean-the-second_%s_protagonist-female-south-locomotion-v2-%s-motion-tick-%03d-%s_m8-w02_%s-%s.png" % [scene_key, mode, tick, fr["key"], stamp, uid]
					cap.save_png(out_abs.path_join(sname))
					samples.append({"tick": tick, "frame": fr["key"], "capture": sname, "sha256": FileAccess.get_sha256(out_abs.path_join(sname))})
				ticks.append(entry)
			Input.action_release("move_down")
			mode_report["start_hero_logical"] = [spec[1].x, start_y]
			mode_report["ground_offset_logical"] = ground_off
			mode_report["logical_px_per_tick_measured"] = (hero.position.y - start_y) / float(mspec[1] - 1)
			mode_report["motion_samples"] = samples
			mode_report["ticks"] = ticks
			scene_report["modes"][mode] = mode_report
			print("MOTION %s %s %d ticks, %.4f px/tick" % [scene_key, mode, ticks.size(), mode_report["logical_px_per_tick_measured"]])
			host.queue_free()
			await get_tree().process_frame
			await get_tree().process_frame
		report_scenes[scene_key] = scene_report
	var report := {
		"project": "Worlds Between", "milestone": "M8", "variant": "m8-w02",
		"purpose": "Isolated in-engine moving captures of female south locomotion v2 (run @ real 140 px/s at 60, 30 and 144 fps, planted walk @ 16 px/s) with w01 baseline and a no-lock ablation.",
		"status": "technical review evidence only; unapproved; not runtime-integrated",
		"art_approved": false, "human_reviewed": false,
		"renderer": "Godot %s windowed, viewport texture capture" % Engine.get_version_info()["string"],
		"canvas": [640, 360], "window": [1280, 720], "scale": 0.5, "filter": "nearest", "shadow": "none",
		"cell_pin": [PIN.x, PIN.y], "manifest": MANIFEST, "manifest_sha256_text_lf_v1": mdigest,
		"runtime_move_speed_logical_px_s": move_speed, "loop_phase_at_tick0_px": PHASE_PX,
		"movement_note": "runtime modes call the area scene's own _process(1/60) with move_down held; walk-16 is moved by this harness",
		"modes": MODES, "sources": sources, "v8_reference_sha256": V8_SHA256,
		"gates_passed": ["manifest/frame/w01/v8 SHA-256 locks", "MOVE_SPEED == 140", "1280x720 captures", "exact-RGB texel fidelity on all stills and every 5th motion tick"],
		"scenes": report_scenes,
	}
	var rpath := out_abs.path_join("rpg-2-star-ocean-the-second_city-outskirts_protagonist-female-south-locomotion-v2-capture-receipt_m8-w02_%s-%s.json" % [stamp, uid])
	var f := FileAccess.open(rpath, FileAccess.WRITE)
	f.store_string(JSON.stringify(report, "\t") + "\n")
	f.close()
	print("REPORT " + rpath)
	get_tree().quit(0)
