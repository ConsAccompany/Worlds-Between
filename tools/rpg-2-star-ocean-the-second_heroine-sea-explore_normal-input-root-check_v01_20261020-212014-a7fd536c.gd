extends SceneTree
# Actual scene movement with the existing generic sprite pilot. One disclosed initial safe placement.
# Registry, output directory, tag, context city|room, fps are user arguments. Not human/art acceptance.
var app:Node
var host:Node
var out:String
var tag:String
var context:String
var fps:int
var rows:=[]
var checks:=0
var failures:=[]
func _initialize()->void:call_deferred("run")
func ck(ok:bool,label:String)->void:
 checks+=1
 if not ok:failures.append(label);print("EXP_ROOT_FAIL ",label)
func tick()->void:
 await process_frame
 await RenderingServer.frame_post_draw
func shot(label:String)->void:
 var img:=root.get_texture().get_image()
 ck(img.get_size()==Vector2i(1280,720),"actual1280capture "+label)
 var file:="rpg-2-star-ocean-the-second_heroine-sea-explore_%s-%s_actual-input-v01_%s.png"%[context,label,tag]
 ck(img.save_png(out.path_join(file))==OK,"save "+label)
func run()->void:
 var args:=OS.get_cmdline_user_args();out=args[1];tag=args[2];context=args[3];fps=int(args[4])
 app=root.get_node("AppState");app.begin_new_run();app.hero_appearance="female";app.language="en" if context=="city" else "zh";app.select_destination("scifi.city");app.current_annex_room=2
 var loader=load("res://scripts/exploration_sprite_set_pilot.gd");loader.enabled_override=1;loader.registry_override=args[0]
 var scene:="res://scenes/scifi_exploration_area.tscn" if context=="city" else "res://scenes/survey_annex.tscn"
 ck(change_scene_to_file(scene)==OK,"normal scene entry")
 for i in 3:await tick()
 host=current_scene;host.hero.position=Vector2(270,210)
 ck(host.sprite_pilot!=null,"existing normal-scene pilot attached")
 if host.sprite_pilot==null:quit(1);return
 ck(host.sprite_pilot.actor_id=="protagonist-female","actual host actor key")
 ck(host.hero.scale==Vector2(0.5,0.5),"48logical display scale")
 ck(host.hero.texture.get_size()==Vector2(80,112),"actual source cell")
 var plan:=[['south','move_down'],['north','move_up'],['west','move_left'],['east','move_right']]
 for item in plan:
  var before:Vector2=host.hero.position
  Input.action_press(item[1])
  var seen:={}
  for i in int(fps*0.58):
   await tick()
   var state:Dictionary=host.sprite_pilot.state();seen[int(state.frame)]=true
   rows.append({"direction":item[0],"frame":i,"state":state,"position":[host.hero.position.x,host.hero.position.y]})
   if i==int(fps*0.25):shot(item[0]+"-walk")
  Input.action_release(item[1]);await tick();await tick()
  ck(host.hero.position.distance_to(before)>10.,"real movement "+item[0])
  ck(host.sprite_pilot.action=="idle" and host.sprite_pilot.facing==item[0],"normal release to idle "+item[0])
  ck(seen.size()>=6,"walk phases genuinely advanced "+item[0])
  shot(item[0]+"-idle")
  for i in int(fps*0.18):await tick()
 var report:={"checks":checks,"failures":failures,"trace":rows,"context":context,"fps":fps,"registry":args[0],"declaredInitialPlacement":[270,210],"normalSceneInput":true,"defaultAdoption":false,"humanPlaytest":false,"artApproved":false,"limits":"Existing generic loader switches directly walk to idle; no authored stop/transition fluency acceptance implied."}
 var f:=FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_heroine-sea-explore_%s-root-proof_v01_%s.json"%[context,tag]),FileAccess.WRITE);f.store_string(JSON.stringify(report," "));f.close()
 host.queue_free();await process_frame;loader.clear_cache()
 if failures.is_empty():print("EXP_NORMAL_ROOT_PASS checks=",checks);quit(0)
 else:print("EXP_NORMAL_ROOT_FAIL ",failures);quit(1)
