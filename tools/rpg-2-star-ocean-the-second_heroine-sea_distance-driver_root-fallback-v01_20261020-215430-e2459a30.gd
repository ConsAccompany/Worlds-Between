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
	sprite.free()
	Loader.clear_cache()
	if failures.is_empty():
		print("SEA_FALLBACK_ROOT_PASS checks=",checks)
		quit(0)
	else:
		quit(1)
