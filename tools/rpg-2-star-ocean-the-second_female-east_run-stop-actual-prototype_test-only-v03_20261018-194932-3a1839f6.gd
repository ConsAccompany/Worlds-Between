extends SceneTree
# v03 ordinary-Input capture: same lane/segments/presenter as v02, bound to the locked v03 model.
# Adds per-frame presented-texture == source RGBA, the sprite's canvas (screen) transform, and
# whether a steady run frame is torso-equivalent to its 280 Hz native cel (the v03 guard can
# hold the torso 1 source px for a frame at 30/60 fps). Usage: -- <folder> <fps> <scene>
const MODEL := preload("res://../tools/rpg-2-star-ocean-the-second_female-east_run-stop-source_unapproved-v03_20261018-193030-48da69c1.gd")
const EXPECTED_MODEL_SHA256 := "e783de5d8ab6b1e3f678299eb8cffde11109d1aab06c47155831ebc4388bb07f"
static func rgba_sha(image: Image) -> String:
	var hasher:=HashingContext.new()
	hasher.start(HashingContext.HASH_SHA256)
	hasher.update(image.get_data())
	return hasher.finish().hex_encode()
class Presenter extends Node2D:
	var model: RefCounted
	var hero: Sprite2D
	var floor_offset := 0.
	var sprite: Sprite2D
	var state := {}
	var west_placeholder: Image
	var source_rgba_sha256 := ""
	func _process(delta: float) -> void:
		state=model.advance(delta,hero.position.x,Input.get_axis("move_left","move_right"))
		var image: Image=west_placeholder if state.mode=="reverse-placeholder" else model.render_pose(state).full
		var hasher:=HashingContext.new()
		hasher.start(HashingContext.HASH_SHA256)
		hasher.update(image.get_data())
		source_rgba_sha256=hasher.finish().hex_encode()
		sprite.texture=ImageTexture.create_from_image(image)
		sprite.position=Vector2(state.renderX,hero.position.y+floor_offset)
var presenter: Presenter
func _initialize() -> void:call_deferred("_run")
func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var folder := args[0]
	var fps := int(args[1])
	var scene_name := args[2]
	var stamp := Time.get_datetime_string_from_system().replace("-","").replace(":","").replace("T","-")+"-%08x"%(randi()&0xffffffff)
	DirAccess.make_dir_recursive_absolute(folder)
	var app: Node=root.get_node("AppState")
	SaveStore.root_path="user://test-saves/female-east-run-prototype-v03"
	assert(app.settings.load_status=="missing")
	app.begin_new_run()
	app.hero_appearance="female"
	app.language="en" if fps==30 else "zh"
	app.select_destination("scifi.city")
	app.current_annex_room=2
	root.size=Vector2i(640,360)
	root.content_scale_size=Vector2i(640,360)
	root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	var host: Node2D=load("res://scenes/scifi_exploration_area.tscn" if scene_name=="city-bright" else "res://scenes/survey_annex.tscn").instantiate()
	root.add_child(host)
	current_scene=host
	await process_frame
	await process_frame
	var hero: Sprite2D=host.hero
	var image:=hero.texture.get_image()
	var bounds:=image.get_used_rect()
	var floor_offset: float=hero.offset.y-image.get_height()*.5+bounds.end.y
	hero.position=Vector2(160,185 if scene_name=="city-bright" else 265)
	hero.visible=false
	presenter=Presenter.new()
	presenter.model=MODEL.new()
	presenter.hero=hero
	presenter.floor_offset=floor_offset
	presenter.process_priority=1
	presenter.model.render_x=hero.position.x
	presenter.model.physical_x=hero.position.x
	presenter.sprite=Sprite2D.new()
	presenter.sprite.centered=false
	presenter.sprite.offset=Vector2(-40,-104)
	presenter.sprite.scale=Vector2(.5,.5)
	presenter.sprite.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST
	presenter.sprite.z_index=int(hero.position.y+floor_offset)
	presenter.add_child(presenter.sprite)
	presenter.west_placeholder=Image.load_from_file(ProjectSettings.globalize_path("res://../outputs/female-west-static-v01/rpg-2-star-ocean-the-second_protagonist-female_west-static_unapproved-v01_20261018-174421-618816ac.png"))
	host.add_child(presenter)
	for warmup in 8:
		await process_frame
		await RenderingServer.frame_post_draw
	var records:=[]
	var checks:=[]
	var previous_x: float=hero.position.x
	var tick:=0
	var recording_start_ms:=Time.get_ticks_msec()
	var segments: Array=[['idle',.30,0],['start-run',1.10,1],['release',.24,0],['run-again',.50,1],['quick-release',1.0/fps,0],['repress',.50,1],['stop',.26,0],['reversal-west-static-placeholder',.20,-1],['east-return',.55,1],['final-stop',.30,0]]
	for segment: Array in segments:
		Input.action_release("move_left")
		Input.action_release("move_right")
		if segment[2]<0:Input.action_press("move_left")
		if segment[2]>0:Input.action_press("move_right")
		for frame in maxi(1,roundi(segment[1]*fps)):
			await process_frame
			await RenderingServer.frame_post_draw
			var capture:=root.get_viewport().get_texture().get_image()
			capture.convert(Image.FORMAT_RGBA8)
			var filename:="rpg-2-star-ocean-the-second_female-east-run-%s-%dfps_frame-%04d_v03_%s.png"%[scene_name,fps,tick,stamp]
			var file:=folder.path_join(filename)
			capture.save_png(file)
			var state: Dictionary=presenter.state.duplicate(true)
			state['body']=[state.body.x,state.body.y]
			var dt: float=presenter.get_process_delta_time()
			checks.append({'key':'fixed-delta-%04d'%tick,'pass':absf(dt-1.0/fps)<.000001})
			checks.append({'key':'physical-input-%04d'%tick,'pass':absf((hero.position.x-previous_x)-segment[2]*140.*dt)<.001,'observedDelta':hero.position.x-previous_x})
			previous_x=hero.position.x
			checks.append({'key':'native-viewport-%04d'%tick,'pass':capture.get_size()==Vector2i(640,360)})
			var presented: Image=presenter.sprite.texture.get_image()
			presented.convert(Image.FORMAT_RGBA8)
			checks.append({'key':'presented-equals-source-%04d'%tick,'pass':rgba_sha(presented)==presenter.source_rgba_sha256})
			var canvas: Transform2D=presenter.sprite.get_global_transform_with_canvas()
			var steady: bool=presenter.state.mode=="run" and presenter.state.age>=.12
			var native_torso: bool=steady and presenter.state.body==Vector2(presenter.model.LEAN,roundi(presenter.model.steady_body(presenter.state.q).y))
			records.append({'tick':tick,'segment':segment[0],'intent':segment[2],'file':filename,'sha256':FileAccess.get_sha256(file),'state':state,'sourceRgbaSha256':presenter.source_rgba_sha256,'delta':presenter.get_process_delta_time(),'heroX':hero.position.x,'spriteCanvasOrigin':[canvas.origin.x,canvas.origin.y],'spriteCanvasScale':[canvas.get_scale().x,canvas.get_scale().y],'spriteOffset':[presenter.sprite.offset.x,presenter.sprite.offset.y],'steadyRun':steady,'torsoEqualsNativeCel':native_torso})
			tick+=1
	Input.action_release("move_left")
	Input.action_release("move_right")
	var report:={'scene':scene_name,'fps':fps,'simulationSeconds':float(tick)/fps,'recordingWallClockMs':Time.get_ticks_msec()-recording_start_ms,'timingScope':'Fixed simulation delta; normal1x movie encoded at declared fps. PNG capture wall time is not a performance benchmark.','prototypeOnly':true,'artApproved':false,'motionApproved':false,'frames':records,'checks':checks,'passed':checks.filter(func(c):return c['pass']).size(),'failed':checks.filter(func(c):return not c['pass']).size(),'modelSha256':FileAccess.get_sha256("res://../tools/rpg-2-star-ocean-the-second_female-east_run-stop-source_unapproved-v03_20261018-193030-48da69c1.gd"),'expectedModelSha256':EXPECTED_MODEL_SHA256,'language':app.language,'input':'Input.action_press/action_release on move_left/move_right; hero moved by the unmodified scene script','checkerSha256':FileAccess.get_sha256(get_script().resource_path)}
	var file:=FileAccess.open(folder.path_join("rpg-2-star-ocean-the-second_female-east-run_actual-report_v03_%s.json"%stamp),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  ")+"\n")
	file.close()
	print("EAST RUN PROTOTYPE captured ",tick," actualframes")
	quit(1 if checks.any(func(c):return not c["pass"]) or report.modelSha256!=EXPECTED_MODEL_SHA256 else 0)
