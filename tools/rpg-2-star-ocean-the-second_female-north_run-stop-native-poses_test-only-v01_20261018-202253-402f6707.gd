extends SceneTree
# NORTH v01 prototype pose bake + small endpoint checks. Every PNG is a real advance() state of the
# model rendered by its own render_pose(). Run: 280 Hz ticks of 1 source px (0.5 world px) north;
# states after tick 256 cover all 128 phases. Stop: a 60 Hz steady run released at the given phase
# and advanced at 1/60 s until idle. Usage: -s <this> -- <new folder> <stamp-id> [release phase]
const MODEL_PATH := "res://../tools/rpg-2-star-ocean-the-second_female-north_run-stop-source_unapproved-v01_20261018-202253-402f6707.gd"
const STATIC_PNG := "res://assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot_unapproved-v01_20261018-090713-6ed8d8dd.png"
const POSES := {"contact":0,"passing":20,"flight":50}
func _initialize() -> void:call_deferred("_run")
func _rgba_sha(image: Image) -> String:
	var h:=HashingContext.new()
	h.start(HashingContext.HASH_SHA256)
	h.update(image.get_data())
	return h.finish().hex_encode()
func _diff(a: Image,b: Image) -> int:
	var n:=0
	for y in 112:
		for x in 80:
			if a.get_pixel(x,y)!=b.get_pixel(x,y):n+=1
	return n
func _serialize(value: Dictionary) -> Dictionary:
	var state:=value.duplicate(true)
	state.body=[state.body.x,state.body.y]
	return state
func _alpha_binary(image: Image) -> bool:
	for y in 112:
		for x in 80:
			var a:=image.get_pixel(x,y).a8
			if a!=0 and a!=255:return false
	return true
func _palette(image: Image) -> Dictionary:
	var out:={}
	for y in 112:
		for x in 80:
			var c:=image.get_pixel(x,y)
			if c.a8>0:out[c.to_html(false)]=true
	return out
func _boot_bottom(image: Image,leg: int) -> int:
	# Lowest opaque row in that leg's columns below the coat (rows >= 75).
	var best:=-1
	for y in range(75,112):
		for x in 80:
			if (x<41 if leg==0 else x>=41) and image.get_pixel(x,y).a8>0:best=y
	return best
func _boot_cols(image: Image,leg: int,bottom: int) -> Array:
	# Union of that leg's opaque columns over the lowest 9 boot rows (heel, sole and lower shaft).
	var lo:=99
	var hi:=-1
	for row in range(bottom-8,bottom+1):
		for x in 80:
			if (x<41 if leg==0 else x>=41) and image.get_pixel(x,row).a8>0:lo=mini(lo,x);hi=maxi(hi,x)
	return [lo,hi]
func _run() -> void:
	var args:=OS.get_cmdline_user_args()
	var folder: String=args[0]
	var tag: String=args[1]
	var release_q:=int(args[2]) if args.size()>2 else 50
	DirAccess.make_dir_recursive_absolute(folder)
	var model: RefCounted=load(MODEL_PATH).new()
	var static_png:=Image.load_from_file(ProjectSettings.globalize_path(STATIC_PNG))
	static_png.convert(Image.FORMAT_RGBA8)
	var checks:=[]
	var static_palette:=_palette(static_png)
	checks.append({"key":"layers-compose-to-static-png","pass":_diff(model.original,static_png)==0})
	# Rest-parameter run render must be the identity (no pop when a stop reaches rest).
	var rest:={"mode":"stop","q":0.,"feet":[model._home(),model._home()],"body":Vector2.ZERO,"live":0.}
	var rest_image: Image=model.render_pose(rest).full
	checks.append({"key":"rest-pose-render-identity","pass":_diff(rest_image,static_png)==0,"diff":_diff(rest_image,static_png)})
	if _diff(rest_image,static_png)!=0:rest_image.save_png(folder.path_join("rpg-2-star-ocean-the-second_female-north-run-rest-render-diagnostic_unapproved-v01_%s.png"%tag))
	# Steady 280 Hz run.
	var y:=1000.
	model.physical_y=y
	model.render_y=y
	var by_q:={}
	for tick in 400:
		y-=.5
		var state: Dictionary=model.advance(1./280.,y,1.)
		if tick>=256:by_q[int(state.q)]=state.duplicate(true)
	checks.append({"key":"all-128-phases","pass":by_q.size()==128})
	var records:={}
	var all_alpha:=true
	var extra_colours:={}
	var stance_ok:=true
	var stance_notes:=[]
	var flight_both_air:=true
	var col_ref:={}
	var prev_body_y:=-999
	var max_body_step:=0
	for qq in range(128):
		var st: Dictionary=by_q[qq]
		var img: Image=model.render_pose(st).full
		if not _alpha_binary(img):all_alpha=false
		for c in _palette(img):
			if not static_palette.has(c):extra_colours[c]=true
		for leg in 2:
			var f: float=fposmod(qq+leg*64.,128.)
			var bottom:=_boot_bottom(img,leg)
			if f<38.:
				# Stance: boot bottom on the floor band, lateral columns fixed through stance.
				# Declared contract: stance sole row within the static sole row -2..+2 (ahead..behind).
				if bottom<model.SOLE[leg]-2 or bottom>model.SOLE[leg]+2:stance_ok=false;stance_notes.append([qq,leg,bottom])
				var cols:=_boot_cols(img,leg,bottom)
				if not col_ref.has(leg):col_ref[leg]=cols
				elif col_ref[leg]!=cols:stance_ok=false;stance_notes.append([qq,leg,"cols",cols,col_ref[leg]])
		var s0: float=fposmod(qq,128.)
		if s0>=44. and s0<60.:
			if st.feet[0].ground or st.feet[1].ground:flight_both_air=false
		if prev_body_y!=-999:max_body_step=maxi(max_body_step,absi(roundi(st.body.y)-prev_body_y))
		prev_body_y=roundi(st.body.y)
	checks.append({"key":"binary-alpha-128-phases","pass":all_alpha})
	checks.append({"key":"palette-subset-or-declared-sole","pass":extra_colours.keys().all(func(c):return c in ["714730","41302b","201c20","302526","0a0a0e"]),"extraColours":extra_colours.keys()})
	checks.append({"key":"stance-floor-band-and-lateral-lock","pass":stance_ok,"notes":stance_notes.slice(0,8)})
	checks.append({"key":"flight-q44-59-both-airborne","pass":flight_both_air})
	checks.append({"key":"steady-torso-step-le-1px-per-phase","pass":max_body_step<=1,"max":max_body_step})
	for pose: String in POSES:
		var st: Dictionary=by_q[POSES[pose]]
		var img: Image=model.render_pose(st).full
		var name:="rpg-2-star-ocean-the-second_female-north-run-%s-native-80x112_unapproved-v01_%s.png"%[pose,tag]
		img.save_png(folder.path_join(name))
		records[pose]={"file":name,"sha256":FileAccess.get_sha256(folder.path_join(name)),"state":_serialize(st)}
	# Start from idle at 60 Hz: first moving frame keeps one foot grounded and the torso within 1 px.
	var m2: RefCounted=load(MODEL_PATH).new()
	y=1000.
	m2.physical_y=y
	m2.render_y=y
	var first: Dictionary=m2.advance(1./60.,y,0.)
	checks.append({"key":"idle-before-press-is-static","pass":_diff(m2.render_pose(first).full,static_png)==0})
	y-=140./60.
	var s1: Dictionary=m2.advance(1./60.,y,1.)
	checks.append({"key":"start-first-frame-run-one-foot-grounded","pass":s1.mode=="run" and (s1.feet[0].ground or s1.feet[1].ground)})
	checks.append({"key":"start-first-frame-torso-le-1px","pass":absi(roundi(s1.body.y))<=1 and absi(roundi(s1.body.x))<=1,"body":[s1.body.x,s1.body.y]})
	# Steady 60 Hz run until the release phase, then release.
	var guard:=0
	var last_q:=-1.
	var landings:=[]
	var run_time:=0.
	var prev: Dictionary=s1
	while guard<600:
		y-=140./60.
		var st: Dictionary=m2.advance(1./60.,y,1.)
		run_time+=1./60.
		for leg in 2:
			if prev.feet[leg].ground==false and st.feet[leg].ground:landings.append(run_time)
		prev=st
		guard+=1
		if guard>=120 and absf(fposmod(st.q-release_q,128.))<4.7:break
	# Cadence from the mean interval between consecutive landings (window counts are biased).
	var cadence: float=float(landings.size()-1)/(landings[-1]-landings[0]) if landings.size()>=3 else 0.
	checks.append({"key":"cadence-4.0-4.5-steps-per-s-at-140","pass":cadence>=4.0 and cadence<=4.5,"stepsPerSecond":cadence,"landings":landings.size()})
	var frames:=[]
	var states:=[]
	var released_q: float=prev.q
	for k in 40:
		var st: Dictionary=m2.advance(1./60.,y,0.)
		frames.append(m2.render_pose(st).full)
		states.append(st.duplicate(true))
		if st.mode=="idle":break
	var final_index:=-1
	for k in frames.size():
		if _diff(frames[k],static_png)==0:
			final_index=k
			break
	var settled:=final_index>=0
	for k in range(maxi(0,final_index),frames.size()):
		if _diff(frames[k],static_png)!=0:settled=false
	checks.append({"key":"stop-reaches-exact-static","pass":settled,"finalFrameIndex":final_index,"seconds":float(final_index+1)/60.})
	checks.append({"key":"stop-settle-le-0.25s","pass":settled and float(final_index+1)/60.<=.25})
	var stop_names:={"penultimate":final_index-2,"last-moving":final_index-1,"final":final_index}
	for pose: String in stop_names:
		var k: int=stop_names[pose]
		if k<0:continue
		var name:="rpg-2-star-ocean-the-second_female-north-run-stop-%s-native-80x112_unapproved-v01_%s.png"%[pose,tag]
		frames[k].save_png(folder.path_join(name))
		records["stop-"+pose]={"file":name,"sha256":FileAccess.get_sha256(folder.path_join(name)),"stopFrameIndex":k,"diffVsStatic":_diff(frames[k],static_png),"state":_serialize(states[k])}
	var report:={"tag":tag,"modelSha256":FileAccess.get_sha256(MODEL_PATH),"bakeSha256":FileAccess.get_sha256(get_script().resource_path),"staticPngSha256":FileAccess.get_sha256(STATIC_PNG),"releasedAtQ":released_q,"poses":records,"checks":checks,"passed":checks.filter(func(c):return c["pass"]).size(),"failed":checks.filter(func(c):return not c["pass"]).size(),"prototypeOnly":true,"artApproved":false,"motionApproved":false}
	var file:=FileAccess.open(folder.path_join("rpg-2-star-ocean-the-second_female-north-run-pose-bake-report_unapproved-v01_%s.json"%tag),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  ")+"\n")
	file.close()
	for c in checks:print(("PASS " if c["pass"] else "FAIL ")+c["key"])
	print("NORTH POSE BAKE passed=",report.passed," failed=",report.failed)
	quit(1 if report.failed>0 else 0)
