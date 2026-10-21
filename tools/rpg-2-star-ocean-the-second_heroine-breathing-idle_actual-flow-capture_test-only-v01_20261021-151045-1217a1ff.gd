extends SceneTree
# Scripted normal input in actual ordinary-default exploration. Not a human playtest.
const CONFIG = preload("res://scripts/hsea16/rpg-2-star-ocean-the-second_heroine-playable-path_config_opt-in-v01_20261021-015453-1036fbad.gd")
const DEFAULTS = preload("res://scripts/hsea18/rpg-2-star-ocean-the-second_heroine-normal-default_policy_runtime-v01_20261021-032237-7c02af94.gd")
var output := ""
var tag := ""
var destination := ""
var language := "en"
var fps := 30
var failures := []
var checks := []
var samples := []
var captures := []
func ck(ok: bool, label: String) -> void:
	checks.append({"label":label,"passed":ok})
	if not ok:
		failures.append(label)
		print("BREATH21_CAPTURE_FAIL ", label)
func _initialize() -> void:
	call_deferred("run")
func tick() -> void:
	await process_frame
	await RenderingServer.frame_post_draw
func shot(label: String) -> void:
	var image := root.get_texture().get_image()
	var name := "rpg-2-star-ocean-the-second_heroine-breathing-idle_"+destination.get_slice(".",1)+"-"+language+"-"+label+"_actual-default-v01_"+tag+".png"
	ck(image.get_size()==Vector2i(1280,720) and image.save_png(output.path_join(name))==OK,"actual capture "+label)
	captures.append({"file":name,"sha256":FileAccess.get_sha256(output.path_join(name))})
func run() -> void:
	var args := OS.get_cmdline_user_args()
	output=args[0];tag=args[1];destination=args[2];language=args[3];fps=int(args[4])
	var app: Node = root.get_node("AppState")
	var prepared: Dictionary=CONFIG.configure(app,language,destination,true)
	ck(prepared.get("ok",false),"ordinary female run configured")
	ck(DEFAULTS.package_ok(),"complete default package including idle supplement validated")
	if not prepared.get("ok",false) or not DEFAULTS.package_ok():quit(2);return
	change_scene_to_file(CONFIG.EXPLORATION_SCENE)
	for i in 5:await tick()
	var host: Node=current_scene
	host.hero.position=Vector2(340,265)
	if destination == "scifi.city":
		for offset in [Vector2.ZERO,Vector2(20,0),Vector2(-20,0),Vector2(0,20),Vector2(0,-20)]:
			ck(host._city_walkable(host.hero.position+offset),"fixture center and cardinal clearance verified")
	var driver: Node=host.sprite_pilot
	ck(CONFIG.driver_attached(host),"normal distance driver active")
	ck(driver.breathing!=null and driver.breathing.clips.size()==4,"four breathing directions attached")
	var rules := [["south","move_down"],["north","move_up"],["west","move_left"],["east","move_right"]]
	for pair in rules:
		var direction: String=pair[0]
		Input.action_press(pair[1])
		for i in 3:await tick()
		Input.action_release(pair[1])
		for i in int(ceil(0.27*fps)):await tick()
		var position: Vector2=host.hero.position
		var seen := {}
		var inhale_saved := false
		var neutral_saved := false
		var stable := true
		for i in int(5.4*fps):
			await tick()
			if current_scene!=host:ck(false,"exploration remained active");quit(2);return
			var state: Dictionary=driver.state()
			stable=stable and host.hero.position.distance_to(position)<0.000001
			var sample: int=int(state.get("idle_frame",-1))
			seen[sample]=true
			samples.append({"direction":direction,"tick":i,"idleFrame":sample,"elapsedMs":state.get("idle_elapsed_ms",-1),"position":[host.hero.position.x,host.hero.position.y]})
			if sample==0 and not neutral_saved:shot(direction+"-neutral");neutral_saved=true
			if sample==3 and not inhale_saved:shot(direction+"-inhale");inhale_saved=true
		ck(stable,"stationary world position "+direction)
		ck(driver.facing==direction and driver.action=="idle","facing and rest state "+direction)
		ck(seen.size()>=4 and not seen.has(-1),"idle visibly advances through authored source samples "+direction)
		ck(neutral_saved and inhale_saved,"neutral and inhale captured "+direction)
		ck(host.hero.scale==Vector2(0.5,0.5) and host.hero.offset==Vector2(0,-46),"display transform unchanged "+direction)
		Input.action_press(pair[1]);await tick();await tick()
		ck(host.hero.position.distance_to(position)>0.001 and driver.action=="walk" and driver.breathing.elapsed_us==0.0,"normal input moves and cancels breathing immediately "+direction)
		Input.action_release(pair[1])
		for i in int(ceil(0.27*fps)):await tick()
	var report={"testOnly":true,"humanPlaytest":false,"artAccepted":false,"destination":destination,"language":language,"fps":fps,"ordinaryDefault":true,"checks":checks,"failures":failures,"captures":captures,"samples":samples,"driverSha256":FileAccess.get_sha256(CONFIG.SEA_DRIVER_PATH),"createdAt":Time.get_datetime_string_from_system(true),"playbackSha256":FileAccess.get_sha256("res://scripts/hsea21/rpg-2-star-ocean-the-second_heroine-breathing-idle_playback-runtime_v01_20261021-151045-1217a1ff.gd"),"idleManifestSha256":"dc6f4496fe268fd07d1ba674c415f8063977263a29549e82a578d5901c657e96"}
	var name := "rpg-2-star-ocean-the-second_heroine-breathing-idle_"+destination.get_slice(".",1)+"-"+language+"_actual-proof-v01_"+tag+".json"
	FileAccess.open(output.path_join(name),FileAccess.WRITE).store_string(JSON.stringify(report,"  ")+"\n")
	if failures.is_empty():
		print("BREATH21_CAPTURE_PASS ",checks.size())
	else:
		print("BREATH21_CAPTURE_FAILED ",failures)
	quit(0 if failures.is_empty() else 1)
