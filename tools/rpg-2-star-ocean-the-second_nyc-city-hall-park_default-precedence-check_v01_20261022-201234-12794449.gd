extends SceneTree
# Bounded selector/rollback fixtures; traversal is verified separately with real held input.
const Policy := preload("res://scripts/sdef35/rpg-2-star-ocean-the-second_mvp-scene-defaults_policy_prepared-v01_20261021-231349-a83c4bae.gd")
var checks: Array = []
var city: Script
var app: Node

func _initialize() -> void:
	call_deferred("run")

func check(key: String, value: bool) -> void:
	checks.append({"key": key, "pass": value})
	assert(value, key)

func detach_audio(node: Node) -> void:
	for child in node.get_children():
		if child is AudioStreamPlayer or child is AudioStreamPlayer2D or child is AudioStreamPlayer3D:
			child.stop()
			child.stream = null
		detach_audio(child)

func run() -> void:
	var args := OS.get_cmdline_user_args()
	app = root.get_node("AppState")
	check("fresh-settings", app.settings.load_status == "missing")
	SaveStore.root_path = "user://nyc53-precedence"
	city = load("res://scripts/city_hall_park_v06_scene.gd")
	check("authorized-city-bit-true", Policy.CITY_V06_DEFAULT)
	check("other-authorized-defaults-still-true", Policy.RUINS_V13_DEFAULT and Policy.RECORDS_ROOM2_DEFAULT and Policy.CHICAGO_V05_DEFAULT)
	var common_flag := args.has(city.STYLE46_FLAG)
	var old_flag := args.has(city.CLI_FLAG)
	var development: String = city.dev_dir()
	var first_mask := ""
	for policy_on in [true, false]:
		Policy.clear_preview()
		if not policy_on:
			Policy.preview_override[Policy.CITY] = false
		for override_value in [-1, 0, 1]:
			city.enabled_override = override_value
			var active_expected: bool = override_value == 1 if override_value >= 0 else (common_flag or old_flag or policy_on)
			var key: String = "default-%s-override-%s" % [str(policy_on), str(override_value)]
			check(key + "-enabled-precedence", city.enabled() == active_expected)
			if not active_expected:
				continue
			var scene: RefCounted = city.new()
			check(key + "-loads", scene.load_scene())
			var common_expected: bool = common_flag or (development.is_empty() and override_value < 0 and not old_flag and policy_on)
			check(key + "-art-directory-precedence", scene.runtime_dir == (city.STYLE46_DIR if common_expected else city.RUN_DIR))
			check(key + "-dev-source-preserved", scene.source_dir == development)
			check(key + "-walk-size", scene.walk_mask.get_size() == Vector2i(640, 360))
			var hashing := HashingContext.new()
			hashing.start(HashingContext.HASH_SHA256)
			hashing.update(scene.walk_mask.get_data())
			var mask_digest := hashing.finish().hex_encode()
			if first_mask.is_empty():
				first_mask = mask_digest
			check(key + "-walk-bytes-identical", first_mask == mask_digest)
	Policy.clear_preview()
	city.enabled_override = 0
	app.begin_new_run()
	app.select_destination("scifi.city")
	app.show_initial_guide = false
	var host: Node = load("res://scenes/scifi_exploration_area.tscn").instantiate()
	root.add_child(host)
	for i in 3:
		await process_frame
	check("explicit-off-normal-scene-restores-old-city", host.city_hall_park == null)
	check("rollback-still-has-hero-and-navigation", host.hero != null and host.back_button != null and host.save_button != null)
	detach_audio(host)
	root.remove_child(host)
	host.free()
	city.enabled_override = -1
	Policy.clear_preview()
	var result := {"checks": checks, "count": checks.size(), "args": args, "commonFlag": common_flag, "oldFlag": old_flag, "developmentSource": development, "walkBytesSha256": first_mask, "fixture": "selector matrix and actual normal scene explicit-off rollback; not a human playtest"}
	var f := FileAccess.open(args[0], FileAccess.WRITE)
	f.store_string(JSON.stringify(result, "  ") + "\n")
	f.close()
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
	print("NYC53_PRECEDENCE_OK checks=", checks.size())
	quit(0)
