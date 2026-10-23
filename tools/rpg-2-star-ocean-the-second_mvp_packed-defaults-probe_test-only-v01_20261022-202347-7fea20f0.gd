extends SceneTree
# Independent current packed-game fixture; external tool is not shipped in the game PCK.
# Direct scene/party setup is declared, not a human campaign or story-recruitment test.
var app: Node
var output: String
var stamp: String
var checks: Array = []
var captures: Array = []

func _initialize() -> void:
	call_deferred("run")

func check(label: String, okay: bool) -> void:
	checks.append({"label": label, "pass": okay})
	assert(okay, label)

func detach_audio(node: Node) -> void:
	for child in node.get_children():
		if child is AudioStreamPlayer or child is AudioStreamPlayer2D or child is AudioStreamPlayer3D:
			child.stop()
			child.stream = null
		detach_audio(child)

func open_scene(path: String) -> Node:
	var scene: Node = load(path).instantiate()
	root.add_child(scene)
	current_scene = scene
	for i in 8:
		await process_frame
	# Chicago's ordinary selector deliberately changes the tree's current scene.
	return current_scene

func capture(node: Node, key: String) -> void:
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	check(key + "-native-image", image.get_size() == Vector2i(640, 360))
	var file := "rpg-2-star-ocean-the-second_mvp_" + key + "_actual-packed-v01_" + stamp + ".png"
	check(key + "-saved", image.save_png(output.path_join(file)) == OK)
	captures.append({"key": key, "file": file, "sha256": FileAccess.get_sha256(output.path_join(file)), "scene": node.scene_file_path})

func close_scene(node: Node) -> void:
	detach_audio(node)
	current_scene = null
	root.remove_child(node)
	node.free()
	await process_frame

func run() -> void:
	var args := OS.get_cmdline_user_args()
	output = args[0]
	stamp = args[1]
	# Godot consumes --main-pack before exposing OS.get_cmdline_args().
	# The independent runner binds the actual flag/PCK hash; require packed metadata here.
	check("packed-project-metadata-present", FileAccess.file_exists("res://project.binary"))
	check("not-editor-hint", not Engine.is_editor_hint())
	check("working-directory-has-no-source-project", not FileAccess.file_exists(OS.get_environment("WB_PLAY54_EMPTY").path_join("project.godot")))
	root.size = Vector2i(640, 360)
	root.content_scale_size = Vector2i(640, 360)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	app = root.get_node("AppState")
	check("fresh-test-profile", app.settings.load_status == "missing")
	SaveStore.root_path = "user://play54-isolated-smoke"
	var policy: Script = load("res://scripts/sdef35/rpg-2-star-ocean-the-second_mvp-scene-defaults_policy_prepared-v01_20261021-231349-a83c4bae.gd")
	check("all-four-scene-defaults-authorized", policy.CITY_V06_DEFAULT and policy.RUINS_V13_DEFAULT and policy.RECORDS_ROOM2_DEFAULT and policy.CHICAGO_V05_DEFAULT)
	check("no-scene-test-overrides", policy.preview_override.is_empty())
	for language in ["zh", "en"]:
		for context in ["menu", "city", "outskirts", "ruins", "records", "chicago", "sentry", "patrol", "growth", "save"]:
			app.begin_new_run()
			app.language = language
			app.hero_appearance = "female" if language == "zh" else "male"
			app.show_initial_guide = false
			app.current_destination_id = "scifi.city"
			var path := "res://scenes/main_menu.tscn"
			if context in ["city", "outskirts", "ruins"]:
				app.current_destination_id = "scifi." + context
				path = "res://scenes/scifi_exploration_area.tscn"
			elif context == "records":
				app.current_destination_id = "scifi.ruins"
				app.current_annex_room = 2
				path = "res://scenes/survey_annex.tscn"
			elif context == "chicago":
				app.current_destination_id = "scifi.loop"
				path = app.area_scene_path("scifi.loop")
			elif context in ["sentry", "patrol", "growth"]:
				# Declared party/rendering fixture: not proof of normal recruitment gating.
				app.recruit_member("liang-xu")
				app.recruit_member("zhao-ling")
				app.ji_records_checked = true
				app.recruit_member("ji-cheng")
				path = "res://scenes/growth_screen.tscn"
				if context in ["sentry", "patrol"]:
					check(language + context + "-battle-setup", app.begin_battle(context, Vector2(340, 253)))
					path = "res://scenes/battle_arena.tscn"
			elif context == "save":
				app.save_screen_mode = "save"
				path = "res://scenes/save_screen.tscn"
			var node: Node = await open_scene(path)
			var key: String = language + "-" + context
			check(key + "-scene-exists", node != null)
			if context == "city":
				check(key + "-style46-default", node.city_hall_park != null and node.city_hall_park.runtime_dir.ends_with("/style46/"))
			elif context == "ruins":
				check(key + "-style45-default", node.style45_active and node.v13_active)
				check(key + "-ji-driver-present", node.field_npc_driver != null and node.field_npc_driver.actor_id == "ji-cheng")
			elif context == "outskirts":
				check(key + "-zhao-driver-present", node.field_npc_driver != null and node.field_npc_driver.actor_id == "zhao-ling")
			elif context == "records":
				check(key + "-style48-default", node._room_two_background().resource_path.contains("/style48/"))
			elif context == "chicago":
				check(key + "-style42-routed", node.scene_file_path.contains("/style42/"))
			elif context in ["sentry", "patrol"]:
				check(key + "-hero-set-present", node.combat_sprite_sets != null and node.combat_sprite_sets.has_set(0))
				check(key + "-all-three-member-sets", node.companion_sets_by_member.has_all(["liang-xu", "zhao-ling", "ji-cheng"]))
				check(key + "-enemy-animation-present", node.enemy_animation_texture != null)
			await capture(node, key)
			await close_scene(node)
	var report := {"checks": checks, "captures": captures, "count": checks.size(), "normalVisualFlags": false, "fixture": "packed normal .tscn contexts; explicit setup party/rendering fixture; no full campaign, audio audition, manual-play or final art claim", "engineVersion": Engine.get_version_info()}
	var file := FileAccess.open(output.path_join("rpg-2-star-ocean-the-second_mvp_packed-defaults-report_v01_" + stamp + ".json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  ") + "\n")
	file.close()
	call_deferred("finish")

func finish() -> void:
	var last := AudioServer.get_time_since_last_mix()
	var mixes := 0
	var deadline := Time.get_ticks_usec() + 500000
	while mixes < 2 and Time.get_ticks_usec() < deadline:
		await process_frame
		var age := AudioServer.get_time_since_last_mix()
		if age < last:
			mixes += 1
		last = age
	assert(mixes == 2)
	print("PLAY54_PACKED_DEFAULTS_OK checks=", checks.size())
	quit(0)
