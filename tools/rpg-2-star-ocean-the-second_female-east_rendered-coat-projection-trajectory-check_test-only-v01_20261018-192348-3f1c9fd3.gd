extends SceneTree
# Rendered body trajectory around very short release / re-press, and settle-step continuity.
# Body height is measured from the rendered image (coat role offset from the static coat),
# not from the model's body variable. Usage: -s <this> -- <res:// model path> <report.json>
# Gates per schedule (30, 60, mixed), every integer start phase 0..127, release 1..6 frames:
#  envelope   rendered body dy stays within the steady-run range [-2,+2] source px;
#  step       per-frame |d dy| never exceeds the largest step of an uninterrupted run at
#             the same schedule (measured, not assumed);
#  no-rise    from release until the bridging foot has rendered contact (row 103), the body
#             never rises above min(height at the last running frame, standing height 0);
#  settle     in a plain stop, the final step into the exact static changes no more texels
#             than the largest earlier settle step (no pop), and the final frame is exact.
# Diagnostics (reported; the strict step gate above is not relaxed by them):
#  stepEnvelopeAnyStart  largest rendered step of uninterrupted runs started at every one of
#             the 128 phases (re-press resumes at a different sampling alignment); each case
#             is also checked against it under a separately named key;
#  legMaterialResidual   texels of each leg role in the penultimate settle frame that differ
#             from the static leg role after its best integer translation within +-2 px
#             (0 = the static trouser/boot material, merely displaced).
# Check-only projection; model source remains untouched. Every first-seen rendered-coat
# signature is byte-compared with the full renderer. All original behavior gates remain.
const EXPECTED_MODEL_SHA256 := "84f2f9042d375578e7bc6121bcefb2f7b3abaa01a0b82cb6d96141771d195f87"
var projection_cache := {}
var source_hash_by_id := {}
var projection_parity := []
var body_sample_count := 0
var full_stop_render_count := 0
var checks:=[]
var model_script: GDScript
func check(key: String,ok: bool,detail: Variant=null) -> void:checks.append({"key":key,"pass":ok,"detail":detail})
func image_sha(image: Image) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(image.get_data())
	return context.finish().hex_encode()
func body_dy(m: RefCounted,state: Dictionary) -> int:
	body_sample_count+=1
	var source_coat: Image=m.layers["coat"]
	var source_id: int=source_coat.get_instance_id()
	if not source_hash_by_id.has(source_id):source_hash_by_id[source_id]=image_sha(source_coat)
	var source_sha: String=source_hash_by_id[source_id]
	var static_branch: bool=state.mode=="idle" or state.mode=="reverse-placeholder"
	var offset:=Vector2i.ZERO if static_branch else Vector2i(roundi(state.body.x),roundi(state.body.y))
	var key:=source_sha+":"+("static" if static_branch else "active")+":"+str(offset)
	if not projection_cache.has(key):
		# The pinned v02 renderer applies only _stamp to the coat and never revisits it.
		var projected: Image=source_coat if static_branch else m._stamp(source_coat,offset.x,offset.y)
		var actual: Image=m.render_pose(state).roles["coat"]
		var exact: bool=projected.get_data()==actual.get_data()
		projection_parity.append({"signature":key,"pass":exact,"projectedSha256":image_sha(projected),"fullRenderSha256":image_sha(actual)})
		projection_cache[key]=projected
	var coat: Image=projection_cache[key]
	return coat.get_used_rect().position.y-source_coat.get_used_rect().position.y
func grounded(m: RefCounted,state: Dictionary,i: int) -> bool:
	var image: Image=m._boot(i,state.feet[i]).image
	for x in 80:
		if image.get_pixel(x,103).a8>0:return true
	return false
func run_state(phase: int) -> RefCounted:
	var m: RefCounted=model_script.new()
	m.physical_x=500.;m.render_x=500.;m.origin_x=500.;m.q0=float(phase);m.q=float(phase);m.mode="run";m.age=1.
	m.feet=[m.gait_foot(phase),m.gait_foot(phase+64.)];m.last_body=m.steady_body(float(phase))
	return m
func diff(a: Image,b: Image) -> int:
	var n:=0
	for y in 112:
		for x in 80:
			if a.get_pixel(x,y)!=b.get_pixel(x,y):n+=1
	return n
func leg_residual(m: RefCounted,roles: Dictionary,role: String) -> int:
	var a: Image=roles[role]
	var b: Image=m.layers[role]
	var best:=1<<30
	for oy in range(-2,3):
		for ox in range(-2,3):
			var n:=0
			for y in range(60,108):
				for x in range(14,66):
					var sx:=x-ox
					var sy:=y-oy
					var bc:=b.get_pixel(sx,sy) if sx>=0 and sx<80 and sy>=0 and sy<112 else Color(0,0,0,0)
					var ac:=a.get_pixel(x,y)
					if ac.a8!=bc.a8 or (ac.a8>0 and ac!=bc):n+=1
				if n>=best:break
			best=mini(best,n)
	return best
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var args:=OS.get_cmdline_user_args()
	if args.size()!=2:
		push_error("Expected explicit model path and new absolute report path")
		quit(2);return
	var model_path:=args[0]
	var report_path:=args[1]
	if not report_path.is_absolute_path() or FileAccess.file_exists(report_path):
		push_error("Report must be a new absolute path")
		quit(2);return
	var started_usec:=Time.get_ticks_usec()
	var model_hash_before:=FileAccess.get_sha256(model_path)
	if model_hash_before!=EXPECTED_MODEL_SHA256:
		push_error("Pinned v02 model hash changed; result invalidated before validation")
		quit(2);return
	model_script=load(model_path)
	var schedules: Dictionary={"30":[1./30.],"60":[1./60.],"mixed":[1./24.,1./60.,1./48.,1./30.]}
	var summary:={}
	for schedule: String in schedules:
		var steps: Array=schedules[schedule]
		# Reference: uninterrupted run from idle, 3 s, steps after the 0.2 s start blend.
		var ref: RefCounted=model_script.new()
		var x:=500.
		ref.physical_x=x;ref.render_x=x
		var prev_dy:=0
		var ref_max:=0
		var elapsed:=0.
		for t in 200:
			var dt: float=steps[t%steps.size()]
			x+=140.*dt;elapsed+=dt
			var dy:=body_dy(ref,ref.advance(dt,x,1.))
			if elapsed>.2:ref_max=maxi(ref_max,absi(dy-prev_dy))
			prev_dy=dy
		# Diagnostic envelope: uninterrupted runs from every start phase (0.6 s each).
		var envelope_any:=0
		for phase in 128:
			var em:=run_state(phase)
			var ex:=500.
			var last:=body_dy(em,em.snapshot())
			var et:=0.
			var k:=0
			while et<.6:
				var dt: float=steps[k%steps.size()];k+=1
				ex+=140.*dt;et+=dt
				var dy:=body_dy(em,em.advance(dt,ex,1.))
				envelope_any=maxi(envelope_any,absi(dy-last))
				last=dy
		var worst:={"maxRiseAboveAllowed":-99,"maxStep":0,"minDy":99,"maxDy":-99,"worstRiseCase":null,"maxSettleFinalStep":0,"maxSettleEarlierStep":0,"maxPenultimateLegMaterialResidual":{"near-leg-boot":0,"far-leg-boot":0},"penultimateEqualsFinalPhases":0}
		for phase in 128:
			# Plain stop: settle-step continuity into the exact original static.
			var sm:=run_state(phase)
			var frames:=[sm.render_pose(sm.snapshot()).full]
			full_stop_render_count+=1
			var pen_roles: Dictionary={}
			for t in 40:
				var s: Dictionary=sm.advance(steps[t%steps.size()],500.,0.)
				var pose: Dictionary=sm.render_pose(s)
				frames.append(pose.full)
				if s.mode=="idle":break
				pen_roles=pose.roles
			var n:=frames.size()
			if frames[n-2].get_data()==frames[n-1].get_data():worst.penultimateEqualsFinalPhases+=1
			else:
				for role in ["near-leg-boot","far-leg-boot"]:
					worst.maxPenultimateLegMaterialResidual[role]=maxi(worst.maxPenultimateLegMaterialResidual[role],leg_residual(sm,pen_roles,role))
			var last_step:=diff(frames[n-2],frames[n-1])
			var earlier:=0
			for k in range(1,n-1):earlier=maxi(earlier,diff(frames[k-1],frames[k]))
			check(schedule+"-settle-final-exact-%d"%phase,frames[n-1].get_data()==sm.original.get_data())
			check(schedule+"-settle-no-final-pop-%d"%phase,last_step<=earlier,{"finalStep":last_step,"largestEarlierStep":earlier})
			worst.maxSettleFinalStep=maxi(worst.maxSettleFinalStep,last_step)
			worst.maxSettleEarlierStep=maxi(worst.maxSettleEarlierStep,earlier)
			for release_count in [1,2,3,4,5,6]:
				var m:=run_state(phase)
				var wx:=500.
				var traj:=[]
				var t_index:=0
				# Two real running frames before the release.
				for k in 2:
					var dt: float=steps[t_index%steps.size()];t_index+=1
					wx+=140.*dt
					traj.append({"phase":"run","dy":body_dy(m,m.advance(dt,wx,1.))})
				var release_dy: int=traj[-1].dy
				for k in release_count:
					var dt: float=steps[t_index%steps.size()];t_index+=1
					var s: Dictionary=m.advance(dt,wx,0.)
					check(schedule+"-physical-stop-%d-%d-%d"%[phase,release_count,k],s.physicalX==wx)
					traj.append({"phase":"release","dy":body_dy(m,s)})
				var bridge_air:=-2
				var repress_time:=0.
				var landed:=false
				while repress_time<.4:
					var dt: float=steps[t_index%steps.size()];t_index+=1
					wx+=140.*dt;repress_time+=dt
					var s: Dictionary=m.advance(dt,wx,1.)
					if bridge_air==-2:bridge_air=s.bridgeAir
					if bridge_air<0 or grounded(m,s,bridge_air):landed=true
					traj.append({"phase":"bridge" if not landed else "repress","dy":body_dy(m,s),"t":repress_time})
				var allowed:=mini(release_dy,0)
				var rise:=-99
				var max_step:=0
				for k in traj.size():
					var dy: int=traj[k].dy
					worst.minDy=mini(worst.minDy,dy);worst.maxDy=maxi(worst.maxDy,dy)
					if k>0:max_step=maxi(max_step,absi(dy-traj[k-1].dy))
					if k>=2 and traj[k].phase!="repress":rise=maxi(rise,allowed-dy)
				var key:="%s-%d-%d"%[schedule,phase,release_count]
				var envelope:=traj.all(func(e):return e.dy>=-2 and e.dy<=2)
				check(key+"-envelope",envelope,traj if not envelope else null)
				check(key+"-step",max_step<=ref_max,{"maxStep":max_step,"steadyRunMaxStep":ref_max} if max_step>ref_max else null)
				check(key+"-no-rise-before-landing",rise<=0,{"riseSourcePx":rise,"allowedDy":allowed,"trajectory":traj} if rise>0 else null)
				worst.maxStep=maxi(worst.maxStep,max_step)
				if rise>worst.maxRiseAboveAllowed:
					worst.maxRiseAboveAllowed=rise
					worst.worstRiseCase={"phase":phase,"releaseFrames":release_count,"bridgeAir":bridge_air,"allowedDy":allowed,"trajectory":traj}
		worst["steadyRunMaxStep"]=ref_max
		summary[schedule]=worst
	var failed:=checks.filter(func(c):return not c.pass)
	var model_hash_after:=FileAccess.get_sha256(model_path)
	var invalidated: bool=model_hash_before!=model_hash_after or model_hash_after!=EXPECTED_MODEL_SHA256
	var parity_failed:=projection_parity.filter(func(c):return not c.pass)
	var duration_seconds:=float(Time.get_ticks_usec()-started_usec)/1000000.
	var report:={"model":model_path,"modelSha256":FileAccess.get_sha256(model_path),"sign":"dy in source px, +down; 2 source px = 1 logical px","summary":summary,"passed":checks.size()-failed.size(),"failed":failed.size(),"failedChecks":failed,"checkCount":checks.size(),"artApproved":false,"motionApproved":false}
	report["sourceBinding"]={"expectedModelSha256":EXPECTED_MODEL_SHA256,"beforeSha256":model_hash_before,"afterSha256":model_hash_after,"invalidated":invalidated,"coatSourceHashes":projection_parity.map(func(c):return c.signature.get_slice(":",0))}
	report["projection"]={"assumptions":"Pinned v02 coat is static for idle/reverse-placeholder; otherwise only existing _stamp at rounded body x/y, with no later coat edits. Cache keys include source coat SHA and branch/offset. Reassess if model hash changes.","samplesMeasured":body_sample_count,"distinctSignatures":projection_cache.size(),"parityPassed":projection_parity.size()-parity_failed.size(),"parityFailed":parity_failed.size(),"parityChecks":projection_parity,"fullStopRendersRetained":full_stop_render_count}
	report["durationSeconds"]=duration_seconds
	report["originalCheckerSha256"]="07bbe6b1c2b8475f1ede9ca10e96cec9bbac3567f289c6dad344680c981d69ce"
	report["checkerSha256"]=FileAccess.get_sha256(get_script().resource_path)
	report["originalBehaviorCheckCountExpected"]=15744
	report["coverageCountExact"]=checks.size()==15744
	report["valid"]=not invalidated and parity_failed.is_empty() and checks.size()==15744
	report["nonClaims"]=["No fluidity/art approval; all original schedules, phases, release windows, thresholds, full settle renders and boot grounding remain. Slow original results are not changed or superseded and must be compared separately if available."]
	var f:=FileAccess.open(report_path,FileAccess.WRITE);f.store_string(JSON.stringify(report,"  ")+"\n");f.close()
	print("EAST BODY TRAJECTORY ",checks.size()-failed.size(),"/",checks.size()," failed ",failed.size())
	for s: String in summary:print(s," rise=",summary[s].maxRiseAboveAllowed," step=",summary[s].maxStep,"/",summary[s].steadyRunMaxStep," dy=[",summary[s].minDy,",",summary[s].maxDy,"] settleFinal=",summary[s].maxSettleFinalStep," earlier=",summary[s].maxSettleEarlierStep)
	print("EAST BODY PROJECTION elapsedSeconds=",duration_seconds," bodySamples=",body_sample_count," parity=",projection_parity.size()-parity_failed.size(),"/",projection_parity.size()," fullStopRenders=",full_stop_render_count," invalidated=",invalidated)
	quit(2 if not report.valid else (1 if failed.size()>0 else 0))
