extends Node

# Test-only gameplay-scale preview of the UNAPPROVED female protagonist south run v3r2 (m8-w03).
# Review evidence only: not art acceptance, not runtime integration.  The creator approved only the
# selout v8 SOUTH IDLE static frame and the 48 logical px display scale; nothing here changes that.
# No runtime script, scene, sprite, save or Game Bible file is edited.  The 16 v3r2 PNGs and the
# manifest are read from disk (their folder has a .gdignore) and hash-locked; saves go to a test path.
#
# Scenes (existing game scenes, used read-only):
#   city-bright       scifi_exploration_area.tscn, scifi.city, default first-visit layout
#   outskirts-bright  scifi_exploration_area.tscn, scifi.outskirts, sunlit paving
#   annex-dark        survey_annex.tscn, scifi.city room 2 (darkest annex floor of the six rooms)
# Movement is the REAL runtime code: the scene's own _process(delta) is called once per tick with
# "move_down" held, so the hidden runtime hero moves at the scene's const MOVE_SPEED (asserted 140).
# The v3r2 frame is drawn at the hero position with the manifest's distance-keyed frame table and
# root lock (bounded draw-only offset that keeps the planted sole fixed in world space).
# Modes per scene:
#   run-140         60 fps ticks, root lock on
#   run-140-30fps   30 fps ticks, root lock on (frames drop at 30 fps; recorded)
#   run-140-144fps  144 fps ticks, root lock on
#   run-140-nolock  60 fps ticks, root lock off (ablation)
# Run windowed from the repository root (headless render capture can hang):
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game res://tests/<this>.tscn -- --motion-dir=<abs scratch dir>
# Writes to outputs/ only separate 1280x720 PNGs (no sheets) and one JSON receipt.  Every tick, the
# per-frame stills and one sprite-free background per scene go to --motion-dir (scratch, for GIFs).
# Gates (exit 1 on failure): manifest sha256-text-lf-v1, 16 frame + v8 sha256-bytes locks, manifest
# cell / pin / scale, binary alpha in every frame, MOVE_SPEED == 140, 1280x720 captures, exact-RGB
# fidelity and untouched transparent texels on every still, fidelity on every 5th motion tick,
# |root offset| <= manifest max, straight-south movement.  Slip, head step and contrast are
# MEASURED on captured pixels and reported, never used to declare visual quality.
const RUN_DIR := "res://assets/characters/run-pilots-v3r2/"
const MANIFEST := "rpg-2-star-ocean-the-second_protagonist-female_south-run-v3r2-manifest_m8-w03_20261015-035446-46ec0bdf.json"
const MANIFEST_SHA256 := "dbf41fdbb45c2c0e925d716e88018d3d6eb212e9ba78841d544f7768dd693c3a"
const V8_PATH := "res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png"
const V8_SHA256 := "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"
const CELL := Vector2i(80, 112)
const PIN := Vector2i(40, 104)
const AREA_SCENE := "res://scenes/scifi_exploration_area.tscn"
const AREA_SCRIPT := "res://scripts/scifi_exploration_area.gd"
const ANNEX_SCENE := "res://scenes/survey_annex.tscn"
const ANNEX_SCRIPT := "res://scripts/survey_annex.gd"
# scene key -> [kind, destination, annex room, hero start (clear straight-south corridor), note]
const SCENES := {
	"city-bright": ["area", "scifi.city", 0, Vector2(340, 165), "science city, default first-visit layout (bright)"],
	"outskirts-bright": ["area", "scifi.outskirts", 0, Vector2(250, 150), "sunlit outskirts warm beige paving (bright)"],
	"annex-dark": ["annex", "scifi.city", 2, Vector2(240, 150), "city survey annex room 2, darkest annex floor (relative luminance ~0.13; dark stone, not a night scene)"],
}
# mode -> [ticks, root lock, tick delta s]; every mode covers 140 logical px = two 70 px loops
const MODES := {
	"run-140": [61, true, 1.0 / 60.0],
	"run-140-30fps": [31, true, 1.0 / 30.0],
	"run-140-144fps": [145, true, 1.0 / 144.0],
	"run-140-nolock": [61, false, 1.0 / 60.0],
}
# Stance frames last exactly one 60 fps tick (7/3 px), so start 1 px into the loop to keep frame
# choice off float boundaries (same as the v2 harness).
const PHASE_PX := 1.0
const FIDELITY_EVERY := 5
# run-140 ticks whose capture is also written to outputs/ (first tick showing each key)
const OUTPUT_MOTION_KEYS := ["run-f01-contact-vr", "run-f03-mid-vr", "run-f07-flight2-vr"]
# frames whose fixed-pin still is also written to outputs/ (all 16 + v8 go to the motion dir)
const OUTPUT_STILL_KEYS := ["v8-idle-reference"]
const CONTRAST_KEYS := ["v8-idle-reference", "run-f01-contact-vr", "run-f07-flight2-vr", "run-f11-mid-vl"]
const LEG_SPLIT_X := 38
const LEG_BAND_TOP := 84
const OUTPUT_DIR := "res://../outputs"
const SLUG := "rpg-2-star-ocean-the-second"
const VARIANT := "m8-w03"


func _ready() -> void:
	call_deferred("_run")


func _fail(reason: String) -> void:
	push_error("M8_SOUTH_RUN_V3R2_PREVIEW: " + reason)
	Input.action_release("move_down")
	get_tree().quit(1)


func _capture() -> Image:
	await RenderingServer.frame_post_draw
	var image := get_tree().root.get_viewport().get_texture().get_image()
	image.convert(Image.FORMAT_RGB8)
	return image


func _load_rgba(path: String) -> Image:
	var image := Image.new()
	if image.load(ProjectSettings.globalize_path(path)) != OK:
		return null
	image.convert(Image.FORMAT_RGBA8)
	return image


func _user_arg(name: String) -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return ""


func _binary_alpha(img: Image) -> bool:
	for y in img.get_height():
		for x in img.get_width():
			var a := img.get_pixel(x, y).a8
			if a != 0 and a != 255:
				return false
	return true


func _opaque_rows(img: Image) -> Vector2i:
	var top := -1
	var bottom := -1
	for y in img.get_height():
		for x in img.get_width():
			if img.get_pixel(x, y).a8 > 0:
				if top < 0:
					top = y
				bottom = y
				break
	return Vector2i(top, bottom)


# Exact-RGB fidelity of opaque texels, and transparent texels that must show the background untouched.
func _fidelity(img: Image, origin: Vector2i, cap: Image, bg: Image) -> Dictionary:
	var total := 0
	var exact := 0
	var clear_total := 0
	var clear_changed := 0
	for y in img.get_height():
		for x in img.get_width():
			var t := img.get_pixel(x, y)
			var s := cap.get_pixel(origin.x + x, origin.y + y)
			if t.a8 == 0:
				if bg != null:
					clear_total += 1
					var b := bg.get_pixel(origin.x + x, origin.y + y)
					if s.r8 != b.r8 or s.g8 != b.g8 or s.b8 != b.b8:
						clear_changed += 1
				continue
			total += 1
			if s.r8 == t.r8 and s.g8 == t.g8 and s.b8 == t.b8:
				exact += 1
	return {"opaque_texels": total, "exact_rgb_matches": exact, "transparent_texels": clear_total, "transparent_changed": clear_changed}


func _lum(c: Color) -> float:
	var ch := [c.r, c.g, c.b]
	var lin := []
	for v in ch:
		lin.append(v / 12.92 if v <= 0.04045 else pow((v + 0.055) / 1.055, 2.4))
	return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


func _ratio(a: float, b: float) -> float:
	return (maxf(a, b) + 0.05) / (minf(a, b) + 0.05)


func _quantile(values: Array, q: float) -> float:
	if values.is_empty():
		return 0.0
	var v := values.duplicate()
	v.sort()
	return float(v[clampi(int(floor(q * float(v.size() - 1))), 0, v.size() - 1)])


# Report-only display contrast: every silhouette edge texel (opaque with a transparent or out-of-cell
# 4-neighbour) against the captured background pixel right outside it; plus mean figure vs ring.
func _contrast(img: Image, origin: Vector2i, cap: Image, bg: Image) -> Dictionary:
	var edge := []
	var fig_l := 0.0
	var fig_n := 0
	for y in img.get_height():
		for x in img.get_width():
			if img.get_pixel(x, y).a8 == 0:
				continue
			var l_fig := _lum(cap.get_pixel(origin.x + x, origin.y + y))
			fig_l += l_fig
			fig_n += 1
			var best := 0.0
			var found := false
			for d in [Vector2i(-1, 0), Vector2i(1, 0), Vector2i(0, -1), Vector2i(0, 1)]:
				var nx: int = x + d.x
				var ny: int = y + d.y
				var outside := nx < 0 or ny < 0 or nx >= img.get_width() or ny >= img.get_height()
				if outside or img.get_pixel(nx, ny).a8 == 0:
					found = true
					best = maxf(best, _ratio(l_fig, _lum(bg.get_pixel(origin.x + nx, origin.y + ny))))
			if found:
				edge.append(best)
	var ring_l := 0.0
	var ring_n := 0
	for y in range(-4, img.get_height() + 4):
		for x in range(-4, img.get_width() + 4):
			var inside := x >= 0 and y >= 0 and x < img.get_width() and y < img.get_height()
			if inside and img.get_pixel(x, y).a8 > 0:
				continue
			var px := origin + Vector2i(x, y)
			if px.x < 0 or px.y < 0 or px.x >= bg.get_width() or px.y >= bg.get_height():
				continue
			ring_l += _lum(bg.get_pixel(px.x, px.y))
			ring_n += 1
	var ge15 := 0
	var ge3 := 0
	for v in edge:
		if v >= 1.5:
			ge15 += 1
		if v >= 3.0:
			ge3 += 1
	var mean_fig := fig_l / maxf(1.0, float(fig_n))
	var mean_ring := ring_l / maxf(1.0, float(ring_n))
	return {
		"edge_texels": edge.size(),
		"edge_contrast_ratio_min": _quantile(edge, 0.0), "edge_contrast_ratio_p10": _quantile(edge, 0.1),
		"edge_contrast_ratio_median": _quantile(edge, 0.5),
		"edge_share_ge_1_5": float(ge15) / maxf(1.0, float(edge.size())),
		"edge_share_ge_3_0": float(ge3) / maxf(1.0, float(edge.size())),
		"figure_mean_relative_luminance": mean_fig, "background_ring_mean_relative_luminance": mean_ring,
		"figure_vs_ring_contrast_ratio": _ratio(mean_fig, mean_ring),
	}


# Sprite mask from the capture (differs from the sprite-free background), per-leg lowest window row
# in the foot band, and the head top.  Measured on pixels, independent of the declared table.
func _measure(cap: Image, bg: Image, origin: Vector2i) -> Dictionary:
	var res := {}
	var head := -1
	var low := {"vl": -1, "vr": -1}
	for y in CELL.y:
		for x in CELL.x:
			var px := origin + Vector2i(x, y)
			if px.x < 0 or px.y < 0 or px.x >= cap.get_width() or px.y >= cap.get_height():
				continue
			var a := cap.get_pixel(px.x, px.y)
			var b := bg.get_pixel(px.x, px.y)
			if a.r8 == b.r8 and a.g8 == b.g8 and a.b8 == b.b8:
				continue
			if head < 0 and x >= 10 and x < 70:
				head = origin.y + y
			if y >= LEG_BAND_TOP:
				var leg := "vl" if x < LEG_SPLIT_X else "vr"
				low[leg] = origin.y + y
	res["head_top_window_y"] = head
	res["sole_window_y"] = {"vl": low["vl"], "vr": low["vr"]}
	return res


# Frame table entry for distance s along the loop: [index, distance into the frame].
func _locate(table: Array, s: float) -> Array:
	var cycle: float = table[table.size() - 1]["end"]
	var c := fposmod(s, cycle)
	for i in table.size():
		if c < float(table[i]["end"]) - 1e-9:
			return [i, c - float(table[i]["start"])]
	return [table.size() - 1, c - float(table[table.size() - 1]["start"])]


func _out_name(scene_key: String, what: String, stamp: String, uid: String, ext: String) -> String:
	return "%s_%s_protagonist-female-south-run-v3r2-gameplay-preview-%s-h48_%s_%s-%s.%s" % [SLUG, scene_key, what, VARIANT, stamp, uid, ext]


func _instantiate(spec: Array, app: Node) -> Node2D:
	app.begin_new_run()
	app.hero_appearance = "female"
	if not app.select_destination(String(spec[1])):
		_fail("destination rejected: " + String(spec[1]))
		return null
	if spec[0] == "annex":
		app.current_annex_room = int(spec[2])
		app.resume_annex_pending = false
	var path := AREA_SCENE if spec[0] == "area" else ANNEX_SCENE
	var host: Node2D = (load(path) as PackedScene).instantiate()
	add_child(host)
	await get_tree().process_frame
	await get_tree().process_frame
	host.set_process(false)
	if String(host.get("destination_id")) != String(spec[1]):
		_fail("scene fell back to " + String(host.get("destination_id")))
		return null
	if spec[0] == "annex" and int(host.get("room")) != int(spec[2]):
		_fail("annex opened room %d, expected %d" % [int(host.get("room")), int(spec[2])])
		return null
	return host


func _run() -> void:
	var motion_dir := _user_arg("motion-dir")
	if motion_dir == "" or DirAccess.make_dir_recursive_absolute(motion_dir) != OK:
		_fail("pass -- --motion-dir=<absolute scratch dir>")
		return
	# sha256-text-lf-v1: the manifest is text, so hash it with CRLF normalised to LF (autocrlf-proof)
	var mtext := FileAccess.get_file_as_string(ProjectSettings.globalize_path(RUN_DIR + MANIFEST)).replace("\r\n", "\n")
	var hasher := HashingContext.new()
	hasher.start(HashingContext.HASH_SHA256)
	hasher.update(mtext.to_utf8_buffer())
	var mdigest := hasher.finish().hex_encode()
	if mdigest != MANIFEST_SHA256:
		_fail("manifest sha256-text-lf-v1 %s != %s" % [mdigest, MANIFEST_SHA256])
		return
	var manifest: Dictionary = JSON.parse_string(mtext)
	var m_cell: Array = manifest["cell"]
	var m_pin: Array = manifest["ground_pin_cell"]
	var m_display: Dictionary = manifest["display"]
	if Vector2i(int(m_cell[0]), int(m_cell[1])) != CELL or Vector2i(int(m_pin[0]), int(m_pin[1])) != PIN:
		_fail("manifest cell/pin differ from harness constants")
		return
	if float(m_display["scale"]) != 0.5 or int(m_display["logical_height_px"]) != 48 or bool(m_display["flip_h"]):
		_fail("manifest display block is not 48 px / scale 0.5 / no flip")
		return
	var root_lock_max: float = float(manifest["cycle"]["root_lock_max_abs_px"])
	var cycle_px: float = float(manifest["cycle"]["cycle_logical_px"])
	var frames: Array = manifest["frames"]
	if frames.size() != 16:
		_fail("expected 16 frames, manifest has %d" % frames.size())
		return
	var table := []
	var sources := []
	var acc := 0.0
	for f in frames:
		var path: String = RUN_DIR + String(f["file"])
		var digest := FileAccess.get_sha256(ProjectSettings.globalize_path(path))
		if digest != String(f["sha256"]):
			_fail("%s sha256-bytes %s != manifest" % [f["key"], digest])
			return
		var img := _load_rgba(path)
		if img == null or img.get_size() != CELL:
			_fail("cannot load 80x112 frame " + path)
			return
		if not _binary_alpha(img):
			_fail("%s has non-binary alpha" % f["key"])
			return
		var hold: float = float(f["hold_px"])
		var rows := _opaque_rows(img)
		table.append({"key": String(f["key"]), "image": img, "texture": ImageTexture.create_from_image(img),
			"planted": f["planted"], "sole": f["sole"], "start": acc, "end": acc + hold,
			"r_start": float(f["root_lock"]["r_start_px"]), "slope": float(f["root_lock"]["slope"]),
			"opaque_rows": [rows.x, rows.y]})
		acc += hold
		sources.append({"key": String(f["key"]), "path": path, "sha256_bytes": digest, "opaque_rows": [rows.x, rows.y]})
	if absf(acc - cycle_px) > 1e-6:
		_fail("hold_px sum %f != cycle %f" % [acc, cycle_px])
		return
	if FileAccess.get_sha256(ProjectSettings.globalize_path(V8_PATH)) != V8_SHA256:
		_fail("v8 sha256-bytes mismatch")
		return
	var v8_image := _load_rgba(V8_PATH)
	var v8_rows := _opaque_rows(v8_image)
	var move_speeds := {}
	for script_path in [AREA_SCRIPT, ANNEX_SCRIPT]:
		var ms: float = float((load(script_path) as GDScript).get_script_constant_map().get("MOVE_SPEED", -1.0))
		if ms != 140.0:
			_fail("%s MOVE_SPEED is %s, expected 140" % [script_path, str(ms)])
			return
		move_speeds[script_path] = ms
	var window := get_tree().root
	window.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	window.content_scale_size = Vector2i(640, 360)
	window.size = Vector2i(1280, 720)
	var out_abs := ProjectSettings.globalize_path(OUTPUT_DIR)
	var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var uid := "%08x" % (randi() & 0xffffffff)
	SaveStore.root_path = "user://test-saves/m8-south-run-v3r2-gameplay-preview"
	var app: Node = get_node("/root/AppState")
	var outputs := []
	var pending := []   # outputs/ images, written only after every gate has passed
	var report_scenes := {}
	for scene_key in SCENES.keys():
		var spec: Array = SCENES[scene_key]
		var scene_report := {"kind": spec[0], "destination": spec[1], "annex_room": spec[2], "note": spec[4], "modes": {}}
		for mode in MODES.keys():
			var mspec: Array = MODES[mode]
			var host: Node2D = await _instantiate(spec, app)
			if host == null:
				return
			var hero: Sprite2D = host.get("hero")
			var start: Vector2 = spec[3]
			hero.position = start
			var ph := hero.texture.get_image()
			ph.convert(Image.FORMAT_RGBA8)
			var ph_bottom := 0
			for y in ph.get_height():
				for x in ph.get_width():
					if ph.get_pixel(x, y).a8 >= 128:
						ph_bottom = y + 1
			# ground row of the runtime hero relative to hero.position (same rule as the v2 harness)
			var ground_off := floorf(hero.offset.y - ph.get_height() * 0.5 + ph_bottom)
			hero.visible = false
			var pilot := Sprite2D.new()
			pilot.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
			pilot.centered = false
			pilot.offset = -Vector2(PIN)
			pilot.scale = Vector2(0.5, 0.5)
			pilot.visible = false
			host.add_child(pilot)
			await get_tree().process_frame
			var bg := await _capture()
			if bg.get_size() != Vector2i(1280, 720):
				_fail("capture size " + str(bg.get_size()))
				return
			var mode_report := {"root_lock": mspec[1], "tick_delta_s": mspec[2], "ground_offset_logical": ground_off}
			if mode == "run-140":
				bg.save_png(motion_dir.path_join("%s_background.png" % scene_key))
				# stills: every v3r2 frame + v8 reference at one fixed pin (the hero's start ground point)
				var stills := []
				var still_list: Array = table.duplicate()
				still_list.append({"key": "v8-idle-reference", "image": v8_image, "texture": ImageTexture.create_from_image(v8_image), "opaque_rows": [v8_rows.x, v8_rows.y]})
				var pin_still := Vector2(start.x, start.y + ground_off)
				pilot.visible = true
				for fr in still_list:
					pilot.texture = fr["texture"]
					pilot.position = pin_still
					pilot.z_index = int(pin_still.y)
					await get_tree().process_frame
					var cap := await _capture()
					var origin := Vector2i(int(round(pin_still.x * 2.0)), int(round(pin_still.y * 2.0))) - PIN
					var fid := _fidelity(fr["image"], origin, cap, bg)
					if fid["exact_rgb_matches"] != fid["opaque_texels"] or fid["transparent_changed"] != 0:
						_fail("%s still %s fidelity %d/%d, transparent changed %d" % [scene_key, fr["key"], fid["exact_rgb_matches"], fid["opaque_texels"], fid["transparent_changed"]])
						return
					var meas := _measure(cap, bg, origin)
					var opaque_rows: Array = fr["opaque_rows"]
					var entry := {"frame": fr["key"], "fidelity": fid, "cell_origin_window_px": [origin.x, origin.y],
						"opaque_height_window_px": int(opaque_rows[1]) - int(opaque_rows[0]) + 1,
						"opaque_height_logical_px": (int(opaque_rows[1]) - int(opaque_rows[0]) + 1) * 0.5,
						"lowest_opaque_window_y": origin.y + int(opaque_rows[1]), "ground_line_window_y": int(round(pin_still.y * 2.0)),
						"measured": meas}
					var scratch_name := "%s_still_%s.png" % [scene_key, fr["key"]]
					cap.save_png(motion_dir.path_join(scratch_name))
					entry["scratch_capture"] = scratch_name
					if fr["key"] in CONTRAST_KEYS:
						entry["contrast_report_only"] = _contrast(fr["image"], origin, cap, bg)
					if fr["key"] in OUTPUT_STILL_KEYS:
						var name := _out_name(scene_key, "still-" + String(fr["key"]), stamp, uid, "png")
						pending.append([name, cap])
						entry["capture"] = name
						outputs.append(name)
					stills.append(entry)
				scene_report["stills"] = stills
				scene_report["background_scratch"] = "%s_background.png" % scene_key
				pilot.visible = false
			pilot.visible = true
			var start_y: float = hero.position.y
			var ticks := []
			var saved_keys := {}
			Input.action_press("move_down")
			for tick in int(mspec[0]):
				if tick > 0:
					var before := hero.position
					host.call("_process", float(mspec[2]))   # the scene's real movement code
					if hero.position.x != before.x or hero.position.y <= before.y:
						_fail("%s %s tick %d: hero did not move straight south (%s -> %s)" % [scene_key, mode, tick, str(before), str(hero.position)])
						return
				hero.visible = false   # the runtime walk code swaps textures; keep the runtime hero hidden
				var s := hero.position.y - start_y + PHASE_PX
				var loc := _locate(table, s)
				var fr: Dictionary = table[loc[0]]
				var r := 0.0
				if mspec[1]:
					r = float(fr["r_start"]) + float(fr["slope"]) * float(loc[1])
					if absf(r) > root_lock_max + 1e-6:
						_fail("%s %s tick %d: |root offset| %f > %f" % [scene_key, mode, tick, r, root_lock_max])
						return
				var pin_logical_y := hero.position.y + ground_off + r
				var screen_y := int(round(pin_logical_y * 2.0))
				pilot.texture = fr["texture"]
				pilot.position = Vector2(hero.position.x, screen_y * 0.5)
				pilot.z_index = int(hero.position.y)
				await get_tree().process_frame
				var cap := await _capture()
				var tick_name := "%s_%s_tick-%03d.png" % [scene_key, mode, tick]
				cap.save_png(motion_dir.path_join(tick_name))
				var origin := Vector2i(int(round(hero.position.x * 2.0)), screen_y) - PIN
				var entry := {"tick": tick, "hero_logical": [hero.position.x, hero.position.y], "distance_logical": s,
					"frame": fr["key"], "planted": fr["planted"], "root_offset_logical": r,
					"cell_origin_window_px": [origin.x, origin.y], "measured": _measure(cap, bg, origin)}
				if tick % FIDELITY_EVERY == 0:
					var fid := _fidelity(fr["image"], origin, cap, null)
					entry["fidelity"] = fid
					if fid["exact_rgb_matches"] != fid["opaque_texels"]:
						_fail("%s %s tick %d fidelity %d/%d" % [scene_key, mode, tick, fid["exact_rgb_matches"], fid["opaque_texels"]])
						return
				if mode == "run-140" and fr["key"] in OUTPUT_MOTION_KEYS and not saved_keys.has(fr["key"]):
					saved_keys[fr["key"]] = true
					var name := _out_name(scene_key, "run-140-motion-tick-%03d-%s" % [tick, fr["key"]], stamp, uid, "png")
					pending.append([name, cap])
					entry["capture"] = name
					outputs.append(name)
				ticks.append(entry)
			Input.action_release("move_down")
			mode_report["start_hero_logical"] = [start.x, start_y]
			mode_report["end_hero_logical"] = [hero.position.x, hero.position.y]
			mode_report["logical_px_per_s_measured"] = (hero.position.y - start_y) / (float(int(mspec[0]) - 1) * float(mspec[2]))
			mode_report["frames_shown"] = _frames_shown(ticks)
			mode_report["slip"] = _slip(ticks)
			mode_report["head_step"] = _head_steps(ticks, float(mspec[2]))
			mode_report["ticks"] = ticks
			scene_report["modes"][mode] = mode_report
			print("MOTION %s %s %d ticks %.3f px/s slip_max %s" % [scene_key, mode, ticks.size(), mode_report["logical_px_per_s_measured"], str(mode_report["slip"]["max_window_px"])])
			host.queue_free()
			await get_tree().process_frame
			await get_tree().process_frame
		report_scenes[scene_key] = scene_report
	var output_hashes := {}
	for p in pending:
		var opath := out_abs.path_join(String(p[0]))
		(p[1] as Image).save_png(opath)
		output_hashes[p[0]] = FileAccess.get_sha256(opath)
	var report := {
		"project": "Worlds Between", "milestone": "M8", "variant": VARIANT,
		"purpose": "Test-only in-engine gameplay-scale preview of the unapproved female south run v3r2 candidate at the real 140 logical px/s in bright city, bright outskirts and dark survey annex.",
		"status": "review evidence only; v3r2 is unapproved; not art acceptance; not runtime-integrated",
		"art_approved": false, "human_reviewed": false, "runtime_integrated": false,
		"approved_scope_unchanged": "selout v8 SOUTH IDLE static frame and the 48 logical px display scale only",
		"renderer": "Godot %s windowed, viewport texture capture" % Engine.get_version_info()["string"],
		"canvas": [640, 360], "window": [1280, 720], "scale": 0.5, "filter": "nearest", "shadow": "none",
		"cell": [CELL.x, CELL.y], "cell_pin": [PIN.x, PIN.y], "manifest": MANIFEST, "manifest_sha256_text_lf_v1": mdigest,
		"v8_reference": V8_PATH, "v8_sha256_bytes": V8_SHA256, "v8_opaque_rows": [v8_rows.x, v8_rows.y],
		"runtime_move_speed_logical_px_s": move_speeds, "loop_phase_at_tick0_px": PHASE_PX,
		"root_lock_max_abs_px": root_lock_max, "cycle_logical_px": cycle_px,
		"movement_note": "each tick calls the scene's own _process(delta) with move_down held; the runtime hero is hidden and the v3r2 frame is drawn at its position",
		"modes": MODES, "sources": sources, "outputs": outputs, "outputs_sha256_bytes": output_hashes,
		"gates_passed": ["manifest sha256-text-lf-v1", "16 frame + v8 sha256-bytes", "manifest cell/pin/48 px/scale 0.5/no flip", "binary alpha", "MOVE_SPEED == 140 (area, annex)", "1280x720 captures", "exact-RGB fidelity + untouched transparent texels on every still", "exact-RGB fidelity every 5th motion tick", "|root offset| <= manifest max", "straight-south runtime movement"],
		"report_only": ["slip", "head_step", "contrast_report_only", "frames_shown"],
		"scenes": report_scenes,
	}
	var rpath := out_abs.path_join(_out_name("city-outskirts-annex", "capture-receipt", stamp, uid, "json"))
	var f := FileAccess.open(rpath, FileAccess.WRITE)
	f.store_string(JSON.stringify(report, "\t") + "\n")
	f.close()
	print("REPORT " + rpath)
	get_tree().quit(0)


func _frames_shown(ticks: Array) -> Dictionary:
	var seen := {}
	for t in ticks:
		seen[t["frame"]] = int(seen.get(t["frame"], 0)) + 1
	return seen


# Planted-sole slip on captured pixels: within a run of consecutive ticks planting the same leg,
# max - min of that leg's lowest masked window row.  The camera is static, so window px = world px.
func _slip(ticks: Array) -> Dictionary:
	var stances := []
	var cur := {}
	for t in ticks:
		var planted: Array = t["planted"]
		var leg := String(planted[0]) if planted.size() == 1 else ""
		if leg == "" or not cur.has("leg") or cur["leg"] != leg:
			if cur.has("leg"):
				stances.append(cur)
			cur = {}
			if leg != "":
				cur = {"leg": leg, "ticks": [], "sole_y": []}
		if leg != "":
			var soles: Dictionary = t["measured"]["sole_window_y"]
			cur["ticks"].append(t["tick"])
			cur["sole_y"].append(int(soles[leg]))
	if cur.has("leg"):
		stances.append(cur)
	var worst := 0
	var multi := 0
	for st in stances:
		var ys: Array = st["sole_y"]
		st["slip_window_px"] = int(ys.max()) - int(ys.min())
		worst = maxi(worst, int(st["slip_window_px"]))
		if ys.size() > 1:
			multi += 1
	return {"stances": stances, "stances_with_2plus_ticks": multi, "max_window_px": worst,
		"note": "a stance seen in only one tick cannot show slip; see stances_with_2plus_ticks"}


func _head_steps(ticks: Array, dt: float) -> Dictionary:
	var steps := []
	for i in range(1, ticks.size()):
		var a := int(ticks[i - 1]["measured"]["head_top_window_y"])
		var b := int(ticks[i]["measured"]["head_top_window_y"])
		steps.append(b - a)
	return {"nominal_window_px_per_tick": 140.0 * dt * 2.0, "min": steps.min() if steps.size() else 0,
		"max": steps.max() if steps.size() else 0, "steps": steps}
