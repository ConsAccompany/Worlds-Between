extends SceneTree
# EAST v03 native bake. Every cel is a real advance() state of the locked v03 model
# (torso step guard included) rendered by its own render_pose(); no approximation helper.
# Run: 400 ticks at 1/280 s, +0.5 world px each (= 1 source px = 1 phase); states after
# tick 256 give all 128 phases. Stop: for every phase, the same 280 Hz run is released at
# that phase and advanced at 1/60 s until idle; the phase whose settle is the worst case
# (largest last step, then latest last-moving frame) is kept as the representative stop.
# Usage: -s <this> -- <new temp folder>
const MODEL_PATH := "res://../tools/rpg-2-star-ocean-the-second_female-east_run-stop-source_unapproved-v03_20261018-193030-48da69c1.gd"
const EXPECTED_MODEL_SHA256 := "e783de5d8ab6b1e3f678299eb8cffde11109d1aab06c47155831ebc4388bb07f"
const TAG := "v03_20261018-194932-3a1839f6"
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
	for y in 112:
		for x in 80:
			if a.get_pixel(x,y)!=b.get_pixel(x,y):n+=1
	return n
func _save(folder: String,kind: String,index: int,state: Dictionary,model: RefCounted) -> Dictionary:
	var data: Dictionary=model.render_pose(state)
	var tag:="rpg-2-star-ocean-the-second_female-east-%s_frame-%03d_%s"%[kind,index,TAG]
	var full_name:=tag+".png"
	data.full.save_png(folder.path_join(full_name))
	var roles:={}
	for role: String in data.roles:
		var filename:=tag+"-role-"+role+".rgba"
		var file:=FileAccess.open(folder.path_join(filename),FileAccess.WRITE)
		file.store_buffer(data.roles[role].get_data())
		file.close()
		roles[role]={"file":filename,"sha256":FileAccess.get_sha256(folder.path_join(filename))}
	return {"kind":kind,"index":index,"state":_serialize(state),"full":{"file":full_name,"sha256":FileAccess.get_sha256(folder.path_join(full_name)),"rgbaSha256":_rgba_sha(data.full)},"roles":roles}
# Real 280 Hz run from idle; returns {q: state} for ticks >= 256 and the model left at the last tick.
func _run_280(model: RefCounted,stop_at_phase: int) -> Dictionary:
	var x:=0.
	var poses:={}
	for i in 400:
		x+=.5
		var state: Dictionary=model.advance(1./280.,x,1.)
		if i>=256:
			poses[int(state.q)]=state
			if stop_at_phase>=0 and int(state.q)==stop_at_phase:
				return {"poses":poses,"x":x,"release":state}
	return {"poses":poses,"x":x,"release":{}}
func _run() -> void:
	var folder:=OS.get_cmdline_user_args()[0]
	DirAccess.make_dir_recursive_absolute(folder)
	var hash_before:=FileAccess.get_sha256(MODEL_PATH)
	if hash_before!=EXPECTED_MODEL_SHA256:
		push_error("locked v03 model hash changed")
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
		# Independent expectation for a steady 280 Hz state: torso is the rounded steady body.
		var expected_y:=roundi(model.steady_body(float(q)).y)
		if s.mode!="run" or s.age<.12 or s.body.y!=float(expected_y) or s.body.x!=model.LEAN:problems.append("run phase %d not steady/rounded: %s"%[q,str(s.body)])
		frames.append(_save(folder,"run",q,s,model))
	# Stop scan over every release phase (60 fps settle after the real 280 Hz run).
	var scan:=[]
	var worst:={"phase":-1,"last":-1,"moveIndex":-1,"moveDiff":-1}
	var finals_exact:=true
	for phase in 128:
		var m: RefCounted=model_script.new()
		var r: Dictionary=_run_280(m,phase)
		if r.release.is_empty():problems.append("release phase %d not reached"%phase);continue
		var x: float=r.x
		var states:=[m.snapshot()]
		var images:=[m.render_pose(states[0]).full]
		for t in 40:
			var s: Dictionary=m.advance(1./60.,x,0.)
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
		scan.append({"phase":phase,"frames":n,"finalExact":exact,"stepChangedTexels":steps,"lastMovingFrame":move,"lastMovingStopAge":states[move].stopAge,"lastMovingChangedTexelsToFinal":move_diff,"releaseBody":[states[0].body.x,states[0].body.y]})
		if steps[-1]>worst.last or (steps[-1]==worst.last and (move>worst.moveIndex or (move==worst.moveIndex and move_diff>worst.moveDiff))):
			worst={"phase":phase,"last":steps[-1],"moveIndex":move,"moveDiff":move_diff,"states":states}
	if worst.phase<0:problems.append("no stop phase")
	else:
		var sm: RefCounted=model_script.new()
		var r2: Dictionary=_run_280(sm,int(worst.phase))
		var stop_states:=[sm.snapshot()]
		for t in 40:
			var s: Dictionary=sm.advance(1./60.,r2.x,0.)
			stop_states.append(s)
			if s.mode=="idle":break
		# The rebuilt representative stop must reproduce the scanned states exactly.
		if JSON.stringify(stop_states.map(_serialize))!=JSON.stringify(worst.states.map(_serialize)):problems.append("representative stop rebuild differs from scan")
		for i in stop_states.size():frames.append(_save(folder,"stop",i,stop_states[i],sm))
	var hash_after:=FileAccess.get_sha256(MODEL_PATH)
	if hash_after!=hash_before:problems.append("model hash changed during bake")
	var report:={"task":"content.char.protagonist-female.walk-east","cell":[80,112],"pivot":[40,104],"scale":.5,"cadenceStepsPerSecond":4.375,"contactSourcePixels":38,"strideSourcePixels":128,
		"runReference":"400 advance() ticks at 1/280 s, +0.5 world px each; kept after tick 256","stopReference":"same 280 Hz run released at the chosen phase, then advance(1/60, x, 0) until idle",
		"representativeStop":{"phase":worst.phase,"lastStepChangedTexels":worst.last,"lastMovingFrame":worst.moveIndex,"lastMovingChangedTexelsToFinal":worst.moveDiff,"selection":"largest final settle step, then latest last-moving frame, then largest last-moving diff, over all 128 release phases at 60 fps"},
		"stopScan60":scan,"allStopFinalsExact":finals_exact,"poses":frames,"problems":problems,
		"modelPath":MODEL_PATH,"modelSha256Before":hash_before,"modelSha256After":hash_after,"artApproved":false,"motionApproved":false}
	var file:=FileAccess.open(folder.path_join("rpg-2-star-ocean-the-second_female-east-run_native-bake-report_%s.json"%TAG),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  ")+"\n")
	file.close()
	print("EAST V03 NATIVE BAKE poses=",frames.size()," stopPhase=",worst.phase," lastStep=",worst.last," finalsExact=",finals_exact," problems=",problems.size())
	for p in problems.slice(0,8):print(p)
	quit(0 if problems.is_empty() and finals_exact else 1)
