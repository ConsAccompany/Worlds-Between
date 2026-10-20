extends SceneTree
# Real scene/autoloads, fixed-step ordinary battle logic and real UI callback. Automated, not a human playtest.
var app: Node
var rows := []
var failures := []
var checks := 0
var out := ""
var tag := ""
var mode := ""
func _initialize() -> void:
 call_deferred("run")
func ck(ok: bool, label: String) -> void:
 checks += 1
 if not ok:
  failures.append(label)
  print("BATTLE_NATIVE_ROOT_FAIL ",label)
func shot(arena: Node, label: String) -> String:
 arena.queue_redraw()
 await process_frame
 await RenderingServer.frame_post_draw
 var path := out.path_join("rpg-2-star-ocean-the-second_battle-native_"+label+"_"+mode+"_"+tag+".png")
 var im := root.get_texture().get_image()
 ck(im.get_size()==Vector2i(640,360),"native viewport "+label)
 ck(im.save_png(path)==OK,"save "+label)
 return path.get_file()
func state(arena: Node) -> Dictionary:
 var members := []
 for f in arena.fighters:
  var member: Dictionary=app.member_state(String(f["id"]))
  members.append({"id":f["id"],"x":f["x"],"hp":member["hp"],"energy":member["energy"],"attack_cooldown":f["attack_cooldown"],"skill_cooldown":f["skill_cooldown"],"guard":f["guard"]})
 return {"members":members,"enemy_x":arena.enemy_x,"enemy_hp":arena.enemy_hp,"enemy_windup":arena.enemy_windup,"enemy_cooldown":arena.enemy_cooldown,"finished":arena.battle_finished,"won":arena.battle_won}
func run() -> void:
 var args:=OS.get_cmdline_user_args()
 out=args[0];tag=args[1];mode=args[2]
 DirAccess.make_dir_recursive_absolute(out)
 root.size=Vector2i(640,360)
 app=root.get_node("AppState")
 SaveStore.root_path="user://test-saves/battle-native-root"
 var script=load("res://scripts/battle_arena.gd")
 script.battle_backdrop_override=1 if mode=="plate" else 0
 for enemy in ["patrol","sentry"]:
  for language in ["en","zh"]:
   seed(94129)
   app.begin_new_run();app.hero_appearance="female"
   app.recruit_member("liang-xu");app.recruit_member("zhao-ling");app.ji_records_checked=true;app.recruit_member("ji-cheng")
   app.select_destination("scifi.outskirts")
   if app.language!=language:app.toggle_language()
   app.begin_battle(enemy,Vector2(330,215))
   var arena=load("res://scenes/battle_arena.tscn").instantiate()
   root.add_child(arena);current_scene=arena
   arena.set_process(false)
   ck(arena.fighters.size()==4,"normal four-person party")
   var initial:=state(arena)
   var label: String=enemy+"-"+language
   var captures := {"entry":await shot(arena,label+"-entry")}
   ck(arena.battle_backdrop_status==("off" if mode=="default" else "loaded"),"backdrop selection "+label)
   if mode!="default":ck(arena.battle_backdrop_texture.get_size()==Vector2(640,212),"native band "+label)
   Input.action_press("move_right")
   for i in 6:arena._process(1.0/60)
   Input.action_release("move_right")
   ck(absf(float(arena.fighters[0]["x"])-151.8)<0.001,"unchanged168speed "+label)
   var trace: Array=[state(arena)]
   arena._toggle_auto()
   for i in 600:
    arena._process(1.0/60)
    trace.append(state(arena))
    if i==30:captures["combat"]=await shot(arena,label+"-combat")
    if arena.battle_finished:break
   ck(arena.battle_finished and arena.battle_won,"natural AI victory "+label)
   captures["result"]=await shot(arena,label+"-result")
   var final:=state(arena)
   ck(arena.result_overlay.visible,"real result overlay "+label)
   arena.result_button.pressed.emit()
   for i in 4:await process_frame
   ck(app.current_destination_id=="scifi.outskirts" and app.battle_enemy_id=="","safe result return "+label)
   rows.append({"enemy":enemy,"language":language,"initial":initial,"trace":trace,"final":final,"captures":captures,"safeReturn":true,"geometry":{"floorY":272,"heroClamp":[28,612],"band":[0,90,640,212]}})
   if current_scene!=null:
    current_scene.queue_free();current_scene=null
    await process_frame
 var report: Dictionary={"mode":mode,"checks":checks,"failures":failures,"cases":rows,"arenaRawSha256":FileAccess.get_sha256("res://scripts/battle_arena.gd"),"harnessRawSha256":FileAccess.get_sha256(get_script().resource_path),"scope":"Normal scene+UI callbacks; manual fixed-step Input/AI. Initial normal party retained. Not human play, art acceptance, new animation or performance benchmark.","artApproved":false,"defaultAdopted":false}
 var f:=FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_battle-native_gameplay-proof_"+mode+"_"+tag+".json"),FileAccess.WRITE)
 f.store_string(JSON.stringify(report," ")+"\n");f.close()
 if failures.is_empty():print("BATTLE_NATIVE_ROOT_PASS checks=",checks);quit(0)
 else:quit(1)
