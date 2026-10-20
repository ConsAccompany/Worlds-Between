extends SceneTree
# Independent facing expectations on the actual packed set. No motion/art approval.
const INDEX:="res://data/heroine-sea-combat-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_spritesheet-index_v01_20261020-201338-38ecfcb0.json"
const BEFORE:="C:/Users/hkzha/Documents/Codex/2026-10-12/rpg-2-star-ocean-the-second/work/max0840-sentry-sync/outputs/hsea07/rpg-2-star-ocean-the-second_combat-facing_before-source_v01_20261020-205251-5a7d3155.gd"
var current:GDScript
var old:GDScript
var checks:=0
var failures:=[]
func _initialize()->void:call_deferred("run")
func ck(ok:bool,label:String)->void:
 checks+=1
 if not ok:failures.append(label)
func fighter(explicit:bool=true)->Dictionary:
 var f:={"x":0.,"visual_action":"","visual_elapsed":0.,"dodge_time":0.,"guard":false,"visual_moving":false}
 if explicit:f.merge({"contact_event_id":0,"contact_event_active":false,"contact_event_clock":0.,"contact_event_facing":1})
 return f
func make(source:GDScript)->RefCounted:
 var loader:RefCounted=source.new();var keys:Array[String]=["hero:female","hero:female"];loader.configure(INDEX,keys);return loader
func begin(f:Dictionary,action:String)->void:
 f["visual_action"]="down" if action=="defeat" else action;f["visual_elapsed"]=0.
 f["dodge_time"]=0.27 if action=="dodge" else 0.
func run()->void:
 current=load("res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd")
 old=GDScript.new();old.source_code=FileAccess.get_file_as_string(BEFORE);assert(old.reload()==OK)
 for action in ["dodge","hit","skill","defeat"]:
  for initial in [1,-1]:
   var loader:=make(current);var f:=fighter();begin(f,action)
   loader.advance(0,f,action!="defeat",initial*100.,0.)
   ck(loader.current_frame(0)["facing"]==initial,action+" initial facing "+str(initial))
   var clock:=0.
   for step in range(1,7):
    clock+=1./60.;f["visual_elapsed"]=clock
    if action=="dodge":f["dodge_time"]=0.27-clock
    loader.advance(0,f,action!="defeat",initial*-100.,1./60.)
    ck(loader.current_frame(0)["facing"]==initial,action+" holds through crossing "+str(initial)+":"+str(step))
   # A genuine same-action restart relatches to the enemy's new side.
   if action!="defeat":
    begin(f,action);loader.advance(0,f,true,initial*-100.,0.)
    ck(loader.current_frame(0)["facing"]==-initial,action+" restart relatches")
   # End event / revive. At the next loop the fighter follows the enemy again.
   f["visual_action"]="";f["visual_elapsed"]=1.;f["dodge_time"]=0.
   loader.advance(0,f,true,initial*-100.,1.)
   ck(loader.current_frame(0)["action"]=="idle" and loader.current_frame(0)["facing"]==-initial,action+" end follows enemy")
 # A second fighter's state is independent.
 var l:=make(current);var f:=fighter();var second:=fighter();begin(f,"skill");begin(second,"hit")
 l.advance(0,f,true,100.,0.);l.advance(1,second,true,-100.,0.)
 var second_before:Dictionary=l.current_frame(1)
 f["visual_elapsed"]=0.02;l.advance(0,f,true,-100.,0.02)
 ck(l.current_frame(1)==second_before,"per-fighter isolation")
 # Nonpilot legacy output agrees exactly with the frozen prior implementation.
 for fps in [30,60]:
  var new_l:=make(current);var old_l:=make(old);var legacy:=fighter(false)
  for step in range(fps*2):
   if step==0:begin(legacy,"skill")
   if step==fps/2:begin(legacy,"hit")
   if step==fps:begin(legacy,"dodge")
   legacy["visual_elapsed"]=float(legacy["visual_elapsed"])+1./fps
   legacy["dodge_time"]=maxf(0.,float(legacy["dodge_time"])-1./fps)
   var enemy:float=100. if step%3==0 else -100.
   new_l.advance(0,legacy,true,enemy,1./fps);old_l.advance(0,legacy,true,enemy,1./fps)
   ck(new_l.current_frame(0)==old_l.current_frame(0),"legacy output unchanged "+str(fps)+":"+str(step))
 var report:={"checks":checks,"failures":failures,"sourceSHA256":FileAccess.get_sha256("res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd"),"beforeSourceSHA256":FileAccess.get_sha256(BEFORE),"actualPackedSet":true,"humanPlaytest":false,"artApproval":false}
 var args:=OS.get_cmdline_user_args()
 if args.size()>0:
  var file:=FileAccess.open(args[0],FileAccess.WRITE);file.store_string(JSON.stringify(report," "));file.close()
 if failures.is_empty():print("ROOT_FACING_PASS checks=",checks);quit(0)
 else:print("ROOT_FACING_FAIL checks=",checks," failures=",failures.size()," first=",failures.slice(0,5));quit(1)
