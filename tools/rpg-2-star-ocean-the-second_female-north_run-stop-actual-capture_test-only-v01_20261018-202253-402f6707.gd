extends SceneTree
# NORTH v01 ordinary-Input capture (test only). The unmodified survey annex scene moves the hero on
# Input.action_press/release("move_up"); a test presenter draws the NORTH model at the hero's half-pixel
# rounded position (pivot 40,104, scale 0.5, nearest) with the scene hero hidden. Fixed simulation delta.
# Usage: -s <this> -- <new frame folder> <fps> <report path>
const MODEL_PATH := "res://../tools/rpg-2-star-ocean-the-second_female-north_run-stop-source_unapproved-v01_20261018-202253-402f6707.gd"
const STATIC_PNG := "res://assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot_unapproved-v01_20261018-090713-6ed8d8dd.png"
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
	var source_rgba_sha256 := ""
	func _process(delta: float) -> void:
		state=model.advance(delta,hero.position.y,Input.get_axis("move_down","move_up"))
		var image: Image=model.render_pose(state).full
		var hasher:=HashingContext.new()
		hasher.start(HashingContext.HASH_SHA256)
		hasher.update(image.get_data())
		source_rgba_sha256=hasher.finish().hex_encode()
		sprite.texture=ImageTexture.create_from_image(image)
		sprite.position=Vector2(roundf(hero.position.x*2.)*.5,state.renderY+floor_offset)
		sprite.z_index=int(state.renderY+floor_offset)
var presenter: Presenter
func _initialize() -> void:call_deferred("_run")
func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var folder := args[0]
	var fps := int(args[1])
	var report_path := args[2]
	DirAccess.make_dir_recursive_absolute(folder)
	var app: Node=root.get_node("AppState")
	SaveStore.root_path="user://test-saves/female-north-run-prototype-v01"
	app.begin_new_run()
	app.hero_appearance="female"
	app.language="en"
	app.select_destination("scifi.city")
	app.current_annex_room=2
	root.size=Vector2i(640,360)
	root.content_scale_size=Vector2i(640,360)
	root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	var host: Node2D=load("res://scenes/survey_annex.tscn").instantiate()
	root.add_child(host)
	current_scene=host
	await process_frame
	await process_frame
	var hero: Sprite2D=host.hero
	var image:=hero.texture.get_image()
	var bounds:=image.get_used_rect()
	var floor_offset: float=hero.offset.y-image.get_height()*.5+bounds.end.y
	# Clear floor lane between the Service Manual and Duty Roster fixtures (no fixture or label overlap).
	hero.position=Vector2(240,300)
	hero.visible=false
	presenter=Presenter.new()
	presenter.model=load(MODEL_PATH).new()
	presenter.hero=hero
	presenter.floor_offset=floor_offset
	presenter.process_priority=1
	presenter.model.render_y=hero.position.y
	presenter.model.physical_y=hero.position.y
	presenter.sprite=Sprite2D.new()
	presenter.sprite.centered=false
	presenter.sprite.offset=Vector2(-40,-104)
	presenter.sprite.scale=Vector2(.5,.5)
	presenter.sprite.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST
	presenter.add_child(presenter.sprite)
	host.add_child(presenter)
	var static_png:=Image.load_from_file(ProjectSettings.globalize_path(STATIC_PNG))
	static_png.convert(Image.FORMAT_RGBA8)
	var static_sha:=rgba_sha(static_png)
	for warmup in 8:
		await process_frame
		await RenderingServer.frame_post_draw
	var records:=[]
	var checks:=[]
	var previous_y: float=hero.position.y
	var tick:=0
	var segments: Array=[["idle",.30,0],["start-run",.80,1],["stop",.40,0],["repress-run",.35,1],["final-stop",.40,0]]
	for segment: Array in segments:
		Input.action_release("move_up")
		if segment[2]>0:Input.action_press("move_up")
		for frame in roundi(segment[1]*fps):
			await process_frame
			await RenderingServer.frame_post_draw
			var capture:=root.get_viewport().get_texture().get_image()
			capture.convert(Image.FORMAT_RGBA8)
			var filename:="f-%04d.png"%tick
			capture.save_png(folder.path_join(filename))
			var dt: float=presenter.get_process_delta_time()
			var moved: float=hero.position.y-previous_y
			previous_y=hero.position.y
			checks.append({"key":"fixed-delta-%04d"%tick,"pass":absf(dt-1.0/fps)<.000001})
			checks.append({"key":"physical-input-%04d"%tick,"pass":absf(moved+segment[2]*140.*dt)<.001,"observedDelta":moved})
			checks.append({"key":"native-viewport-%04d"%tick,"pass":capture.get_size()==Vector2i(640,360)})
			var presented: Image=presenter.sprite.texture.get_image()
			presented.convert(Image.FORMAT_RGBA8)
			checks.append({"key":"presented-equals-source-%04d"%tick,"pass":rgba_sha(presented)==presenter.source_rgba_sha256})
			var state: Dictionary=presenter.state.duplicate(true)
			state["body"]=[state.body.x,state.body.y]
			records.append({"tick":tick,"segment":segment[0],"intentNorth":segment[2],"file":filename,"pngSha256":FileAccess.get_sha256(folder.path_join(filename)),"heroY":hero.position.y,"movedY":moved,"state":state,"sourceRgbaSha256":presenter.source_rgba_sha256,"isStatic":presenter.source_rgba_sha256==static_sha})
			tick+=1
	Input.action_release("move_up")
	# Endpoint expectations on the actual frames.
	var first_run:=-1
	for r in records:
		if r.segment=="start-run":first_run=r.tick;break
	checks.append({"key":"idle-segment-renders-static","pass":records.slice(0,first_run).all(func(r):return r.isStatic)})
	checks.append({"key":"start-first-press-frame-moves-and-runs","pass":records[first_run].movedY<0. and records[first_run].state.mode=="run" and not records[first_run].isStatic})
	for name in ["stop","final-stop"]:
		var seg:=records.filter(func(r):return r.segment==name)
		checks.append({"key":name+"-immediate-physical-stop","pass":seg.all(func(r):return r.movedY==0.)})
		var first_static:=-1
		for k in seg.size():
			if seg[k].isStatic:first_static=k;break
		var settled:=first_static>=0 and seg.slice(first_static).all(func(r):return r.isStatic)
		checks.append({"key":name+"-settles-to-exact-static","pass":settled,"framesToStatic":first_static+1,"seconds":float(first_static+1)/fps})
	# Cadence = contacts per second from the mean interval between consecutive landings in the first run
	# (counting events inside a fixed window is biased by where the window starts and ends).
	var landings:=[]
	var run_frames:=records.filter(func(r):return r.segment=="start-run")
	for k in range(1,run_frames.size()):
		for leg in 2:
			if not run_frames[k-1].state.feet[leg].ground and run_frames[k].state.feet[leg].ground:landings.append(run_frames[k].tick)
	var cadence:=0.
	if landings.size()>=3:cadence=float(landings.size()-1)/(float(landings[-1]-landings[0])/fps)
	checks.append({"key":"steady-cadence-4.0-4.5-steps-per-s","pass":cadence>=4.0 and cadence<=4.5,"landingTicks":landings,"stepsPerSecond":cadence})
	var report:={"scene":"survey_annex room 2 (scifi.city)","language":app.language,"fps":fps,"simulationSeconds":float(tick)/fps,"timingScope":"Fixed simulation delta; PNG capture wall time is not a performance benchmark.","prototypeOnly":true,"artApproved":false,"motionApproved":false,"input":"Input.action_press/action_release move_up; hero moved by the unmodified survey_annex.gd","frames":records,"checks":checks,"passed":checks.filter(func(c):return c["pass"]).size(),"failed":checks.filter(func(c):return not c["pass"]).size(),"modelSha256":FileAccess.get_sha256(MODEL_PATH),"captureSha256":FileAccess.get_sha256(get_script().resource_path),"staticPngSha256":FileAccess.get_sha256(STATIC_PNG)}
	var file:=FileAccess.open(report_path,FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  ")+"\n")
	file.close()
	for c in checks:
		if not c["pass"] or not (c["key"] as String).contains("-0"):print(("PASS " if c["pass"] else "FAIL ")+c["key"])
	print("NORTH RUN CAPTURE frames=",tick," passed=",report.passed," failed=",report.failed)
	quit(1 if report.failed>0 else 0)
