extends SceneTree
# NORTH v06 native bake (v05 bake tool re-bound to the frozen v06 model; only model path, hash, tag and labels differ).
# NORTH v05 native bake (EAST v03 bake conventions, 80x128 NORTH cell). Every cel is a real advance() state
# of the locked v05 model rendered by its own render_pose(); no approximation helper.
# Run: 420 ticks at 1/280 s, -0.5 world px (north) each (= 1 source row = 1 phase); states after tick 256
# give all 128 phases. Stop: for every phase the same 280 Hz run is released at that phase and advanced at
# 1/60 s with the world position held (physical stop) until idle; the phase whose settle is the worst case
# (largest final step, then latest last-moving frame, then largest last-moving diff) is the representative
# stop. Per-role RGBA cells are written next to each full PNG for the PXO/ORA packager.
# Usage: -s <this> -- <new temp folder>
const MODEL_PATH := "res://../tools/rpg-2-star-ocean-the-second_female-north_run-stop-source_unapproved-v06_20261019-001844-7759f49b.gd"
const EXPECTED_MODEL_SHA256 := "1f25c2aac2837d14a21eb2c8ddd60f93c19f2570cd486716003394e6f7789562"
const TAG := "v06_20261019-004238-ad92c263"
func _initialize() -> void:call_deferred("_run")
func _serialize(value: Dictionary) -> Dictionary:
	var state:=value.duplicate(true)
	state.body=[state.body.x,state.body.y]
	return state
func _rgba_sha(image: Image) -> String:
	var h:=HashingContext.new()
	h.start(HashingContext.HASH_SHA256)
	h.update(image.get_data())
	return h.finish().hex_encode()
func _diff(a: Image,b: Image) -> int:
	var n:=0
	for y in 128:
		for x in 80:
			if a.get_pixel(x,y)!=b.get_pixel(x,y):n+=1
	return n
func _save(folder: String,kind: String,index: int,state: Dictionary,model: RefCounted) -> Dictionary:
	var data: Dictionary=model.render_pose(state)
	var tag:="fn-%s-%03d"%[kind,index]
	var full_name:=tag+".png"
	data.full.save_png(folder.path_join(full_name))
	var roles:={}
	for role: String in model.layers:
		var filename:=tag+"-"+role+".rgba"
		var file:=FileAccess.open(folder.path_join(filename),FileAccess.WRITE)
		file.store_buffer((data.roles[role] as Image).get_data())
		file.close()
		roles[role]={"file":filename,"sha256":FileAccess.get_sha256(folder.path_join(filename))}
	return {"kind":kind,"index":index,"state":_serialize(state),"full":{"file":full_name,"sha256":FileAccess.get_sha256(folder.path_join(full_name)),"rgbaSha256":_rgba_sha(data.full)},"roles":roles}
func _run_280(model: RefCounted,stop_at_phase: int) -> Dictionary:
	var y:=500.
	model.physical_y=y
	model.render_y=y
	var poses:={}
	for i in 420:
		y-=.5
		var state: Dictionary=model.advance(1./280.,y,1.)
		if i>=256:
			poses[int(state.q)]=state
			if stop_at_phase>=0 and int(state.q)==stop_at_phase:
				return {"poses":poses,"y":y,"release":state}
	return {"poses":poses,"y":y,"release":{}}
func _run() -> void:
	var folder:=OS.get_cmdline_user_args()[0]
	DirAccess.make_dir_recursive_absolute(folder)
	var hash_before:=FileAccess.get_sha256(MODEL_PATH)
	if hash_before!=EXPECTED_MODEL_SHA256:
		push_error("locked v06 model hash changed")
		quit(2);return
	var model_script: GDScript=load(MODEL_PATH)
	var model: RefCounted=model_script.new()
	var run: Dictionary=_run_280(model,-1)
	var poses: Dictionary=run.poses
	var frames:=[]
	var problems:=[]
	for q in 128:
		if not poses.has(q):problems.append("missing run phase %d"%q);continue
		var s: Dictionary=poses[q]
		if s.mode!="run" or s.age<.12 or s.live!=1.:problems.append("run phase %d not steady"%q)
		frames.append(_save(folder,"run",q,s,model))
	var scan:=[]
	var worst:={"phase":-1,"last":-1,"moveIndex":-1,"moveDiff":-1}
	var finals_exact:=true
	for phase in 128:
		var m: RefCounted=model_script.new()
		var r: Dictionary=_run_280(m,phase)
		if r.release.is_empty():problems.append("release phase %d not reached"%phase);continue
		var states:=[m.snapshot()]
		var images:=[m.render_pose(states[0]).full]
		for t in 40:
			var s: Dictionary=m.advance(1./60.,r.y,0.)
			states.append(s)
			images.append(m.render_pose(s).full)
			if s.mode=="idle":break
		var n:=images.size()
		var exact: bool=states[n-1].mode=="idle" and images[n-1].get_data()==m.original.get_data()
		finals_exact=finals_exact and exact
		var steps:=[]
		for k in range(1,n):steps.append(_diff(images[k-1],images[k]))
		var move:=n-1
		while move>0 and images[move].get_data()==images[n-1].get_data():move-=1
		var move_diff:=_diff(images[move],images[n-1])
		var last_change:=steps.size()-1
		while last_change>0 and steps[last_change]==0:last_change-=1
		scan.append({"phase":phase,"frames":n,"finalExact":exact,"stepChangedTexels":steps,"lastMovingFrame":move,"lastMovingStopAge":states[move].stopAge,"lastMovingChangedTexelsToFinal":move_diff,"firstStaticFrame":move+1,"firstStaticStopAge":states[mini(move+1,n-1)].stopAge,"releaseBody":[states[0].body.x,states[0].body.y],"releaseFeetGround":[states[0].feet[0].ground,states[0].feet[1].ground]})
		var last: int=steps[last_change]
		if last>worst.last or (last==worst.last and (move>worst.moveIndex or (move==worst.moveIndex and move_diff>worst.moveDiff))):
			worst={"phase":phase,"last":last,"moveIndex":move,"moveDiff":move_diff,"states":states}
	if worst.phase<0:problems.append("no stop phase")
	else:
		var sm: RefCounted=model_script.new()
		var r2: Dictionary=_run_280(sm,int(worst.phase))
		var stop_states:=[sm.snapshot()]
		for t in 40:
			var s: Dictionary=sm.advance(1./60.,r2.y,0.)
			stop_states.append(s)
			if s.mode=="idle":break
		if JSON.stringify(stop_states.map(_serialize))!=JSON.stringify(worst.states.map(_serialize)):problems.append("representative stop rebuild differs from scan")
		for i in stop_states.size():frames.append(_save(folder,"stop",i,stop_states[i],sm))
	var hash_after:=FileAccess.get_sha256(MODEL_PATH)
	if hash_after!=hash_before:problems.append("model hash changed during bake")
	var role_order:=[]
	for role: String in model.layers:role_order.append(role)
	var report:={"task":"content.char.protagonist-female.walk-north","cell":[80,128],"pivot":[40,104],"scale":.5,"cadenceStepsPerSecond":4.375,"stanceSourceRows":20,"strideSourceRows":64,"roleOrder":role_order,
		"runReference":"420 advance() ticks at 1/280 s, -0.5 world px (north) each; kept after tick 256","stopReference":"same 280 Hz run released at the chosen phase, then advance(1/60, y held, 0) until idle",
		"representativeStop":{"phase":worst.phase,"lastStepChangedTexels":worst.last,"lastMovingFrame":worst.moveIndex,"lastMovingChangedTexelsToFinal":worst.moveDiff,"selection":"largest final settle step, then latest last-moving frame, then largest last-moving diff, over all 128 release phases at 60 fps"},
		"stopScan60":scan,"allStopFinalsExact":finals_exact,"poses":frames,"problems":problems,
		"modelPath":MODEL_PATH,"modelSha256Before":hash_before,"modelSha256After":hash_after,"bakeToolSha256":FileAccess.get_sha256(get_script().resource_path),"artApproved":false,"motionApproved":false}
	var file:=FileAccess.open(folder.path_join("fn-native-bake-report_%s.json"%TAG),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  ")+"\n")
	file.close()
	print("NORTH V06 NATIVE BAKE poses=",frames.size()," stopPhase=",worst.phase," lastStep=",worst.last," finalsExact=",finals_exact," problems=",problems.size())
	for p in problems.slice(0,8):print(p)
	if problems.is_empty() and finals_exact:print("NORTH_V06_BAKE_OK")
	quit(0 if problems.is_empty() and finals_exact else 1)
