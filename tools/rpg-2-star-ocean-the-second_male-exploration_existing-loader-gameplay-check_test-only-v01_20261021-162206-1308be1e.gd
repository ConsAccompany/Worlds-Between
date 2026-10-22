extends SceneTree
# New source-set compatibility using existing normal exploration host/input. Not default adoption or human playtest.
# Authored stop source integrity/contact checks are separate; this generic loader hands off directly to idle.
# Optional fifth positional actor: companion sources use an explicitly labelled test-only avatar injection.
# Normal roster assignments/defaults stay unchanged; the existing male invocation remains supported.
const Pilot=preload("res://scripts/exploration_sprite_set_pilot.gd")
var checks: Array=[]
var captures: Array=[]
var timeline: Array=[]
var failed:=false
var out: String
var tag: String
var language: String
var fps: int
var host: Node
var source_actor := "protagonist-male"
var output_subject := "male-exploration"
func ck(ok: bool,label: String,detail: Variant=null) -> void:
 checks.append({"check":label,"passed":ok,"detail":detail})
 if not ok:
  failed=true
  print("MEXP23_FAIL ",label," ",detail)
func _initialize() -> void:
 call_deferred("run")
 create_timer(55).timeout.connect(func():print("MEXP23_TIMEOUT");quit(2))
func tick() -> void:
 await process_frame
 await RenderingServer.frame_post_draw
func shot(label: String) -> void:
 var image: Image=root.get_texture().get_image()
 var path=out.path_join("rpg-2-star-ocean-the-second_%s_%s-%s_actual-input-v01_%s.png"%[output_subject,language,label,tag])
 ck(image.get_size()==Vector2i(640,360) and DisplayServer.get_name()!="headless","actual renderer "+label)
 ck(image.save_png(path)==OK,"capture saved "+label)
 captures.append({"label":label,"path":path,"sha256":FileAccess.get_sha256(path)})
func run() -> void:
 var args:=OS.get_cmdline_user_args()
 if args.size()<4:
  quit(2);return
 out=args[0];tag=args[1];language=args[2];fps=int(args[3])
 if args.size()>4 and not args[4].begins_with("--"):
  source_actor=args[4]
  output_subject=source_actor+"-exploration"
 if not source_actor in ["protagonist-male","zhao-ling","liang-xu","ji-cheng"]:
  print("MEXP23_BAD_ACTOR");quit(2);return
 DirAccess.make_dir_recursive_absolute(out)
 root.size=Vector2i(640,360)
 ck(Pilot.enabled() and Pilot.enabled_override==-1,"existing opt-in CLI enabled with no test override")
 var app:=root.get_node("AppState")
 app.begin_new_run();app.hero_appearance="male";app.language=language
 ck(app.select_destination("scifi.outskirts"),"normal destination selected")
 host=load("res://scenes/scifi_exploration_area.tscn").instantiate()
 root.add_child(host)
 await tick()
 if source_actor!="protagonist-male":
  ck(host.sprite_pilot==null,"test-only source fit begins with the host legacy avatar, not two active drivers")
  if host.sprite_pilot!=null:
   quit(1);return
  host.sprite_pilot=Pilot.attach(host.hero,source_actor,"south")
 ck(host.sprite_pilot!=null,"host attached source candidate")
 if host.sprite_pilot==null:
  quit(1);return
 ck(host.sprite_pilot.actor_id==source_actor,"source actor identity")
 ck(host.hero.scale==Vector2(0.5,0.5),"48logical display scale")
 var sprite_set: Dictionary=host.sprite_pilot.sprite_set
 var source_path: String=Pilot.load_registry(Pilot.registry_path()).actors[source_actor]
 for action in ["idle","walk"]:
  for direction in ["south","west","north","east"]:
   var clip: Dictionary=sprite_set.clips[action][direction]
   ck(clip.textures.size()>1,"authored loop "+action+"/"+direction)
   for i in clip.ends_us.size():
    var begin: int=0 if i==0 else int(clip.ends_us[i-1])
    ck(Pilot.frame_at(clip,begin)==i,"exact clip boundary %s/%s/%d"%[action,direction,i])
   ck(Pilot.frame_at(clip,int(clip.cycle_us))==0,"loop wraps "+action+"/"+direction)
 host.hero.position=Vector2(220,115)
 await tick()
 var rect=[{"input":"move_right","direction":"east","delta":Vector2.RIGHT},{"input":"move_down","direction":"south","delta":Vector2.DOWN},{"input":"move_left","direction":"west","delta":Vector2.LEFT},{"input":"move_up","direction":"north","delta":Vector2.UP}]
 for leg in rect:
  var start: Vector2=host.hero.position
  var seen: Dictionary={}
  Input.action_press(leg.input)
  var n:=int(round(0.6*fps))
  for i in n:
   await tick()
   var state: Dictionary=host.sprite_pilot.state()
   ck(state.action=="walk" and state.facing==leg.direction,"normal walk state %s/%d"%[leg.direction,i])
   seen[int(state.frame)]=true
   timeline.append({"direction":leg.direction,"step":i,"x":host.hero.position.x,"y":host.hero.position.y,"frame":state.frame,"path":state.path})
   if i==int(n/2):shot(leg.direction+"-walk")
  Input.action_release(leg.input)
  var actual: Vector2=host.hero.position-start
  var expected: Vector2=leg.delta*140.0*0.6
  ck(actual.distance_to(expected)<0.1,"presentation preserves normal movement "+leg.direction,[actual.x,actual.y])
  ck(seen.size()==sprite_set.clips.walk[leg.direction].textures.size(),"all authored gait frames observed "+leg.direction,seen.keys())
  var stopped: Vector2=host.hero.position
  var idle_seen: Dictionary={}
  for i in int(ceil((float(sprite_set.clips.idle[leg.direction].cycle_us)/1000000.0+0.1)*fps)):
   await tick()
   ck(host.hero.position.distance_to(stopped)<0.001,"stop has no physical drift %s/%d"%[leg.direction,i])
   ck(host.sprite_pilot.state().action=="idle","existing generic idle handoff %s/%d"%[leg.direction,i])
   idle_seen[int(host.sprite_pilot.state().frame)]=true
  ck(idle_seen.size()==sprite_set.clips.idle[leg.direction].textures.size(),"idle loop observed "+leg.direction,idle_seen.keys())
  shot(leg.direction+"-idle")
 ck(host.hero.position.distance_to(Vector2(220,115))<0.1,"normal rectangle returns to start")
 var rep={"schema":"worlds-between.exploration-source-gameplay/1","actor":source_actor,"testOnlyAvatarInjection":source_actor!="protagonist-male","rosterAssignmentsChanged":false,"scope":"normal Input + existing generic opt-in loader; authored stop sources separately checked; no default/adoption/human approval","language":language,"fps":fps,"harnessSha256":FileAccess.get_sha256(get_script().resource_path),"registry":Pilot.registry_path(),"registrySha256":FileAccess.get_sha256(Pilot.registry_path()),"sourceSet":source_path,"sourceSha256":FileAccess.get_sha256(source_path),"checks":checks,"captures":captures,"timeline":timeline,"passed":not failed}
 var report_path=out.path_join("rpg-2-star-ocean-the-second_%s_%s-%sfps_actual-input-proof-v01_%s.json"%[output_subject,language,fps,tag])
 var file=FileAccess.open(report_path,FileAccess.WRITE);file.store_string(JSON.stringify(rep,"  ")+"\n")
 print("MEXP23_PASS" if not failed else "MEXP23_FAILED")
 quit(1 if failed else 0)
