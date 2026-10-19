extends SceneTree
# NORTH v06 transition diagnostic (test only, not a gate). Replays selected release / re-press cases of the
# frozen v05 matrix procedure (same 280 Hz seeds, same schedules, same raster heel-template search) on any
# model and prints one line per frame: mode, q, body, live, per-foot state and raster hits. Used to locate
# the cause of the v05 failure families before the single v06 change, and to confirm the targeted families
# on the v06 model before the full frozen matrix run.
# Usage: -s <this> -- <model res path> <report path> [case ...]   case = schedule:phase:releaseCount (0 = stop only)
const STATIC_PNG := "res://assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot_unapproved-v01_20261018-090713-6ed8d8dd.png"
const CORE := [[26,39],[42,54]]
const SOLE := [103,102]
const SPEED := 140.
var templates:=[]
var seeds:={}
var original: Image
var model: GDScript
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
func seed_into(m: RefCounted,phase: int) -> void:
	var s: Dictionary=seeds[phase]
	m.physical_y=500.;m.render_y=500.;m.origin_y=500.;m.q0=float(phase);m.q=float(phase);m.mode="run";m.age=1.
	m.feet=m._copy_feet(s.feet)
	m.start_feet=m._copy_feet(s.feet)
	for i in 2:m.start_feet[i].phase=-2.
	m.last_body=s.body;m.start_body=s.body;m.live=1.;m.start_live=1.
func foot_txt(f: Dictionary) -> String:
	return "%s d%.2f l%.2f r%.2f b%.2f ph%.1f"%["G" if f.ground else "a",f.depth,f.lift,f.reveal,f.bend,f.phase]
func rows86(img: Image) -> int:
	var n:=0
	for y in range(86,128):
		for x in 80:
			if img.get_pixel(x,y)!=original.get_pixel(x,y):n+=1
	return n
func line(tag: String,t: float,s: Dictionary,img: Image) -> String:
	return "%s t=%.4f %s q=%.0f body=(%d,%d) live=%.2f | L0 %s hits%s decl%d | L1 %s hits%s decl%d | diff86=%d static=%s"%[tag,t,s.mode,s.q,s.body.x,s.body.y,s.live,foot_txt(s.feet[0]),str(find(img,0)),SOLE[0]-roundi(s.feet[0].depth)-roundi(s.feet[0].lift),foot_txt(s.feet[1]),str(find(img,1)),SOLE[1]-roundi(s.feet[1].depth)-roundi(s.feet[1].lift),rows86(img),str(img.get_data()==original.get_data())]
func run() -> void:
	var args:=OS.get_cmdline_user_args()
	model=load(args[0])
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
	original=model.new().original
	var sm=model.new()
	var sy:=500.
	sm.physical_y=sy;sm.render_y=sy
	for i in 420:
		sy-=.5
		var st: Dictionary=sm.advance(1./280.,sy,1.)
		if i>=256:seeds[int(st.q)]=st
	var schedules: Dictionary={"30":[1./30.],"60":[1./60.],"mixed":[1./24.,1./60.,1./48.,1./30.]}
	var out:=PackedStringArray()
	out.append("model %s sha256 %s"%[args[0],FileAccess.get_sha256(args[0])])
	for spec: String in args.slice(2):
		var p:=spec.split(":")
		var steps: Array=schedules[p[0]]
		var phase:=int(p[1])
		var rc:=int(p[2])
		out.append("== case %s"%spec)
		var m=model.new()
		seed_into(m,phase)
		var s0: Dictionary=m.snapshot()
		out.append(line("seed",0.,s0,m.render_pose(s0).full))
		var ty:=500.
		var time:=0.
		var n_release:=rc if rc>0 else 40
		for t in n_release:
			var dt: float=steps[t%steps.size()]
			time+=dt
			var s: Dictionary=m.advance(dt,ty,0.)
			out.append(line("stop",time,s,m.render_pose(s).full))
			if rc==0 and s.mode=="idle":break
		if rc>0:
			time=0.
			for t in 16:
				var dt: float=steps[t%steps.size()]
				time+=dt
				ty-=SPEED*dt
				var s: Dictionary=m.advance(dt,ty,1.)
				out.append(line("run",time,s,m.render_pose(s).full))
	var text:="\n".join(out)+"\n"
	var f:=FileAccess.open(args[1],FileAccess.WRITE)
	f.store_string(text)
	f.close()
	print(text)
	print("NORTH_V06_DIAG_DONE")
	quit(0)
