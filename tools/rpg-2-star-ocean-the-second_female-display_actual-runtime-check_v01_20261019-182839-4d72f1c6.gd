extends SceneTree
const TAG := "20261019-182839-4d72f1c6"
const Helper := preload("res://scripts/rpg-2-star-ocean-the-second_protagonist-female_display-portrait-helper_v01_20261019-182839-4d72f1c6.gd")
var app: Node
var output: String
var checks: Array = []
func _initialize() -> void: call_deferred("run")
func ck(key: String, pass_: bool) -> void: checks.append({"key":key,"pass":pass_})
func setup(lang: String, portrait: int, skin: int, frozen := false) -> Control:
	app.begin_new_run(); app.language=lang; app.hero_appearance="female"
	app.recruit_member("liang-xu")
	var script: Script = load(output.path_join("rpg-2-star-ocean-the-second_female-display_growth-frozen-before-wiring_v01_"+TAG+".gd") if frozen else "res://scripts/growth_screen.gd")
	script.management_ui_skin_override=skin
	if not frozen: script.female_display_portrait_override=portrait
	var screen: Control=script.new() if frozen else load("res://scenes/growth_screen.tscn").instantiate()
	screen.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.add_child(screen); current_scene=screen
	await process_frame; await process_frame; await RenderingServer.frame_post_draw
	return screen
func dispose(screen: Control) -> void:
	screen.queue_free(); await process_frame
func image(label: String) -> Image:
	await process_frame; await RenderingServer.frame_post_draw
	var im:=root.get_texture().get_image(); im.convert(Image.FORMAT_RGBA8)
	ck("capture-"+label,im.save_png(output.path_join("rpg-2-star-ocean-the-second_female-display_"+label+"_actual-640_v01_"+TAG+".png"))==OK)
	return im
func controls(screen: Control) -> Array:
	var rows: Array=[]
	for n in screen.find_children("*","Control",true,false):
		if n is Helper or (screen.get("female_display_portrait")!=null and screen.female_display_portrait.is_ancestor_of(n)): continue
		rows.append([n.get_class(),n.get_global_rect(),n.get_combined_minimum_size(),n.visible,String(n.text) if n is Label or n is Button else "",n.mouse_filter,n.focus_mode])
	return rows
func click(p: Vector2) -> void:
	var motion:=InputEventMouseMotion.new(); motion.position=p; root.push_input(motion,true)
	for press in [true,false]:
		var event:=InputEventMouseButton.new(); event.position=p; event.button_index=MOUSE_BUTTON_LEFT; event.pressed=press; root.push_input(event,true)
func settle() -> void:
	await process_frame; await process_frame; await RenderingServer.frame_post_draw
func run() -> void:
	output=OS.get_cmdline_user_args()[0]; app=root.get_node("AppState")
	root.size=Vector2i(640,360);root.content_scale_size=Vector2i(640,360);root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	await process_frame
	for lang in ["en","zh"]:
		for skin in [0,1]:
			var old:=await setup(lang,0,skin,true); var old_state:=controls(old);var old_im:=await image(lang+str(skin)+"-frozen");await dispose(old)
			var off:=await setup(lang,0,skin);var off_im:=await image(lang+str(skin)+"-off")
			ck(lang+str(skin)+"-default0px",old_im.get_data()==off_im.get_data());ck(lang+str(skin)+"-default-controls",old_state==controls(off));await dispose(off)
			var on:=await setup(lang,1,skin);var portrait: Control=on.female_display_portrait
			ck(lang+str(skin)+"-shown",portrait.visible);ck(lang+str(skin)+"-original-controls",old_state==controls(on))
			print("PORTRAIT_STATE "+JSON.stringify(portrait.get_debug_state()))
			ck("fixed-rect",portrait.get_rect()==Rect2(522,88,96,124));ck("passive-input",portrait.mouse_filter==Control.MOUSE_FILTER_IGNORE and portrait.focus_mode==Control.FOCUS_NONE)
			ck("native239x311",portrait.get_texture_size()==Vector2i(239,311));ck("below-overlay",portrait.get_index()+1==on.node_panel.get_index())
			await image(lang+str(skin)+"-female-main")
			click(on.member_buttons[1].get_global_rect().get_center());await settle();ck("party-realclick",on.selected_id=="liang-xu" and not portrait.visible)
			click(on.member_buttons[0].get_global_rect().get_center());await settle();ck("hero-realclick",portrait.visible)
			click(on.nodes_button.get_global_rect().get_center());await settle();ck("overlay-realclick-hide",on.node_panel.visible and not portrait.visible);await image(lang+str(skin)+"-nodes")
			click(on.node_close_button.get_global_rect().get_center());await settle();ck("overlay-close",not on.node_panel.visible and portrait.visible)
			app.hero_appearance="male";on._refresh();await settle();ck("male-hide",not portrait.visible)
			# An actual button below the invisible portrait remains clickable. Overlap refuses the portrait.
			var receiver:=Button.new();receiver.position=Vector2(540,100);receiver.size=Vector2(30,30);on.add_child(receiver);on.move_child(receiver,portrait.get_index());var hits: Array=[];receiver.pressed.connect(func():hits.append(true))
			click(receiver.get_global_rect().get_center());await settle();ck("hidden-click-through",hits.size()==1);receiver.free();await process_frame
			app.hero_appearance="female";on._refresh();await settle();ck("female-restored",portrait.visible);print("RESTORE_STATE "+JSON.stringify(portrait.get_debug_state()))
			var original: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(on.female_display_portrait_manifest))
			var bads: Array=[null,[],{"schema":[]},"malformed"]
			for spec in [["source","sha256",{}],["display","image_sha256",[]],["display","image_path","../outside.png"],["display","image_width",239.0001],["crop","resampled",0],["provenance","human_artist",0],["source","width",1916.01],["display","image_path","missing.png"]]:
				var m: Dictionary=original.duplicate(true);m[spec[0]][spec[1]]=spec[2];bads.append(m)
			for index in bads.size():
				var path:=output.path_join("rpg-2-star-ocean-the-second_female-display_invalid-case-"+str(index)+"_v01_"+TAG+".json")
				var f:=FileAccess.open(path,FileAccess.WRITE);f.store_string("{" if bads[index] is String else JSON.stringify(bads[index]));f.close()
				ck("malformed-"+str(index),not portrait.apply_appstate(path,app,"hero","hero",true,true) and not portrait.visible)
			ck("missing-safe",not portrait.apply_appstate("res://does-not-exist.json",app,"hero","hero",true,true))
			portrait.apply_appstate(on.female_display_portrait_manifest,app,"hero","hero",true,true);await settle();ck("recover-after-invalid",portrait.visible)
			var conflict:=Label.new();conflict.text="real text";conflict.position=Vector2(530,110);on.add_child(conflict);await settle();portrait.refresh("female","hero","hero",true);ck("actual-text-overlap-refusal",not portrait.visible and conflict.text=="real text" and conflict.position==Vector2(530,110));conflict.queue_free();await process_frame
			await dispose(on)
	# One normal scene-change route with all four pilot flags, not a replacement fixture.
	var growth_script: Script=load("res://scripts/growth_screen.gd")
	growth_script.female_display_portrait_override=-1;growth_script.management_ui_skin_override=-1
	app.begin_new_run();app.language="en";app.hero_appearance="female"
	var protected_state: Array=[app.hero_state.duplicate(true),app.active_party_ids.duplicate(),app.current_destination_id]
	change_scene_to_file("res://scenes/scifi_world_map.tscn");await settle()
	var map: Node=current_scene
	ck("normal-route-map",map.has_method("_open_growth"));click(map.growth_button.get_global_rect().get_center());await settle()
	var growth: Control=current_scene
	ck("normal-route-growth",growth.has_method("_refresh_display_portrait") and growth.female_display_portrait.visible)
	ck("normal-route-management",growth.management_ui_skin_status=="applied")
	await image("combined-flags-normal-growth")
	click(growth.back_button.get_global_rect().get_center());await settle()
	ck("normal-route-back",current_scene.has_method("_open_growth"))
	ck("normal-route-state-preserved",protected_state==[app.hero_state,app.active_party_ids,app.current_destination_id])
	await image("combined-flags-return-map")
	current_scene.queue_free();current_scene=null;await process_frame
	var passed:=0
	for row in checks:
		if row.pass:passed+=1
		else:print("FAILED "+row.key)
	var file:=FileAccess.open(output.path_join("rpg-2-star-ocean-the-second_female-display_actual-runtime-report_v01_"+TAG+".json"),FileAccess.WRITE);file.store_string(JSON.stringify({"passed":passed,"total":checks.size(),"checks":checks},"\t"));file.close()
	print("PORTRAIT_ACTUAL ",passed,"/",checks.size());quit(0 if passed==checks.size() else 1)
