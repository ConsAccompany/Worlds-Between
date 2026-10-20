extends SceneTree
var failures: Array[String] = []
var output := ""
var capture_tag := ""
func _initialize():
 call_deferred("run")
func need(ok: bool, label: String):
 if not ok: failures.append(label)
func run():
 for a in OS.get_cmdline_user_args():
  if a.begins_with("--capture-dir="): output = a.trim_prefix("--capture-dir=")
  if a.begins_with("--capture-tag="): capture_tag = a.trim_prefix("--capture-tag=")
 need(not output.is_empty() and not capture_tag.is_empty(), "unique output")
 var app = root.get_node("AppState")
 var arena = load("res://scripts/battle_arena.gd")
 var loader_path = arena.PATROL_ANIMATION_LOADER
 # Runtime uses ResourceLoader.load, which resolves exported compiled script remaps.
 # It does not consume raw source via FileAccess; source hashes are frozen at export.
 need(ResourceLoader.exists(loader_path), "compiled loader remap included")
 need(load(loader_path) != null, "compiled loader resolves")
 root.size = Vector2i(640,360)
 Engine.max_fps = 60
 for lang in ["en","zh"]:
  for enemy_id in ["patrol","sentry"]:
   app.begin_new_run()
   app.hero_appearance="male"
   app.recruit_member("liang-xu")
   app.recruit_member("zhao-ling")
   app.ji_records_checked = true
   app.recruit_member("ji-cheng")
   app.select_destination("scifi.outskirts" if enemy_id=="patrol" else "scifi.ruins")
   if app.language!=lang: app.toggle_language()
   app.begin_battle(enemy_id,Vector2(330,215))
   var battle=load("res://scenes/battle_arena.tscn").instantiate()
   root.add_child(battle)
   for i in range(5): await process_frame
   need(battle.enemy_id==enemy_id,"normal enemy selected")
   need((battle.enemy_animation_texture!=null)==(enemy_id=="patrol"), "optional patrol loaded / sentry untouched")
   if enemy_id=="patrol":
    need(battle.enemy_animation.states.size()==6,"all states")
    need(battle.enemy["max_hp"]==64 and battle.enemy["damage"]==12,"protected stats")
    need(FileAccess.file_exists(arena.PATROL_ANIMATION_PACKAGE),"raw package included")
   await RenderingServer.frame_post_draw
   var file=output+"/rpg-2-star-ocean-the-second_patrol_packed-normal-"+enemy_id+"-"+lang+"-640_unapproved-v01_"+capture_tag+".png"
   need(root.get_texture().get_image().save_png(file)==OK,"actual viewport saved")
   for i in range(30): await process_frame
   battle.queue_free()
   await process_frame
   await process_frame
 print("PATROL_PACKED_PROBE "+JSON.stringify({"passed":failures.is_empty(),"failures":failures,"gameplayMutations":false,"artAccepted":false}))
 if failures.is_empty(): print("PATROL_PACKED_PROBE_OK")
 quit(0 if failures.is_empty() else 1)
