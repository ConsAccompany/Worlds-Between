extends SceneTree
var checks: Array=[]
var app: Node
var out: String
var candidate: Script
var baseline: Script
const TAG="20261019-164412-1f3bff80"
const DURATIONS={"attack":0.22,"dodge":0.27,"guard":0.30,"hit":0.20,"heal":0.55}
func ck(label: String, value: bool) -> void:
 checks.append({"key":label,"pass":value})
func _initialize() -> void: call_deferred("run")
func setup(script: Script, common: int) -> Node2D:
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
 script.encounter_feedback_override=0
 seed(43821)
 var arena=script.new()
 root.add_child(arena)
 current_scene=arena
 arena.set_process(false)
 return arena
func snap(arena: Node2D) -> Dictionary:
 return {"hp":arena.enemy_hp,"x":arena.enemy_x,"windup":arena.enemy_windup,"cooldown":arena.enemy_cooldown,"fighters":arena.fighters.duplicate(true),"finished":arena.battle_finished,"won":arena.battle_won,"hero":app.hero_state.duplicate(true),"members":app.member_states.duplicate(true)}
func dispose(arena: Node2D) -> void:
 arena.queue_free()
 await process_frame
func shot(arena: Node2D, name: String) -> Image:
 arena.queue_redraw()
 await process_frame
 await RenderingServer.frame_post_draw
 var image=root.get_texture().get_image()
 image.convert(Image.FORMAT_RGBA8)
 ck("saved-"+name,image.save_png(out.path_join("rpg-2-star-ocean-the-second_common-vfx_"+name+"_actual-640_v01_"+TAG+".png"))==OK)
 return image
func unit(helper: Script) -> void:
 var a=helper.new()
 ck("invalid-kind",not a.emit("other",Vector2.ZERO))
 ck("nonfinite-position",not a.emit("hit",Vector2(NAN,0)))
 ck("nonfinite-facing",not a.emit("hit",Vector2.ZERO,INF))
 ck("invalid-no-events",a.events.is_empty() and a.emitted==0)
 for kind in DURATIONS:
  a=helper.new()
  ck(kind+"-emit",a.emit(kind,Vector2(10.3,20.8),-1))
  ck(kind+"-rounded-origin",a.events[0].origin==Vector2(10,21))
  ck(kind+"-negative-facing",a.events[0].facing==-1.)
  a.advance(-1.)
  a.advance(NAN)
  a.advance(INF)
  ck(kind+"-bad-delta-does-not-advance",a.events[0].age==0.)
  a.advance(float(DURATIONS[kind])-0.000002)
  ck(kind+"-before-expiry",a.events.size()==1)
  a.advance(0.000002)
  ck(kind+"-at-expiry",a.events.is_empty())
  var b=helper.new()
  a=helper.new()
  a.emit(kind,Vector2.ZERO)
  b.emit(kind,Vector2.ZERO)
  for n in 3:a.advance(1./30.)
  for n in 6:b.advance(1./60.)
  ck(kind+"-30-60-elapsed-parity",is_equal_approx(a.events[0].age,b.events[0].age))
 a=helper.new()
 for n in 100:a.emit("hit",Vector2(n,0))
 ck("queue-cap-drop-oldest",a.events.size()==24 and a.events[0].origin.x==76. and a.emitted==100)
func run() -> void:
 var args=OS.get_cmdline_user_args()
 baseline=load(args[0])
 candidate=load("res://scripts/battle_arena.gd")
 var helper=load(args[1])
 out=args[2]
 DirAccess.make_dir_recursive_absolute(out)
 root.size=Vector2i(640,360)
 root.content_scale_size=Vector2i(640,360)
 root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 await process_frame
 SaveStore.root_path="user://common-vfx-root"
 app=root.get_node("AppState")
 unit(helper)
 var old=setup(baseline,0)
 var old_image=await shot(old,"baseline-off")
 await dispose(old)
 var off=setup(candidate,-1)
 ck("default-helper-absent",off.battle_vfx==null)
 var off_image=await shot(off,"candidate-default")
 ck("default-zero-pixel-difference",old_image.get_data()==off_image.get_data())
 await dispose(off)
 var histories=[]
 for item in [{"script":baseline,"on":0},{"script":candidate,"on":0},{"script":candidate,"on":1}]:
  var arena=setup(item.script,item.on)
  arena.auto_mode=true
  var history=[]
  for tick in 600:
   arena._process(1./60.)
   history.append(snap(arena))
  histories.append(history)
  await dispose(arena)
 for tick in 600:
  ck("off-simulation-"+str(tick),histories[0][tick]==histories[1][tick])
  ck("on-simulation-"+str(tick),histories[0][tick]==histories[2][tick])
 for language in ["en","zh"]:
  for kind in DURATIONS:
   var arena=setup(candidate,1)
   ck(kind+"-"+language+"-native-eight-loaded",arena.battle_vfx._frames_by_kind[kind].size()==8)
   app.language=language
   app.language_changed.emit()
   arena.paused=true
   for index in 4:arena.fighters[index]["x"]=170.+90.*index
   arena.enemy_x=200.
   arena.enemy_hp=1000
   arena.enemy_target_index=0
   match kind:
    "attack":ck("actual-attack-hook",arena._try_attack(0))
    "dodge":ck("actual-dodge-hook",arena._try_dodge(0))
    "guard":
     arena.fighters[0]["guard"]=true
     arena._apply_enemy_hit()
    "hit":arena._apply_enemy_hit()
    "heal":
     var hp=int(app.member_state("hero")["hp"])
     var energy=int(app.member_state("hero")["energy"])
     ck("actual-heal-presentation-hook",arena.show_heal_vfx(0))
     ck("heal-no-gameplay-mutation",int(app.member_state("hero")["hp"])==hp and int(app.member_state("hero")["energy"])==energy)
   ck(kind+"-"+language+"-actual-event",arena.battle_vfx.events.size()==1 and arena.battle_vfx.events[0].kind==kind)
   var native_bounds=Rect2i(Vector2i(arena.battle_vfx.events[0].origin)-Vector2i(32,32),Vector2i(64,64))
   var before=arena.battle_vfx.events[0].age
   arena._process(.1)
   ck(kind+"-"+language+"-pause-freezes",arena.battle_vfx.events[0].age==before)
   arena.battle_vfx.advance(float(DURATIONS[kind])*0.4375)
   var image=await shot(arena,kind+"-"+language)
   arena.battle_vfx.events.clear()
   arena.queue_redraw()
   await process_frame
   await RenderingServer.frame_post_draw
   var blank=root.get_texture().get_image()
   blank.convert(Image.FORMAT_RGBA8)
   var changed=0
   var outside=0
   for y in 360:
    for x in 640:
     if image.get_pixel(x,y)!=blank.get_pixel(x,y):
      changed+=1
      if not native_bounds.has_point(Vector2i(x,y)):outside+=1
   ck(kind+"-"+language+"-visible-localized",changed>0 and outside==0)
   ck(kind+"-"+language+"-heal-is-presentation-only",not arena.show_heal_vfx(-1))
   await dispose(arena)
 candidate.battle_vfx_override=-1
 var failed=checks.filter(func(c):return not c.pass)
 var report={"passed":checks.size()-failed.size(),"failed":failed.size(),"failures":failed,"checks":checks,"arenaSha256":FileAccess.get_sha256("res://scripts/battle_arena.gd"),"helperSha256":FileAccess.get_sha256(args[1]),"artApproved":false,"pilotOnly":true}
 var file=FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_common-vfx_root-runtime-report_v01_"+TAG+".json"),FileAccess.WRITE)
 file.store_string(JSON.stringify(report," ")+"\n")
 file.close()
 print(JSON.stringify({"passed":report.passed,"failed":report.failed,"failures":failed}))
 print("COMMON_VFX_ROOT_DONE")
 quit(1 if failed.size()>0 else 0)
