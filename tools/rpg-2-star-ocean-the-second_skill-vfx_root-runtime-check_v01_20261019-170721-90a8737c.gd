extends SceneTree
var checks:Array=[]
var app:Node
var out:String
var candidate:Script
var baseline:Script
const TAG="20261019-170721-90a8737c"
const CASES={"personal-hero":0,"personal-liang-xu":1,"personal-zhao-ling":2,"personal-ji-cheng":3,"job-sword":0,"job-firearms":2,"job-tactics":1,"job-relics":3}
func ck(k:String,v:bool)->void:checks.append({"key":k,"pass":v})
func _initialize()->void:call_deferred("run")
func setup(script:Script,mode:int)->Node2D:
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
 script.battle_vfx_override=0
 script.encounter_feedback_override=0
 if script==candidate:script.skill_vfx_override=mode
 seed(43821)
 var arena=script.new()
 root.add_child(arena)
 current_scene=arena
 arena.set_process(false)
 return arena
func dispose(arena:Node2D)->void:
 arena.queue_free()
 await process_frame
func snap(a:Node2D)->Dictionary:return {"hp":a.enemy_hp,"x":a.enemy_x,"windup":a.enemy_windup,"cooldown":a.enemy_cooldown,"fighters":a.fighters.duplicate(true),"finished":a.battle_finished,"won":a.battle_won,"hero":app.hero_state.duplicate(true),"members":app.member_states.duplicate(true),"bonus":a.next_attack_bonus}
func position(a:Node2D)->void:
 for i in 4:a.fighters[i]["x"]=170.+90.*i
 a.enemy_x=200.
 a.enemy_hp=1000
 a.enemy_target_index=0
func action(a:Node2D,kind:String)->bool:
 if kind.begins_with("personal-"):return a._use_skill(CASES[kind])
 return a._use_job_skill(CASES[kind])
func shot(a:Node2D,label:String)->Image:
 a._refresh_text()
 a.queue_redraw()
 await process_frame
 await RenderingServer.frame_post_draw
 var image=root.get_texture().get_image()
 image.convert(Image.FORMAT_RGBA8)
 ck("save-"+label,image.save_png(out.path_join("rpg-2-star-ocean-the-second_skill-vfx_"+label+"_actual-640_v01_"+TAG+".png"))==OK)
 return image
func run()->void:
 var args=OS.get_cmdline_user_args()
 baseline=load(args[0])
 candidate=load("res://scripts/battle_arena.gd")
 out=args[1]
 DirAccess.make_dir_recursive_absolute(out)
 root.size=Vector2i(640,360)
 root.content_scale_size=Vector2i(640,360)
 root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 SaveStore.root_path="user://skill-vfx-root"
 await process_frame
 app=root.get_node("AppState")
 var old=setup(baseline,0)
 var oldimage=await shot(old,"baseline-off")
 await dispose(old)
 var off=setup(candidate,-1)
 ck("default-no-skill-layer",off.skill_vfx==null)
 var offimage=await shot(off,"default-off")
 ck("default-zero-pixel-change",oldimage.get_data()==offimage.get_data())
 await dispose(off)
 var traces=[]
 for item in [{"script":baseline,"on":0},{"script":candidate,"on":0},{"script":candidate,"on":1}]:
  var a=setup(item.script,item.on)
  a.auto_mode=true
  var trace=[]
  for tick in 600:
   a._process(1./60.)
   trace.append(snap(a))
  traces.append(trace)
  await dispose(a)
 for tick in 600:
  ck("off-parity-"+str(tick),traces[0][tick]==traces[1][tick])
  ck("on-parity-"+str(tick),traces[0][tick]==traces[2][tick])
 for kind in CASES:
  var states=[]
  for item in [{"script":baseline,"on":0},{"script":candidate,"on":1}]:
   var a=setup(item.script,item.on)
   position(a)
   ck(kind+"-valid-action",action(a,kind))
   states.append(snap(a))
   if item.script==candidate:ck(kind+"-one-authored-event",a.skill_vfx.events.size()==1 and a.skill_vfx.events[0].kind==kind)
   await dispose(a)
  ck(kind+"-action-state-parity",states[0]==states[1])
 for kind in ["job-sword","job-firearms","job-tactics","job-relics"]:
  var states=[]
  for item in [{"script":baseline,"on":0},{"script":candidate,"on":1}]:
   var a=setup(item.script,item.on)
   position(a)
   var member=app.member_state(String(a.fighters[CASES[kind]]["id"]))
   var series=String(member["job_series"])
   member["job_stage"]=2
   member["job_records"][series]=GrowthRules.new_job_record(series,2)
   ck(kind+"-second-stage-valid",action(a,kind))
   states.append(snap(a))
   if item.script==candidate:ck(kind+"-second-stage-same-family",a.skill_vfx.events.size()==1 and a.skill_vfx.events[0].kind==kind)
   await dispose(a)
  ck(kind+"-second-stage-state-parity",states[0]==states[1])
 for language in ["en","zh"]:
  for kind in CASES:
   var a=setup(candidate,1)
   position(a)
   app.language=language
   app.language_changed.emit()
   ck(kind+"-eight-native-cels",a.skill_vfx._frames_by_kind[kind].size()==8)
   ck(kind+"-"+language+"-hook",action(a,kind))
   var origin:Vector2=a.skill_vfx.events[0].origin
   a.paused=true
   a._process(.1)
   ck(kind+"-pause-freezes",a.skill_vfx.events[0].age==0.)
   var duration=float(a.skill_vfx.DURATIONS[kind])
   a.skill_vfx.advance(duration*.4375)
   var image=await shot(a,kind+"-"+language)
   a.skill_vfx.events.clear()
   a.queue_redraw()
   await process_frame
   await RenderingServer.frame_post_draw
   var blank=root.get_texture().get_image()
   blank.convert(Image.FORMAT_RGBA8)
   var changed=0
   var outside=0
   var box=Rect2i(Vector2i(origin)-Vector2i(32,32),Vector2i(64,64))
   for y in 360:
    for x in 640:
     if image.get_pixel(x,y)!=blank.get_pixel(x,y):
      changed+=1
      if not box.has_point(Vector2i(x,y)):outside+=1
   ck(kind+"-"+language+"-visible-local",changed>0 and outside==0)
   a.skill_vfx.emit(kind,origin)
   a.skill_vfx.advance(duration-.000002)
   ck(kind+"-pre-expiry",a.skill_vfx.events.size()==1)
   a.skill_vfx.advance(.000002)
   ck(kind+"-exact-expiry",a.skill_vfx.events.is_empty())
   await dispose(a)
 for condition in ["no-energy","cooldown","dead","finished","far","merchant","locked"]:
  var a=setup(candidate,1)
  position(a)
  match condition:
   "no-energy":app.member_state("hero")["energy"]=0
   "cooldown":a.fighters[0]["skill_cooldown"]=2.
   "dead":app.member_state("hero")["hp"]=0
   "finished":a.battle_finished=true
   "far":a.enemy_x=600.
   "merchant":app.member_state("hero")["job_series"]="merchant"
  var ok=a._use_job_skill(0,"sword_arc" if condition=="locked" else "")
  ck(condition+"-job-rejected-no-event",not ok and a.skill_vfx.events.is_empty())
  if condition in ["no-energy","cooldown","dead","finished"]:ck(condition+"-personal-rejected-no-event",not a._use_skill(0) and a.skill_vfx.events.is_empty())
  await dispose(a)
 oldimage=null
 offimage=null
 candidate.skill_vfx_override=-1
 var failed=checks.filter(func(c):return not c.pass)
 var report={"passed":checks.size()-failed.size(),"failed":failed.size(),"failures":failed,"checks":checks,"arenaSha256":FileAccess.get_sha256("res://scripts/battle_arena.gd"),"artApproved":false,"pilotOnly":true,"newMechanics":false}
 var file=FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_skill-vfx_root-runtime-report_v01_"+TAG+".json"),FileAccess.WRITE)
 file.store_string(JSON.stringify(report," ")+"\n")
 file.close()
 print(JSON.stringify({"passed":report.passed,"failed":report.failed,"failures":failed}))
 candidate=null
 baseline=null
 app=null
 print("SKILL_VFX_ROOT_DONE")
 quit(1 if failed.size()>0 else 0)
