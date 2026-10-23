extends SceneTree
# Scene-entry fixture for visual review, not a full-menu journey or human play.
# CLI selects existing optional UI only; no static overrides/default writes.
const SCENES := {
	"menu": "main_menu", "map": "scifi_world_map",
	"exploration": "scifi_exploration_area", "annex": "survey_annex",
	"growth": "growth_screen", "nodes": "growth_screen",
	"save": "save_screen", "battle": "battle_arena"
}
var app: Node
var rows: Array = []
var folder: String
var stamp: String
var mode: String

func _initialize() -> void:
	call_deferred("run")

func detach_audio(node: Node) -> void:
	for child in node.get_children():
		if child is AudioStreamPlayer or child is AudioStreamPlayer2D or child is AudioStreamPlayer3D:
			child.stop()
			child.stream = null
		detach_audio(child)

func visible_controls(node: Node) -> Array:
	var result: Array = []
	for child in node.get_children():
		if child is Control and child.is_visible_in_tree():
			var text := String(child.text) if child is Label or child is Button else ""
			if not text.is_empty():
				result.append({"name": str(child.get_path()), "text": text, "rect": var_to_str(child.get_global_rect()), "fontSize": child.get_theme_font_size("font_size")})
		result.append_array(visible_controls(child))
	return result

func run() -> void:
	var args := OS.get_cmdline_user_args()
	assert(args.size() >= 3)
	folder = args[0]
	stamp = args[1]
	mode = args[2]
	assert(mode in ["ordinary", "ui-pilot"])
	root.size = Vector2i(640, 360)
	root.content_scale_size = Vector2i(640, 360)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	app = root.get_node("AppState")
	assert(app.settings.load_status == "missing")
	SaveStore.root_path = "user://ui-review-isolated-fixture"
	for language in ["en", "zh"]:
		for kind in SCENES:
			app.begin_new_run()
			app.language = language
			app.hero_appearance = "female" if language == "en" else "male"
			app.hero_name = "Heroine" if language == "en" else "主角"
			app.current_destination_id = "scifi.city"
			app.current_annex_room = 1
			app.show_initial_guide = false
			app.save_screen_mode = "save"
			app.recruit_member("liang-xu")
			app.recruit_member("zhao-ling")
			app.ji_records_checked = true
			app.recruit_member("ji-cheng")
			if kind == "battle":
				assert(app.begin_battle("patrol", Vector2(320, 240)))
			var path: String = "res://scenes/" + SCENES[kind] + ".tscn"
			var node: Node = load(path).instantiate()
			root.add_child(node)
			current_scene = node
			for i in 6:
				await process_frame
			if kind == "nodes":
				node._show_nodes(true)
				for i in 3:
					await process_frame
			await RenderingServer.frame_post_draw
			var image := root.get_texture().get_image()
			assert(image.get_size() == Vector2i(640, 360))
			var file := "rpg-2-star-ocean-the-second_ui-%s-%s_actual-640-%s_%s.png" % [kind, language, mode, stamp]
			assert(image.save_png(folder.path_join(file)) == OK)
			rows.append({"kind": kind, "language": language, "mode": mode, "file": file, "sha256": FileAccess.get_sha256(folder.path_join(file)), "scene": path, "sceneScriptSha256": FileAccess.get_sha256(node.get_script().resource_path), "visibleTextControls": visible_controls(node)})
			detach_audio(node)
			current_scene = null
			root.remove_child(node)
			node.free()
			await process_frame
	var report := {"cases": rows, "count": rows.size(), "mode": mode, "args": args, "scriptSha256": FileAccess.get_sha256(get_script().resource_path), "fixture": "direct normal scenes; populated party/new isolated run; battle entry fixture; no flow or manual-play claim", "creatorApproved": false}
	var f := FileAccess.open(folder.path_join("rpg-2-star-ocean-the-second_ui-runtime_capture-report_%s_%s.json" % [mode, stamp]), FileAccess.WRITE)
	f.store_string(JSON.stringify(report, "  ") + "\n")
	f.close()
	call_deferred("finish")

func finish() -> void:
	var previous := AudioServer.get_time_since_last_mix()
	var mixes := 0
	var deadline := Time.get_ticks_usec() + 500000
	while mixes < 2 and Time.get_ticks_usec() < deadline:
		await process_frame
		var age := AudioServer.get_time_since_last_mix()
		if age < previous:
			mixes += 1
		previous = age
	assert(rows.size() == 16 and mixes == 2)
	print("UI52_CAPTURE_OK cases=16 mode=", mode)
	quit(0)
