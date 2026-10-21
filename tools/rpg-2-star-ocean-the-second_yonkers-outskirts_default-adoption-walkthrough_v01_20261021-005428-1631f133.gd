extends SceneTree
# Actual scene + ordinary action/button paths; deterministic manual fixed-step automation, not human play.
var app: Node
var mode := ""
var folder := ""
var tag := ""
var checks := 0
var failures := []
var cases := []
func _initialize(): call_deferred("run")
func ck(ok: bool, label: String):
 checks += 1
 if not ok: failures.append(label); print("OUTSKIRTS_NATIVE_FAIL ", label)
func settle():
 for i in 4: await process_frame
func area():
 var s=current_scene
 s.set_process(false)
 return s
func event(s: Node, action: String):
 var e:=InputEventAction.new();e.action=action;e.pressed=true;s._unhandled_input(e)
func move(s: Node, to: Vector2, label: String, encounter: bool=false):
 var steps := 0
 for axis in 2:
  for i in 400:
   if s.encounter_count > 0:break
   var delta:float=(to.x-s.hero.position.x) if axis==0 else (to.y-s.hero.position.y)
   if absf(delta)<2.4:break
   var act:String=("move_right" if delta>0 else "move_left") if axis==0 else ("move_down" if delta>0 else "move_up")
   Input.action_press(act);s._process(1.0/60);Input.action_release(act);steps+=1
 ck(s.encounter_count>0 if encounter else s.hero.position.distance_to(to)<3.5,label)
 return {"label":label,"steps":steps,"position":[s.hero.position.x,s.hero.position.y],"encounter":s.encounter_count,"relay":app.relay_checked,"bypass":app.machine_observed,"traces":app.field_trace_count("scifi.outskirts")}
func shot(s: Node,label:String):
 s.queue_redraw();await process_frame;await RenderingServer.frame_post_draw
 var n="rpg-2-star-ocean-the-second_yonkers-outskirts-adopted_"+label+"_"+mode+"_"+tag+".png"
 var im=root.get_texture().get_image();ck(im.get_size()==Vector2i(640,360),"native viewport "+label);ck(im.save_png(folder.path_join(n))==OK,"save "+label);return n
func fresh(language:String):
 if current_scene!=null:current_scene.queue_free();current_scene=null;await process_frame
 app.begin_new_run();app.hero_appearance="female";app.select_destination("scifi.outskirts")
 if app.language!=language:app.toggle_language()
 change_scene_to_file("res://scenes/scifi_exploration_area.tscn");await settle();return area()
func run():
 var args=OS.get_cmdline_user_args();folder=args[0];tag=args[1];mode=args[2];root.size=Vector2i(640,360);DirAccess.make_dir_recursive_absolute(folder)
 app=root.get_node("AppState");SaveStore.root_path="user://test-saves/outskirts-native-"+tag
 for lang in ["en","zh"]:
  seed(88124)
  var s=await fresh(lang);ck(s.destination_id=="scifi.outskirts","outskirts scene");ck(s.hero.position==Vector2(82,260),"spawn unchanged")
  if mode=="default":ck(s.outskirts_native_active,"native selector loaded")
  var captures={"entry":await shot(s,lang+"-entry")};var trace=[]
  trace.append(move(s,Vector2(125,240),"trace1 approach"));event(s,"interact");ck(s.dialogue_mode=="trace" and app.field_trace_count("scifi.outskirts")==1,"trace1 real interaction");s.later_button.pressed.emit()
  trace.append(move(s,Vector2(125,150),"npc north approach"));trace.append(move(s,Vector2(190,150),"npc approach"));event(s,"interact");ck(s.dialogue_open,"recruit dialogue");s.invite_button.pressed.emit();ck(app.recruited_members.has("zhao-ling"),"recruit Zhao")
  trace.append(move(s,Vector2(190,95),"north path"));trace.append(move(s,Vector2(408,95),"trace2 approach"));event(s,"interact");ck(app.field_trace_count("scifi.outskirts")==2,"trace2 real interaction");s.later_button.pressed.emit()
  trace.append(move(s,Vector2(470,128),"relay approach"));event(s,"interact");ck(app.relay_checked,"relay interaction");captures["relay"]=await shot(s,lang+"-relay")
  var saved_position:Vector2=s.hero.position;s.save_button.pressed.emit();await settle();var saves=current_scene;ck(saves.name=="SaveScreen","real save screen");saves.manual_save_buttons[0].pressed.emit();ck(saves.manual_load_buttons[0].disabled==false,"manual slot exists");saves.manual_load_buttons[0].pressed.emit();await settle();s=area();ck(s.hero.position==saved_position and app.relay_checked and app.field_trace_count("scifi.outskirts")==2,"save and load exact position/state")
  trace.append(move(s,Vector2(575,128),"bypass path"));trace.append(move(s,Vector2(575,258),"east path"));trace.append(move(s,Vector2(505,258),"assist approach"));event(s,"interact");ck(s.dialogue_mode=="assist","field assist dialogue");s.invite_button.pressed.emit();ck(app.field_insights.has("scifi.outskirts"),"field assist completion");s.later_button.pressed.emit()
  trace.append(move(s,Vector2(558,277),"survey approach"));var return_position:Vector2=s.hero.position;event(s,"interact");await settle();var annex=current_scene;ck(annex.room==1,"normal annex entry");annex.back_button.pressed.emit();await settle();s=area();ck(s.hero.position==return_position and s.destination_id=="scifi.outskirts","exact annex return")
  var surface={"trace":trace,"relay":app.relay_checked,"traces":app.field_trace_count("scifi.outskirts"),"assist":app.field_insights.has("scifi.outskirts"),"annexReturn":[s.hero.position.x,s.hero.position.y]}
  s=await fresh(lang);app.recruit_member("liang-xu");app.recruit_member("zhao-ling");app.ji_records_checked=true;app.recruit_member("ji-cheng")
  var battle_approach=move(s,Vector2(355,238),"normal encounter approach",true);await settle();var battle=current_scene;battle.set_process(false);ck(battle.name=="BattleArena","normal patrol encounter");battle._toggle_auto()
  for i in 700:
   battle._process(1.0/60)
   if battle.battle_finished:break
  ck(battle.battle_finished and battle.battle_won,"natural normal battle victory");var safe:Vector2=app.battle_return_position;battle.result_button.pressed.emit();await settle();s=area();ck(s.destination_id=="scifi.outskirts" and s.hero.position==safe and not s.enemy_visible,"safe battle return")
  if mode=="default":ck(s.outskirts_native_active,"native selector survives return")
  captures["battleReturn"]=await shot(s,lang+"-battle-return");cases.append({"language":lang,"surface":surface,"battleApproach":battle_approach,"safeReturn":[safe.x,safe.y],"captures":captures})
 if current_scene!=null:current_scene.queue_free();current_scene=null;await process_frame
 var report={"mode":mode,"checks":checks,"failures":failures,"cases":cases,"areaRawSha256":FileAccess.get_sha256("res://scripts/scifi_exploration_area.gd"),"harnessRawSha256":FileAccess.get_sha256(get_script().resource_path),"scope":"Real scene and ordinary action/button callbacks; manual fixed-step Input walkthrough; normal recruitment and no stat/HP/cooldown injection. Not a human playtest or art approval."}
 var f=FileAccess.open(folder.path_join("rpg-2-star-ocean-the-second_yonkers-outskirts-adopted_runtime-proof_"+mode+"_"+tag+".json"),FileAccess.WRITE);f.store_string(JSON.stringify(report," ")+"\n");f.close()
 if failures.is_empty():print("OUTSKIRTS_DEFAULT_PASS checks=",checks);quit(0)
 else:quit(1)
