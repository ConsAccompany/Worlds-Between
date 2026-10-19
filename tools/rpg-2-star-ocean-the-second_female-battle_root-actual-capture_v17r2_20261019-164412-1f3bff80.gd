extends SceneTree
# TEST-ONLY v17r2 capture. Forked from the v17 density harness
# (tools/rpg-2-star-ocean-the-second_female-battle-static_ci1280-density-capture_test-only-v17_20261018-220631-5a17d0c3.gd,
# sha256 28e5e7d5...). The gameplay captures are unchanged from v17: an in-memory subclass of res://scripts/battle_arena.gd
# replaces ONLY the hero draw call (draw_texture_rect into Rect2(round(x)-32, 204, 68, 72), nearest, no mipmaps).
# Added (diag=occluder, ci1280 only): ONE separately labelled MASK-ONLY DIAGNOSTIC render per language. The same arena
# instance, same frozen state and same root transform redraws ONLY what the canonical _draw() emits AFTER the hero
# (fighters 1..n via _draw_fighter, a front-state enemy via _draw_enemy, battle_vfx.draw) over a solid key colour,
# twice (key A magenta, key B green); the UI CanvasLayer stays drawn on top exactly as in play. Pixels equal in both
# key frames are fully opaque later-draw pixels (difference matte) and carry the occluder colour. These frames are NOT
# gameplay images; after them the normal draw is restored and the injected frame is re-captured and must be identical.
# Args: sprite_png sprite_sha256 out_dir tag revision mode(ci1280|native640) plate(default|outskirts) diag(occluder|none)
const ARENA_SHA := "b1d10da49929de7823d6583efba92d7454ebe3f174064534901ed877192e1842"
const KEY_A := Color(1, 0, 1, 1)
const KEY_B := Color(0, 1, 0, 1)
# The occluder branch repeats canonical battle_arena.gd _draw() lines after the hero loop index 0 (arena sha pinned).
const PROBE_SOURCE := "extends \"res://scripts/battle_arena.gd\"\nvar candidate: Texture2D\nvar inject := false\nvar occluder_only := false\nvar key_color := Color(1, 0, 1, 1)\nfunc _draw() -> void:\n\tif not occluder_only:\n\t\tsuper._draw()\n\t\treturn\n\tdraw_rect(Rect2(0, 0, 640, 360), key_color)\n\tvar enemy_behind := enemy_texture != null and not _enemy_visual_in_front()\n\tvar enemy_shown := enemy_hp > 0 or enemy_animation_texture != null\n\tfor index in range(1, fighters.size()):\n\t\t_draw_fighter(fighters[index], index)\n\tif enemy_shown and not enemy_behind:\n\t\t_draw_enemy()\n\tif battle_vfx != null:\n\t\tbattle_vfx.draw(self)\nfunc _draw_fighter(fighter: Dictionary, index: int) -> void:\n\tif not inject or String(fighter[\"id\"]) != \"hero\":\n\t\tsuper._draw_fighter(fighter,index)\n\t\treturn\n\tvar x: float=fighter[\"x\"]\n\tif _is_alive(index) and index==controlled_index and not auto_mode:\n\t\tdraw_circle(Vector2(x,272),13.0,Color(\"#f5e1a6\"))\n\tdraw_texture_rect(candidate,Rect2(roundf(x)-32.,272.-68.,68.,72.),false)\n"

func _initialize() -> void:
	call_deferred("_run")

func _hash(image: Image) -> String:
	var h := HashingContext.new()
	h.start(HashingContext.HASH_SHA256)
	h.update(image.get_data())
	return h.finish().hex_encode()

func _capture(arena: Node2D, path: String, size: Vector2i) -> Image:
	arena.queue_redraw()
	await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	assert(image.get_size() == size, "Backing image must be the declared size")
	image.convert(Image.FORMAT_RGBA8)
	assert(image.save_png(path) == OK)
	return image

func _controls(arena: Node) -> Array:
	var out := []
	for node in arena.find_children("*", "Control", true, false):
		var c: Control = node
		if not c.is_visible_in_tree():
			continue
		var r := c.get_global_rect()
		out.append([String(arena.get_path_to(c)), snappedf(r.position.x, 0.01), snappedf(r.position.y, 0.01), snappedf(r.size.x, 0.01), snappedf(r.size.y, 0.01)])
	return out

func _run() -> void:
	var args := OS.get_cmdline_user_args()
	assert(args.size() == 8, "sprite sha out tag revision mode plate diag")
	var sprite_path: String = args[0]
	var sprite_sha: String = args[1]
	var out: String = args[2]
	var tag: String = args[3]
	var revision: String = args[4]
	var mode: String = args[5]
	var plate_mode := args[6] == "outskirts"
	var diag := args[7] == "occluder"
	assert(mode == "ci1280" or mode == "native640")
	assert(args[6] == "default" or args[6] == "outskirts")
	assert(args[7] == "occluder" or args[7] == "none")
	assert(not diag or mode == "ci1280", "Occluder diagnostic is a 1280 render only")
	assert(FileAccess.get_sha256("res://scripts/battle_arena.gd") == ARENA_SHA, "Occluder branch mirrors this exact arena source")
	assert(not DirAccess.dir_exists_absolute(out), "Use a fresh unique output folder")
	DirAccess.make_dir_recursive_absolute(out)
	var diag_dir := out.path_join("diag-occl")   # short: Windows MAX_PATH
	if diag:
		DirAccess.make_dir_recursive_absolute(diag_dir)
	var backing := Vector2i(1280, 720) if mode == "ci1280" else Vector2i(640, 360)
	var factor := 2 if mode == "ci1280" else 1
	assert(root.content_scale_mode == Window.CONTENT_SCALE_MODE_CANVAS_ITEMS, "Project stretch mode must stay canvas_items")
	assert(root.content_scale_size == Vector2i(640, 360), "Logical game size must stay 640x360")
	root.size = backing
	await process_frame
	await process_frame
	assert(root.size == backing)
	var visible := root.get_visible_rect().size
	assert(visible == Vector2(640, 360), "Logical visible rect must stay 640x360")
	var final_xf := root.get_final_transform()
	assert(is_equal_approx(final_xf.get_scale().x, float(factor)) and is_equal_approx(final_xf.get_scale().y, float(factor)), "Canvas stretch factor")
	var app: Node = root.get_node("AppState")
	SaveStore.root_path = "user://test-saves/v17r2-occluder-capture"
	assert(FileAccess.get_sha256(sprite_path) == sprite_sha, "Candidate sprite hash")
	var sprite := Image.load_from_file(sprite_path)
	assert(sprite != null and (sprite.get_size() == Vector2i(68, 72) or sprite.get_size() == Vector2i(136, 144)))
	assert(not sprite.has_mipmaps())
	var texture := ImageTexture.create_from_image(sprite)
	var base_script: GDScript = load("res://scripts/battle_arena.gd")
	base_script.sentry_v2_override = 0
	base_script.battle_backdrop_override = 1 if plate_mode else 0
	base_script.combat_sprite_set_override = 0
	var records := []
	for language in ["en", "zh"]:
		app.begin_new_run()
		app.hero_appearance = "female"
		app.recruit_member("liang-xu")
		app.recruit_member("zhao-ling")
		app.ji_records_checked = true
		app.recruit_member("ji-cheng")
		app.select_destination("scifi.outskirts" if plate_mode else "scifi.city")
		if app.language != language:
			app.toggle_language()
		app.begin_battle("patrol" if plate_mode else "sentry", Vector2(330, 215))
		var probe := GDScript.new()
		probe.source_code = PROBE_SOURCE
		assert(probe.reload() == OK)
		var arena: Node2D = probe.new()
		arena.candidate = texture
		root.add_child(arena)
		current_scene = arena
		arena.set_process(false)
		assert(arena.texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST)
		assert(arena.fighters.size() == 4)
		assert(arena.fighters[0]["id"] == "hero")
		var xs := []
		for fighter: Dictionary in arena.fighters:
			xs.append(float(fighter["x"]))
		assert(xs == [135., 171., 207., 243.], "Keep normal current-main party positions")
		if plate_mode:
			assert(arena.battle_backdrop_status == "loaded" and arena.battle_backdrop_arena_id == "outskirts")
		var hero_x := roundf(float(arena.fighters[0]["x"]))
		var prefix: String = out.path_join("rpg-2-star-ocean-the-second_female-battle-v17r2-") + mode + "-" + args[6] + "-" + language
		var baseline_path: String = prefix + "-mainhero_test-only_" + tag + ".png"
		var candidate_path: String = prefix + "-injected_test-only_" + tag + ".png"
		var baseline: Image = await _capture(arena, baseline_path, backing)
		var controls_before := _controls(arena)
		arena.inject = true
		var actual: Image = await _capture(arena, candidate_path, backing)
		var controls_after := _controls(arena)
		assert(controls_before == controls_after, "Injection must not move UI controls")
		var diag_record := {}
		if diag:
			var dprefix: String = diag_dir.path_join("rpg-2-star-ocean-the-second_female-battle-v17r2-diag-occl-") + args[6] + "-" + language
			var key_a_path: String = dprefix + "-keya_test-only_" + tag + ".png"
			var key_b_path: String = dprefix + "-keyb_test-only_" + tag + ".png"
			arena.occluder_only = true
			arena.key_color = KEY_A
			var key_a: Image = await _capture(arena, key_a_path, backing)
			arena.key_color = KEY_B
			var key_b: Image = await _capture(arena, key_b_path, backing)
			arena.occluder_only = false
			var controls_diag := _controls(arena)
			assert(controls_diag == controls_after, "Diagnostic must not move UI controls")
			var restored_path: String = dprefix + "-restored_test-only_" + tag + ".png"
			var restored: Image = await _capture(arena, restored_path, backing)
			assert(restored.get_data() == actual.get_data(), "Normal draw restored: injected frame re-captured identically")
			diag_record = {"label": "MASK-ONLY DIAGNOSTIC (not a gameplay image)", "diagnosticOnly": true, "notGameplayImage": true,
				"drawn": "canonical post-hero _draw() tail: _draw_fighter(1..3), front-state _draw_enemy, battle_vfx.draw; UI CanvasLayer on top as in play",
				"keyA": key_a_path.get_file(), "keyB": key_b_path.get_file(), "restoredRecheck": restored_path.get_file(),
				"keyAFileSha256": FileAccess.get_sha256(key_a_path), "keyBFileSha256": FileAccess.get_sha256(key_b_path),
				"restoredFileSha256": FileAccess.get_sha256(restored_path), "restoredEqualsInjected": true,
				"keyAColor": [1, 0, 1], "keyBColor": [0, 1, 0]}
		var original_texture: Texture2D = arena._female_combat_texture(arena.fighters[0], 0)
		var original_rect := Rect2i(Vector2i(int(hero_x), 272) - Vector2i(arena.HERO_COMBAT_ANCHOR), Vector2i(original_texture.get_size()))
		var candidate_rect := Rect2i(Vector2i(int(hero_x) - 32, 272 - 68), Vector2i(68, 72))
		var bounds := original_rect.merge(candidate_rect)
		var phys := Rect2i(bounds.position * factor, bounds.size * factor)
		var changed := 0
		var outside := 0
		for y in backing.y:
			for x in backing.x:
				if baseline.get_pixel(x, y) != actual.get_pixel(x, y):
					changed += 1
					if not phys.has_point(Vector2i(x, y)):
						outside += 1
		assert(changed > 0 and outside == 0, "Only the hero replacement bounds may change")
		# Controls still follow the current arena: one simulated 0.1 s right step at the normal 168 px/s (logical units).
		var initial_x: float = arena.fighters[0]["x"]
		Input.action_press("move_right")
		arena._process(.1)
		Input.action_release("move_right")
		var moved_x: float = arena.fighters[0]["x"]
		assert(absf(moved_x - initial_x - 16.8) < .01, "Normal 168 px/s battle movement in logical units")
		records.append({"language": language, "partyX": xs, "baseline": baseline_path.get_file(), "injected": candidate_path.get_file(),
			"baselineFileSha256": FileAccess.get_sha256(baseline_path), "injectedFileSha256": FileAccess.get_sha256(candidate_path),
			"baselineRgbaSha256": _hash(baseline), "injectedRgbaSha256": _hash(actual), "changedPixels": changed, "changedOutsideHeroBounds": outside,
			"heroLogicalUnionRect": [bounds.position.x, bounds.position.y, bounds.size.x, bounds.size.y],
			"candidateLogicalRect": [candidate_rect.position.x, candidate_rect.position.y, 68, 72],
			"candidatePhysicalRect": [candidate_rect.position.x * factor, candidate_rect.position.y * factor, 68 * factor, 72 * factor],
			"controlsLogical": controls_after, "moveProbe": {"initialX": initial_x, "afterX": moved_x, "seconds": .1, "humanInput": false},
			"occluderDiagnostic": diag_record})
		current_scene = null
		arena.queue_free()
		await process_frame
	var report := {"testOnly": true, "sourceDefaultChanged": false, "gameCodeEdited": false, "simulationFrozenForCapture": true,
		"mode": mode, "plate": args[6], "backing": [backing.x, backing.y], "logicalVisible": [visible.x, visible.y],
		"contentScaleMode": "canvas_items", "contentScaleSize": [640, 360], "stretchFactor": factor,
		"drawCall": "draw_texture_rect(candidate, Rect2(round(x)-32, 204, 68, 72), tile=false); arena texture_filter NEAREST; ImageTexture without mipmaps",
		"testedRevision": revision, "arenaSha256": FileAccess.get_sha256("res://scripts/battle_arena.gd"),
		"projectSha256": FileAccess.get_sha256("res://project.godot"),
		"captureToolSha256": FileAccess.get_sha256(get_script().resource_path), "spriteSha256": sprite_sha,
		"spriteSize": [sprite.get_width(), sprite.get_height()], "logicalExtent": [68, 72], "logicalPin": [32, 68],
		"bakedReferenceRatio": .65, "backdropPilotEnabled": plate_mode, "occluderDiagnostic": diag, "records": records,
		"artAccepted": false, "motionTested": false, "humanPlaytest": false}
	var file := FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_female-battle-v17r2-" + mode + "-" + args[6] + "_report_test-only_" + tag + ".json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  ") + "\n")
	file.close()
	print("V17R2_CAPTURE_OK mode=", mode, " plate=", args[6], " diag=", args[7], " records=", records.size())
	quit(0)
