extends SceneTree
const Policy := preload("res://scripts/sdef35/rpg-2-star-ocean-the-second_mvp-scene-defaults_policy_prepared-v01_20261021-231349-a83c4bae.gd")
var output := ""
var tag := ""
var checks := []
var app: Node

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var args := OS.get_cmdline_user_args()
	output = args[0]
	tag = args[1]
	DirAccess.make_dir_recursive_absolute(output)
	root.size = Vector2i(640,360)
	root.content_scale_size = Vector2i(640,360)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	app = root.get_node("AppState")
	SaveStore.root_path = "user://test-saves/records-default-precedence"
	var flag_new: bool = args.has("--wdc-records-style48")
	var flag_old: bool = args.has("--wdc-records-chamber-v01")
	for enabled in [true,false]:
		Policy.clear_preview()
		if not enabled: Policy.preview_override[Policy.RECORDS] = false
		app.begin_new_run()
		app.hero_appearance = "female"
		app.select_destination("scifi.ruins")
		app.current_annex_room = 2
		var host: Node2D = load("res://scenes/survey_annex.tscn").instantiate()
		root.add_child(host)
		current_scene = host
		host.set_process(false)
		await process_frame
		var common_expected: bool = flag_new or (not flag_old and enabled)
		var fixtures_expected: bool = flag_new or flag_old or enabled
		var actual: String = host._room_two_background().resource_path
		var okay: bool = actual.contains("/style48/") == common_expected and host.wdc_room_two == fixtures_expected
		var row := {"defaultEnabled":enabled,"newFlag":flag_new,"legacyFlag":flag_old,
			"texture":actual,"commonExpected":common_expected,"fixturesExpected":fixtures_expected,"passed":okay}
		checks.append(row)
		if not okay:
			push_error("records default precedence "+JSON.stringify(row))
			quit(1)
			return
		await process_frame
		await RenderingServer.frame_post_draw
		var image := root.get_texture().get_image()
		var suffix := "common" if common_expected else "legacy"
		var file := output.path_join("rpg-2-star-ocean-the-second_wdc-records-room2_precedence-%s-default-%s_style50_%s.png" % [suffix,str(enabled).to_lower(),tag])
		if image.get_size() != Vector2i(640,360) or image.save_png(file) != OK:
			push_error("precedence capture failed")
			quit(1)
			return
		host.queue_free()
		current_scene = null
		await process_frame
	Policy.clear_preview()
	var report := FileAccess.open(output.path_join("rpg-2-star-ocean-the-second_wdc-records-room2_default-precedence_style50_%s.json" % tag),FileAccess.WRITE)
	report.store_string(JSON.stringify({"passed":true,"checks":checks,"fixture":"process frozen only for deterministic precedence captures; no gameplay claim"},"  "))
	print("STYLE50_PRECEDENCE_ALL_OK")
	quit()
