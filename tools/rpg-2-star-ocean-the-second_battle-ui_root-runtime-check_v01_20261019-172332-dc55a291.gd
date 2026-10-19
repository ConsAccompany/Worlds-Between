extends SceneTree
var checks:Array=[]
var app:Node
var candidate:Script
var baseline:Script
var out:String
const TAG="20261019-172332-dc55a291"
func ck(k:String,v:bool)->void:checks.append({"key":k,"pass":v})
func _initialize()->void:call_deferred("run")
func setup(script:Script,mode:int,lang:String)->Node2D:
 app.begin_new_run()
 app.language=lang
 app.hero_appearance="female"
 app.recruit_member("liang-xu")
 app.recruit_member("zhao-ling")
 app.ji_records_checked=true
 app.recruit_member("ji-cheng")
 app.select_destination("scifi.city")
 app.begin_battle("patrol",Vector2(330,215))
 script.battle_vfx_override=0
 script.encounter_feedback_override=0
 script.skill_vfx_override=0
 script.sentry_v2_override=0
 script.combat_sprite_set_override=0
 if script==candidate:script.battle_ui_skin_override=mode
 seed(4832)
 var a=script.new()
 root.add_child(a)
 current_scene=a
 a.set_process(false)
 return a
func dispose(a:Node2D)->void:
 a.queue_free()
 await process_frame
func state(a:Node2D)->Dictionary:return {"fighters":a.fighters.duplicate(true),"enemy_hp":a.enemy_hp,"enemy_x":a.enemy_x,"cooldown":a.enemy_cooldown,"windup":a.enemy_windup,"finished":a.battle_finished,"won":a.battle_won,"hero":app.hero_state.duplicate(true),"members":app.member_states.duplicate(true),"queuedSkill":a.queued_skill,"queuedJob":a.queued_job_skill}
func controls(a:Node2D)->Array:
 var rows=[]
 for n in a.find_children("*","Control",true,false):
  if not n.is_visible_in_tree() or n.name=="BattleUiSkinPilotPlate":continue
  var text=String(n.text) if n is Button or n is Label else ""
  var row=[n.get_class(),n.get_global_rect(),n.get_combined_minimum_size(),text,n.get_theme_font_size("font_size")]
  if n is Button:
   var methods=[]
   for conn in n.pressed.get_connections():methods.append(String(conn.callable.get_method()))
   row.append([n.disabled,n.focus_mode,methods])
  rows.append(row)
 return rows
func context(a:Node2D,mode:String)->void:
 if mode=="pause":a._toggle_pause()
 elif mode=="victory":a._finish_battle(true)
 elif mode=="defeat":a._finish_battle(false)
func shot(a:Node2D,label:String)->Image:
 a.queue_redraw()
 await process_frame
 await RenderingServer.frame_post_draw
 var im=root.get_texture().get_image()
 im.convert(Image.FORMAT_RGBA8)
 ck("saved-"+label,im.save_png(out.path_join("rpg-2-star-ocean-the-second_battle-ui_"+label+"_actual-640_v01_"+TAG+".png"))==OK)
 return im
func click_at(at:Vector2)->void:
 var motion=InputEventMouseMotion.new()
 motion.position=at
 root.push_input(motion,true)
 for pressed in [true,false]:
  var event=InputEventMouseButton.new()
  event.position=at
  event.button_index=MOUSE_BUTTON_LEFT
  event.pressed=pressed
  root.push_input(event,true)
func run()->void:
 var args=OS.get_cmdline_user_args()
 baseline=load(args[0])
 candidate=load("res://scripts/battle_arena.gd")
 out=args[1]
 DirAccess.make_dir_recursive_absolute(out)
 root.size=Vector2i(640,360)
 root.content_scale_size=Vector2i(640,360)
 root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 await process_frame
 app=root.get_node("AppState")
 SaveStore.root_path="user://battle-ui-root"
 var b=setup(baseline,0,"en")
 var bimage=await shot(b,"baseline-default")
 await dispose(b)
 var off=setup(candidate,-1,"en")
 ck("default-skin-absent",off.battle_ui_skin==null and off.battle_ui_skin_status=="off")
 var offimage=await shot(off,"candidate-default-off")
 ck("default-zero-pixel-difference",bimage.get_data()==offimage.get_data())
 await dispose(off)
 var traces=[]
 for item in [{"script":baseline,"on":0},{"script":candidate,"on":0},{"script":candidate,"on":1}]:
  var a=setup(item.script,item.on,"en")
  a.auto_mode=true
  if item.on==1:ck("skin-applied-in-ready",a.battle_ui_skin_status=="applied")
  var rows=[]
  for tick in 600:
   a._process(1./60.)
   rows.append(state(a))
  traces.append(rows)
  await dispose(a)
 for tick in 600:
  ck("off-combat-parity-"+str(tick),traces[0][tick]==traces[1][tick])
  ck("on-combat-parity-"+str(tick),traces[0][tick]==traces[2][tick])
 for language in ["en","zh"]:
  for mode in ["normal","pause","victory","defeat"]:
   var contexts=[]
   for enabled in [0,1]:
    var a=setup(candidate,enabled,language)
    context(a,mode)
    await process_frame
    await process_frame
    contexts.append(controls(a))
    if enabled==1:
     ck(language+"-"+mode+"-applied",a.battle_ui_skin_status=="applied")
     var plates=[]
     for n in a.find_children("*","NinePatchRect",true,false):
      if n.name=="BattleUiSkinPilotPlate":plates.append(n)
     ck(language+"-"+mode+"-four-nonblocking-plates",plates.size()==4 and plates.all(func(n):return n.mouse_filter==Control.MOUSE_FILTER_IGNORE and n.focus_mode==Control.FOCUS_NONE))
     await shot(a,language+"-"+mode+"-skin")
     ck(language+"-"+mode+"-idempotent",a.battle_ui_skin.apply(a))
    await dispose(a)
   ck(language+"-"+mode+"-all-visible-rect-text-font-input-identical",contexts[0]==contexts[1])
 var a=setup(candidate,1,"en")
 await process_frame
 var center=a.party_buttons[1].get_global_rect().get_center()
 click_at(center)
 await process_frame
 ck("real-mouse-party-switch-through-skin",a.controlled_index==1)
 var energy=int(app.member_state("liang-xu")["energy"])
 click_at(a.quick_skill_button.get_global_rect().get_center())
 await process_frame
 ck("real-mouse-personal-skill-through-skin",int(app.member_state("liang-xu")["energy"])==energy-16)
 a._toggle_pause()
 await process_frame
 click_at(a.pause_resume_button.get_global_rect().get_center())
 await process_frame
 ck("real-mouse-pause-resume-through-skin",not a.paused)
 var helper=a.battle_ui_skin
 helper.revert()
 ck("revert-clears-state",not helper.applied)
 await process_frame
 ck("revert-removes-four-plates",a.find_children("BattleUiSkinPilotPlate","NinePatchRect",true,false).is_empty())
 await dispose(a)
 candidate.battle_ui_skin_override=-1
 var failed=checks.filter(func(c):return not c.pass)
 var report={"passed":checks.size()-failed.size(),"failed":failed.size(),"failures":failed,"checks":checks,"arenaSha256":FileAccess.get_sha256("res://scripts/battle_arena.gd"),"artApproved":false,"pilotOnly":true}
 var file=FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_battle-ui_root-runtime-report_v01_"+TAG+".json"),FileAccess.WRITE)
 file.store_string(JSON.stringify(report," ")+"\n")
 file.close()
 print(JSON.stringify({"passed":report.passed,"failed":report.failed,"failures":failed}))
 print("BATTLE_UI_ROOT_DONE")
 quit(1 if failed.size()>0 else 0)
