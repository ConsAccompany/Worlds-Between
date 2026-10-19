extends SceneTree
const TAG := "20261019-185434-7c95e421"
const Helper := preload("res://scripts/rpg-2-star-ocean-the-second_mvp-display_portrait-helper_v01_20261019-185434-7c95e421.gd")
var app: Node
var output: String
var checks: Array=[]
func _initialize() -> void:call_deferred("run")
func ck(key: String, okay: bool) -> void:checks.append({"key":key,"pass":okay})
func settle() -> void:await process_frame;await process_frame;await RenderingServer.frame_post_draw
func setup(lang: String, generic: int, female: int, skin: int, frozen := false) -> Control:
	app.begin_new_run();app.language=lang;app.hero_appearance="female"
	app.recruit_member("liang-xu");app.recruit_member("zhao-ling");app.ji_records_checked=true;app.recruit_member("ji-cheng")
	var script: Script=load(output.path_join("rpg-2-star-ocean-the-second_mvp-display_growth-frozen-before-wiring_v01_"+TAG+".gd") if frozen else "res://scripts/growth_screen.gd")
	script.management_ui_skin_override=skin;script.female_display_portrait_override=female
	if not frozen:script.mvp_display_portraits_override=generic
	var scene: Control=script.new() if frozen else load("res://scenes/growth_screen.tscn").instantiate()
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT);root.add_child(scene);current_scene=scene;await settle();return scene
func dispose(scene: Control) -> void:scene.queue_free();await process_frame
func capture(label: String) -> Image:
	label=label.replace("[","-").replace("]","").replace(", ","-").replace(" ","-")
	await settle();var im:=root.get_texture().get_image();im.convert(Image.FORMAT_RGBA8)
	ck("capture-"+label,im.save_png(output.path_join("rpg-2-star-ocean-the-second_mvp-display_"+label+"_actual-640_v01_"+TAG+".png"))==OK);return im
func controls(scene: Control) -> Array:
	var rows: Array=[]
	for node in scene.find_children("*","Control",true,false):
		if node.name in ["FemaleDisplayPortraitPilot","MvpDisplayPortraitsPilot"]:continue
		if node.get_parent().name in ["FemaleDisplayPortraitPilot","MvpDisplayPortraitsPilot"]:continue
		var row: Array=[node.get_class(),node.get_global_rect(),node.get_combined_minimum_size(),node.visible,node.mouse_filter,node.focus_mode]
		if node is Label or node is BaseButton:row.append(node.text);row.append(node.get_theme_font_size("font_size"))
		if node is BaseButton:
			var methods: Array=[]
			for connection in node.pressed.get_connections():methods.append(String(connection.callable.get_method()))
			row.append([node.disabled,methods])
		rows.append(row)
	return rows
func click(point: Vector2) -> void:
	var motion:=InputEventMouseMotion.new();motion.position=point;root.push_input(motion,true)
	for press in [true,false]:
		var event:=InputEventMouseButton.new();event.position=point;event.button_index=MOUSE_BUTTON_LEFT;event.pressed=press;root.push_input(event,true)
func run() -> void:
	output=OS.get_cmdline_user_args()[0];app=root.get_node("AppState");root.size=Vector2i(640,360);root.content_scale_size=Vector2i(640,360);root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS;await process_frame
	var fresh:=Helper.new();ck("constructor-no-io-state",fresh.get_child_count()==0 and fresh.get_debug_state().cached.is_empty() and fresh.get_texture_size()==Vector2i.ZERO);fresh.free()
	var default_old:=await setup("en",0,0,0,true);var default_before:=await capture("default-all-off-frozen");await dispose(default_old)
	var default_new:=await setup("en",0,0,0);var default_after:=await capture("default-all-off-current");ck("all-off-default-0px",default_before.get_data()==default_after.get_data());await dispose(default_new)
	for lang in ["en","zh"]:
		# Four new/old-flag combinations, including exact legacy and default parity.
		for flags in [[0,0],[0,1],[1,0],[1,1]]:
			var old:=await setup(lang,0,flags[1],1,true);var baseline:=await capture(lang+str(flags)+"-frozen");var original:=controls(old);await dispose(old)
			var current:=await setup(lang,flags[0],flags[1],1)
			ck(lang+str(flags)+"-original-controls",original==controls(current))
			if flags[0]==0:
				var actual:=await capture(lang+str(flags)+"-legacy-or-default");ck(lang+str(flags)+"-0px",baseline.get_data()==actual.get_data())
			else:
				ck(lang+str(flags)+"-generic-priority",current.mvp_display_portraits!=null and current.female_display_portrait==null)
				ck(lang+str(flags)+"-only-one-helper",current.find_children("MvpDisplayPortraitsPilot","Control",true,false).size()==1 and current.find_children("FemaleDisplayPortraitPilot","Control",true,false).is_empty())
			await dispose(current)
		var scene:=await setup(lang,1,1,1);var portrait: Control=scene.mvp_display_portraits
		for appearance in ["male","female"]:
			app.hero_appearance=appearance
			for index in 4:
				# Native game actions update actual selected_id; real click selects each member.
				if index!=0:click(scene.member_buttons[index].get_global_rect().get_center())
				else:scene._select(0)
				await settle()
				var id: String=app.active_party_ids[index];var expected: String="protagonist-"+appearance if id=="hero" else id
				ck(lang+expected+"-identity",portrait.visible and portrait.get_active_variant()==expected)
				ck(lang+expected+"-fixed-passive",portrait.get_rect()==Rect2(522,88,96,124) and portrait.mouse_filter==Control.MOUSE_FILTER_IGNORE and portrait.focus_mode==Control.FOCUS_NONE and portrait.get_index()+1==scene.node_panel.get_index())
				var after:=controls(scene);portrait.visible=false;await settle();ck(lang+expected+"-original-geometry-text-actions",after==controls(scene));portrait.update(appearance,id,true)
				if appearance=="male" or index==0:await capture(lang+"-"+expected)
		var cached: Dictionary=portrait.get("_textures").duplicate();ck(lang+"-all-five-cached",cached.size()==5)
		for index in 4:scene._select(index);await settle()
		ck(lang+"-same-validated-texture-objects",cached==portrait.get("_textures"))
		scene._select(0);app.hero_appearance="female";scene._refresh();await settle()
		click(scene.nodes_button.get_global_rect().get_center());await settle();ck(lang+"-real-node-overlay-hides",scene.node_panel.visible and not portrait.visible)
		click(scene.node_close_button.get_global_rect().get_center());await settle();ck(lang+"-real-node-close-restores",portrait.visible)
		ck(lang+"-bad-types-safe",not portrait.update(1,{},"false") and not portrait.visible)
		scene.selected_id="unknown";ck(lang+"-unknown-id-hides",not portrait.update("male","unknown",true) and not portrait.visible)
		scene.selected_id="hero";ck(lang+"-unknown-hero-appearance-hides",not portrait.update("other","hero",true) and not portrait.visible)
		var blocker:=HSlider.new();blocker.position=Vector2(530,110);blocker.size=Vector2(70,20);scene.add_child(blocker);await settle()
		ck(lang+"-interactive-slider-overlap-refuses",not portrait.update("female","hero",true) and not portrait.visible and blocker.position==Vector2(530,110));blocker.free();portrait.update("female","hero",true)
		var decoration:=ColorRect.new();decoration.position=Vector2(530,110);decoration.size=Vector2(70,20);decoration.mouse_filter=Control.MOUSE_FILTER_IGNORE;scene.add_child(decoration);ck(lang+"-passive-decoration-ignored",portrait.update("female","hero",true));decoration.free()
		for kind in ["missing","bad-hash"]:
			var source:=FileAccess.get_file_as_string("res://scripts/rpg-2-star-ocean-the-second_mvp-display_portrait-helper_v01_20261019-185434-7c95e421.gd").replace("class_name MvpDisplayPortraitsPilot\n","")
			if kind=="missing":source=source.replace("res://assets/portraits/mvp-display-v01/rpg-2-star-ocean-the-second_protagonist-male_display-portrait-crop_v01_20261019-224538-744e4841.png","res://missing-mvp-portrait.png")
			else:source=source.replace("8b47f7a8d4f7aa7e205573de6c62ff24190e638a61cbba6e4a67ffa6e65bdefe","0".repeat(64))
			var path:=output.path_join("rpg-2-star-ocean-the-second_mvp-display_"+kind+"-fixture_v01_"+TAG+".gd");var f:=FileAccess.open(path,FileAccess.WRITE);f.store_string(source);f.close()
			var helper: Control=load(path).new();helper.install(scene,scene.node_panel);ck(lang+kind+"-safe",not helper.update("male","hero",true) and not helper.visible);helper.free()
		await dispose(scene)
	# Actual normal route with all relevant flags and both portrait flags supplied.
	var growth_script: Script=load("res://scripts/growth_screen.gd");growth_script.mvp_display_portraits_override=-1;growth_script.female_display_portrait_override=-1;growth_script.management_ui_skin_override=-1
	app.begin_new_run();app.language="en";app.hero_appearance="male";var protected_state: Array=[app.hero_state.duplicate(true),app.active_party_ids.duplicate(),app.current_destination_id]
	change_scene_to_file("res://scenes/scifi_world_map.tscn");await settle();var map: Node=current_scene;click(map.growth_button.get_global_rect().get_center());await settle();var growth: Control=current_scene
	ck("normal-route-generic-only",growth.mvp_display_portraits.visible and growth.female_display_portrait==null and growth.mvp_display_portraits.get_active_variant()=="protagonist-male")
	ck("normal-route-management-applied",growth.management_ui_skin_status=="applied");await capture("combined-normal-growth")
	click(growth.back_button.get_global_rect().get_center());await settle();ck("normal-route-map-return",current_scene.has_method("_open_growth"));ck("normal-route-state-preserved",protected_state==[app.hero_state,app.active_party_ids,app.current_destination_id]);current_scene.queue_free();current_scene=null;await process_frame
	var failed:=checks.filter(func(row):return not row.pass);var report: Dictionary={"passed":checks.size()-failed.size(),"total":checks.size(),"failures":failed,"checks":checks,"growthRawSha256":FileAccess.get_sha256("res://scripts/growth_screen.gd"),"helperRawSha256":FileAccess.get_sha256("res://scripts/rpg-2-star-ocean-the-second_mvp-display_portrait-helper_v01_20261019-185434-7c95e421.gd"),"artApproved":false}
	var file:=FileAccess.open(output.path_join("rpg-2-star-ocean-the-second_mvp-display_actual-runtime-report_v01_"+TAG+".json"),FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	for row in failed:print("FAILED "+row.key)
	print("MVP_PORTRAITS_ROOT ",report.passed,"/",report.total);quit(0 if failed.is_empty() else 1)
