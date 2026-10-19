extends SceneTree
var checks: Array=[]
var out: String
var app: Node
var current_arena: Node2D
const TAG="20261019-002430-8f76aebf"
func ck(key: String, ok: bool) -> void: checks.append({"key":key,"pass":ok})
func _initialize() -> void: call_deferred("run")
func setup(script: Script, enabled: int, common: int=0) -> Node2D:
 app.begin_new_run()
 app.language="en"
 app.hero_appearance="female"
 app.recruit_member("liang-xu")
 app.recruit_member("zhao-ling")
 app.ji_records_checked=true
 app.recruit_member("ji-cheng")
 app.select_destination("scifi.city")
 app.begin_battle("patrol",Vector2(330,215))
 script.sentry_v2_override=0
 script.combat_sprite_set_override=0
 script.battle_vfx_override=common
 if script==load("res://scripts/battle_arena.gd"): script.encounter_feedback_override=enabled
 seed(43821)
 var arena=script.new()
 root.add_child(arena)
 current_scene=arena
 arena.set_process(false)
 return arena
func snapshot(arena: Node2D) -> Dictionary:
 return {"enemy_hp":arena.enemy_hp,"enemy_x":arena.enemy_x,"enemy_windup":arena.enemy_windup,"enemy_cooldown":arena.enemy_cooldown,"fighters":arena.fighters.duplicate(true),"finished":arena.battle_finished,"won":arena.battle_won,"hero":app.hero_state.duplicate(true),"members":app.member_states.duplicate(true)}
func result_frames_clear_ui(arena: Node2D) -> bool:
 for event in arena.encounter_feedback.events:
  for texture in arena.encounter_feedback._frames_by_kind[event.kind]:
   var used: Rect2i=texture.get_image().get_used_rect()
   if not used.has_area():continue
   var box=Rect2(event.origin-Vector2(64,48)+Vector2(used.position),Vector2(used.size))
   if box.position.y<90 or box.end.y>302 or box.position.x<0 or box.end.x>640:return false
   if box.intersects(Rect2(136,110,368,156)):return false
 return true
func dispose(arena: Node2D) -> void:
 arena.queue_free()
 await process_frame
func shot(arena: Node2D, label: String) -> Image:
 arena.queue_redraw()
 await process_frame
 await RenderingServer.frame_post_draw
 var image=root.get_texture().get_image()
 image.convert(Image.FORMAT_RGBA8)
 ck("capture-"+label,image.save_png(out.path_join("rpg-2-star-ocean-the-second_encounter-feedback_"+label+"_actual-640_v01_"+TAG+".png"))==OK)
 return image
func run() -> void:
 out=OS.get_cmdline_user_args()[1]
 DirAccess.make_dir_recursive_absolute(out)
 root.size=Vector2i(640,360)
 root.content_scale_size=Vector2i(640,360)
 root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 await process_frame
 SaveStore.root_path="user://encounter-feedback-coordinator-only"
 app=root.get_node("AppState")
 var baseline=load(OS.get_cmdline_user_args()[0])
 var candidate=load("res://scripts/battle_arena.gd")
 var old=setup(baseline,0)
 var old_image=await shot(old,"baseline-off")
 await dispose(old)
 var off=setup(candidate,0)
 ck("forced-off-null",off.encounter_feedback==null)
 ck("forced-off-no-foreground-layer",off.encounter_result_layer==null and off.encounter_result_surface==null)
 var off_image=await shot(off,"candidate-off")
 ck("default-render-zero-pixel-difference",old_image.get_data()==off_image.get_data())
 await dispose(off)
 var histories=[]
 for item in [{"script":baseline,"on":0},{"script":candidate,"on":0},{"script":candidate,"on":1}]:
  var arena=setup(item.script,item.on)
  arena.auto_mode=true
  var history=[]
  for tick in 600:
   arena._process(1./60.)
   history.append(snapshot(arena))
  histories.append(history)
  await dispose(arena)
 for tick in 600:
  ck("off-simulation-"+str(tick),histories[0][tick]==histories[1][tick])
  ck("on-simulation-"+str(tick),histories[0][tick]==histories[2][tick])
 var arena=setup(candidate,1,1)
 ck("encounter-on-ready",arena.encounter_feedback.events.size()==1 and arena.encounter_feedback.events[0].kind=="encounter")
 ck("encounter-keeps-normal-actor-layer",is_instance_valid(arena.encounter_result_surface) and not arena.encounter_result_surface.visible)
 ck("common-coexists",arena.battle_vfx!=null)
 arena.encounter_feedback.advance(.2)
 await shot(arena,"encounter-en")
 var age=arena.encounter_feedback.events[0].age
 arena.paused=true
 arena._process(.1)
 ck("paused-feedback-freezes",arena.encounter_feedback.events[0].age==age)
 arena.paused=false
 arena.encounter_feedback.advance(1.)
 var before=arena.encounter_feedback.emitted
 arena._finish_battle(true)
 ck("victory-exactly-once",arena.encounter_feedback.events.filter(func(e):return e.kind=="victory").size()==1)
 ck("results-use-foreground-surface",arena.encounter_result_surface.visible and arena.encounter_result_layer.layer>0 and arena._encounter_result_surface_draws())
 ck("all-result-frame-bounds-clear-panel-text-and-hud",result_frames_clear_ui(arena))
 var living=0
 for i in arena.fighters.size():
  if arena._is_alive(i):living+=1
 ck("recovery-matches-existing-recovered-living-party",arena.encounter_feedback.events.filter(func(e):return e.kind=="recovery").size()==living)
 var count=arena.encounter_feedback.emitted
 arena._finish_battle(true)
 ck("duplicate-finish-does-not-emit",arena.encounter_feedback.emitted==count)
 arena._process(.2)
 app.language="zh"
 app.language_changed.emit()
 await shot(arena,"victory-recovery-zh")
 arena._process(1.)
 ck("finished-presentation-expires",arena.encounter_feedback.events.is_empty())
 ck("expired-foreground-surface-hidden",not arena.encounter_result_surface.visible)
 await dispose(arena)
 arena=setup(candidate,1)
 app.language="zh"
 app.language_changed.emit()
 arena.encounter_feedback.advance(1.)
 arena._finish_battle(false)
 ck("defeat-exactly-once",arena.encounter_feedback.events.size()==1 and arena.encounter_feedback.events[0].kind=="defeat")
 arena._process(.25)
 await shot(arena,"defeat-zh")
 await dispose(arena)
 var failed=checks.filter(func(c):return not c.pass)
 var report={"passed":checks.size()-failed.size(),"failed":failed.size(),"checks":checks,"arenaSha256":FileAccess.get_sha256("res://scripts/battle_arena.gd"),"artApproved":false,"pilotOnly":true}
 var file=FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_encounter-feedback_root-arena-report_v01_"+TAG+".json"),FileAccess.WRITE)
 file.store_string(JSON.stringify(report," ")+"\n")
 file.close()
 print(JSON.stringify({"passed":report.passed,"failed":report.failed,"failures":failed}))
 print("ENCOUNTER_ARENA_ROOT_DONE")
 quit(1 if failed.size()>0 else 0)
