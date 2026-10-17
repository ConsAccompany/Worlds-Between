extends SceneTree

# NYC City Hall Park v06 (UNAPPROVED) -- exported-build check.
# 1. Export a pack from an isolated copy of game/ with the unchanged "Windows Desktop" preset:
#      Godot --headless --path <copy of game> --export-pack "Windows Desktop" <abs>/x.pck
# 2. Run this script against the pack only (no --path):
#      Godot --main-pack <abs>/x.pck -s <this file> -- [--out=<abs dir>]
# Proves every file the v06 scene needs is inside the export (scene data ships as a .tres
# resource because the preset's include filter only adds data/*.json for non-resource files).

const RUN_DIR := "res://assets/environments/candidates/nyc-chp-v06_20261017-165253-4519dffe/"
const PARK_V06 := "res://scripts/city_hall_park_v06_scene.gd"
const TAG := "unapproved-v06_20261017-165253-4519dffe"

var failures := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(ok: bool, message: String) -> void:
	print(("CHP6_EXPORT_PASS " if ok else "CHP6_EXPORT_FAIL ") + message)
	if not ok:
		failures += 1


func _run() -> void:
	var out_dir := ""
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--out="):
			out_dir = argument.trim_prefix("--out=")
	var park_script: GDScript = load(PARK_V06)
	_check(park_script != null, "v06 runtime script is in the pack")
	var resource: Resource = load(RUN_DIR + park_script.SCENE_RES)
	_check(resource != null and resource.has_meta("scene_json"), "scene data .tres is in the pack")
	var data = JSON.parse_string(resource.get_meta("scene_json") if resource != null else "")
	_check(typeof(data) == TYPE_DICTIONARY, "scene data parses")
	if typeof(data) != TYPE_DICTIONARY:
		_finish()
		return
	var files: Array = [data["base"], data["walkmask"]]
	for entry in data["ysort"]:
		files.append(entry["png"])
	var loaded := 0
	for file_name in files:
		var texture: Texture2D = load(RUN_DIR + file_name)
		if texture != null and texture.get_image() != null and texture.get_image().get_size() == Vector2i(640, 360):
			loaded += 1
	_check(loaded == files.size(), "all %d scene textures load with readable 640x360 images (%d)" % [files.size(), loaded])
	# Recorded, not gated: Godot 4.7.2 treats .json as a resource type, so all_resources ships it too.
	print("CHP6_EXPORT_INFO v06 scene JSON in pack: %s; v05 scene JSON in pack: %s" % [
		FileAccess.file_exists(RUN_DIR + park_script.SCENE_JSON),
		FileAccess.file_exists("res://assets/environments/candidates/nyc-chp-v05_20261017-015916-23a7984f/rpg-2-star-ocean-the-second_nyc-city-hall-park_scene_unapproved-v05_20261017-015916-23a7984f.json")])
	Engine.max_fps = 60
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(640, 360)
	var app := root.get_node("AppState")
	load("res://scripts/save_store.gd").root_path = "user://test-saves/chp6-export-check"
	app.begin_new_run()
	app.hero_appearance = "female"
	app.language = "en"
	app.select_destination("scifi.city")
	park_script.enabled_override = 1
	var host: Node2D = (load("res://scenes/scifi_exploration_area.tscn") as PackedScene).instantiate()
	root.add_child(host)
	current_scene = host
	await process_frame
	await process_frame
	var park = host.city_hall_park
	_check(park != null and park.get_script() == park_script, "exported city scene runs the v06 layers")
	if park != null:
		_check(park.walkable(Vector2(340, 253)) and host.hero.position == Vector2(340, 253), "spawn walkable in the exported build")
		_check(park.safe_position(Vector2(82, 260)) == Vector2(82, 203.5), "legacy migration data present in the exported build")
		_check(host.get_node("CityHallParkV06_tree_east_elm").material is ShaderMaterial, "crown reveal shader compiles in the exported build")
	await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_viewport().get_texture().get_image()
	_check(image.get_size() == Vector2i(640, 360), "exported build renders at 640x360")
	if not out_dir.is_empty() and DisplayServer.get_name() != "headless":
		DirAccess.make_dir_recursive_absolute(out_dir)
		var path := out_dir.path_join("rpg-2-star-ocean-the-second_nyc-city-hall-park_godot-exported-pack-en-entry-640x360_%s.png" % TAG)
		_check(image.save_png(path) == OK, "saved exported-build capture")
		print("CHP6_EXPORT_CAPTURE " + path)
	_finish()


func _finish() -> void:
	if failures == 0:
		print("CHP6_EXPORT_CHECK_OK")
	quit(0 if failures == 0 else 1)
