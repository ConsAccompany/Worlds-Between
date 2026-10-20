extends SceneTree
# Explicit resource-order boundary fixtures; these are not natural victories or human playtests.
var app:Node
var arena:Node2D
var arena_script:GDScript
var count:=0
var failed:=[]
func _initialize()->void:
 call_deferred("run")
func ck(ok:bool,label:String)->void:
 count+=1
 if not ok:failed.append(label);print("BONUS_ORDER_FAIL ",label)
func open()->void:
 if is_instance_valid(arena):arena.queue_free();await process_frame
 app.begin_new_run();app.hero_appearance="female";app.recruit_member("liang-xu");app.recruit_member("zhao-ling");app.ji_records_checked=true;app.recruit_member("ji-cheng")
 app.select_destination("scifi.outskirts");app.begin_battle("sentry",Vector2(330,215))
 arena_script.heroine_sea_contact_override=1;arena_script.combat_sprite_set_override=0;arena_script.sentry_v2_override=0
 arena=load("res://scenes/battle_arena.tscn").instantiate();arena.set_process(false);root.add_child(arena);current_scene=arena;await process_frame;arena.set_process(false)
 arena.enemy_x=300.0
 for fighter in arena.fighters:fighter["x"]=270.0
func damage(index:int)->int:
 return int(app.MEMBER_DEFS[String(arena.fighters[index]["id"])]["attack_damage"])
func run()->void:
 app=root.get_node("AppState");arena_script=load("res://scripts/battle_arena.gd")
 var saves:GDScript=load("res://scripts/save_store.gd");saves.root_path="user://test-saves/shared-bonus-root"
 await open()
 var hp:int=arena.enemy_hp
 var hd:=damage(0);var ad:=damage(1)
 arena.next_attack_bonus=10;arena.fighters[0]["boost"]=3
 ck(arena._try_attack(0),"hero pending request starts")
 ck(arena.enemy_hp==hp and arena.next_attack_bonus==10 and arena.fighters[0]["boost"]==3,"request does not reserve shared or own bonus")
 ck(arena._try_attack(1),"ally hit before hero contact")
 ck(arena.enemy_hp==hp-ad-10 and arena.next_attack_bonus==0,"ally consumes shared bonus once at earlier hit")
 arena._advance_contact_events(5.0/30.0)
 ck(arena.enemy_hp==hp-ad-10-hd-3 and arena.fighters[0]["boost"]==0,"hero later contact consumes only own boost")
 arena._advance_contact_events(0.5)
 ck(arena.enemy_hp==hp-ad-10-hd-3 and arena.contact_event_log.size()==1,"no duplicated delayed hit/bonus")
 await open();hp=arena.enemy_hp;hd=damage(0);ad=damage(1);arena.next_attack_bonus=10
 arena._try_attack(0);arena._advance_contact_events(5.0/30.0)
 ck(arena.enemy_hp==hp-hd-10 and arena.next_attack_bonus==0,"hero first contact consumes shared bonus")
 arena._try_attack(1)
 ck(arena.enemy_hp==hp-hd-10-ad,"later ally receives no duplicate shared bonus")
 await open();hp=arena.enemy_hp;hd=damage(0);arena._try_attack(0);arena._use_skill(2)
 var generated:int=8*int(app.member_state("zhao-ling").get("personal_skill_rank",1))
 ck(arena.next_attack_bonus==generated and arena.fighters[0]["contact_event_active"],"other fighter skill can add shared bonus without interrupting hero")
 arena._advance_contact_events(5.0/30.0)
 ck(arena.enemy_hp==hp-hd-generated and arena.next_attack_bonus==0,"new bonus belongs to first successful contact")
 await open();hp=arena.enemy_hp;ad=damage(1);arena.next_attack_bonus=10;arena.fighters[0]["boost"]=3;arena._try_attack(0);arena._try_dodge(0)
 ck(arena.next_attack_bonus==10 and arena.fighters[0]["boost"]==3,"cancellation retains unspent bonuses")
 arena._try_attack(1);arena._advance_contact_events(1.0)
 ck(arena.enemy_hp==hp-ad-10 and arena.fighters[0]["boost"]==3,"cancelled hero never steals bonus or applies orphan damage")
 await open();hp=arena.enemy_hp;arena.next_attack_bonus=10;var d1:=damage(1);var d2:=damage(2)
 arena._try_attack(1);arena._try_attack(2)
 ck(arena.enemy_hp==hp-d1-10-d2 and arena.next_attack_bonus==0,"two immediate allies in one step consume shared bonus once")
 # Staged low-HP boundary, separate from natural-encounter evidence.
 await open();arena.enemy_hp=damage(1);arena._try_attack(0);arena._try_attack(1)
 ck(arena.battle_finished and arena.battle_won and arena.enemy_hp==0,"ally finishing hit wins while hero pending")
 ck(not arena.fighters[0]["contact_event_active"] and arena.contact_event_log.size()==1 and arena.contact_event_log[0]["outcome"]=="cancelled_result","ally result cancels pending hero event")
 var xp:int=arena.result_reward_xp;var jp:int=arena.result_reward_jp
 arena._advance_contact_events(1.0)
 ck(arena.enemy_hp==0 and arena.result_reward_xp==xp and arena.result_reward_jp==jp and arena.contact_event_log.size()==1,"no extra reward or hit behind ally results")
 var report:={"checks":count,"failures":failed,"stagedBoundaryFixtures":true,"naturalVictory":false,"humanPlaytest":false,"arenaRawSHA256":FileAccess.get_sha256("res://scripts/battle_arena.gd")}
 var args:=OS.get_cmdline_user_args()
 if args.size()>0:
  var file:=FileAccess.open(args[0],FileAccess.WRITE);file.store_string(JSON.stringify(report," "));file.close()
 if failed.is_empty():print("ROOT_SHARED_BONUS_PASS checks=",count);quit(0)
 else:print("ROOT_SHARED_BONUS_FAIL ",failed);quit(1)
