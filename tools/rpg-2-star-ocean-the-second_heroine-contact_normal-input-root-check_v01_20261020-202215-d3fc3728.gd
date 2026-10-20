extends SceneTree
# Controlled normal-arena input probe, real packed art, no renderer subclass/pose replacement.
# Ally attack cooldowns/enemy cooldown held high to isolate heroine timing. Not a human playtest.
const FLOOR_Y := 272
var app: Node
var arena: Node2D
var battle_script: GDScript
var checks := 0
var failures := []
var out := ""
var package_index := ""
var records := []
func _initialize() -> void:
 call_deferred("run")
func ck(ok: bool, label: String) -> void:
 checks += 1
 if not ok: failures.append(label);print("ROOT_CONTACT_FAIL ",label)
func snapshot(label: String) -> Dictionary:
 var fr: Dictionary = arena.combat_sprite_sets.current_frame(0)
 var f: Dictionary = arena.fighters[0]
 return {"label":label,"enemyHP":arena.enemy_hp,"event":f.get("contact_event_id"),"clock":f.get("contact_event_clock"),"active":f.get("contact_event_active"),"state":f.get("contact_event_state"),"sprite":fr,"finished":arena.battle_finished,"outcomes":arena.contact_event_log.duplicate(true)}
func setup(lang: String, plate: bool) -> void:
 if is_instance_valid(arena):
  arena.queue_free(); await process_frame
 Input.action_release("battle_attack");Input.action_release("battle_dodge")
 app.begin_new_run();app.hero_appearance="female"
 app.recruit_member("liang-xu");app.recruit_member("zhao-ling");app.ji_records_checked=true;app.recruit_member("ji-cheng")
 app.select_destination("scifi.outskirts" if plate else "scifi.city")
 if app.language!=lang:app.toggle_language()
 app.begin_battle("patrol" if plate else "sentry",Vector2(330,215))
 battle_script.combat_sprite_set_override=1;battle_script.combat_sprite_set_index_override=package_index
 battle_script.heroine_sea_contact_override=1;battle_script.battle_backdrop_override=1 if plate else 0;battle_script.sentry_v2_override=0
 arena=load("res://scenes/battle_arena.tscn").instantiate();arena.set_process(false);root.add_child(arena);current_scene=arena
 await process_frame
 arena.set_process(false)
 arena.fighters[0]["x"]=300.0;arena.enemy_x=350.0;arena.enemy_cooldown=999.0;arena.enemy_windup=0.0
 for i in range(1,arena.fighters.size()):arena.fighters[i]["attack_cooldown"]=999.0
 ck(arena.combat_sprite_sets.has_set(0),"actual heroine package loads")
 ck(arena.combat_sprite_sets.sets[0]["draw_cell"]==Vector2i(68,72),"actual draw dimensions")
func step(dt: float) -> void:
 arena._process(dt)
 await process_frame
func picture(label: String) -> void:
 arena.queue_redraw();await process_frame;await RenderingServer.frame_post_draw
 var img: Image=root.get_texture().get_image();ck(img.get_size()==Vector2i(1280,720),"native backing size")
 var file: String="rpg-2-star-ocean-the-second_heroine-contact_"+label+"_normal-input-v01_"+OS.get_cmdline_user_args()[2]+".png"
 ck(img.save_png(out.path_join(file))==OK,"capture saved "+label)
 var r:=snapshot(label);r["capture"]=file;r["sha256"]=FileAccess.get_sha256(out.path_join(file));records.append(r)
func run() -> void:
 app=root.get_node("AppState");battle_script=load("res://scripts/battle_arena.gd")
 var args:=OS.get_cmdline_user_args();out=args[0];package_index=args[1]
 root.size=Vector2i(1280,720);await process_frame
 for fps in [30,60]:
  await setup("en" if fps==30 else "zh",fps==30)
  var hp: int=arena.enemy_hp
  Input.action_press("battle_attack");await step(1.0/fps);Input.action_release("battle_attack")
  ck(arena.enemy_hp==hp and arena.fighters[0]["contact_event_clock"]==0.0,"request has zero age/damage "+str(fps))
  await picture(str(fps)+"fps-request")
  for i in range(5*fps/30-1): await step(1.0/fps)
  ck(arena.enemy_hp==hp,"no damage before contact "+str(fps))
  await picture(str(fps)+"fps-before-contact")
  await step(1.0/fps)
  ck(arena.enemy_hp<hp and arena.contact_event_log.size()==1,"exactly one contact "+str(fps))
  ck(arena.combat_sprite_sets.current_frame(0)["frame"]==3,"authored contact frame "+str(fps))
  await picture(str(fps)+"fps-contact")
  for i in range(10):await step(1.0/fps)
  ck(arena.contact_event_log.size()==1,"no duplicate after contact "+str(fps))
  # A finishing contact must still visibly show the contact pose when results begin.
  await setup("en" if fps==30 else "zh",fps==30);arena.enemy_hp=5
  Input.action_press("battle_attack");await step(1.0/fps);Input.action_release("battle_attack")
  for i in range(5*fps/30):await step(1.0/fps)
  ck(arena.battle_finished and arena.battle_won,"finishing contact ends battle "+str(fps))
  var final_frame: Dictionary=arena.combat_sprite_sets.current_frame(0)
  ck(final_frame["action"]=="attack" and final_frame["frame"]==3,"finishing hit remains visible at contact "+str(fps))
  ck(not arena.result_overlay.visible and arena.result_button.disabled,"result cannot obscure or skip finishing contact "+str(fps))
  await picture(str(fps)+"fps-finishing-contact")
  var xp: int=arena.result_reward_xp
  for i in range(30):await step(1.0/fps)
  ck(arena.result_reward_xp==xp and arena.contact_event_log.size()==1,"finishing reward/contact exactly once "+str(fps))
  ck(not arena.fighters[0]["contact_event_active"] and arena.combat_sprite_sets.current_frame(0)["action"]!="attack","finishing recovery ends without orphan presentation "+str(fps))
  ck(arena.result_overlay.visible and not arena.result_button.disabled,"result revealed after finishing recovery "+str(fps))
 var report:={"checks":checks,"failures":failures,"records":records,"normalArena":true,"actualPackedArt":true,"scriptedInput":true,"humanPlaytest":false,"defaultAdoption":false,"artApproved":false,"arenaSHA256":FileAccess.get_sha256("res://scripts/battle_arena.gd"),"loaderSHA256":FileAccess.get_sha256("res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd"),"index":package_index}
 var f:=FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_heroine-contact_normal-input-proof_v01_"+args[2]+".json"),FileAccess.WRITE);f.store_string(JSON.stringify(report," "));f.close()
 if failures.is_empty():print("ROOT_NORMAL_CONTACT_PASS checks=",checks);quit(0)
 else:print("ROOT_NORMAL_CONTACT_FAILED checks=",checks," failures=",failures);quit(1)
