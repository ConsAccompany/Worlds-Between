extends SceneTree
# Heya i159 four-direction idle: test-only normal-speed source-fit capture. No defaults, interaction or art credit.
var started_ms := 0

func _initialize() -> void:
	call_deferred("run")
	create_timer(75).timeout.connect(func(): push_error("HEYA_I159_IDLE_FIT_TIMEOUT"); quit(2))

func quiet(node: Node) -> void:
	node.process_mode = Node.PROCESS_MODE_DISABLED
	if node is AudioStreamPlayer or node is AudioStreamPlayer2D or node is AudioStreamPlayer3D:
		node.stop()
		node.stream = null
	for child in node.get_children():
		quiet(child)

func textures_for(base: String, entries: Array) -> Array:
	var texs: Array = []
	for i in range(entries.size()):
		var path: String = base.path_join(String(entries[i]["file"]))
		var img := Image.load_from_file(path)
		if img == null or img.get_size() != Vector2i(80, 112):
			push_error("bad idle frame " + path)
			quit(2)
			return texs
		texs.append(ImageTexture.create_from_image(img))
	return texs

func frame_at(elapsed_ms: int) -> int:
	var acc := 0
	for i in range(4):
		acc += [700, 200, 400, 200][i]
		if elapsed_ms < acc:
			return i
	return 3

func run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 3:
		push_error("expected runtime_json outdir tag")
		quit(2)
		return
	var runtime = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if runtime == null or runtime.get("actions", {}).get("idle", null) == null:
		push_error("runtime idle manifest invalid")
		quit(2)
		return
	var base := args[0].get_base_dir()
	var dirs := ["south", "west", "north", "east"]
	var all_tex := {}
	for d in dirs:
		all_tex[d] = textures_for(base, runtime["actions"]["idle"][d])
	var app = root.get_node("AppState")
	app.set_process(false)
	SaveStore.root_path = "user://test-saves/heya-idle-i159-normal-speed"
	root.size = Vector2i(640, 360)
	var files: Array = []
	for destination in ["scifi.city", "scifi.ruins"]:
		for language in ["en", "zh"]:
			app.begin_new_run()
			app.hero_appearance = "female"
			app.current_destination_id = destination
			app.language = language
			app.show_initial_guide = false
			app.run_active = false
			var host = load("res://scenes/scifi_exploration_area.tscn").instantiate()
			root.add_child(host)
			quiet(host)
			for tween in get_processed_tweens():
				tween.kill()
			var layer := CanvasLayer.new()
			layer.layer = 12
			layer.process_mode = Node.PROCESS_MODE_ALWAYS
			root.add_child(layer)
			var panel := ColorRect.new()
			panel.position = Vector2(292, 198)
			panel.size = Vector2(206, 102)
			panel.color = Color(0.04, 0.05, 0.07, 0.72)
			layer.add_child(panel)
			var sprites := {}
			for idx in range(4):
				var d: String = dirs[idx]
				var s := Sprite2D.new()
				s.texture = all_tex[d][0]
				s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
				s.scale = Vector2(0.5, 0.5)
				s.position = Vector2(318 + idx * 44, 256)
				layer.add_child(s)
				sprites[d] = s
				var lab := Label.new()
				lab.text = d.to_upper()
				lab.position = Vector2(306 + idx * 44, 280)
				lab.add_theme_font_size_override("font_size", 9)
				layer.add_child(lab)
			var title := Label.new()
			title.text = "HEYA IDLE 4-DIR / NORMAL SPEED / TEST ONLY" if language == "en" else "赫娅 四向待机 / 正常速度 / 仅测试"
			title.position = Vector2(296, 202)
			title.add_theme_font_size_override("font_size", 9)
			layer.add_child(title)
			for d in dirs:
				sprites[d].texture = all_tex[d][0]
			await process_frame
			await RenderingServer.frame_post_draw
			started_ms = Time.get_ticks_msec()
			for target in [100, 1000, 1350]:
				while Time.get_ticks_msec() - started_ms < target:
					var e0 := Time.get_ticks_msec() - started_ms
					for d in dirs:
						sprites[d].texture = all_tex[d][frame_at(e0)]
					await process_frame
				var elapsed := Time.get_ticks_msec() - started_ms
				for d in dirs:
					sprites[d].texture = all_tex[d][frame_at(elapsed)]
				await RenderingServer.frame_post_draw
				var png := root.get_texture().get_image()
				if png.get_size() != Vector2i(640, 360):
					push_error("wrong viewport size")
					quit(2)
					return
				var indices := {}
				for d in dirs:
					indices[d] = frame_at(elapsed)
				var file := "rpg-2-star-ocean-the-second_heya_idle-four-direction_normal-speed-%s-%s-t%d_test-only-640-v01_%s.png" % [destination.replace("scifi.", ""), language, target, args[2]]
				var path: String = args[1].path_join(file)
				if png.save_png(path) != OK:
					push_error("capture write failed")
					quit(2)
					return
				files.append({"file": file, "sha256": FileAccess.get_sha256(path), "destination": destination,
					"language": language, "target_ms": target, "elapsed_ms": elapsed,
					"frame_indices": indices, "cycle_ms": 1500, "durations_ms": [700, 200, 400, 200],
					"normal_speed": true, "testOnly": true})
			layer.queue_free()
			host.free()
			await process_frame
	var report := FileAccess.open(args[1].path_join("rpg-2-star-ocean-the-second_heya_idle-four-direction_normal-speed-manifest_test-only-v01_%s.json" % args[2]), FileAccess.WRITE)
	report.store_string(JSON.stringify({"captures": files, "runtimeAdopted": false, "artApproved": false,
		"inputKind": "four-direction animated idle source-fit overlay; normal-speed playback",
		"runtimeManifest": args[0], "runtimeManifestSha256": FileAccess.get_sha256(args[0])}, "  ") + "\n")
	report.close()
	print("HEYA_I159_IDLE_NORMAL_SPEED_PASS captures=", files.size())
	quit(0)
