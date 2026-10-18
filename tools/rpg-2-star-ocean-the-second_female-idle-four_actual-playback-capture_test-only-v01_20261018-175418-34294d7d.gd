extends SceneTree
# Real AnimatedSprite2D clock and animation changes; no frame-by-frame pose override.
const MANIFEST := "res://../outputs/female-idle-four-v01/rpg-2-star-ocean-the-second_female-idle-four_direction-manifest_unapproved-v01_20261018-175418-34294d7d.json"
var checks := 0
func _initialize() -> void:call_deferred("_run")
func _check(ok: bool, message: String) -> bool:
	if not ok:
		push_error("IDLE_FOUR FAIL " + message)
		quit(1)
		return false
	checks += 1
	print("PASS " + message)
	return true
func _bounds(image: Image) -> Rect2i:
	var lo := image.get_size()
	var hi := Vector2i(-1,-1)
	for y in image.get_height():
		for x in image.get_width():
			if image.get_pixel(x,y).a8==255:
				lo=Vector2i(mini(lo.x,x),mini(lo.y,y))
				hi=Vector2i(maxi(hi.x,x),maxi(hi.y,y))
	return Rect2i(lo,hi-lo+Vector2i.ONE)
func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var folder := args[0]
	var scene_name := args[1]
	var fps := int(args[2])
	var stamp := args[3]
	DirAccess.make_dir_recursive_absolute(folder)
	var app: Node = root.get_node("AppState")
	SaveStore.root_path="user://test-saves/female-idle-four"
	if not _check(app.settings.load_status=="missing","isolated fresh settings"):
		return
	app.begin_new_run()
	app.hero_appearance="female"
	app.language="en" if fps==30 else "zh"
	app.select_destination("scifi.city")
	app.current_annex_room=2
	root.size=Vector2i(640,360)
	root.content_scale_size=Vector2i(640,360)
	root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	var host: Node2D=load("res://scenes/scifi_exploration_area.tscn" if scene_name=="city-bright" else "res://scenes/survey_annex.tscn").instantiate()
	root.add_child(host)
	current_scene=host
	await process_frame
	await process_frame
	host.set_process(false)
	var hero: Sprite2D=host.hero
	var original := hero.texture.get_image()
	var floor_y: float=hero.position.y+hero.offset.y-original.get_height()*.5+_bounds(original).end.y
	hero.visible=false
	var manifest: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
	var frames := SpriteFrames.new()
	frames.remove_animation("default")
	var source_hashes := {}
	for direction: String in manifest.directions:
		frames.add_animation(direction)
		frames.set_animation_speed(direction,1.)
		frames.set_animation_loop(direction,true)
		var row: Dictionary=manifest.directions[direction]
		for i in row.frames.size():
			var path: String=ProjectSettings.globalize_path("res://../"+row.frames[i].files.png.file)
			var image := Image.load_from_file(path)
			if not _check(image!=null and FileAccess.get_sha256(path)==row.frames[i].files.png.sha256,"source "+direction+"/"+str(i)):
				return
			frames.add_frame(direction,ImageTexture.create_from_image(image),manifest.phases[i].seconds)
		source_hashes[direction]=row.sha256
	var sprite := AnimatedSprite2D.new()
	sprite.sprite_frames=frames
	sprite.centered=false
	sprite.offset=Vector2(-40,-104)
	sprite.position=Vector2(hero.position.x,floor_y)
	sprite.scale=Vector2(.5,.5)
	sprite.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.z_index=int(floor_y)
	host.add_child(sprite)
	# Let engine startup delta smoothing settle before recording native playback.
	for warmup in 8:
		await process_frame
		await RenderingServer.frame_post_draw
	var records := []
	var critical := []
	var tick := 0
	var previous_process := -1
	for direction: String in ["south","north","west","east"]:
		sprite.play(direction)
		var seen := {}
		var saved := {}
		var foot_reference: Image
		for local_tick in int(round(5.2*fps)):
			await process_frame
			await RenderingServer.frame_post_draw
			var process := Engine.get_process_frames()
			if previous_process>=0 and not _check(process==previous_process+1,"consecutive real playback tick "+str(tick)):
				return
			if not _check(absf(sprite.get_process_delta_time()-1.0/fps)<0.000001,"exact recorded delta "+str(tick)):
				return
			previous_process=process
			var frame := sprite.frame
			seen[frame]=true
			var image := root.get_viewport().get_texture().get_image()
			image.convert(Image.FORMAT_RGBA8)
			var foot := image.get_region(Rect2i(int(sprite.position.x)-24,int(floor_y)-12,48,12))
			if local_tick==0:
				foot_reference=foot
			if not _check(foot.get_data()==foot_reference.get_data(),"planted feet "+direction+"/"+str(local_tick)):
				return
			var name := "rpg-2-star-ocean-the-second_female-idle-%s-%dfps_frame-%04d_test-only-v01_%s.png" % [scene_name,fps,tick,stamp]
			var file := folder.path_join(name)
			image.save_png(file)
			records.append({"file":name,"sha256":FileAccess.get_sha256(file),"tick":tick,"direction":direction,"frame":frame,"progress":sprite.frame_progress,"delta":sprite.get_process_delta_time(),"processFrame":process})
			if frame in [0,4,7] and not saved.has(frame):
				saved[frame]=true
				critical.append({"file":name,"direction":direction,"phase":frame,"tick":tick})
			tick+=1
		if not _check(seen.size()==12 and saved.size()==3,"all12 phases and3 critical captures "+direction):
			return
	var report := {"task":"content.char.protagonist-female.idle-anim","scene":scene_name,"fps":fps,"canvas":[640,360],"language":app.language,"seconds":float(tick)/fps,"cycleSeconds":4.8,"spritePlayback":"AnimatedSprite2D native time clock and play(direction); no manual phase setting","sources":source_hashes,"manifestSha256":FileAccess.get_sha256(MANIFEST),"checks":checks,"artApproved":false,"motionApproved":false,"frames":records,"critical":critical}
	var file := FileAccess.open(folder.path_join("rpg-2-star-ocean-the-second_female-idle-%s-%dfps_actual-report_v01_%s.json" % [scene_name,fps,stamp]),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  ")+"\n")
	file.close()
	print("IDLE_FOUR_CAPTURE PASS scene=%s fps=%d frames=%d checks=%d" % [scene_name,fps,tick,checks])
	quit(0)
