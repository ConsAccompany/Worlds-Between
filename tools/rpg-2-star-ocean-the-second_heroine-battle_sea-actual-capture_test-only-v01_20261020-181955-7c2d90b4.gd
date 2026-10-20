extends SceneTree
# TEST-ONLY Sea-of-Stars heroine battle static v01 capture. Modernized COPY of
# tools/rpg-2-star-ocean-the-second_female-battle_root-actual-capture_v17r2_20261019-164412-1f3bff80.gd (its arena SHA b1d10da4...
# is historical). Binds the raw CURRENT res://scripts/battle_arena.gd SHA. The occluder mask diagnostic is omitted (not needed:
# no occlusion claim is made). FROZEN STATIC CAPTURE of a normal battle start, NOT a playthrough: an in-memory subclass of the
# arena replaces ONLY the hero draw call (draw_texture_rect into Rect2(round(x)-32, 204, 68, 72), nearest, no mipmaps).
# Baseline (canonical super._draw) and candidate are rendered by the SAME arena instance in the same frozen state; no compositing.
# After the candidate the injection is switched off and the canonical frame is re-rendered and must equal the baseline.
# Args: sprite_png sprite_sha256 out_dir tag revision mode(ci1280|native640) plate(default|outskirts)
const ARENA_SHA := "d7c4fb46bbdff55596aac443d7eafc470be51728f00a78f2cc45b1a2301dec95"
const PROBE_SOURCE := "extends \"res://scripts/battle_arena.gd\"
var candidate: Texture2D
var inject := false
func _draw_fighter(fighter: Dictionary, index: int) -> void:
	if not inject or String(fighter[\"id\"]) != \"hero\":
		super._draw_fighter(fighter,index)
		return
	var x: float=fighter[\"x\"]
	if _is_alive(index) and index==controlled_index and not auto_mode:
		draw_circle(Vector2(x,272),13.0,Color(\"#f5e1a6\"))
	draw_texture_rect(candidate,Rect2(roundf(x)-32.,272.-68.,68.,72.),false)
"
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
	if path != "":
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
	assert(args.size() == 7, "sprite sha out tag revision mode plate")
	var sprite_path: String = args[0]
	var sprite_sha: String = args[1]
	var out: String = args[2]
	var tag: String = args[3]
	var revision: String = args[4]
	var mode: String = args[5]
	var plate_mode := args[6] == "outskirts"
	assert(mode == "ci1280" or mode == "native640")
	assert(args[6] == "default" or args[6] == "outskirts")
	assert(FileAccess.get_sha256("res://scripts/battle_arena.gd") == ARENA_SHA, "Bind the raw current arena source")
	assert(not DirAccess.dir_exists_absolute(out), "Use a fresh unique output folder")
	DirAccess.make_dir_recursive_absolute(out)
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
	SaveStore.root_path = "user://test-saves/hsea01-capture"
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
		var prefix: String = out.path_join("rpg-2-star-ocean-the-second_heroine-battle-sea-v01-") + mode + "-" + args[6] + "-" + language
		var baseline_path: String = prefix + "-mainhero_test-only_" + tag + ".png"
		var candidate_path: String = prefix + "-injected_test-only_" + tag + ".png"
		var baseline: Image = await _capture(arena, baseline_path, backing)
		var controls_before := _controls(arena)
		arena.inject = true
		var actual: Image = await _capture(arena, candidate_path, backing)
		var controls_after := _controls(arena)
		assert(controls_before == controls_after, "Injection must not move UI controls")
		arena.inject = false
		var restored: Image = await _capture(arena, "", backing)
		assert(restored.get_data() == baseline.get_data(), "Injection off: canonical default draw re-renders identically")
		assert(_controls(arena) == controls_before, "Restore must not move UI controls")
		arena.inject = true
		var again: Image = await _capture(arena, "", backing)
		assert(again.get_data() == actual.get_data(), "Candidate render is repeatable in the same instance")
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
			"baselineRgbaSha256": _hash(baseline), "injectedRgbaSha256": _hash(actual), "restoredEqualsBaseline": true, "changedPixels": changed, "changedOutsideHeroBounds": outside,
			"heroLogicalUnionRect": [bounds.position.x, bounds.position.y, bounds.size.x, bounds.size.y],
			"candidateLogicalRect": [candidate_rect.position.x, candidate_rect.position.y, 68, 72],
			"candidatePhysicalRect": [candidate_rect.position.x * factor, candidate_rect.position.y * factor, 68 * factor, 72 * factor],
			"controlsLogical": controls_after, "moveProbe": {"initialX": initial_x, "afterX": moved_x, "seconds": .1, "humanInput": false},
			"heroX": hero_x})
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
		"bakedReferenceRatio": .65, "backdropPilotEnabled": plate_mode, "occluderDiagnostic": false, "records": records,
		"frozenStaticCapture": true, "playthrough": false, "screenshotCompositing": false, "sameArenaInstance": true,
		"artAccepted": false, "motionTested": false, "humanPlaytest": false}
	var file := FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_heroine-battle-sea-v01-" + mode + "-" + args[6] + "_report_test-only_" + tag + ".json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  ") + "\n")
	file.close()
	print("HSEA01_CAPTURE_OK mode=", mode, " plate=", args[6], " records=", records.size())
	quit(0)
