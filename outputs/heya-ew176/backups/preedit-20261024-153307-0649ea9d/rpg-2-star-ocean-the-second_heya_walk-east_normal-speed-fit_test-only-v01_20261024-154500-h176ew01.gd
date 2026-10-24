extends SceneTree
# Heya east walk/stop h176ew01: test-only normal-speed source-fit capture. No defaults, runtime adoption or art credit.
# Timeline: start -> walk -> phase-derived stop(s1,s2,idle f00) -> repress -> reverse supplemental stop bridge
# (s2,s1,restored walk entry,idle f00); bright/dark + EN/ZH. "Reverse" means replaying the supplemental stop
# bridge in reverse order, NOT an actual direction/host reversal.
# Loads the optional source sprite set + stop supplement, renders a 3x source preview and the 0.5x game-scale
# sprite with pivot (40,104), and captures at exact walk/stop timeline targets under Dummy audio.
const WALK_MS := 40
const START_MS := 320
const STOP_MS := 800
const IDLE_MS := 940
const REPRESS_MS := 940
const REV_MS := 1420
const END_MS := 1560
var started_ms := 0
var walk_tex: Array = []
var idle_tex: Array = []
var s1_tex: Texture2D
var s2_tex: Texture2D
var walk_files: Array = []
var idle_files: Array = []
var s1_file := ""
var s2_file := ""
var stop_phase := 0
var rev_phase := 0
var preview: Sprite2D
var game: Sprite2D
var state_label: Label
var host_label: Label
var captures: Array = []

func _initialize() -> void:
	call_deferred("run")
	create_timer(75).timeout.connect(func(): push_error("HEYA_HEW176_EAST_FIT_TIMEOUT"); quit(2))

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
	if ms < START_MS:
		return {"kind": "start", "index": 0, "texture": idle_tex[0], "file": idle_files[0]}
	if ms < STOP_MS:
		var p := int((ms - START_MS) / WALK_MS) % 12
		return {"kind": "walk", "index": p, "texture": walk_tex[p], "file": walk_files[p]}
	if ms < STOP_MS + WALK_MS:
		return {"kind": "s1", "index": 0, "texture": s1_tex, "file": s1_file}
	if ms < STOP_MS + 2 * WALK_MS:
		return {"kind": "s2", "index": 0, "texture": s2_tex, "file": s2_file}
	if ms < REPRESS_MS:
		return {"kind": "idle", "index": 0, "texture": idle_tex[0], "file": idle_files[0]}
	if ms < REV_MS:
		var q := int((ms - REPRESS_MS) / WALK_MS) % 12
		return {"kind": "walk", "index": q, "texture": walk_tex[q], "file": walk_files[q]}
	if ms < REV_MS + WALK_MS:
		return {"kind": "s2", "index": 0, "texture": s2_tex, "file": s2_file}
	if ms < REV_MS + 2 * WALK_MS:
		return {"kind": "s1", "index": 0, "texture": s1_tex, "file": s1_file}
	if ms < END_MS:
		return {"kind": "walk", "index": rev_phase, "texture": walk_tex[rev_phase], "file": walk_files[rev_phase]}
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
	if runtime.get("actions", {}).get("walk", {}).get("east", null) == null:
		push_error("runtime walk/east missing")
		quit(2)
		return
	var base: String = args[0].get_base_dir()
	for entry in runtime["actions"]["walk"]["east"]:
		if int(entry.get("duration_ms", 0)) != WALK_MS:
			push_error("walk duration is not 40 ms")
			quit(2)
			return
		walk_files.append(String(entry["file"]))
		walk_tex.append(load_tex(base.path_join(String(entry["file"])), String(entry.get("sha256", ""))))
	for entry in runtime["actions"]["idle"]["east"]:
		idle_files.append(String(entry["file"]))
		idle_tex.append(load_tex(base.path_join(String(entry["file"])), String(entry.get("sha256", ""))))
	if walk_tex.size() != 12 or idle_tex.size() != 4:
		push_error("walk/idle frame count")
		quit(2)
		return
	# Derive the stop entry from the frozen timing (the last walk frame before STOP_MS) instead of a
	# literal bridge name. The reverse stop test starts from the final reverse-walk frame, also derived.
	stop_phase = int((STOP_MS - 1 - START_MS) / WALK_MS) % 12
	rev_phase = int((REV_MS - 1 - REPRESS_MS) / WALK_MS) % 12
	if stop_phase != rev_phase:
		push_error("forward/reverse pre-stop phase mismatch")
		quit(2)
		return
	var bridge_key := "phase%d" % stop_phase
	var east_bridges: Dictionary = stop["phase_bridges"]["east"]
	if not east_bridges.has(bridge_key):
		push_error("derived stop bridge missing " + bridge_key)
		quit(2)
		return
	var bridge: Array = east_bridges[bridge_key]
	if bridge.size() != 4 or bridge[0].get("ref", "") != "walk" or int(bridge[0].get("index", -1)) != stop_phase \
			or bridge[3].get("ref", "") != "idle" or int(bridge[3].get("index", -1)) != 0:
		push_error("stop bridge shape for " + bridge_key)
		quit(2)
		return
	# Explicit pre-stop == selected-entry predicate and stop/reverse endpoint continuity.
	var fwd_pre := state_at(STOP_MS - 1)
	var rev_pre := state_at(REV_MS - 1)
	if fwd_pre["kind"] != "walk" or int(fwd_pre["index"]) != stop_phase:
		push_error("forward pre-stop walk phase != selected stop entry")
		quit(2)
		return
	if rev_pre["kind"] != "walk" or int(rev_pre["index"]) != rev_phase or int(rev_pre["index"]) != int(bridge[0].get("index", -1)):
		push_error("reverse pre-stop walk phase != selected stop entry")
		quit(2)
		return
	if state_at(STOP_MS)["kind"] != "s1" or state_at(STOP_MS + WALK_MS)["kind"] != "s2" \
			or state_at(STOP_MS + 2 * WALK_MS)["kind"] != "idle" or state_at(REPRESS_MS - 1)["kind"] != "idle":
		push_error("forward stop endpoints not continuous")
		quit(2)
		return
	if state_at(REV_MS)["kind"] != "s2" or state_at(REV_MS + WALK_MS)["kind"] != "s1" \
			or state_at(REV_MS + 2 * WALK_MS)["kind"] != "walk" or int(state_at(REV_MS + 2 * WALK_MS)["index"]) != rev_phase \
			or state_at(END_MS)["kind"] != "idle":
		push_error("reverse stop endpoints not continuous")
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
	title.text = "HEYA EAST WALK / NORMAL SPEED / TEST ONLY"
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
	host_label.text = "start->walk 40ms/phase->stop p%d(120ms)->repress->reverse stop bridge p%d; EN/ZH bright/dark" % [stop_phase, stop_phase]
	host_label.position = Vector2(276, 78)
	host_label.add_theme_font_size_override("font_size", 8)
	root.add_child(host_label)
	apply_state(0)
	await process_frame
	await RenderingServer.frame_post_draw
	started_ms = Time.get_ticks_msec()
	var targets := [160, 560, 780, 820, 860, 900, 960, 1200, 1440, 1480, 1520, 1560]
	for target in targets:
		while Time.get_ticks_msec() - started_ms < target:
			apply_state(Time.get_ticks_msec() - started_ms)
			await process_frame
		var elapsed := Time.get_ticks_msec() - started_ms
		var st := apply_state(elapsed)
		var theme := "bright" if target < 960 else "dark"
		if theme == "bright":
			bg.color = Color(0.86, 0.87, 0.82, 1.0)
			ground.color = Color(0.35, 0.38, 0.42, 1.0)
		else:
			bg.color = Color(0.055, 0.062, 0.075, 1.0)
			ground.color = Color(0.36, 0.39, 0.44, 1.0)
		var label := "%s / %s  %s / %s" % [st["kind"], {"start":"起步", "walk":"行走", "s1":"停1", "s2":"停2", "idle":"静止"}[st["kind"]], theme, ("明亮" if theme == "bright" else "暗色")]
		state_label.text = label
		var ink := Color(0.08, 0.09, 0.10) if theme == "bright" else Color(0.90, 0.92, 0.95)
		title.add_theme_color_override("font_color", ink)
		sub.add_theme_color_override("font_color", ink)
		host_label.add_theme_color_override("font_color", ink)
		await RenderingServer.frame_post_draw
		var png := root.get_texture().get_image()
		if png.get_size() != Vector2i(640, 360):
			push_error("wrong viewport size")
			quit(2)
			return
		var file := "rpg-2-star-ocean-the-second_heya_walk-east_normal-speed-%s-%s-t%d_test-only-640-v01_%s.png" % [st["kind"], theme, target, args[3]]
		var path: String = args[2].path_join(file)
		if png.save_png(path) != OK:
			push_error("capture write failed")
			quit(2)
			return
		captures.append({"file": file, "sha256": FileAccess.get_sha256(path), "target_ms": target,
			"elapsed_ms": elapsed, "kind": st["kind"], "frame_index": st["index"], "theme": theme, "label_bilingual": label,
			"target_kind": state_at(target)["kind"], "target_frame_index": state_at(target)["index"],
			"frame_file": st["file"], "frame_sha256": FileAccess.get_sha256(base.path_join(String(st["file"]))),
			"walk_ms": WALK_MS, "cycle_ms": 480, "start_ms": START_MS, "stop_ms": STOP_MS, "repress_ms": REPRESS_MS, "reversal_ms": REV_MS, "settle_ms_inclusive": 120,
			"stop_phase": stop_phase, "reverse_phase": rev_phase,
			"pivot": [40, 104], "scale": 0.5, "logical_height_px": 48,
			"texture_size": [80, 112], "sprite_rect": [40.0, 56.0], "host_logical_px": elapsed * 140.0 / 1000.0,
			"normal_speed": true, "testOnly": true})
	var report := FileAccess.open(args[2].path_join("rpg-2-star-ocean-the-second_heya_walk-east_normal-speed-manifest_test-only-v01_%s.json" % args[3]), FileAccess.WRITE)
	report.store_string(JSON.stringify({"captures": captures, "runtimeAdopted": false, "artApproved": false,
		"inputKind": "east walk + phase-%d supplemental stop bridge forward/reverse source-fit overlay (not host direction reversal); bright/dark EN/ZH; normal-speed playback" % stop_phase,
		"stopPhase": stop_phase, "reversePhase": rev_phase,
		"runtimeManifest": args[0], "runtimeManifestSha256": FileAccess.get_sha256(args[0]),
		"stopManifest": args[1], "stopManifestSha256": FileAccess.get_sha256(args[1])}, "  ") + "\n")
	report.close()
	print("HEYA_HEW176_EAST_WALK_NORMAL_SPEED_PASS captures=", captures.size())
	quit(0)
