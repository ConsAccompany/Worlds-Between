extends SceneTree
const MODEL := preload("res://../tools/rpg-2-star-ocean-the-second_female-west_run-stop-source_unapproved-v01_20261018-181150-a94f021c.gd")
var checks:=[]
func check(key: String,ok: bool,detail: Variant=null) -> void:checks.append({"key":key,"pass":ok,"detail":detail})
func boot_bottom(model: RefCounted,state: Dictionary,i: int) -> Dictionary:
 var image: Image=model._boot(i,state.feet[i]).image
 var points:=[]
 var bottom:=-1
 for y in 112:
  for x in 80:
   if image.get_pixel(x,y).a8>0:
    bottom=maxi(bottom,y)
    if y==103:points.append(state.renderX+x*.5)
 return {"bottom":bottom,"points":points}
func expected_body(q: float) -> Vector2:
 var phase:=fposmod(q,64.)
 return Vector2(-2.,2.*sin(PI*phase/38.) if phase<38. else -2.*sin(PI*(phase-38.)/26.))
func full_floor_check(model: RefCounted,state: Dictionary,key: String) -> void:
 var image: Image=model.render_pose(state).full
 var actual:=[]
 var expected:=[]
 for i in 2:
  var boot: Image=model._boot(i,state.feet[i]).image
  for x in 80:
   if boot.get_pixel(x,103).a8>0 and not expected.has(x):expected.append(x)
 for x in 80:
  if image.get_pixel(x,103).a8>0:actual.append(x)
 expected.sort()
 check(key,actual==expected,{"actual":actual,"expected":expected})
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var schedules: Dictionary={"30":[1./30.],"60":[1./60.],"mixed":[1./24.,1./60.,1./48.,1./30.]}
 for schedule: String in schedules:
  var steps: Array=schedules[schedule]
  var m:=MODEL.new()
  var x:=500.
  m.physical_x=x;m.render_x=x
  var prev: Dictionary={}
  var pins: Array=[null,null]
  var visible_pins: Array=[boot_bottom(m,m.snapshot(),0).points,boot_bottom(m,m.snapshot(),1).points]
  for t in 200:
   var dt: float=steps[t%steps.size()]
   x-=140.*dt
   var s: Dictionary=m.advance(dt,x,-1.)
   for i in 2:
    var b:=boot_bottom(m,s,i)
    if b.bottom==103:
     if visible_pins[i]!=null:
      var overlap:=[]
      for point in visible_pins[i]:
       if b.points.has(point):overlap.append(point)
      check(schedule+"-run-visible-world-contact-%d-%d"%[t,i],not overlap.is_empty(),{"previous":visible_pins[i],"current":b.points})
      visible_pins[i]=overlap
     else:visible_pins[i]=b.points
    else:visible_pins[i]=null
    if s.feet[i].ground:
     check(schedule+"-contact-pixels-%d-%d"%[t,i],b.bottom==103 and not b.points.is_empty(),b)
     var natural: bool=s.age>=.12 and s.feet[i].phase<38.
     var same_stance: bool=not prev.is_empty() and prev.feet[i].ground and prev.feet[i].phase<=s.feet[i].phase and natural
     if same_stance and pins[i]!=null:
      var intersection:=[]
      for point in pins[i]:
       if b.points.has(point):intersection.append(point)
      check(schedule+"-rendered-world-contact-%d-%d"%[t,i],not intersection.is_empty(),{"previous":pins[i],"current":b.points})
      pins[i]=intersection
     else:pins[i]=b.points
    else:pins[i]=null
   prev=s
  # Every integer source phase is exercised without excluding seam or flight.
  for phase in 128:
   var base:=MODEL.new()
   base.physical_x=500.;base.render_x=500.;base.origin_x=500.;base.q0=float(phase);base.q=float(phase);base.mode="run";base.age=1.;base.feet=[base.gait_foot(phase),base.gait_foot(phase+64.)];base.last_body=expected_body(float(phase))
   var initial: Dictionary=base.snapshot()
   var elapsed:=0.
   var landed: Array=[-1.,-1.]
   var previous_x:=base.physical_x
   var settled:=-1.
   var ib0:=boot_bottom(base,initial,0)
   var ib1:=boot_bottom(base,initial,1)
   var stop_pins: Array=[ib0.points if ib0.bottom==103 else null,ib1.points if ib1.bottom==103 else null]
   full_floor_check(base,initial,schedule+"-run-full-floor-%d"%phase)
   for t in 20:
    var dt: float=steps[t%steps.size()]
    elapsed+=dt
    var s: Dictionary=base.advance(dt,previous_x,0.)
    check(schedule+"-physical-stop-%d-%d"%[phase,t],s.physicalX==previous_x)
    if t==0:full_floor_check(base,s,schedule+"-stop-boundary-full-floor-%d"%phase)
    for i in 2:
     var b:=boot_bottom(base,s,i)
     if b.bottom>=103 and landed[i]<0.:landed[i]=elapsed
     if b.bottom==103:
      if stop_pins[i]!=null:
       var overlap:=[]
       for point in stop_pins[i]:
        if b.points.has(point):overlap.append(point)
       check(schedule+"-stop-visible-world-contact-%d-%d-%d"%[phase,t,i],not overlap.is_empty(),{"previous":stop_pins[i],"current":b.points})
       stop_pins[i]=overlap
      else:stop_pins[i]=b.points
     else:stop_pins[i]=null
    if s.mode=="idle":
     settled=elapsed
     check(schedule+"-final-static-%d"%phase,base.render_pose(s).full.get_data()==base.original.get_data())
     break
   check(schedule+"-settle-deadline-%d"%phase,settled>0. and settled<=(.300001 if schedule=="mixed" else .250001),settled)
   for i in 2:
    check(schedule+"-raised-foot-deadline-%d-%d"%[phase,i],landed[i]>=0. and landed[i]<=.100001,landed[i])
   # Re-press after each 1/2/3 frame stop, retaining all boundaries.
   for release_count in [1,2,3]:
    var r:=MODEL.new()
    r.physical_x=500.;r.render_x=500.;r.origin_x=500.;r.q0=float(phase);r.q=float(phase);r.mode="run";r.age=1.;r.feet=initial.feet.duplicate(true);r.last_body=expected_body(float(phase))
    for t in release_count:r.advance(steps[t%steps.size()],500.,0.)
    var rx:=500.
    var had_support:=false
    var first_support:=-1.
    var repress_time:=0.
    var pre: Dictionary=r.snapshot()
    var rb0:=boot_bottom(r,pre,0)
    var rb1:=boot_bottom(r,pre,1)
    var repress_pins: Array=[rb0.points if rb0.bottom==103 else null,rb1.points if rb1.bottom==103 else null]
    for t in 12:
     var dt: float=steps[t%steps.size()]
     repress_time+=dt;rx-=140.*dt
     var s: Dictionary=r.advance(dt,rx,-1.)
     if t==0:full_floor_check(r,s,schedule+"-repress-boundary-full-floor-%d-%d"%[phase,release_count])
     var b0:=boot_bottom(r,s,0)
     var b1:=boot_bottom(r,s,1)
     for i in 2:
      var b: Dictionary=b0 if i==0 else b1
      if b.bottom==103:
       if repress_pins[i]!=null:
        var overlap:=[]
        for point in repress_pins[i]:
         if b.points.has(point):overlap.append(point)
        check(schedule+"-repress-visible-world-contact-%d-%d-%d-%d"%[phase,release_count,t,i],not overlap.is_empty(),{"previous":repress_pins[i],"current":b.points})
        repress_pins[i]=overlap
       else:repress_pins[i]=b.points
      else:repress_pins[i]=null
     var grounded: bool=b0.bottom>=103 or b1.bottom>=103
     if grounded and first_support<0.:first_support=repress_time
     # The bridge must establish support by 100ms, then retain support until
     # its authored next genuine flight (chosen landing phase38 at~186ms).
     if s.bridgeAir>=0 and repress_time>=.100001 and repress_time<.18:
      check(schedule+"-repress-support-%d-%d-%d"%[phase,release_count,t],grounded,{"time":repress_time,"feet":s.feet,"bottoms":[b0.bottom,b1.bottom]})
    check(schedule+"-repress-landing-%d-%d"%[phase,release_count],first_support>0. and first_support<=.100001,first_support)
 var failed:=checks.filter(func(c):return not c.pass)
 var report:={"checks":checks,"passed":checks.size()-failed.size(),"failed":failed.size(),"modelSha256":FileAccess.get_sha256("res://../tools/rpg-2-star-ocean-the-second_female-west_run-stop-source_unapproved-v01_20261018-181150-a94f021c.gd"),"artApproved":false,"motionApproved":false}
 var f:=FileAccess.open(OS.get_cmdline_user_args()[0],FileAccess.WRITE);f.store_string(JSON.stringify(report,"  ")+"\n");f.close()
 print("WEST TRANSITIONS ",checks.size()-failed.size(),"/",checks.size()," failed ",failed.size())
 for c in failed.slice(0,8):print(JSON.stringify(c))
 quit(1 if failed.size()>0 else 0)
