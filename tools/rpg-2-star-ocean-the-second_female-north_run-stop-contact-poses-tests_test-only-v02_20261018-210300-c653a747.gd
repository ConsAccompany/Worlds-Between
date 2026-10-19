extends SceneTree
# NORTH v02 source-bound pose bake + small 30/60 Hz contact tests (test only).
# Contact is measured from the rendered raster, not from the model's declared feet: in every frame the
# static heel block of each boot (boots-layer texels, rows sole-3..sole of that leg, taken from the static
# PNG/pxo composite) is searched as an exact RGBA template in the rendered 80x128 cell. Its bottom row is
# the heel cap underside; world Y of that edge = renderY + (row + 1 - 104) * 0.5 (the presenter's pivot
# and scale). Every frame the model calls grounded must contain exactly one exact match, and each
# continuous grounded run (all frames, boundaries included) must keep the edge within 1 world px.
# Usage: -s <this> -- <new folder> <stamp-id> <report path>
const MODEL_PATH := "res://../tools/rpg-2-star-ocean-the-second_female-north_run-stop-source_unapproved-v02_20261018-210300-c653a747.gd"
const V01_PATH := "res://../tools/rpg-2-star-ocean-the-second_female-north_run-stop-source_unapproved-v01_20261018-202253-402f6707.gd"
const STATIC_PNG := "res://assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot_unapproved-v01_20261018-090713-6ed8d8dd.png"
const CORE := [[26,39],[42,54]]
const SOLE := [103,102]
var checks := []
func _initialize() -> void:call_deferred("_run")
func _sha(image: Image) -> String:
	var h:=HashingContext.new()
	h.start(HashingContext.HASH_SHA256)
	h.update(image.get_data())
	return h.finish().hex_encode()
func _check(key: String,ok: bool,detail: Variant=null) -> void:
	var c:={"key":key,"pass":ok}
	if detail!=null:c["detail"]=detail
	checks.append(c)
func _templates(boots: Image) -> Array:
	var out:=[]
	for leg in 2:
		var t:=[]
		for y in range(SOLE[leg]-3,SOLE[leg]+1):
			for x in range(CORE[leg][0],CORE[leg][1]+1):
				var c:=boots.get_pixel(x,y)
				if c.a8>0:t.append([x,y-SOLE[leg],c])
		out.append(t)
	return out
# Exact template matches of a leg's heel block: returns [[bottomRow, dx], ...].
func _find(image: Image,template: Array) -> Array:
	var hits:=[]
	for bottom in range(60,image.get_height()):
		for dx in range(-2,3):
			var ok:=true
			for t: Array in template:
				var x: int=t[0]+dx
				var y: int=bottom+t[1]
				if y<0 or y>=image.get_height() or image.get_pixel(x,y)!=t[2]:ok=false;break
			if ok:hits.append([bottom,dx])
	return hits
func _alpha_binary(image: Image) -> bool:
	for y in image.get_height():
		for x in image.get_width():
			var a:=image.get_pixel(x,y).a8
			if a!=0 and a!=255:return false
	return true
func _palette(image: Image) -> Dictionary:
	var out:={}
	for y in image.get_height():
		for x in image.get_width():
			var c:=image.get_pixel(x,y)
			if c.a8>0:out[c.to_html(false)]=true
	return out
func _ser(state: Dictionary) -> Dictionary:
	var s:=state.duplicate(true)
	s.body=[s.body.x,s.body.y]
	return s
# One ordinary-input schedule at a fixed rate: idle, run, release, re-press, release.
func _simulate(model: RefCounted,fps: int,start_y: float,templates: Array,original: Image) -> Dictionary:
	model.physical_y=start_y
	model.render_y=roundf(start_y*2.)*.5
	var y:=start_y
	var frames:=[]
	var segments:=[["idle",.10,0],["run",1.20,1],["stop",.40,0],["repress",.60,1],["final-stop",.40,0]]
	var tick:=0
	for seg: Array in segments:
		for f in roundi(seg[1]*fps):
			if seg[2]>0:y-=140./fps
			var state: Dictionary=model.advance(1./fps,y,float(seg[2]))
			var image: Image=model.render_pose(state).full
			var measured:=[]
			for leg in 2:
				var hits:=_find(image,templates[leg])
				measured.append({"hits":hits,"worldY":(state.renderY+(float(hits[0][0])+1.-104.)*.5) if hits.size()==1 else null,"col":hits[0][1] if hits.size()==1 else null})
			frames.append({"tick":tick,"segment":seg[0],"state":state,"measured":measured,"isStatic":image.get_data()==original.get_data(),"image":image})
			tick+=1
	return {"fps":fps,"startY":start_y,"frames":frames}
func _contact_segments(run: Dictionary) -> Array:
	var out:=[]
	for leg in 2:
		var current:=[]
		for fr in run.frames+[null]:
			var grounded: bool=fr!=null and fr.state.mode!="idle" and fr.state.feet[leg].ground
			if grounded:current.append(fr)
			elif current.size()>0:
				var ys:=[]
				var cols:=[]
				var missing:=0
				var declared_mismatch:=0
				for g: Dictionary in current:
					var m: Dictionary=g.measured[leg]
					if m.worldY==null:missing+=1;continue
					ys.append(m.worldY)
					cols.append(m.col)
				var travel: float=(ys.max()-ys.min()) if ys.size()>0 else INF
				var phases:=[]
				for g: Dictionary in current:phases.append(g.state.feet[leg].phase)
				out.append({"leg":leg,"firstTick":current[0].tick,"lastTick":current[-1].tick,"frames":current.size(),"segments":current.map(func(g):return g.segment),"mode":current.map(func(g):return g.state.mode),"stancePhases":phases,"missingMatches":missing,"heelCapWorldY":ys,"heelCapTravelWorldPx":travel,"lateralShiftCols":cols})
				current=[]
	return out
func _run() -> void:
	var args:=OS.get_cmdline_user_args()
	var folder: String=args[0]
	var tag: String=args[1]
	var report_path: String=args[2]
	DirAccess.make_dir_recursive_absolute(folder)
	var model: RefCounted=load(MODEL_PATH).new()
	var static_png:=Image.load_from_file(ProjectSettings.globalize_path(STATIC_PNG))
	static_png.convert(Image.FORMAT_RGBA8)
	var padded:=Image.create(80,128,false,Image.FORMAT_RGBA8)
	padded.blit_rect(static_png,Rect2i(0,0,80,112),Vector2i.ZERO)
	var original: Image=model.original
	var consts: Dictionary=(load(MODEL_PATH) as Script).get_script_constant_map()
	_check("cell-80x128-pivot-40-104",consts.CELL==Vector2i(80,128) and consts.PIVOT==Vector2i(40,104))
	_check("padded-composite-equals-static-png-top-112-rows-bottom-16-transparent",original.get_data()==padded.get_data())
	var templates:=_templates(padded)
	_check("heel-templates-nonempty",templates[0].size()>=20 and templates[1].size()>=20,[templates[0].size(),templates[1].size()])
	var hits_static:=[_find(padded,templates[0]),_find(padded,templates[1])]
	_check("static-heel-template-unique-at-static-sole",hits_static[0]==[[103,0]] and hits_static[1]==[[102,0]],hits_static)
	var rest: Image=model.render_pose({"mode":"run","q":19.,"feet":[model._home(),model._home()],"body":Vector2.ZERO,"live":0.}).full
	_check("rest-parameters-render-exact-static",rest.get_data()==original.get_data())
	var static_palette:=_palette(padded)
	# Steady poses: 280 Hz ticks of exactly one source row (0.5 world px) north.
	var y:=300.
	model.physical_y=y
	model.render_y=y
	var by_q:={}
	for t in 400:
		y-=.5
		var st: Dictionary=model.advance(1./280.,y,1.)
		if t>=128:by_q[int(st.q)]=st
	_check("all-128-phases-reached",by_q.size()==128,by_q.size())
	var alpha_ok:=true
	var palette_ok:=true
	var extra:={}
	var lowest:=0
	for qq: int in by_q:
		var img: Image=model.render_pose(by_q[qq]).full
		alpha_ok=alpha_ok and _alpha_binary(img)
		for c in _palette(img):
			if not static_palette.has(c):palette_ok=false;extra[c]=true
		var used:=img.get_used_rect()
		lowest=maxi(lowest,used.end.y-1)
	_check("all-phases-binary-alpha",alpha_ok)
	_check("all-phases-static-palette-only",palette_ok,extra.keys())
	_check("lowest-opaque-row-inside-128-cell",lowest<=127,lowest)
	# Passing = stance-phase frame where the swing heel is closest in depth to the planted heel.
	var passing_q:=0
	var best:=INF
	for qq in range(0,38):
		var d: float=absf(by_q[qq].feet[1].depth-by_q[qq].feet[0].depth)
		if d<best:best=d;passing_q=qq
	var poses:={"contact":0,"passing":passing_q,"stance-end":37,"peel":42,"flight":52,"kick":58}
	var pose_report:={}
	for name: String in poses:
		var st: Dictionary=by_q[poses[name]]
		var r: Dictionary=model.render_pose(st)
		var img: Image=r.full
		var path:=folder.path_join("rpg-2-star-ocean-the-second_female-north-run-%s-native-80x128_unapproved-v02_%s.png"%[name,tag])
		img.save_png(path)
		pose_report[name]={"q":poses[name],"file":path.get_file(),"sha256":FileAccess.get_sha256(path),"state":_ser(st),"legs":r.legs,"usedRect":[img.get_used_rect().position.x,img.get_used_rect().position.y,img.get_used_rect().size.x,img.get_used_rect().size.y]}
	# 30/60 Hz ordinary-input schedules from three sub-pixel start positions.
	var runs:=[]
	var all_segments:=[]
	for fps in [60,30]:
		for start in [300.,300.25,300.1]:
			var m: RefCounted=load(MODEL_PATH).new()
			var run:=_simulate(m,fps,start,templates,original)
			var segs:=_contact_segments(run)
			for s: Dictionary in segs:
				s["fps"]=fps
				s["startY"]=start
			all_segments.append_array(segs)
			var name:="%dhz-start%s"%[fps,str(start)]
			# Frame-level checks.
			var declared_ok:=true
			var guard_ok:=true
			var prev_body:=0
			for fr: Dictionary in run.frames:
				for leg in 2:
					var m2: Dictionary=fr.measured[leg]
					if fr.state.mode!="idle" and fr.state.feet[leg].ground and m2.worldY!=null:
						var declared: int=SOLE[leg]-roundi(fr.state.feet[leg].depth)-roundi(fr.state.feet[leg].lift)
						if declared!=m2.hits[0][0]:declared_ok=false
				var by: int=roundi(fr.state.body.y)
				if absi(by-prev_body)>ceili(48./fps-0.000000001):guard_ok=false
				prev_body=by
			_check(name+"-declared-sole-row-equals-raster-heel-cap",declared_ok)
			_check(name+"-rendered-torso-step-within-guard",guard_ok)
			for stop_name in ["stop","final-stop"]:
				var seg: Array=run.frames.filter(func(fr):return fr.segment==stop_name)
				var first:=-1
				for k in seg.size():
					if seg[k].isStatic:first=k;break
				_check(name+"-"+stop_name+"-settles-to-exact-static",first>=0 and seg.slice(first).all(func(fr):return fr.isStatic),{"framesToStatic":first+1,"seconds":float(first+1)/fps})
			var idle_ok: bool=run.frames.filter(func(fr):return fr.segment=="idle").all(func(fr):return fr.isStatic)
			_check(name+"-idle-is-exact-static",idle_ok)
			var first_run: Dictionary=run.frames.filter(func(fr):return fr.segment=="run")[0]
			_check(name+"-first-press-frame-runs-not-static",first_run.state.mode=="run" and not first_run.isStatic)
			# Cadence from landings in the first run.
			var landings:=[]
			var rf: Array=run.frames.filter(func(fr):return fr.segment=="run")
			for k in range(1,rf.size()):
				for leg in 2:
					if not rf[k-1].state.feet[leg].ground and rf[k].state.feet[leg].ground:landings.append(rf[k].tick)
			var cadence:=0.
			if landings.size()>=3:cadence=float(landings.size()-1)/(float(landings[-1]-landings[0])/fps)
			_check(name+"-cadence-4.0-4.5",cadence>=4.0 and cadence<=4.5,{"landingTicks":landings,"stepsPerSecond":cadence})
			runs.append({"name":name,"fps":fps,"startY":start,"frames":run.frames.map(func(fr):return {"tick":fr.tick,"segment":fr.segment,"state":_ser(fr.state),"heelCap":fr.measured.map(func(m):return {"matches":m.hits.size(),"worldY":m.worldY,"col":m.col}),"isStatic":fr.isStatic})})
			if fps==60 and start==300.:
				# Settle pose from the first stop: the middle moving frame.
				var seg: Array=run.frames.filter(func(fr):return fr.segment=="stop")
				var moving: Array=seg.filter(func(fr):return not fr.isStatic)
				var mid: Dictionary=moving[moving.size()/2]
				for item in [["settle",mid],["final",seg[-1]]]:
					var path:=folder.path_join("rpg-2-star-ocean-the-second_female-north-run-%s-native-80x128_unapproved-v02_%s.png"%[item[0],tag])
					(item[1].image as Image).save_png(path)
					pose_report[item[0]]={"tick":item[1].tick,"file":path.get_file(),"sha256":FileAccess.get_sha256(path),"state":_ser(item[1].state),"isStatic":item[1].isStatic}
	# Contact segment checks: every grounded frame matched; travel <= 1 world px; steady stances complete.
	var worst:=0.
	var missing_total:=0
	var steady_run_segments:=0
	for s: Dictionary in all_segments:
		worst=maxf(worst,s.heelCapTravelWorldPx)
		missing_total+=s.missingMatches
		var lateral_ok: bool=s.lateralShiftCols.all(func(c):return c==s.lateralShiftCols[0])
		_check("contact-%dhz-start%s-leg%d-ticks%d-%d-heel-cap-travel<=1px"%[s.fps,str(s.startY),s.leg,s.firstTick,s.lastTick],s.missingMatches==0 and s.heelCapTravelWorldPx<=1. and lateral_ok,{"frames":s.frames,"travel":s.heelCapTravelWorldPx,"missing":s.missingMatches})
		var run_only: bool=s.mode.all(func(m):return m=="run")
		if run_only and s.stancePhases.size()>0 and s.stancePhases[0]<9.4 and s.stancePhases[-1]>37.-9.4:steady_run_segments+=1
	_check("no-grounded-frame-without-unique-heel-match",missing_total==0,missing_total)
	_check("full-run-stances-observed-at-both-rates",steady_run_segments>=12,steady_run_segments)
	# v01 baseline on the same raster measure, for comparison only (v01 cell is 80x112).
	var v01: RefCounted=load(V01_PATH).new()
	var v01_templates:=_templates(static_png)
	var v01_run:=_simulate(v01,60,300.,v01_templates,v01.original)
	var v01_segs:=_contact_segments(v01_run)
	var v01_worst:=0.
	for s: Dictionary in v01_segs:
		if s.heelCapTravelWorldPx<INF:v01_worst=maxf(v01_worst,s.heelCapTravelWorldPx)
	var report:={"tool":"NORTH v02 contact poses/tests","prototypeOnly":true,"artApproved":false,"motionApproved":false,"modelSha256":FileAccess.get_sha256(MODEL_PATH),"toolSha256":FileAccess.get_sha256(get_script().resource_path),"staticPngSha256":FileAccess.get_sha256(STATIC_PNG),"v01ModelSha256":FileAccess.get_sha256(V01_PATH),"measure":"Exact RGBA template of each boot's static heel block (rows sole-3..sole, boots layer) searched in every rendered cell; heel cap underside world Y = renderY + (row+1-104)*0.5.","poses":pose_report,"passingQ":passing_q,"contactSegments":all_segments,"worstHeelCapTravelWorldPx":worst,"v01SameMeasure60HzWorstTravelWorldPx":v01_worst,"v01SameMeasureSegments":v01_segs,"runs":runs,"checks":checks,"passed":checks.filter(func(c):return c["pass"]).size(),"failed":checks.filter(func(c):return not c["pass"]).size()}
	var file:=FileAccess.open(report_path,FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  ")+"\n")
	file.close()
	for c in checks:
		if not c["pass"]:print("FAIL ",c["key"]," ",c.get("detail"))
	print("worst heel-cap travel world px v02=",worst," v01 same measure=",v01_worst)
	print("NORTH V02 TESTS passed=",report.passed," failed=",report.failed)
	if report.failed==0:print("NORTH_V02_TESTS_OK")
	quit(1 if report.failed>0 else 0)
