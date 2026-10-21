extends SceneTree
const DRIVER = preload("res://scripts/hsea09/rpg-2-star-ocean-the-second_heroine-sea_distance-driver_opt-in-v01_20261020-214620-4be375a2.gd")
const LOADER = preload("res://scripts/exploration_sprite_set_pilot.gd")
const POLICY = preload("res://scripts/hsea18/rpg-2-star-ocean-the-second_heroine-normal-default_policy_runtime-v01_20261021-032237-7c02af94.gd")
const BREATH = preload("res://scripts/hsea21/rpg-2-star-ocean-the-second_heroine-breathing-idle_playback-runtime_v01_20261021-151045-1217a1ff.gd")
var failed := 0
var checks := 0
func ck(ok: bool,label: String) -> void:
	checks+=1
	if not ok:failed+=1;print("BREATH21_PARITY_FAIL ",label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	ck(POLICY.package_ok(),"whole source package validated")
	var target=Sprite2D.new();root.add_child(target)
	var default_driver: Node=LOADER.attach(target,"protagonist-female","south")
	var compare=Sprite2D.new();root.add_child(compare)
	var explicit: Node=DRIVER.attach_registry(compare,"protagonist-female","south",POLICY.REGISTRY_PATH)
	ck(default_driver!=null and explicit!=null,"default and explicit package both attach")
	if default_driver==null or explicit==null:quit(2);return
	ck(default_driver.breathing.clips.size()==4,"all four idle clips loaded")
	for direction in ["south","west","north","east"]:
		default_driver.model.reset(direction);default_driver.breathing.reset(direction)
		explicit.model.reset(direction);explicit.breathing.reset(direction)
		for entry in [[0.4,Vector2.ZERO],[0.22,Vector2.ZERO],[0.18,Vector2.ZERO],[0.1,Vector2(1.4,0)],[0.033333333,Vector2.ZERO],[0.02,Vector2(2.8,0)],[0.12,Vector2.ZERO],[0.12,Vector2.ZERO],[1.0,Vector2.ZERO]]:
			default_driver.step(entry[0],Vector2.ZERO,entry[1],direction)
			explicit.step(entry[0],Vector2.ZERO,entry[1],direction)
			ck(default_driver.state()==explicit.state(),"default/explicit state parity "+direction)
			ck(target.texture==compare.texture,"default/explicit exact texture parity "+direction)
			ck(target.position==Vector2.ZERO and compare.position==Vector2.ZERO,"presentation cannot move root "+direction)
		ck(target.scale==Vector2(0.5,0.5) and target.offset==Vector2(0,-46),"original display transform "+direction)
	var male=Sprite2D.new();root.add_child(male)
	ck(LOADER.attach(male,"protagonist-male","south")==null,"male retains original fallback")
	ck(male.texture==null and male.scale==Vector2.ONE,"male sprite unmodified")
	DRIVER.enabled_override=0
	var disabled=Sprite2D.new();root.add_child(disabled)
	ck(LOADER.attach(disabled,"protagonist-female","south")==null,"explicit Sea-disable preserved")
	DRIVER.enabled_override=-1;LOADER.enabled_override=0
	ck(LOADER.attach(disabled,"protagonist-female","south")==null,"explicit generic-disable preserved")
	LOADER.enabled_override=-1;LOADER.registry_override="res://nonexistent-override.json"
	ck(LOADER.attach(disabled,"protagonist-female","south")==null,"explicit registry override blocks implicit default")
	LOADER.registry_override=""
	ck(BREATH.load_supplement("res://missing-idle21.json","bad","bad",{},LOADER).is_empty(),"missing idle manifest refused")
	var candidate: Dictionary=default_driver.sprite_set
	var bad_file="user://rpg-2-star-ocean-the-second_idle21_bad-schema_test-only.json"
	FileAccess.open(bad_file,FileAccess.WRITE).store_string("{}")
	ck(BREATH.load_supplement(bad_file,FileAccess.get_sha256(bad_file),"bad",candidate,LOADER).is_empty(),"hash-correct invalid schema refused")
	DirAccess.remove_absolute(bad_file)
	print("BREATH21_PARITY_PASS " if failed==0 else "BREATH21_PARITY_FAILED ",checks," checks; failures ",failed)
	quit(0 if failed==0 else 1)
