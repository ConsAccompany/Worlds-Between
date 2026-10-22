extends "res://../tools/rpg-2-star-ocean-the-second_nyc-city-hall-park_godot-entry-traversal-collision-check_unapproved-v06_20261017-165253-4519dffe.gd"
var expected_base := ""
var capture_files: Array[String] = []
func _capture(name: String) -> void:
 var image: Image=await _frame_image()
 _check(image.get_size()==Vector2i(640,360),"native640x360 "+name)
 var file="rpg-2-star-ocean-the-second_nyc-city-hall-park_"+name+"_style46-v01_20261022-183638-a4e273b9.png"
 _check(image.save_png(out_dir.path_join(file))==OK,"capture "+name)
 capture_files.append(file)
func digest(b: PackedByteArray) -> String:
 var ctx:=HashingContext.new()
 ctx.start(HashingContext.HASH_SHA256);ctx.update(b)
 return ctx.finish().hex_encode()
func _run() -> void:
 for a in OS.get_cmdline_user_args():
  if a.begins_with("--out="):out_dir=a.trim_prefix("--out=")
  elif a.begins_with("--style46-expected="):expected_base=a.trim_prefix("--style46-expected=")
 DirAccess.make_dir_recursive_absolute(out_dir)
 root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 root.content_scale_size=Vector2i(640,360);root.size=Vector2i(640,360);Engine.max_fps=60
 SaveStore.root_path="user://test-saves/style46"
 app=root.get_node("AppState")
 _check(OS.get_cmdline_user_args().has("--nyc-common-style46"),"actual opt-in flag")
 _check(load(PARK_V06).enabled_override==-1,"no test enable override")
 for lang in ["zh","en"]:
  app.begin_new_run();app.hero_appearance="female";app.select_destination("scifi.city")
  app.language=lang
  await _open_city()
  _check(park!=null,"actual shared scene park loaded "+lang)
  if park==null:_finish();return
  _check(digest(park.nodes[0].texture.get_image().get_data())==expected_base,"new base pixels actually drawn "+lang)
  _check(host.hero.position==Vector2(340,253),"unchanged spawn "+lang)
  _check(host.city_npc.position==Vector2(282,180),"unchanged Liang position "+lang)
  await _capture(lang+"-entry")
  _check(await _route([Vector2(320,253),Vector2(320,214),Vector2(320,192),Vector2(300,192)]),"held-input central axis "+lang)
  await _capture(lang+"-promenade")
  _check(await _route([Vector2(170,192),Vector2(170,214),Vector2(110,240),Vector2(104,262),Vector2(120,292),Vector2(171,298),Vector2(226,288),Vector2(244,258),Vector2(196,238)]),"held-input fountain circuit "+lang)
  _check(host.hero.z_index<host.get_node("CityHallParkV06_fountain_centre").z_index,"fountain foreground order "+lang)
  await _capture(lang+"-fountain-occlusion")
  _check(await _route([Vector2(240,258),Vector2(285,258),Vector2(285,262)]),"held-input trace site "+lang)
  await actual_interact()
  _check(app.field_traces.has("scifi.city:0"),"real trace interaction "+lang)
  await _capture(lang+"-trace-recorded")
  host._close_dialogue()
  _check(await _route([Vector2(320,258),Vector2(400,258),Vector2(470,250)]),"held-input report site "+lang)
  await actual_interact()
  _check(host.feedback_key=="report_locked","real report interaction "+lang)
  await _capture(lang+"-report-response")
  host._close_dialogue()
  _check(await _route([Vector2(470,220),Vector2(470,196),Vector2(566,196),Vector2(594,203)]),"held-input east canopy route "+lang)
  await _settle_reveal(30)
  var elm: Sprite2D=host.get_node("CityHallParkV06_tree_east_elm")
  _check(elm.z_index==305 and elm.material is ShaderMaterial,"original canopy pivot and reveal shader "+lang)
  await _capture(lang+"-canopy-reveal")
 _check(off_mask_frames==0,"all actual traversal feet remain on unchanged walk mask")
 var f=FileAccess.open(out_dir.path_join("rpg-2-star-ocean-the-second_nyc-style46_runtime-result_v01_20261022-183638-a4e273b9.json"),FileAccess.WRITE)
 f.store_string(JSON.stringify({"passes":passes,"failures":failures,"offMaskFrames":off_mask_frames,"movedFrames":moved_frames,"captures":capture_files,"expectedBase":expected_base,"fixture":"Fresh isolated runs and actual shared scene instantiated directly; current ordinary heroine; actual held paths/interact; not ordinary default or human play","artAccepted":false},"  ")+"\n")
 print("STYLE46_RUNTIME_OK checks=",passes)
 quit(0 if failures.is_empty() else 1)

func actual_interact() -> void:
 var down:=InputEventAction.new()
 down.action="interact";down.pressed=true
 Input.parse_input_event(down)
 await process_frame
 var up:=InputEventAction.new()
 up.action="interact";up.pressed=false
 Input.parse_input_event(up)
 await process_frame
