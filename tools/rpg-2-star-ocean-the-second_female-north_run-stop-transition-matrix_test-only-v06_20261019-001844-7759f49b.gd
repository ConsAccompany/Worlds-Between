extends SceneTree
# NORTH v06-bound copy of the frozen v05 full release / re-press matrix (test only). Only the model path,
# its expected hash and the report/print labels differ from v05 e3f72f3f; every check and threshold is v05's.
# NORTH v05 full release / re-press matrix (test only). Every integer source phase 0..127 is the start of a
# release (stop) and of three re-presses (after 1, 2 and 3 released frames), at 30 Hz, 60 Hz and a mixed
# 1/24, 1/60, 1/48, 1/30 s schedule, plus a 200-tick mixed-dt steady run. Seeds are the real 280 Hz
# advance() states of the locked v05 model (the native PXO cels); each seed is checked against expectations
# written here independently of the model (stance law, weight shift, torso bob table) and its 280 Hz
# continuation must equal the real run's next state.
# Contact is raster-measured exactly as in the v04/v05 tests: the static PNG heel block (rows sole-3..sole)
# of each boot is searched as an exact RGBA template in the rendered cell. During a stop render_y is fixed,
# so the same cell row is the same world point. Thresholds (never widened): visual settle to the exact
# static <= 250 ms at 30/60 Hz and <= 300 ms mixed; every foot airborne at release reaches ground contact
# <= 100 ms; re-press support <= 100 ms; heel-cap world travel <= 1 world px over every grounded interval.
# Usage: -s <this> -- <new absolute report path>
const MODEL_PATH := "res://../tools/rpg-2-star-ocean-the-second_female-north_run-stop-source_unapproved-v06_20261019-001844-7759f49b.gd"
const EXPECTED_MODEL_SHA256 := "1f25c2aac2837d14a21eb2c8ddd60f93c19f2570cd486716003394e6f7789562"
const STATIC_PNG := "res://assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot_unapproved-v01_20261018-090713-6ed8d8dd.png"
const MODEL := preload(MODEL_PATH)
const CORE := [[26,39],[42,54]]
const SOLE := [103,102]
# Independent expectations (literal values from the root-accepted v04 contract, not read from the model).
const X_STANCE := 20
const X_MID := 12
const X_BOB := [[0.,2.],[6.,3.],[13.,3.],[19.,1.],[26.,0.],[34.,-1.],[46.,-1.],[56.,0.],[61.,1.],[64.,2.]]
const SPEED := 140.
const LIMIT := {"30":.250001,"60":.250001,"mixed":.300001}
var checks:=[]
var failed_n:=0
var seeds:={}
var seed_tick:={}
var templates:=[]
var original: Image
var static_padded: Image
func check(key: String,ok: bool,detail: Variant=null) -> void:
	var c:={"key":key,"pass":ok}
	if not ok:
		c["detail"]=detail
		failed_n+=1
	checks.append(c)
func _initialize() -> void:call_deferred("run")
func ser(state: Dictionary) -> Dictionary:
	var s:=state.duplicate(true)
	s.body=[s.body.x,s.body.y]
	return s
func x_bob(p: float) -> float:
	var k:=0
	while k<X_BOB.size()-2 and p>X_BOB[k+1][0]:k+=1
	var t: float=(p-X_BOB[k][0])/(X_BOB[k+1][0]-X_BOB[k][0])
	t=clampf(t,0.,1.)
	return lerpf(X_BOB[k][1],X_BOB[k+1][1],t*t*(3.-2.*t))
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
# Raster lift of a foot (rows above its world ground point) is not observable in a back view (depth and lift
# both move the heel up the cell), so the model's declared lift is used only after the raster heel row is
# verified to equal sole - round(depth) - round(lift).
func declared_row(foot: Dictionary,leg: int) -> int:return SOLE[leg]-roundi(foot.depth)-roundi(foot.lift)
func rows_equal_static(image: Image,y0: int) -> bool:
	for y in range(y0,128):
		for x in 80:
			if image.get_pixel(x,y)!=original.get_pixel(x,y):return false
	return true
func run() -> void:
	var started_usec:=Time.get_ticks_usec()
	var hash_before:=FileAccess.get_sha256(MODEL_PATH)
	if hash_before!=EXPECTED_MODEL_SHA256:
		push_error("locked v06 model hash changed")
		quit(2);return
	var png:=Image.load_from_file(ProjectSettings.globalize_path(STATIC_PNG))
	png.convert(Image.FORMAT_RGBA8)
	static_padded=Image.create(80,128,false,Image.FORMAT_RGBA8)
	static_padded.blit_rect(png,Rect2i(0,0,80,112),Vector2i.ZERO)
	for leg in 2:
		var t:=[]
		for y in range(SOLE[leg]-3,SOLE[leg]+1):
			for x in range(CORE[leg][0],CORE[leg][1]+1):
				var c:=static_padded.get_pixel(x,y)
				if c.a8>0:t.append([x,y-SOLE[leg],c])
		templates.append(t)
	var probe:=MODEL.new()
	original=probe.original
	check("model-static-composite-equals-north-static-png",original.get_data()==static_padded.get_data())
	check("static-heel-templates-unique-at-static-soles",find(static_padded,0)==[[103,0]] and find(static_padded,1)==[[102,0]])
	# Real 280 Hz steady run: one advance() state per phase (the native PXO cels).
	var sm:=MODEL.new()
	var sy:=500.
	sm.physical_y=sy;sm.render_y=sy
	var ticks:=[]
	for i in 420:
		sy-=.5
		var st: Dictionary=sm.advance(1./280.,sy,1.)
		if i>=256:
			ticks.append(st)
			seeds[int(st.q)]=st
			seed_tick[int(st.q)]=ticks.size()-1
	for phase in 128:
		var ok: bool=seeds.has(phase)
		var why:=""
		if ok:
			var s: Dictionary=seeds[phase]
			ok=s.mode=="run" and s.age>=.12 and s.live==1.
			if not ok:why="mode/age/live"
			for i in 2:
				var p: int=(phase+64*i)%128
				var f: Dictionary=s.feet[i]
				if p<X_STANCE:
					if not (f.ground and f.depth==float(X_MID-p) and f.lift==0. and f.reveal==0.):ok=false;why="stance law leg%d"%i
				else:
					if f.ground or (roundi(f.lift)<1 and roundi(5.*f.reveal)<1):ok=false;why="swing visibly airborne leg%d"%i
			var ex:=Vector2(roundf(-cos((float(phase)-10.)*TAU/128.)),roundf(x_bob(float(phase%64))))
			if s.body!=ex:ok=false;why="body %s expected %s"%[str(s.body),str(ex)]
			# 280 Hz continuation of the seeded model equals the real run's next state.
			var k: int=seed_tick[phase]
			if ok and k>=0 and k+1<ticks.size():
				var m:=MODEL.new()
				seed_into(m,phase)
				var nxt: Dictionary=m.advance(1./280.,499.5,1.)
				var real: Dictionary=ticks[k+1].duplicate(true)
				for key in ["physicalY","renderY","age"]:
					nxt.erase(key);real.erase(key)
				if JSON.stringify(ser(nxt))!=JSON.stringify(ser(real)):ok=false;why="continuation differs"
		check("seed-real-advance-state-%d"%phase,ok,why)
	var schedules: Dictionary={"30":[1./30.],"60":[1./60.],"mixed":[1./24.,1./60.,1./48.,1./30.]}
	var summary:={}
	for schedule: String in schedules:
		var steps: Array=schedules[schedule]
		var settle_times:=[]
		var land_times:=[]
		var support_times:=[]
		var last_step_diffs:=[]
		# Steady run under this schedule: raster contact on every grounded frame, <= 1 world px per interval.
		var rm:=MODEL.new()
		var ry:=500.
		rm.physical_y=ry;rm.render_y=ry
		var open:=[[],[]]
		for t in 200:
			var dt: float=steps[t%steps.size()]
			ry-=SPEED*dt
			var s: Dictionary=rm.advance(dt,ry,1.)
			var img: Image=rm.render_pose(s).full
			for i in 2:
				if s.feet[i].ground:
					var h:=find(img,i)
					var row_ok: bool=h.size()==1 and h[0][0]==declared_row(s.feet[i],i) and h[0][1]==0
					check(schedule+"-run-contact-raster-%d-%d"%[t,i],row_ok,{"hits":h,"declared":declared_row(s.feet[i],i)})
					if h.size()==1:open[i].append(s.renderY+(float(h[0][0])+1.-104.)*.5)
				elif open[i].size()>0:
					check(schedule+"-run-contact-travel-end%d-%d"%[t,i],open[i].max()-open[i].min()<=1.,open[i])
					open[i]=[]
		for phase in 128:
			# ---------------- release (stop) ----------------
			var base:=MODEL.new()
			seed_into(base,phase)
			var s0: Dictionary=base.snapshot()
			var img0: Image=base.render_pose(s0).full
			var planted_row:=[-1,-1]
			for i in 2:
				if s0.feet[i].ground:
					planted_row[i]=declared_row(s0.feet[i],i)
					check(schedule+"-release-contact-raster-%d-%d"%[phase,i],find(img0,i)==[[planted_row[i],0]],find(img0,i))
			var elapsed:=0.
			var landed:=[0. if s0.feet[0].ground else -1.,0. if s0.feet[1].ground else -1.]
			var settled:=-1.
			var static_since:=-1
			var frames:=[]
			var off_episodes:=[0 if s0.feet[0].ground else 1,0 if s0.feet[1].ground else 1]
			var was_off:=[not s0.feet[0].ground,not s0.feet[1].ground]
			var left_plant:=[false,false]
			var idle_seen:=-1
			for t in 40:
				var dt: float=steps[t%steps.size()]
				elapsed+=dt
				var s: Dictionary=base.advance(dt,500.,0.)
				var img: Image=base.render_pose(s).full
				check(schedule+"-physical-stop-%d-%d"%[phase,t],s.physicalY==500. and s.renderY==500. and s.mode!="run",[s.physicalY,s.renderY,s.mode])
				var is_static: bool=img.get_data()==original.get_data()
				frames.append({"t":elapsed,"img":img,"static":is_static,"state":s})
				if is_static and static_since<0:static_since=t
				if not is_static:static_since=-1
				for i in 2:
					var h:=find(img,i)
					var home: bool=h==[[SOLE[i],0]]
					var planted: bool=planted_row[i]>=0 and h==[[planted_row[i],0]] and not left_plant[i]
					var f: Dictionary=s.feet[i]
					if s.mode!="idle" and f.ground:
						# Planted foot: exact same cell row = same world point (0 travel) while the model grounds it.
						check(schedule+"-stop-planted-world-contact-%d-%d-%d"%[phase,t,i],planted or home,{"hits":h,"planted":planted_row[i]})
					var contact: bool=home or (planted and (s.mode=="idle" or f.ground))
					if not contact:
						if planted_row[i]>=0:left_plant[i]=true
						# Off the ground: declared airborne and drawn where declared, at least 1 row up or sole showing.
						var vis: bool=s.mode!="idle" and not f.ground and (roundi(f.lift)>=1 or roundi(5.*f.reveal)>=1)
						if h.size()==1:vis=vis and h[0][0]==declared_row(f,i)
						check(schedule+"-stop-airborne-visible-%d-%d-%d"%[phase,t,i],vis,{"hits":h,"foot":f})
						if not was_off[i]:off_episodes[i]+=1
					elif landed[i]<0.:
						landed[i]=elapsed
					was_off[i]=not contact
				if s.mode=="idle" and idle_seen<0:idle_seen=t
				if idle_seen>=0 and t>=idle_seen+2:break
			# Visual settle: first sample from which every later sample (through idle + 2) is the exact static.
			if static_since>=0:settled=frames[static_since].t
			settle_times.append(settled)
			check(schedule+"-settle-deadline-%d"%phase,settled>0. and settled<=LIMIT[schedule],settled)
			check(schedule+"-idle-reached-and-exact-static-%d"%phase,idle_seen>=0 and frames[-1].img.get_data()==static_padded.get_data())
			for i in 2:
				land_times.append(landed[i])
				check(schedule+"-raised-foot-deadline-%d-%d"%[phase,i],landed[i]>=0. and landed[i]<=.100001,landed[i])
				check(schedule+"-stop-single-step-no-relift-%d-%d"%[phase,i],off_episodes[i]<=1,off_episodes[i])
			# No late material pop: the last two moving frames have legs/boots rows (>= 86) exactly static.
			var moving:=frames.filter(func(f):return not f.static)
			var tail:=moving.slice(maxi(0,moving.size()-2))
			var tail_detail:=tail.map(func(f):return {"t":f.t,"body":[f.state.body.x,f.state.body.y],"feetHome":f.state.feet.all(func(ft):return ft.depth==0. and ft.lift==0. and ft.reveal==0.),"heelBlocksAtStaticRows":find(f.img,0)==[[SOLE[0],0]] and find(f.img,1)==[[SOLE[1],0]]})
			check(schedule+"-no-late-leg-material-pop-%d"%phase,tail.all(func(f):return rows_equal_static(f.img,86)),tail_detail)
			if moving.size()>0:
				var n:=0
				var a: Image=moving[-1].img
				for y in 128:
					for x in 80:
						if a.get_pixel(x,y)!=original.get_pixel(x,y):n+=1
				last_step_diffs.append(n)
			# ---------------- re-press after 1/2/3 released frames ----------------
			for release_count in [1,2,3]:
				var r:=MODEL.new()
				seed_into(r,phase)
				var ty:=500.
				for t in release_count:r.advance(steps[t%steps.size()],ty,0.)
				var pre: Dictionary=r.snapshot()
				var pre_img: Image=r.render_pose(pre).full
				var pre_contact:=[false,false]
				for i in 2:pre_contact[i]=pre.feet[i].ground and find(pre_img,i)==[[declared_row(pre.feet[i],i),0]]
				var time:=0.
				var support:=-1.
				var lifts:=[[roundi(pre.feet[0].lift)],[roundi(pre.feet[1].lift)]]
				var grounded_since:=[-1,-1]
				var contact_y:=[[],[]]
				for i in 2:
					if pre_contact[i]:contact_y[i].append(500.+(float(declared_row(pre.feet[i],i))+1.-104.)*.5)
				var prev_contact:=pre_contact.duplicate()
				for t in 16:
					var dt: float=steps[t%steps.size()]
					time+=dt
					ty-=SPEED*dt
					var s: Dictionary=r.advance(dt,ty,1.)
					var img: Image=r.render_pose(s).full
					if t==0:
						check(schedule+"-repress-first-frame-runs-%d-%d"%[phase,release_count],s.mode=="run" and absf(s.physicalY-(500.-SPEED*dt))<.000001 and img.get_data()!=original.get_data())
					var now_contact:=[false,false]
					for i in 2:
						var f: Dictionary=s.feet[i]
						var h:=find(img,i)
						if f.ground:
							var ok: bool=h.size()==1 and h[0][0]==declared_row(f,i) and h[0][1]==0
							check(schedule+"-repress-contact-raster-%d-%d-%d-%d"%[phase,release_count,t,i],ok,h)
							now_contact[i]=ok
							if ok:contact_y[i].append(s.renderY+(float(h[0][0])+1.-104.)*.5)
							if grounded_since[i]<0:grounded_since[i]=t
						else:
							var vis: bool=roundi(f.lift)>=1 or roundi(5.*f.reveal)>=1
							if h.size()==1:vis=vis and h[0][0]==declared_row(f,i)
							check(schedule+"-repress-airborne-visible-%d-%d-%d-%d"%[phase,release_count,t,i],vis,{"hits":h,"foot":f})
							if contact_y[i].size()>0:
								check(schedule+"-repress-world-contact-%d-%d-%d-%d"%[phase,release_count,t,i],contact_y[i].max()-contact_y[i].min()<=1.,contact_y[i])
								contact_y[i]=[]
							if grounded_since[i]<0:lifts[i].append(roundi(f.lift))
					if (now_contact[0] or now_contact[1]) and support<0.:support=time
					# No hop: both feet must not leave raster contact on the same frame.
					check(schedule+"-repress-no-double-lift-%d-%d-%d"%[phase,release_count,t],not (prev_contact[0] and prev_contact[1] and not now_contact[0] and not now_contact[1]))
					prev_contact=now_contact
				for i in 2:
					if contact_y[i].size()>0:check(schedule+"-repress-world-contact-end-%d-%d-%d"%[phase,release_count,i],contact_y[i].max()-contact_y[i].min()<=1.,contact_y[i])
					# Single rise per foot before its first contact: no rise after a fall (no double re-press rise).
					var seq: Array=lifts[i]
					var fell:=false
					var rerise:=false
					for k in range(1,seq.size()):
						if seq[k]<seq[k-1]:fell=true
						elif seq[k]>seq[k-1] and fell:rerise=true
					check(schedule+"-repress-no-double-rise-%d-%d-%d"%[phase,release_count,i],not rerise,seq)
				support_times.append(support)
				check(schedule+"-repress-support-deadline-%d-%d"%[phase,release_count],support>=0. and support<=.100001,support)
		var valid_settle:=settle_times.filter(func(v):return v>0.)
		var valid_land:=land_times.filter(func(v):return v>=0.)
		var valid_support:=support_times.filter(func(v):return v>=0.)
		summary[schedule]={"settleMaxSeconds":valid_settle.max() if valid_settle.size()>0 else null,"settleMinSeconds":valid_settle.min() if valid_settle.size()>0 else null,"settleMissing":settle_times.size()-valid_settle.size(),"landingMaxSeconds":valid_land.max() if valid_land.size()>0 else null,"landingOver100ms":land_times.filter(func(v):return v>.100001).size(),"supportMaxSeconds":valid_support.max() if valid_support.size()>0 else null,"supportOver100ms":support_times.filter(func(v):return v>.100001 or v<0.).size(),"lastMovingFrameDiffTexelsMax":last_step_diffs.max() if last_step_diffs.size()>0 else 0}
	var hash_after:=FileAccess.get_sha256(MODEL_PATH)
	var fails:=checks.filter(func(c):return not c.pass)
	var by_family:={}
	for c in fails:
		# Family = key without its trailing numeric indices (schedule prefix 30/60/mixed kept).
		var parts: PackedStringArray=(c.key as String).split("-")
		while parts.size()>1 and parts[-1].is_valid_int():parts.remove_at(parts.size()-1)
		var key_family:="-".join(parts)
		by_family[key_family]=by_family.get(key_family,0)+1
	var report:={"tool":"NORTH v06 release/re-press transition matrix (v05 checks, v06 model)","checks":checks,"passed":checks.size()-failed_n,"failed":failed_n,"failuresByFamily":by_family,"summary":summary,
		"modelSha256Before":hash_before,"modelSha256After":hash_after,"invalidated":hash_before!=hash_after,"checkerSha256":FileAccess.get_sha256(get_script().resource_path),"staticPngSha256":FileAccess.get_sha256(STATIC_PNG),
		"thresholds":{"settleSeconds":LIMIT,"raisedFootSeconds":.100001,"repressSupportSeconds":.100001,"contactTravelWorldPx":1.},
		"seedSource":"real 280 Hz advance() states (native PXO cels), checked against literal stance/weight-shift/bob expectations and their own 280 Hz continuation",
		"durationSeconds":float(Time.get_ticks_usec()-started_usec)/1000000.,"artApproved":false,"motionApproved":false}
	var f:=FileAccess.open(OS.get_cmdline_user_args()[0],FileAccess.WRITE)
	f.store_string(JSON.stringify(report," ")+"\n")
	f.close()
	print("NORTH V06 MATRIX ",checks.size()-failed_n,"/",checks.size()," failed ",failed_n)
	print("families ",by_family)
	print("summary ",summary)
	for c in fails.slice(0,10):print(JSON.stringify(c).left(400))
	print("NORTH_V06_MATRIX_DONE")
	quit(1 if failed_n>0 else 0)
