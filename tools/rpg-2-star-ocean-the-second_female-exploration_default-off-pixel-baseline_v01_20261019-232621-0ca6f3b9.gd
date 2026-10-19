extends SceneTree
# Six frozen actual .tscn contexts. Reuse after integration with optional third user arg = baseline report.
const CASES := [
	{"kind":"city","scene":"res://scenes/scifi_exploration_area.tscn","destination":"scifi.city","room":1,"position":Vector2(340,253)},
	{"kind":"public-facilities-room2","scene":"res://scenes/survey_annex.tscn","destination":"scifi.city","room":2,"position":Vector2(320,285)},
	{"kind":"chicago","scene":"res://scenes/rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn","destination":"scifi.loop","room":1,"position":Vector2(320,286)}]
const SOURCES := ["res://scripts/scifi_exploration_area.gd","res://scripts/survey_annex.gd","res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v02_20261017-160959-55667f46.gd","res://scripts/exploration_sprite_set_pilot.gd","res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-scene-opt-in-selector_unapproved-v04_20261017-230650-c0d4b7f0.gd","res://scripts/app_state.gd"]
var rows := []
var hashes := {}
var folder := ""
var report_path := ""
var baseline := {}
var stamp := ""

func _initialize() -> void:call_deferred("run")
func sha(bytes: PackedByteArray) -> String:
	var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256)
	if not bytes.is_empty():h.update(bytes)
	return h.finish().hex_encode()
func freeze(node: Node) -> void:
	node.process_mode=Node.PROCESS_MODE_DISABLED
	node.set_process(false);node.set_physics_process(false);node.set_process_input(false);node.set_process_unhandled_input(false)
	if node is AnimationPlayer:node.stop()
	if node is AnimatedSprite2D:node.stop()
	if node is Timer:node.stop()
	for child in node.get_children():freeze(child)
func detach_audio(node: Node) -> void:
	for child in node.get_children():
		if child is AudioStreamPlayer or child is AudioStreamPlayer2D or child is AudioStreamPlayer3D:child.stop();child.stream=null
		detach_audio(child)
func diff_pixels(a: Image,b: Image) -> int:
	if a.get_size()!=b.get_size():return -1
	a.convert(Image.FORMAT_RGBA8);b.convert(Image.FORMAT_RGBA8)
	var x:=a.get_data();var y:=b.get_data();var total:=0
	for i in range(0,x.size(),4):
		if x[i]!=y[i] or x[i+1]!=y[i+1] or x[i+2]!=y[i+2] or x[i+3]!=y[i+3]:total+=1
	return total
func capture(app: Node,c: Dictionary,language: String) -> Dictionary:
	app.begin_new_run();app.hero_appearance="female";app.language=language
	app.current_destination_id=c.destination;app.current_annex_room=c.room
	app.show_initial_guide=false;app.returning_from_battle=false;app.resume_area_pending=false;app.resume_annex_pending=false
	app.play_time_seconds=84.0;app.run_active=false;app.set_process(false)
	var node: Node=load(c.scene).instantiate();root.add_child(node)
	freeze(node)
	node.hero.position=c.position
	if c.kind=="city":node.hero.z_index=int(c.position.y);node._update_city_labels()
	node._refresh_text()
	for tween in get_processed_tweens():tween.kill()
	for i in 3:await process_frame
	await RenderingServer.frame_post_draw
	var image:=root.get_texture().get_image();image.convert(Image.FORMAT_RGBA8)
	var info:={"image":image,"sceneScript":node.get_script().resource_path,"heroPosition":var_to_str(node.hero.position),"heroScale":var_to_str(node.hero.scale),"heroOffset":var_to_str(node.hero.offset),"heroFlipH":node.hero.flip_h,"heroTextureRgbaSha256":sha(node.hero.texture.get_image().get_data()),"frozen":node.process_mode==Node.PROCESS_MODE_DISABLED,"native640":image.get_size()==Vector2i(640,360)}
	detach_audio(node);root.remove_child(node);node.free();await process_frame
	return info
func write_report(passed: bool,reason: String) -> void:
	var after:={}
	for path in SOURCES:after[path]=FileAccess.get_sha256(path)
	var report:={"purpose":"unscored actual default-off pixel protection only","passed":passed,"reason":reason,"cases":rows,"sourceRawSha256Before":hashes,"sourceRawSha256After":after,"probeRawSha256":FileAccess.get_sha256(get_script().resource_path),"fixedPlaySeconds":84.0,"flags":OS.get_cmdline_user_args(),"freeze":"host+all descendants PROCESS_MODE_DISABLED immediately after ready; AnimationPlayer/AnimatedSprite stopped; timers stopped; tweens killed; application clock disabled; GUI input disabled","baselineCompared":not baseline.is_empty(),"motionOrArtApproval":false}
	var f:=FileAccess.open(report_path,FileAccess.WRITE);assert(f!=null);f.store_string(JSON.stringify(report,"  ")+"\n");f.close()
func run() -> void:
	var args:=OS.get_cmdline_user_args();assert(args.size()>=2)
	folder=args[0];report_path=args[1]
	assert(not args.has("--female-complete-exploration-pilot") and not args.has("--exploration-sprite-set-pilot"))
	if args.size()>2:baseline=JSON.parse_string(FileAccess.get_file_as_string(args[2]));assert(baseline.get("passed",false) and baseline.get("cases",[]).size()==6)
	stamp=Time.get_datetime_string_from_system(true).replace("-","").replace(":","").replace("T","-")+"-0ca6f3b9"
	for path in SOURCES:hashes[path]=FileAccess.get_sha256(path)
	root.size=Vector2i(640,360);root.gui_disable_input=true
	var app: Node=root.get_node("AppState");assert(app.settings.load_status=="missing")
	SaveStore.root_path="user://test-saves/fexp-default-off"
	for language in ["en","zh"]:
		for c in CASES:
			var first: Dictionary=await capture(app,c,language)
			var second: Dictionary=await capture(app,c,language)
			var row:=first.duplicate();row.erase("image");row["kind"]=c.kind;row["language"]=language;row["scene"]=c.scene
			var image: Image=first.image
			row["repeatDiffPixels"]=diff_pixels(image,second.image)
			row["rgbaSha256"]=sha(image.get_data());row["repeatRgbaSha256"]=sha(second.image.get_data())
			row["file"]="rpg-2-star-ocean-the-second_female-exploration_default-off-%s-%s-640_baseline-v01_%s.png"%[c.kind,language,stamp]
			assert(image.save_png(folder.path_join(row.file))==OK)
			row["pngSha256"]=FileAccess.get_sha256(folder.path_join(row.file))
			if not baseline.is_empty():
				var matches: Array=baseline.cases.filter(func(item):return item.kind==c.kind and item.language==language)
				assert(matches.size()==1)
				var source_image:=Image.load_from_file(String(args[2]).get_base_dir().path_join(matches[0].file))
				assert(source_image!=null)
				row["baselineDiffPixels"]=diff_pixels(source_image,image)
			rows.append(row)
			if not row.native640 or not row.frozen or row.repeatDiffPixels!=0 or row.get("baselineDiffPixels",0)!=0:
				write_report(false,"pixel protection failed "+c.kind+" "+language);print("FEXP_DEFAULT_OFF_FAIL "+JSON.stringify(row));call_deferred("finish",false);return
	write_report(true,"");print("FEXP_DEFAULT_OFF_OK cases=6 repeatDiffPixels=0");call_deferred("finish",true)
func finish(passed: bool) -> void:
	var previous:=AudioServer.get_time_since_last_mix();var mixes:=0;var deadline:=Time.get_ticks_usec()+300000
	while mixes<2 and Time.get_ticks_usec()<deadline:
		await process_frame
		var age:=AudioServer.get_time_since_last_mix()
		if age<previous:mixes+=1
		previous=age
	print("FEXP_AUDIO_CLEANUP_MIX_BOUNDARIES ",mixes)
	quit(0 if passed and mixes==2 else 1)
