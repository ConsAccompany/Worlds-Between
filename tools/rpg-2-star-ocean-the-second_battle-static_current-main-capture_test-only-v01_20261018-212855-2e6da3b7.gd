extends SceneTree
# Current canonical arena with only a test static substituted for hero art. Not default adoption or animation.
# The reference 0.65 proportion is already baked into the 68x72 PNG: draw at pixel scale1, pin32,68.
# Args: absolute sprite PNG, new output folder, unique stamp-id, tested Git revision.
const PROBE_SOURCE := "extends \"res://scripts/battle_arena.gd\"\nvar candidate: Texture2D\nvar inject := false\nfunc _draw_fighter(fighter: Dictionary, index: int) -> void:\n\tif not inject or String(fighter[\"id\"]) != \"hero\":\n\t\tsuper._draw_fighter(fighter,index)\n\t\treturn\n\tvar x: float=fighter[\"x\"]\n\tif _is_alive(index) and index==controlled_index and not auto_mode:\n\t\tdraw_circle(Vector2(x,272),13.0,Color(\"#f5e1a6\"))\n\tdraw_texture(candidate,Vector2(roundf(x)-32.,272.-68.))\n"
func _initialize() -> void:call_deferred("_run")
func _hash(image: Image) -> String:
	var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(image.get_data());return h.finish().hex_encode()
func _capture(arena: Node2D,path: String) -> Image:
	arena.queue_redraw()
	await process_frame
	await RenderingServer.frame_post_draw
	var image:=root.get_texture().get_image()
	assert(image.get_size()==Vector2i(640,360))
	assert(image.save_png(path)==OK)
	return image
func _run() -> void:
	var args:=OS.get_cmdline_user_args()
	assert(args.size()==4 or args.size()==5)
	var plate_mode:=args.size()==5 and args[4]=="outskirts"
	var sprite_path: String=args[0]
	var out: String=args[1]
	var tag: String=args[2]
	var revision: String=args[3]
	assert(not DirAccess.dir_exists_absolute(out),"Use a fresh unique output folder")
	DirAccess.make_dir_recursive_absolute(out)
	root.size=Vector2i(640,360)
	var app: Node=root.get_node("AppState")
	SaveStore.root_path="user://test-saves/current-static-capture"
	var sprite:=Image.load_from_file(sprite_path)
	assert(sprite!=null and sprite.get_size()==Vector2i(68,72))
	var texture:=ImageTexture.create_from_image(sprite)
	var base_script: GDScript=load("res://scripts/battle_arena.gd")
	base_script.sentry_v2_override=0
	base_script.battle_backdrop_override=1 if plate_mode else 0
	base_script.combat_sprite_set_override=0
	var records:=[]
	for language in ["en","zh"]:
		app.begin_new_run()
		app.hero_appearance="female"
		app.recruit_member("liang-xu")
		app.recruit_member("zhao-ling")
		app.ji_records_checked=true
		app.recruit_member("ji-cheng")
		app.select_destination("scifi.outskirts" if plate_mode else "scifi.city")
		if app.language!=language:app.toggle_language()
		app.begin_battle("patrol" if plate_mode else "sentry",Vector2(330,215))
		var probe:=GDScript.new()
		probe.source_code=PROBE_SOURCE
		assert(probe.reload()==OK)
		var arena: Node2D=probe.new()
		arena.candidate=texture
		root.add_child(arena)
		current_scene=arena
		arena.set_process(false)
		assert(arena.fighters.size()==4)
		assert(arena.fighters[0]["id"]=="hero")
		var xs:=[]
		for fighter: Dictionary in arena.fighters:xs.append(float(fighter["x"]))
		assert(xs==[135.,171.,207.,243.],"Keep normal current-main party positions")
		var plate_check: Dictionary={}
		if plate_mode:
			assert(arena.battle_backdrop_status=="loaded" and arena.battle_backdrop_arena_id=="outskirts")
			assert(arena.battle_backdrop_texture.get_size()==Vector2(640,212))
			var initial_x: float=arena.fighters[0]["x"]
			Input.action_press("move_right")
			arena._process(.1)
			Input.action_release("move_right")
			var moved_x: float=arena.fighters[0]["x"]
			assert(absf(moved_x-initial_x-16.8)<.01,"Normal168px/s battle movement remains playable")
			plate_check={"loaded":true,"arena":"outskirts","textureSize":[640,212],"heroInitialX":initial_x,"heroAfterMoveX":moved_x,"simulatedMoveSeconds":.1,"humanInput":false,"manualBandOverlay":false,"bandResource":String(base_script.BATTLE_BACKDROP_BANDS["outskirts"]),"bandSha256":FileAccess.get_sha256(String(base_script.BATTLE_BACKDROP_BANDS["outskirts"]))}
		var hero_x:=roundf(float(arena.fighters[0]["x"]))
		var prefix: String=out.path_join("rpg-2-star-ocean-the-second_battle-static-current-main-")+language
		var baseline_path: String=prefix+"-baseline_test-only-v01_"+tag+".png"
		var candidate_path: String=prefix+"-injected_test-only-v01_"+tag+".png"
		var baseline: Image=await _capture(arena,baseline_path)
		arena.inject=true
		var actual: Image=await _capture(arena,candidate_path)
		var original_texture: Texture2D=arena._female_combat_texture(arena.fighters[0],0)
		var original_rect:=Rect2i(Vector2i(int(hero_x),272)-Vector2i(arena.HERO_COMBAT_ANCHOR),Vector2i(original_texture.get_size()))
		var candidate_rect:=Rect2i(Vector2i(int(hero_x)-32,272-68),Vector2i(68,72))
		var bounds:=original_rect.merge(candidate_rect)
		var changed:=0
		var outside:=0
		for y in 360:
			for x in 640:
				if baseline.get_pixel(x,y)!=actual.get_pixel(x,y):
					changed+=1
					if not bounds.has_point(Vector2i(x,y)):outside+=1
		assert(changed>0 and outside==0,"Only the hero replacement bounds may change")
		records.append({"language":language,"partyX":xs,"heroIndex":0,"plateCheck":plate_check,"baseline":baseline_path.get_file(),"injected":candidate_path.get_file(),"baselineFileSha256":FileAccess.get_sha256(baseline_path),"injectedFileSha256":FileAccess.get_sha256(candidate_path),"baselineRgbaSha256":_hash(baseline),"injectedRgbaSha256":_hash(actual),"changedPixels":changed,"changedOutsideHeroBounds":outside,"heroUnionRect":[bounds.position.x,bounds.position.y,bounds.size.x,bounds.size.y]})
		current_scene=null
		arena.queue_free()
		await process_frame
	var report:={"testOnly":true,"sourceDefaultChanged":false,"simulationFrozenForCapture":true,"movementProbeApplied":plate_mode,"viewport":[640,360],"testedRevision":revision,"arenaSha256":FileAccess.get_sha256("res://scripts/battle_arena.gd"),"captureToolSha256":FileAccess.get_sha256(get_script().resource_path),"spriteSha256":FileAccess.get_sha256(sprite_path),"sourceCell":[68,72],"pin":[32,68],"runtimePixelScale":1.,"bakedReferenceRatio":.65,"backdropPilotEnabled":plate_mode,"context":"Current canonical arena (geometric default or explicitly flagged outskirts plate as declared). Only hero art is test-injected. No manual legacy-band or contact-shadow overlay, position rearrangement or production adoption.","records":records,"artAccepted":false,"motionTested":false,"humanPlaytest":false}
	var file:=FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_battle-static-current-main_report_test-only-v01_"+tag+".json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  ")+"\n");file.close()
	print("CURRENT_MAIN_STATIC_CAPTURE_OK records=",records.size())
	quit(0)
