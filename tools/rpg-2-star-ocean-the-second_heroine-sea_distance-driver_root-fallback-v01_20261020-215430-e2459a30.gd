extends SceneTree
var failures := []
var checks := 0
func ck(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures.append(label)
		print("SEA_FALLBACK_FAIL ",label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var args := OS.get_cmdline_user_args()
	var Loader = load("res://scripts/exploration_sprite_set_pilot.gd")
	var Driver = load("res://scripts/hsea09/rpg-2-star-ocean-the-second_heroine-sea_distance-driver_opt-in-v01_20261020-214620-4be375a2.gd")
	var sprite := Sprite2D.new()
	sprite.position = Vector2(31,42)
	sprite.scale = Vector2(2,3)
	sprite.offset = Vector2(7,8)
	Loader.clear_cache()
	Driver.enabled_override = 0
	Loader.registry_override = "res://missing-registry-must-not-be-read.json"
	ck(Driver.attach(sprite,"protagonist-female","south") == null,"flag off refuses")
	ck(Loader.manifest_reads == 0 and Loader.texture_loads == 0,"flag off no data reads")
	Driver.enabled_override = 1
	ck(Driver.attach(sprite,"protagonist-male","south") == null,"other actor no attachment")
	ck(Driver.attach(sprite,"protagonist-female","upward") == null,"unknown facing no attachment")
	ck(Loader.manifest_reads == 0,"invalid actor/facing no reads")
	Loader.registry_override = args[0]
	var driver = Driver.attach(sprite,"protagonist-female","south")
	if args[1] == "refuse":
		ck(driver == null,"mutated bridge refuses whole package")
		ck(sprite.scale == Vector2(2,3) and sprite.offset == Vector2(7,8) and sprite.texture == null and sprite.get_child_count() == 0,"refusal leaves target unchanged")
	else:
		ck(driver != null,"valid package attaches")
		if driver != null:
			ck(sprite.scale == Vector2(0.5,0.5) and sprite.offset == Vector2(0,-46),"expected display transform")
			for n in 100:
				driver.step(1.0/60,Vector2(31,42),Vector2(31,42),"south")
			ck(driver.action == "idle" and driver.frame == 0,"blocked zero actual displacement stays idle")
			ck(sprite.position == Vector2(31,42),"driver never moves target")
	if args[1] == "phase" and driver != null:
		ck(driver.bridges.has("phase_bridges"), "phase-aware package active")
		var points := [[0.0,0], [0.249999,0], [0.25,1], [0.499999,1], [0.5,2], [0.799999,2], [0.8,3], [1.0,3]]
		for direction in ["east", "west"]:
			for phase in range(12):
				for sample in points:
					driver._apply({"action":"settle", "facing":direction, "frame":6 if phase < 6 else 0, "settle_entry_frame":phase, "settle_progress":sample[0], "diagnostics":{"settle_target_frame":0}})
					ck(sprite.texture == driver.bridges["phase_bridges"][direction][phase][sample[1]], "%s actual entry phase%d boundary%s" % [direction,phase,sample[0]])
					ck(driver.state().get("bridge_phase") == phase and driver.state().get("bridge_frame") == sample[1], "state records phase sample")
				ck(driver.bridges["phase_bridges"][direction][phase][0].get_image().get_data() == driver.sprite_set["clips"]["walk"][direction]["textures"][phase].get_image().get_data(), "entry exact walk")
				ck(driver.bridges["phase_bridges"][direction][phase][3].get_image().get_data() == driver.sprite_set["clips"]["idle"][direction]["textures"][0].get_image().get_data(), "end exact idle")
		for direction in ["north", "south"]:
			driver._apply({"action":"settle", "facing":direction, "frame":0, "settle_entry_frame":3, "settle_progress":0.6, "diagnostics":{"settle_target_frame":6}})
			ck(sprite.texture == driver.bridges[direction][6][0], "legacy front/back contact remains " + direction)
		var reg: Dictionary = Loader.load_registry(args[0])
		var setpath: String = reg["actors"]["protagonist-female"]
		var profile: Dictionary = Driver._profile_for_set(FileAccess.get_sha256(setpath))
		var manifest_path: String = profile["transition_path"]
		var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(manifest_path))
		var broken: Dictionary = data.duplicate(true)
		broken["phase_bridges"]["east"].erase("phase4")
		ck(Driver._load_phase_bridges(Loader, manifest_path, broken, driver.sprite_set).is_empty(), "missing phase refuses")
		broken = data.duplicate(true)
		broken["phase_bridges"]["west"]["phase3"]["from_walk_frame"] = 4
		ck(Driver._load_phase_bridges(Loader, manifest_path, broken, driver.sprite_set).is_empty(), "wrong outgoing index refuses")
		broken = data.duplicate(true)
		broken["phase_bridges"]["east"]["phase3"]["bridge"][0] = broken["phase_bridges"]["east"]["phase4"]["bridge"][0]
		ck(Driver._load_phase_bridges(Loader, manifest_path, broken, driver.sprite_set).is_empty(), "valid other-pose endpoint refuses")
		broken = data.duplicate(true)
		broken["phase_bridges"]["east"]["phase0"]["bridge"][1]["file"] = "../escape.png"
		ck(Driver._load_phase_bridges(Loader, manifest_path, broken, driver.sprite_set).is_empty(), "traversal refuses")
		ck(sprite.position == Vector2(31,42), "phase selection does not move physical target")
	sprite.free()
	Loader.clear_cache()
	if failures.is_empty():
		print("SEA_FALLBACK_ROOT_PASS checks=",checks)
		quit(0)
	else:
		quit(1)
