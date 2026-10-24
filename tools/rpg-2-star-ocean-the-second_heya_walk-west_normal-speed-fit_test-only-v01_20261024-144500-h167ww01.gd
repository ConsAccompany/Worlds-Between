extends SceneTree
# Heya west walk/stop h167ww01: test-only normal-speed source-fit capture. No defaults, runtime adoption or art credit.
# Loads the optional source sprite set + stop supplement, renders a 3x source preview and the 0.5x game-scale
# sprite with pivot (40,104), and captures at exact walk/stop timeline targets under Dummy audio.
const WALK_MS := 40
const RELEASE_MS := 800
const IDLE_HOLD_MS := 900
var started_ms := 0
var walk_tex: Array = []
var idle_tex: Array = []
var s1_tex: Texture2D
var s2_tex: Texture2D
var walk_files: Array = []
var idle_files: Array = []
var s1_file := ""
var s2_file := ""
var preview: Sprite2D
var game: Sprite2D
var state_label: Label
var host_label: Label
var captures: Array = []

func _initialize() -> void:
	call_deferred("run")
	create_timer(75).timeout.connect(func(): push_error("HEYA_HWW167_FIT_TIMEOUT"); quit(2))

func load_tex(path: String, expected_sha: String) -> Texture2D:
	var img := Image.load_from_file(path)
	if img == null or img.get_size() != Vector2i(80, 112):
		push_error("bad frame " + path)
		quit(2)
		return null
	if expected_sha != "" and FileAccess.get_sha256(path) != expected_sha:
		push_error("frame hash mismatch " + path)
		quit(2)
		return null
	return ImageTexture.create_from_image(img)

func state_at(ms: int) -> Dictionary:
	if ms < RELEASE_MS:
		var p := int(ms / WALK_MS) % 12
		return {"kind": "walk", "index": p, "texture": walk_tex[p], "file": walk_files[p]}
	if ms < RELEASE_MS + WALK_MS:
		return {"kind": "s1", "index": 0, "texture": s1_tex, "file": s1_file}
	if ms < RELEASE_MS + 2 * WALK_MS:
		return {"kind": "s2", "index": 0, "texture": s2_tex, "file": s2_file}
	return {"kind": "idle", "index": 0, "texture": idle_tex[0], "file": idle_files[0]}

func apply_state(ms: int) -> Dictionary:
	var st := state_at(ms)
	preview.texture = st["texture"]
	game.texture = st["texture"]
	state_label.text = "state=%s idx=%d  t=%d ms  host=%.1f logical px" % [st["kind"], st["index"], ms, ms * 140.0 / 1000.0]
	return st

func run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 4:
		push_error("expected runtime_json stop_json outdir tag")
		quit(2)
		return
	var runtime = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	var stop = JSON.parse_string(FileAccess.get_file_as_string(args[1]))
	if runtime == null or stop == null:
		push_error("manifest JSON invalid")
		quit(2)
		return
	if runtime.get("actions", {}).get("walk", {}).get("west", null) == null:
		push_error("runtime walk/west missing")
		quit(2)
		return
	var base: String = args[0].get_base_dir()
	for entry in runtime["actions"]["walk"]["west"]:
		if int(entry.get("duration_ms", 0)) != WALK_MS:
			push_error("walk duration is not 40 ms")
			quit(2)
			return
		walk_files.append(String(entry["file"]))
		walk_tex.append(load_tex(base.path_join(String(entry["file"])), String(entry.get("sha256", ""))))
	for entry in runtime["actions"]["idle"]["west"]:
		idle_files.append(String(entry["file"]))
		idle_tex.append(load_tex(base.path_join(String(entry["file"])), String(entry.get("sha256", ""))))
	if walk_tex.size() != 12 or idle_tex.size() != 4:
		push_error("walk/idle frame count")
		quit(2)
		return
	var bridge: Array = stop["phase_bridges"]["west"]["phase7"]
	if bridge.size() != 4 or bridge[0].get("ref", "") != "walk" or int(bridge[0].get("index", -1)) != 7 \
			or bridge[3].get("ref", "") != "idle" or int(bridge[3].get("index", -1)) != 0:
		push_error("stop bridge phase7 shape")
		quit(2)
		return
	s1_file = String(bridge[1]["file"])
	s2_file = String(bridge[2]["file"])
	s1_tex = load_tex(base.path_join(s1_file), String(bridge[1].get("sha256", "")))
	s2_tex = load_tex(base.path_join(s2_file), String(bridge[2].get("sha256", "")))
	root.size = Vector2i(640, 360)
	var bg := ColorRect.new()
	bg.position = Vector2.ZERO
	bg.size = Vector2(640, 360)
	bg.color = Color(0.055, 0.062, 0.075, 1.0)
	root.add_child(bg)
	# ground line and host-distance ticks (140 logical px/s => 5.6 logical px per 40 ms)
	var ground := ColorRect.new()
	ground.position = Vector2(0, 332)
	ground.size = Vector2(640, 2)
	ground.color = Color(0.36, 0.39, 0.44, 1.0)
	root.add_child(ground)
	for i in range(9):
		var tick := ColorRect.new()
		tick.position = Vector2(0, 334 + i * 0)
		tick.size = Vector2(2, 3)
		tick.color = Color(0.22, 0.24, 0.28, 1.0)
		root.add_child(tick)
	var preview_panel := ColorRect.new()
	preview_panel.position = Vector2(8, 8)
	preview_panel.size = Vector2(256, 344)
	preview_panel.color = Color(0.10, 0.11, 0.13, 1.0)
	root.add_child(preview_panel)
	preview = Sprite2D.new()
	preview.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	preview.scale = Vector2(3, 3)
	preview.position = Vector2(136, 186)
	root.add_child(preview)
	game = Sprite2D.new()
	game.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	game.scale = Vector2(0.5, 0.5)
	game.position = Vector2(500, 306)
	root.add_child(game)
	var title := Label.new()
	title.text = "HEYA WEST WALK / NORMAL SPEED / TEST ONLY"
	title.position = Vector2(276, 18)
	title.add_theme_font_size_override("font_size", 12)
	root.add_child(title)
	var sub := Label.new()
	sub.text = "3x source preview (left)   game 0.5x / pivot 40,104 (right)"
	sub.position = Vector2(276, 40)
	sub.add_theme_font_size_override("font_size", 9)
	root.add_child(sub)
	state_label = Label.new()
	state_label.position = Vector2(276, 58)
	state_label.add_theme_font_size_override("font_size", 9)
	root.add_child(state_label)
	host_label = Label.new()
	host_label.text = "walk 40 ms/phase, cycle 480 ms; stop release at phase 7, settle 120 ms inclusive"
	host_label.position = Vector2(276, 78)
	host_label.add_theme_font_size_override("font_size", 8)
	root.add_child(host_label)
	apply_state(0)
	await process_frame
	await RenderingServer.frame_post_draw
	started_ms = Time.get_ticks_msec()
	var targets := [100, 470, 760, 800, 840, 880]
	for target in targets:
		while Time.get_ticks_msec() - started_ms < target:
			apply_state(Time.get_ticks_msec() - started_ms)
			await process_frame
		var elapsed := Time.get_ticks_msec() - started_ms
		var st := apply_state(elapsed)
		await RenderingServer.frame_post_draw
		var png := root.get_texture().get_image()
		if png.get_size() != Vector2i(640, 360):
			push_error("wrong viewport size")
			quit(2)
			return
		var file := "rpg-2-star-ocean-the-second_heya_walk-west_normal-speed-%s-t%d_test-only-640-v01_%s.png" % [st["kind"], target, args[3]]
		var path: String = args[2].path_join(file)
		if png.save_png(path) != OK:
			push_error("capture write failed")
			quit(2)
			return
		captures.append({"file": file, "sha256": FileAccess.get_sha256(path), "target_ms": target,
			"elapsed_ms": elapsed, "kind": st["kind"], "frame_index": st["index"],
			"target_kind": state_at(target)["kind"], "target_frame_index": state_at(target)["index"],
			"frame_file": st["file"], "frame_sha256": FileAccess.get_sha256(base.path_join(String(st["file"]))),
			"walk_ms": WALK_MS, "cycle_ms": 480, "release_ms": RELEASE_MS, "settle_ms_inclusive": 120,
			"pivot": [40, 104], "scale": 0.5, "logical_height_px": 48,
			"texture_size": [80, 112], "sprite_rect": [40.0, 56.0], "host_logical_px": elapsed * 140.0 / 1000.0,
			"normal_speed": true, "testOnly": true})
	var report := FileAccess.open(args[2].path_join("rpg-2-star-ocean-the-second_heya_walk-west_normal-speed-manifest_test-only-v01_%s.json" % args[3]), FileAccess.WRITE)
	report.store_string(JSON.stringify({"captures": captures, "runtimeAdopted": false, "artApproved": false,
		"inputKind": "west walk + phase-7 stop bridge source-fit overlay; normal-speed playback",
		"runtimeManifest": args[0], "runtimeManifestSha256": FileAccess.get_sha256(args[0]),
		"stopManifest": args[1], "stopManifestSha256": FileAccess.get_sha256(args[1])}, "  ") + "\n")
	report.close()
	print("HEYA_HWW167_WEST_WALK_NORMAL_SPEED_PASS captures=", captures.size())
	quit(0)
