extends SceneTree
# Source-production pose probe in the real arena. TEST-ONLY: not normal input, default adoption or human playtest.
const Loader = preload("res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd")
var checks: Array = []
var captures: Array = []
var failed := false
var out := ""
var tag := ""
var language := ""
func ck(ok: bool, label: String) -> void:
 checks.append({"check":label,"passed":ok})
 if not ok:
  failed = true
  print("MALE22_FAIL ",label)
func _initialize() -> void:
 call_deferred("run")
 create_timer(45.0).timeout.connect(func(): print("MALE22_TIMEOUT");quit(2))
func tick() -> void:
 await process_frame
 await RenderingServer.frame_post_draw
func run() -> void:
 var args := OS.get_cmdline_user_args()
 if args.size() < 4:
  quit(2)
  return
 var index_path: String = args[0]
 out=args[1];tag=args[2];language=args[3]
 DirAccess.make_dir_recursive_absolute(out)
 root.size=Vector2i(640,360)
 var app := root.get_node("AppState")
 app.begin_new_run()
 app.hero_appearance="male"
 app.language=language
 app.recruit_member("liang-xu")
 app.recruit_member("zhao-ling")
 app.ji_records_checked=true
 app.recruit_member("ji-cheng")
 app.select_destination("ruins" if language=="zh" else "city")
 app.battle_enemy_id="sentry" if language=="zh" else "patrol"
 var host_script=load("res://scripts/battle_arena.gd")
 ck(not host_script.heroine_default_battle_applies(app.active_party_ids,"male"),"male default policy remains off")
 host_script.combat_sprite_set_override=1
 host_script.combat_sprite_set_index_override=index_path
 var scene=load("res://scenes/battle_arena.tscn").instantiate()
 root.add_child(scene)
 scene.set_process(false)
 scene.set_physics_process(false)
 await tick()
 ck(scene.combat_sprite_sets!=null,"explicit source candidate uses actual arena loader")
 if scene.combat_sprite_sets==null:
  quit(1);return
 var model=scene.combat_sprite_sets
 ck(model.loaded_count()==1 and model.has_set(0),"exactly male hero set loaded")
 ck(not scene.heroine_default_active,"heroine ordinary default not overridden by candidate")
 if not model.has_set(0):
  print(model.statuses);quit(1);return
 var source: Dictionary=model.sets[0]
 for action in ["idle","move","guard","attack","dodge","skill","hit","defeat"]:
  ck(source.actions.has(action),"required source action "+action)
  var clip: Dictionary=source.actions[action]
  var actor: Dictionary=scene.fighters[0].duplicate(true)
  actor.visual_action=action if action in ["attack","skill","hit"] else ""
  actor.visual_elapsed=0.0
  actor.guard=action=="guard"
  actor.visual_moving=action=="move"
  actor.dodge_time=0.2 if action=="dodge" else 0.0
  model.states[0].last_visual_action=""
  model.advance(0,actor,action!="defeat",scene.enemy_x,0.0)
  ck(model.current_frame(0).action==action,"combat state selects "+action)
  var distinct := {}
  for i in clip.frames.size():
   var t: float=0.0
   if i > 0: t=float(clip.frames[i-1].end)
   var cell: int=Loader.frame_at(clip,t)
   ck(cell==i,"exact source frame boundary %s/%s"%[action,i])
   distinct[clip.frames[i].cell]=true
  model.states[0].clock=float(clip.duration)*0.45
  scene.queue_redraw()
  await tick()
  var image: Image=root.get_texture().get_image()
  var path=out.path_join("rpg-2-star-ocean-the-second_male-combat_%s-%s_arena-source-probe-v01_%s.png"%[language,action,tag])
  ck(image.get_size()==Vector2i(640,360) and DisplayServer.get_name()!="headless","actual window capture "+action)
  ck(image.save_png(path)==OK,"capture saved "+action)
  captures.append({"action":action,"path":path,"sha256":FileAccess.get_sha256(path),"sourceCell":model.current_frame(0).cell,"distinctCells":distinct.size()})
  # A held oneshot must reach the final authored cell; looping clips wrap to loop_start.
  var end: int=Loader.frame_at(clip,float(clip.duration))
  ck(end==(int(clip.get("loop_start",0)) if clip.loop else clip.frames.size()-1),"clip end behavior "+action)
 var report={"schema":"worlds-between.male-combat-source-probe/1","scope":"actual-arena scripted pose probe; not normal input/default or approval","language":language,"indexPath":index_path,"indexSha256":FileAccess.get_sha256(index_path),"checks":checks,"captures":captures,"passed":not failed}
 var file=FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_male-combat_%s_arena-source-proof-v01_%s.json"%[language,tag]),FileAccess.WRITE)
 file.store_string(JSON.stringify(report,"  ")+"\n")
 print("MALE22_PASS" if not failed else "MALE22_FAILED")
 quit(1 if failed else 0)
