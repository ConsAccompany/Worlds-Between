extends SceneTree
const MODEL := preload("res://../tools/rpg-2-star-ocean-the-second_female-west_run-stop-source_unapproved-v01_20261018-181150-a94f021c.gd")
func _initialize() -> void:call_deferred("_run")
func _serialize(value: Dictionary) -> Dictionary:
	var state:=value.duplicate(true)
	state.body=[state.body.x,state.body.y]
	return state
func _save(root_path: String,kind: String,index: int,state: Dictionary,model: RefCounted) -> Dictionary:
	var data: Dictionary=model.render_pose(state)
	var tag:="rpg-2-star-ocean-the-second_female-west-%s_frame-%02d_source-v01_20261018-181150-a94f021c"%[kind,index]
	var full_name:=tag+".png"
	data.full.save_png(root_path.path_join(full_name))
	var roles:={}
	for role: String in data.roles:
		var filename:=tag+"-role-"+role+".rgba"
		var file:=FileAccess.open(root_path.path_join(filename),FileAccess.WRITE)
		file.store_buffer(data.roles[role].get_data())
		file.close()
		roles[role]={"file":filename,"sha256":FileAccess.get_sha256(root_path.path_join(filename))}
	return {"kind":kind,"index":index,"state":_serialize(state),"full":{"file":full_name,"sha256":FileAccess.get_sha256(root_path.path_join(full_name))},"roles":roles}
func _run() -> void:
	var folder:=OS.get_cmdline_user_args()[0]
	DirAccess.make_dir_recursive_absolute(folder)
	var model: RefCounted=MODEL.new()
	var x:=0.
	var poses:={}
	for i in 400:
		x-=.5
		var state: Dictionary=model.advance(1./280.,x,-1.)
		if i>=256:poses[int(state.q)]=state
	var frames:=[]
	for q in range(128):
		assert(poses.has(q))
		frames.append(_save(folder,"run",q,poses[q],model))
	var release: Dictionary=poses[47]
	model.mode="run"
	model.q=release.q
	model.feet=model._copy_feet(release.feet)
	model.last_body=release.body
	model.physical_x=x
	model.render_x=roundf(x*2.)*.5
	frames.append(_save(folder,"stop",0,model.snapshot(),model))
	for i in range(1,10):frames.append(_save(folder,"stop",i,model.advance(.025,x,0.),model))
	var report:={"task":"content.char.protagonist-female.walk-west","cell":[80,112],"pivot":[40,104],"scale":.5,"cadence":4.375,"contactSourcePixels":38,"strideSourcePixels":128,"runReferenceFps":280,"stopReferenceFps":40,"poses":frames,"modelSha256":FileAccess.get_sha256("res://../tools/rpg-2-star-ocean-the-second_female-west_run-stop-source_unapproved-v01_20261018-181150-a94f021c.gd"),"artApproved":false,"motionApproved":false}
	var file:=FileAccess.open(folder.path_join("rpg-2-star-ocean-the-second_female-west-run_native-bake-report_v01_20261018-181150-a94f021c.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  ")+"\n")
	file.close()
	print("WEST NATIVE BAKE poses=",frames.size())
	quit(0)
