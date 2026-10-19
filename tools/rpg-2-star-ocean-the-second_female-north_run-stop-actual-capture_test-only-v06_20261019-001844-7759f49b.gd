extends SceneTree
# NORTH v06-bound copy of the v05 gameplay capture (only model path, hash, save folder and labels differ).
# NORTH v05 gameplay capture (test only) = the v04 capture method bound to the locked v05 model, with two
# scenes and genuine key input: W key InputEventKey (keycode + physical_keycode) press/release events go
# through Input.parse_input_event and the game's own InputMap action move_up; the unmodified scene script
# moves the hero (real collisions/clamps). Scenes: 'city-bright' = scifi_exploration_area (scifi.city) lane
# x=360 from y=305 (walkable to y=160, ~1.04 s of northward running) and 'annex-dark' = survey_annex room 2
# lane x=240 from y=300 (as v04). The presenter replaces only the hidden hero sprite; scene occluders and
# z-order are the scene's own. v04 header follows.
# NORTH v04 (compact stance) ordinary-Input capture (test only). The unmodified survey annex scene moves the hero on
# Input.action_press/release("move_up"); a test presenter draws the v04 model at the hero's half-pixel
# rounded position (pivot 40,104, scale 0.5, nearest) with the scene hero hidden. Fixed simulation delta.
# The window is 1280x720 with the game's 640x360 canvas stretched 2x, so one source texel is one screen
# pixel. Contact is measured from the captured viewport image itself: each boot's static heel block
# (rows sole-3..sole of the static PNG) is searched as an exact RGB template near the sprite, and the
# matched heel-cap underside is mapped back to scene coordinates through the engine's own transforms.
# Usage: -s <this> -- <new frame folder> <fps> <report path> <city-bright|annex-dark> <en|zh>
const MODEL_PATH := "res://../tools/rpg-2-star-ocean-the-second_female-north_run-stop-source_unapproved-v06_20261019-001844-7759f49b.gd"
const EXPECTED_MODEL_SHA256 := "1f25c2aac2837d14a21eb2c8ddd60f93c19f2570cd486716003394e6f7789562"
const STATIC_PNG := "res://assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot_unapproved-v01_20261018-090713-6ed8d8dd.png"
const CORE := [[26,39],[42,54]]
const SOLE := [103,102]
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
	var legs := []
	var source_rgba_sha256 := ""
	func _process(delta: float) -> void:
		state=model.advance(delta,hero.position.y,Input.get_axis("move_down","move_up"))
		var rendered: Dictionary=model.render_pose(state)
		legs=rendered.get("legs",[])
		var image: Image=rendered.full
		source_rgba_sha256=_sha(image)
		sprite.texture=ImageTexture.create_from_image(image)
		sprite.position=Vector2(roundf(hero.position.x*2.)*.5,state.renderY+floor_offset)
		sprite.z_index=int(state.renderY+floor_offset)
	func _sha(image: Image) -> String:
		var hasher:=HashingContext.new()
		hasher.start(HashingContext.HASH_SHA256)
		hasher.update(image.get_data())
		return hasher.finish().hex_encode()
var presenter: Presenter
func _initialize() -> void:call_deferred("_run")
func _templates(image: Image) -> Array:
	var out:=[]
	for leg in 2:
		var t:=[]
		for y in range(SOLE[leg]-3,SOLE[leg]+1):
			for x in range(CORE[leg][0],CORE[leg][1]+1):
				var c:=image.get_pixel(x,y)
				if c.a8>0:t.append([x,y-SOLE[leg],c])
		out.append(t)
	return out
# Exact RGB matches of a heel template in the screen image within a window. Returns [[x0, bottom], ...]
# where x0 is the screen column of template column 0 and bottom the screen row of the heel-cap underside.
func _find(capture: Image,template: Array,center: Vector2i,radius: Vector2i) -> Array:
	var hits:=[]
	for by in range(maxi(4,center.y-radius.y),mini(capture.get_height(),center.y+radius.y)):
		for x0 in range(maxi(0,center.x-radius.x),mini(capture.get_width()-80,center.x+radius.x)):
			var ok:=true
			for t: Array in template:
				var c:=capture.get_pixel(x0+t[0],by+t[1])
				var e: Color=t[2]
				if c.r8!=e.r8 or c.g8!=e.g8 or c.b8!=e.b8:ok=false;break
			if ok:hits.append([x0,by])
	return hits
func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var folder := args[0]
	var fps := int(args[1])
	var report_path := args[2]
	var scene_name := args[3]
	var language := args[4]
	DirAccess.make_dir_recursive_absolute(folder)
	if FileAccess.get_sha256(MODEL_PATH)!=EXPECTED_MODEL_SHA256:
		push_error("locked v06 model hash changed")
		quit(2);return
	var app: Node=root.get_node("AppState")
	SaveStore.root_path="user://test-saves/female-north-run-v06-capture"
	app.begin_new_run()
	app.hero_appearance="female"
	app.language=language
	app.select_destination("scifi.city")
	if scene_name=="annex-dark":app.current_annex_room=2
	root.size=Vector2i(1280,720)
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
	# Annex: clear floor lane between the Service Manual and Duty Roster fixtures (same lane as v01-v04).
	# City: open plaza lane east of the garden obstacle and west of the planter (CityNavigation polygons).
	hero.position=Vector2(360,305) if scene_name=="city-bright" else Vector2(240,300)
	var start_y: float=hero.position.y
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
	var padded:=Image.create(80,128,false,Image.FORMAT_RGBA8)
	padded.blit_rect(static_png,Rect2i(0,0,80,112),Vector2i.ZERO)
	var static_sha:=rgba_sha(padded)
	var templates:=_templates(padded)
	for warmup in 8:
		await process_frame
		await RenderingServer.frame_post_draw
	var records:=[]
	var checks:=[]
	var previous_y: float=hero.position.y
	var tick:=0
	var segments: Array=[["idle",.30,0],["start-run",.70,1],["stop",.40,0],["repress-run",.28,1],["final-stop",.45,0]] if scene_name=="city-bright" else [["idle",.30,0],["start-run",.75,1],["stop",.40,0],["repress-run",.35,1],["final-stop",.45,0]]
	var key_down:=false
	for segment: Array in segments:
		var want: bool=segment[2]>0
		if want!=key_down:
			var ev:=InputEventKey.new()
			ev.keycode=KEY_W
			ev.physical_keycode=KEY_W
			ev.pressed=want
			Input.parse_input_event(ev)
			key_down=want
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
			checks.append({"key":"viewport-1280x720-%04d"%tick,"pass":capture.get_size()==Vector2i(1280,720)})
			checks.append({"key":"inputmap-move-up-state-%04d"%tick,"pass":Input.is_action_pressed("move_up")==(segment[2]>0)})
			var presented: Image=presenter.sprite.texture.get_image()
			presented.convert(Image.FORMAT_RGBA8)
			checks.append({"key":"presented-equals-source-%04d"%tick,"pass":rgba_sha(presented)==presenter.source_rgba_sha256})
			# Engine transforms: sprite texel space -> screen pixels, and screen pixels -> host scene space.
			var to_screen: Transform2D=root.get_final_transform()*presenter.sprite.get_global_transform_with_canvas()
			var screen_to_scene: Transform2D=(root.get_final_transform()*host.get_global_transform_with_canvas()).affine_inverse()
			var origin: Vector2=to_screen*presenter.sprite.offset
			var heel:=[]
			for leg in 2:
				var expect: Vector2=to_screen*(presenter.sprite.offset+Vector2(0,SOLE[leg]))
				var hits:=_find(capture,templates[leg],Vector2i(roundi(origin.x),roundi(expect.y)),Vector2i(4,40))
				var entry:={"matches":hits.size()}
				if hits.size()==1:
					var p: Vector2=screen_to_scene*Vector2(float(hits[0][0]),float(hits[0][1])+1.)
					entry["screen"]=hits[0]
					entry["sceneX"]=p.x
					entry["sceneY"]=p.y
				heel.append(entry)
			var state: Dictionary=presenter.state.duplicate(true)
			state["body"]=[state.body.x,state.body.y]
			# Airborne honesty: a foot the model calls airborne is drawn at least 1 row off the ground or
			# with its sole showing (no relabelled flat boot).
			for leg in 2:
				if state.mode!="idle" and not state.feet[leg].ground:
					var info: Dictionary=presenter.legs[leg]
					if roundi(state.feet[leg].lift)<1 and int(info.patch)<1:checks.append({"key":"airborne-visible-leg%d-%04d"%[leg,tick],"pass":false})
			records.append({"tick":tick,"segment":segment[0],"intentNorth":segment[2],"file":filename,"pngSha256":FileAccess.get_sha256(folder.path_join(filename)),"heroY":hero.position.y,"movedY":moved,"state":state,"heelCapFromCapture":heel,"sourceRgbaSha256":presenter.source_rgba_sha256,"isStatic":presenter.source_rgba_sha256==static_sha})
			tick+=1
	var up:=InputEventKey.new()
	up.keycode=KEY_W
	up.physical_keycode=KEY_W
	up.pressed=false
	Input.parse_input_event(up)
	var first_run:=-1
	for r in records:
		if r.segment=="start-run":first_run=r.tick;break
	checks.append({"key":"idle-segment-renders-static","pass":records.slice(0,first_run).all(func(r):return r.isStatic)})
	checks.append({"key":"start-first-press-frame-moves-and-runs","pass":records[first_run].movedY<0. and records[first_run].state.mode=="run" and not records[first_run].isStatic})
	var rp: Array=records.filter(func(r):return r.segment=="repress-run")
	checks.append({"key":"repress-first-press-frame-moves-and-runs","pass":rp[0].movedY<0. and rp[0].state.mode=="run" and not rp[0].isStatic})
	checks.append({"key":"airborne-frames-visibly-off-ground","pass":not checks.any(func(c):return (c.key as String).begins_with("airborne-visible-"))})
	for name in ["stop","final-stop"]:
		var seg:=records.filter(func(r):return r.segment==name)
		checks.append({"key":name+"-immediate-physical-stop","pass":seg.all(func(r):return r.movedY==0.)})
		var first_static:=-1
		for k in seg.size():
			if seg[k].isStatic:first_static=k;break
		var settled:=first_static>=0 and seg.slice(first_static).all(func(r):return r.isStatic)
		checks.append({"key":name+"-settles-to-exact-static","pass":settled,"framesToStatic":first_static+1,"seconds":float(first_static+1)/fps})
	# Contact: every continuous grounded run of a leg (all frames, boundaries included, run and stop).
	var contacts:=[]
	for leg in 2:
		var current:=[]
		for r in records+[null]:
			var grounded: bool=r!=null and r.state.mode!="idle" and r.state.feet[leg].ground
			if grounded:current.append(r)
			elif current.size()>0:
				var ys:=[]
				var xs:=[]
				var missing:=0
				for g in current:
					var h: Dictionary=g.heelCapFromCapture[leg]
					if h.matches!=1:missing+=1;continue
					ys.append(h.sceneY)
					xs.append(h.sceneX)
				var travel_y: float=(ys.max()-ys.min()) if ys.size()>0 else INF
				var travel_x: float=(xs.max()-xs.min()) if xs.size()>0 else INF
				var item:={"leg":leg,"firstTick":current[0].tick,"lastTick":current[-1].tick,"frames":current.size(),"segments":current.map(func(g):return g.segment),"stancePhases":current.map(func(g):return g.state.feet[leg].phase),"missingMatches":missing,"heelCapSceneY":ys,"heelCapTravelY":travel_y,"heelCapTravelX":travel_x}
				contacts.append(item)
				checks.append({"key":"contact-leg%d-ticks%d-%d-heel-cap-capture-travel<=1px"%[leg,item.firstTick,item.lastTick],"pass":missing==0 and travel_y<=1. and travel_x<=1.,"travelY":travel_y,"travelX":travel_x,"frames":item.frames})
				current=[]
	var full_stances:=contacts.filter(func(c):return c.segments.all(func(s):return s.ends_with("run")) and c.stancePhases[0]<9.4 and c.stancePhases[-1]>19.-9.4)
	checks.append({"key":"at-least-two-full-run-stances-measured","pass":full_stances.size()>=2,"count":full_stances.size()})
	var landings:=[]
	var run_frames:=records.filter(func(r):return r.segment=="start-run")
	for k in range(1,run_frames.size()):
		for leg in 2:
			if not run_frames[k-1].state.feet[leg].ground and run_frames[k].state.feet[leg].ground:landings.append(run_frames[k].tick)
	var cadence:=0.
	if landings.size()>=3:cadence=float(landings.size()-1)/(float(landings[-1]-landings[0])/fps)
	checks.append({"key":"steady-cadence-4.0-4.5-steps-per-s","pass":cadence>=4.0 and cadence<=4.5,"landingTicks":landings,"stepsPerSecond":cadence})
	var worst:=0.
	for c in contacts:worst=maxf(worst,maxf(c.heelCapTravelY,c.heelCapTravelX))
	var report:={"scene":("scifi_exploration_area scifi.city lane x=360 from y=%s"%start_y) if scene_name=="city-bright" else ("survey_annex room 2 (scifi.city) lane x=240 from y=%s"%start_y),"sceneKey":scene_name,"language":app.language,"lowestHeroY":records.map(func(r):return r.heroY).min(),"segments":segments,"fps":fps,"window":"1280x720, canvas 640x360 stretched 2x (canvas_items)","simulationSeconds":float(tick)/fps,"timingScope":"Fixed simulation delta; PNG capture wall time is not a performance benchmark.","prototypeOnly":true,"artApproved":false,"motionApproved":false,"input":"InputEventKey W (keycode+physical_keycode) via Input.parse_input_event -> InputMap move_up; hero moved by the unmodified scene script","expectedModelSha256":EXPECTED_MODEL_SHA256,"contactMeasure":"Exact RGB template of each boot's static heel block found in the captured viewport image; heel-cap underside screen row+1 mapped to scene space by (root final transform * host canvas transform)^-1.","contacts":contacts,"worstHeelCapCaptureTravelScenePx":worst,"frames":records,"checks":checks,"passed":checks.filter(func(c):return c["pass"]).size(),"failed":checks.filter(func(c):return not c["pass"]).size(),"modelSha256":FileAccess.get_sha256(MODEL_PATH),"captureSha256":FileAccess.get_sha256(get_script().resource_path),"staticPngSha256":FileAccess.get_sha256(STATIC_PNG)}
	var file:=FileAccess.open(report_path,FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  ")+"\n")
	file.close()
	for c in checks:
		if not c["pass"] or not (c["key"] as String).contains("-0"):print(("PASS " if c["pass"] else "FAIL ")+c["key"])
	print("NORTH V06 CAPTURE scene=",scene_name," lang=",language," fps=",fps," frames=",tick," worst heel-cap travel=",worst," passed=",report.passed," failed=",report.failed)
	if report.failed==0:print("NORTH_V06_CAPTURE_OK")
	quit(1 if report.failed>0 else 0)
