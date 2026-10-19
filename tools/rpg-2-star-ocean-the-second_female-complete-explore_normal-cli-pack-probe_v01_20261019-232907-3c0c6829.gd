extends SceneTree
# Six frozen actual .tscn contexts. Reuse after integration with optional third user arg = baseline report.
const CASES := [
	{"kind":"city","scene":"res://scenes/scifi_exploration_area.tscn","destination":"scifi.city","room":1,"position":Vector2(340,253)},
	{"kind":"public-facilities-room2","scene":"res://scenes/survey_annex.tscn","destination":"scifi.city","room":2,"position":Vector2(320,285)},
	{"kind":"chicago","scene":"res://scenes/rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn","destination":"scifi.loop","room":1,"position":Vector2(320,286)}]
const SOURCES := ["res://scripts/scifi_exploration_area.gd","res://scripts/survey_annex.gd","res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v02_20261017-160959-55667f46.gd","res://scripts/exploration_sprite_set_pilot.gd","res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-scene-opt-in-selector_unapproved-v04_20261017-230650-c0d4b7f0.gd","res://scripts/app_state.gd"]
var rows:=[]
func _initialize() -> void:call_deferred("run")
func detach_audio(node: Node) -> void:
 for child in node.get_children():
  if child is AudioStreamPlayer or child is AudioStreamPlayer2D or child is AudioStreamPlayer3D:child.stop();child.stream=null
  detach_audio(child)
func run() -> void:
 var args:=OS.get_cmdline_user_args()
 assert(args.has("--female-complete-exploration-pilot"))
 var folder:=args[0];var report_path:=args[1]
 root.size=Vector2i(640,360);root.content_scale_size=Vector2i(640,360)
 var app:Node=root.get_node("AppState")
 for language in ["en","zh"]:
  for c in CASES:
   app.begin_new_run();app.hero_appearance="female";app.language=language;app.current_destination_id=c.destination;app.current_annex_room=c.room
   app.show_initial_guide=false;app.returning_from_battle=false;app.resume_area_pending=false;app.resume_annex_pending=false
   var node:Node=load(c.scene).instantiate();root.add_child(node);current_scene=node
   var pilot=node.sprite_pilot
   if pilot==null:
    var driver:Script=load("res://scripts/fexp/rpg-2-star-ocean-the-second_female-complete-explore_driver_pilot-v01_20261019-184900-f2c0a7e1.gd")
    print("FEXP_ATTACH_REFUSAL ",JSON.stringify(driver.last_refusal))
   assert(pilot!=null and pilot.has_method("step"))
   node.hero.position=c.position
   # Real host _process, real action input; no pose injection or override flags.
   var cardinal_proof:=[]
   for action in ["move_right","move_up","move_left","move_down"]:
    var facing: String={"move_right":"east","move_up":"north","move_left":"west","move_down":"south"}[action]
    var before:Vector2=node.hero.position
    Input.action_press(action)
    for i in 25:await process_frame
    Input.action_release(action)
    for i in 24:await process_frame
    var rep_dir:Dictionary=pilot.report()
    assert(node.hero.position.distance_to(before)>1 and rep_dir.showing_idle and rep_dir.facing==facing)
    cardinal_proof.append({"facing":facing,"position":var_to_str(node.hero.position),"showing_idle":rep_dir.showing_idle,"steps":rep_dir.steps})
   var rep:Dictionary=pilot.report()
   assert(rep.steps>=195 and rep.showing_idle and rep.facing=="south" and rep.switches==4)
   await RenderingServer.frame_post_draw
   var image:=root.get_texture().get_image();assert(image.get_size()==Vector2i(640,360))
   var file:="rpg-2-star-ocean-the-second_female-complete-explore_normal-%s-%s-640_unapproved-v01_"%[c.kind,language]+"20261019-233014-c65cf1fb"+".png"
   assert(image.save_png(folder.path_join(file))==OK)
   rows.append({"kind":c.kind,"language":language,"sceneScript":node.get_script().resource_path,"driver":rep,"cardinalProof":cardinal_proof,"file":file,"position":var_to_str(node.hero.position),"textureSize":var_to_str(node.hero.texture.get_size()),"scale":var_to_str(node.hero.scale),"pngSha256":FileAccess.get_sha256(folder.path_join(file))})
   detach_audio(node);root.remove_child(node);node.free();pilot=null;await process_frame
 var f:=FileAccess.open(report_path,FileAccess.WRITE);assert(f!=null);f.store_string(JSON.stringify({"passed":true,"cases":rows,"flags":args,"artMotionApproval":false},"  "));f.close()
 var previous:=AudioServer.get_time_since_last_mix();var mixes:=0;var deadline:=Time.get_ticks_usec()+300000
 while mixes<2 and Time.get_ticks_usec()<deadline:
  await process_frame
  var age:=AudioServer.get_time_since_last_mix()
  if age<previous:mixes+=1
  previous=age
 assert(mixes==2)
 print("FEXP_NORMAL_CLI_PACK_OK cases=6")
 quit(0)
