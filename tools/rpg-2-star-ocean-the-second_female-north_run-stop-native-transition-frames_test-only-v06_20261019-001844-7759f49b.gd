extends SceneTree
# NORTH v06 native transition frames (test only). For the representative v05 matrix failure cases it replays
# the frozen matrix procedure (real 280 Hz seed state, same schedule, same release / re-press inputs) on the
# locked v05 and v06 models and saves every frame as its own native 80x128 RGBA PNG (one source texel = one
# screen pixel of the 1280x720 game window, i.e. real gameplay scale), plus a JSON index with each frame's
# state, raster heel hits and hashes. It also gates that v06's steady run is v05-exact: the 128 steady
# 280 Hz states and cels, and 30/60 Hz steady runs (states and cels), must be identical.
# Usage: -s <this> -- <output folder> <index json path>
const V05 := "res://../tools/rpg-2-star-ocean-the-second_female-north_run-stop-source_unapproved-v05_20261018-221035-f3932915.gd"
const V05_SHA := "903a75f3d5e0a294a03dd2c64ba6759aee899f9001b5a434576cc1adfd26d2c7"
const V06 := "res://../tools/rpg-2-star-ocean-the-second_female-north_run-stop-source_unapproved-v06_20261019-001844-7759f49b.gd"
const V06_SHA := "1f25c2aac2837d14a21eb2c8ddd60f93c19f2570cd486716003394e6f7789562"
const STATIC_PNG := "res://assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot_unapproved-v01_20261018-090713-6ed8d8dd.png"
const PREFIX := "rpg-2-star-ocean-the-second_female-north-v06-native_"
const SUFFIX := "_v06_20261019-001844-7759f49b.png"
const CORE := [[26,39],[42,54]]
const SOLE := [103,102]
const SPEED := 140.
# [name, schedule, seed phase, released frames before re-press (0 = stop only), v05 family shown]
const CASES := [
	["stop-planted-behind-60-q16","60",16,0,"stop-single-step-no-relift"],
	["stop-peel-60-q22","60",22,0,"stop-single-step-no-relift"],
	["stop-double-airborne-30-q30","30",30,0,"raised-foot-deadline"],
	["stop-stance-bob-30-q3","30",3,0,"no-late-leg-material-pop"],
	["repress-both-home-30-q12-r3","30",12,3,"repress-no-double-lift + support"],
	["repress-both-home-mixed-q12-r3","mixed",12,3,"repress-no-double-lift + support"],
	["repress-one-down-mixed-q0-r1","mixed",0,1,"repress-support-deadline"],
	["repress-planted-behind-60-q15-r1","60",15,1,"repress-support-deadline"]]
var templates:=[]
var checks:=[]
func check(key: String,ok: bool,detail: Variant=null) -> void:
	checks.append({"key":key,"pass":ok,"detail":detail})
func _initialize() -> void:call_deferred("run")
func find(image: Image,leg: int) -> Array:
	var hits:=[]
	for bottom in range(60,128):
		for dx in range(-2,3):
			var ok:=true
			for t: Array in templates[leg]:
				var x: int=t[0]+dx
				var y: int=bottom+t[1]
				if y<0 or y>=128 or image.get_pixel(x,y)!=t[2]:ok=false;break
			if ok:hits.append([bottom,dx])
	return hits
func steady(script: GDScript,dt: float,ticks: int,keep_from: int) -> Array:
	var m=script.new()
	var y:=500.
	m.physical_y=y;m.render_y=y
	var out:=[]
	for i in ticks:
		y-=SPEED*dt
		var s: Dictionary=m.advance(dt,y,1.)
		if i>=keep_from:out.append({"state":JSON.stringify(ser(s)),"cel":m.render_pose(s).full.get_data()})
	return out
func ser(state: Dictionary) -> Dictionary:
	var s:=state.duplicate(true)
	s.body=[s.body.x,s.body.y]
	return s
func seeds_of(script: GDScript) -> Dictionary:
	var sm=script.new()
	var sy:=500.
	sm.physical_y=sy;sm.render_y=sy
	var seeds:={}
	for i in 420:
		sy-=.5
		var st: Dictionary=sm.advance(1./280.,sy,1.)
		if i>=256:seeds[int(st.q)]=st
	return seeds
func seed_into(m: RefCounted,s: Dictionary,phase: int) -> void:
	m.physical_y=500.;m.render_y=500.;m.origin_y=500.;m.q0=float(phase);m.q=float(phase);m.mode="run";m.age=1.
	m.feet=m._copy_feet(s.feet)
	m.start_feet=m._copy_feet(s.feet)
	for i in 2:m.start_feet[i].phase=-2.
	m.last_body=s.body;m.start_body=s.body;m.live=1.;m.start_live=1.
func run() -> void:
	var args:=OS.get_cmdline_user_args()
	var folder: String=args[0]
	DirAccess.make_dir_recursive_absolute(folder)
	var sha05:=FileAccess.get_sha256(V05)
	var sha06:=FileAccess.get_sha256(V06)
	if sha05!=V05_SHA or sha06!=V06_SHA:
		push_error("locked model hash changed")
		quit(2);return
	var m05: GDScript=load(V05)
	var m06: GDScript=load(V06)
	var png:=Image.load_from_file(ProjectSettings.globalize_path(STATIC_PNG))
	png.convert(Image.FORMAT_RGBA8)
	var padded:=Image.create(80,128,false,Image.FORMAT_RGBA8)
	padded.blit_rect(png,Rect2i(0,0,80,112),Vector2i.ZERO)
	for leg in 2:
		var t:=[]
		for y in range(SOLE[leg]-3,SOLE[leg]+1):
			for x in range(CORE[leg][0],CORE[leg][1]+1):
				var c:=padded.get_pixel(x,y)
				if c.a8>0:t.append([x,y-SOLE[leg],c])
		templates.append(t)
	# Steady run v05-exact (gait cadence, stance, swing, bob and art unchanged).
	var a:=steady(m05,1./280.,420,256)
	var b:=steady(m06,1./280.,420,256)
	check("steady-280hz-164-ticks-states-identical-to-v05",a.map(func(r):return r.state)==b.map(func(r):return r.state))
	check("steady-280hz-164-ticks-cels-identical-to-v05",a.map(func(r):return r.cel)==b.map(func(r):return r.cel))
	var seeds05:=seeds_of(m05)
	var seeds06:=seeds_of(m06)
	check("all-128-steady-seed-phases-present",seeds05.size()==128 and seeds06.size()==128,[seeds05.size(),seeds06.size()])
	for rate in [30,60]:
		var a2:=steady(m05,1./float(rate),rate*3,rate)
		var b2:=steady(m06,1./float(rate),rate*3,rate)
		check("steady-%dhz-2s-after-first-second-states-identical-to-v05"%rate,a2.map(func(r):return r.state)==b2.map(func(r):return r.state))
		check("steady-%dhz-2s-after-first-second-cels-identical-to-v05"%rate,a2.map(func(r):return r.cel)==b2.map(func(r):return r.cel))
	var schedules: Dictionary={"30":[1./30.],"60":[1./60.],"mixed":[1./24.,1./60.,1./48.,1./30.]}
	var index:=[]
	for c: Array in CASES:
		var steps: Array=schedules[c[1]]
		for tag in ["v05","v06"]:
			var script: GDScript=m05 if tag=="v05" else m06
			var seeds: Dictionary=seeds05 if tag=="v05" else seeds06
			var m=script.new()
			seed_into(m,seeds[c[2]],c[2])
			var frames:=[]
			var s0: Dictionary=m.snapshot()
			frames.append({"label":"seed","t":0.,"state":s0,"img":m.render_pose(s0).full})
			var ty:=500.
			var time:=0.
			var n_stop: int=c[3] if c[3]>0 else 12
			for k in n_stop:
				var dt: float=steps[k%steps.size()]
				time+=dt
				var s: Dictionary=m.advance(dt,ty,0.)
				frames.append({"label":"stop","t":time,"state":s,"img":m.render_pose(s).full})
			if c[3]>0:
				time=0.
				for k in 5:
					var dt: float=steps[k%steps.size()]
					time+=dt
					ty-=SPEED*dt
					var s: Dictionary=m.advance(dt,ty,1.)
					frames.append({"label":"repress","t":time,"state":s,"img":m.render_pose(s).full})
			for k in frames.size():
				var f: Dictionary=frames[k]
				var name: String=PREFIX+"%s-%s-f%02d-%s"%[c[0],tag,k,f.label]+SUFFIX
				var path: String=folder.path_join(name)
				f.img.save_png(path)
				var st: Dictionary=ser(f.state)
				index.append({"case":c[0],"v05Family":c[4],"schedule":c[1],"seedPhase":c[2],"releasedFrames":c[3],"model":tag,"frame":k,"label":f.label,"t":f.t,"file":name,"pngSha256":FileAccess.get_sha256(path),"rgbaSha256":_rgba_sha(f.img),"isStatic":f.img.get_data()==padded.get_data(),"heelHits":[find(f.img,0),find(f.img,1)],"state":st})
	var failed:=checks.filter(func(x):return not x.pass).size()
	var report:={"tool":"NORTH v06 native transition frames + steady identity gate","v05ModelSha256":sha05,"v06ModelSha256":sha06,"toolSha256":FileAccess.get_sha256(get_script().resource_path),"staticPngSha256":FileAccess.get_sha256(STATIC_PNG),"scale":"native 80x128 cel; at the game's 0.5 sprite scale on the 640x360 canvas in the 1280x720 window one texel is one screen pixel","checks":checks,"passed":checks.size()-failed,"failed":failed,"frames":index,"artApproved":false,"motionApproved":false}
	var f:=FileAccess.open(args[1],FileAccess.WRITE)
	f.store_string(JSON.stringify(report," ")+"\n")
	f.close()
	for x in checks:print(("PASS " if x.pass else "FAIL ")+x.key)
	print("NORTH V06 NATIVE frames=",index.size()," checks ",checks.size()-failed,"/",checks.size())
	if failed==0:print("NORTH_V06_NATIVE_OK")
	quit(1 if failed>0 else 0)
func _rgba_sha(image: Image) -> String:
	var h:=HashingContext.new()
	h.start(HashingContext.HASH_SHA256)
	h.update(image.get_data())
	return h.finish().hex_encode()
