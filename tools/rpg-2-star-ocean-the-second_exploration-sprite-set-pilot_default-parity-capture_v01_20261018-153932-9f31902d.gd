extends SceneTree

# Exploration sprite set pilot: default-render parity captures. Knows nothing about the pilot, so the same file
# runs on the base tree (origin/main before the pilot) and on the pilot branch; the Python check compares the
# PNGs pixel by pixel. Run windowed at a fixed frame rate so walking lands on identical positions:
#   Godot --path <game dir> --fixed-fps 60 -s <this file> -- <out dir> [extra user args, e.g. the pilot flag]
# For every normal exploration scene type (area city/outskirts/ruins, survey annex room 1 x3 and room 2 x2,
# Chicago Loop) it enters the scene like the game does and captures 640x360 frames: standing at entry (zh, en),
# after 0.4 s walking east, after 0.3 s walking north, and 0.2 s after stopping. Nothing in the project is written.
const ANNEX_SCENE := "res://scenes/survey_annex.tscn"
const SCENES := [["area-city", "scifi.city", 0], ["area-outskirts", "scifi.outskirts", 0], ["area-ruins", "scifi.ruins", 0],
	["annex-city-room1", "scifi.city", 1], ["annex-outskirts-room1", "scifi.outskirts", 1], ["annex-ruins-room1", "scifi.ruins", 1],
	["annex-city-room2", "scifi.city", 2], ["annex-ruins-room2", "scifi.ruins", 2], ["chicago-loop", "scifi.loop", 0]]
const STEPS := [["entry", "", 0.0], ["walk-east", "move_right", 0.4], ["walk-north", "move_up", 0.3], ["stopped", "", 0.2]]

var app: Node
var out_dir := ""
var written := 0


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	out_dir = OS.get_cmdline_user_args()[0]
	DirAccess.make_dir_recursive_absolute(out_dir)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(640, 360)
	SaveStore.root_path = "user://test-saves/ssp-parity"
	app = root.get_node("AppState")
	for scene in SCENES:
		app.begin_new_run()
		app.hero_appearance = "female" if scene[0].contains("city") or scene[0].contains("loop") else "male"
		if app.language != "zh":
			app.toggle_language()
		app.select_destination(scene[1])
		var path: String = app.area_scene_path(scene[1])
		if scene[2] > 0:
			app.current_annex_room = scene[2]
			path = ANNEX_SCENE
		change_scene_to_file(path)
		for i in 3:
			await process_frame
		for step in STEPS:
			if step[1] != "":
				Input.action_press(step[1])
			for n in int(round(float(step[2]) * 60.0)):
				await RenderingServer.frame_post_draw
			if step[1] != "":
				Input.action_release(step[1])
			await RenderingServer.frame_post_draw
			_save("%s_%s-zh" % [scene[0], step[0]])
			if step[0] == "entry":
				app.toggle_language()
				await RenderingServer.frame_post_draw
				_save("%s_%s-en" % [scene[0], step[0]])
				app.toggle_language()
				await RenderingServer.frame_post_draw
	print("SSP_PARITY_DONE %d" % written)
	quit()


func _save(label: String) -> void:
	var image := root.get_viewport().get_texture().get_image()
	var path := out_dir.path_join("rpg-2-star-ocean-the-second_exploration-sprite-set-pilot_parity_%s_20261018-153932-9f31902d.png" % label)
	if image.get_size() == Vector2i(640, 360) and image.save_png(path) == OK:
		written += 1
	else:
		push_error("capture failed " + path)
