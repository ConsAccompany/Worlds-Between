extends SceneTree
# Two sampled actual pilot poses through normal Input and host movement; no visibility/z-sort overrides.
var rows := []
var folder := ""
var report_path := ""
var source_hashes := {}
func _initialize() -> void:call_deferred("run")
func sources() -> Dictionary:
	var result:={}
	for path in ["res://scripts/scifi_exploration_area.gd","res://scripts/exploration_sprite_set_pilot.gd","res://scripts/app_state.gd"]:result[path]=FileAccess.get_sha256(path)
	for file in DirAccess.get_files_at("res://scripts/fexp"):
		if file.ends_with(".gd"):result["res://scripts/fexp/"+file]=FileAccess.get_sha256("res://scripts/fexp/"+file)
	return result
func detach_audio(node: Node) -> void:
	for child in node.get_children():
		if child is AudioStreamPlayer or child is AudioStreamPlayer2D or child is AudioStreamPlayer3D:child.stop();child.stream=null
		detach_audio(child)
func run() -> void:
	var args:=OS.get_cmdline_user_args();assert(args.size()>=3 and args.has("--female-complete-exploration-pilot"))
	folder=args[0];report_path=args[1];source_hashes=sources()
	root.size=Vector2i(640,360);root.gui_disable_input=true
	var app: Node=root.get_node("AppState");SaveStore.root_path="user://test-saves/fexp-clear-plaza"
	assert(app.settings.load_status=="missing")
	var stamp:=Time.get_datetime_string_from_system(true).replace("-","").replace(":","").replace("T","-")+"-d81336a7"
	for spec in [{"facing":"north","language":"en","action":"move_up","start":Vector2(360,260)},{"facing":"south","language":"zh","action":"move_down","start":Vector2(360,230)}]:
		app.begin_new_run();app.hero_appearance="female";app.language=spec.language;app.current_destination_id="scifi.city"
		app.show_initial_guide=false;app.returning_from_battle=false;app.resume_area_pending=false;app.resume_annex_pending=false
		app.play_time_seconds=84.0;app.run_active=false;app.set_process(false)
		var scene: Node=load("res://scenes/scifi_exploration_area.tscn").instantiate();root.add_child(scene)
		scene.set_process(false)
		scene.hero.position=spec.start;scene._update_city_labels();scene._refresh_text()
		var pilot: Node=scene.sprite_pilot;assert(pilot!=null and pilot.name=="FemaleCompleteExplorationPilot")
		Input.action_press(spec.action)
		for frame in 8:
			scene._process(1.0/60.0)
			await process_frame
		Input.action_release(spec.action)
		await RenderingServer.frame_post_draw
		assert(pilot.facing==spec.facing and not pilot.showing_idle and not scene.city_hero_silhouette.visible)
		var image:=root.get_texture().get_image();assert(image.get_size()==Vector2i(640,360))
		var file:="rpg-2-star-ocean-the-second_female-exploration_clear-plaza-%s-%s-critical-640_pilot-unapproved-v01_%s.png"%[spec.facing,spec.language,stamp]
		assert(image.save_png(folder.path_join(file))==OK)
		rows.append({"facing":spec.facing,"language":spec.language,"file":file,"pngSha256":FileAccess.get_sha256(folder.path_join(file)),"scene":"res://scenes/scifi_exploration_area.tscn","inputAction":spec.action,"actualInputFrames":8,"fixedDelta":1.0/60.0,"startPosition":var_to_str(spec.start),"actualPosition":var_to_str(scene.hero.position),"heroScale":var_to_str(scene.hero.scale),"heroOffset":var_to_str(scene.hero.offset),"normalZIndex":scene.hero.z_index,"canopySilhouetteVisible":scene.city_hero_silhouette.visible,"pilotMode":pilot.model_mode,"lastState":var_to_str(pilot.last_state),"pilotReport":pilot.report()})
		print("FEXP_CLEAR_PLAZA_CAPTURE "+folder.path_join(file))
		detach_audio(scene);root.remove_child(scene);scene.free();await process_frame
	var report:={"purpose":"unscored separate clear-plaza sampled-pose evidence; no art/fluidity acceptance","cases":rows,"sourceRawSha256Before":source_hashes,"sourceRawSha256After":sources(),"toolRawSha256":FileAccess.get_sha256(get_script().resource_path),"flags":args,"subtreeVisibilityOrZSortOverrides":false}
	var f:=FileAccess.open(report_path,FileAccess.WRITE);assert(f!=null);f.store_string(JSON.stringify(report,"  ")+"\n");f.close()
	print("FEXP_CLEAR_PLAZA_OK captures=2");call_deferred("finish")
func finish() -> void:
	var previous:=AudioServer.get_time_since_last_mix();var mixes:=0;var deadline:=Time.get_ticks_usec()+300000
	while mixes<2 and Time.get_ticks_usec()<deadline:
		await process_frame
		var age:=AudioServer.get_time_since_last_mix()
		if age<previous:mixes+=1
		previous=age
	print("FEXP_CLEAR_PLAZA_AUDIO_MIX_BOUNDARIES ",mixes);quit(0 if mixes==2 else 1)
