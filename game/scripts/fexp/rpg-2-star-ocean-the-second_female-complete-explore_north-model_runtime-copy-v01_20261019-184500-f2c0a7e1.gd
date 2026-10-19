extends RefCounted
# NORTH (back-view) run/stop v06 = v05 903a75f3 + one root-authorized stop/re-press mechanical change.
# Gait (128 phases, 20-phase stance +12..-7, swing knots, bob, weight shift), 140 px/s, cell, palette, role
# layers, leg drawing and the static endpoint are v05-exact; the 128 steady states and cels are unchanged.
# Changed (stop / re-press transition code only), against the v05 matrix failure families:
#  1. Stop landings: the first foot steps home over 0-0.060 s, the second over 0.020-0.078 s (v05 0-0.07 and
#     0.04-0.11 s), so both are down by the 1/24+1/60+1/48 s mixed sample (0.0792 s) and every 30/60 Hz
#     sample <= 100 ms.
#  2. Stop step path in screen rows: a foot that starts above its home row stays >= 1 row above it until it
#     lands; a foot that starts at/below it (behind) rises to it without passing it, heel peeled (one sole
#     row showing) until it lands. v05 let a recovery heel cross the home row and rise again (dip-relift).
#  3. Torso settle 0.12 s (v05 0.24 s; arms/hair/scarf keep 0.24 s), so the torso's last 1 px and the shin
#     row it gives back happen with the landings, not as an isolated leg re-extension in the last frames.
#  4. Run (re)start contact: from the exact static a planted foot has only 7 world-locked rows left before
#     the gait peel, less than one 30 Hz (9.3 rows) or 24 Hz (11.7 rows) frame. The first frame's travel is
#     known at (re)start: a grounded lead that survives it keeps v05's rule. Otherwise, with both feet down
#     (pre-press double contact) the lead holds its world point through the first frame only (push-off; past
#     the -7 stance end by at most that frame's excess) instead of both feet lifting together (hop); with
#     one or no foot down, the airborne foot re-enters at late swing q108 and lands after 20 rows (71 ms).
#     Restart blends take 0.07 s (v05 0.08 s), and a foot leaving a held contact blends from that contact,
#     not from the pre-press pose (v05 pulled a leaving foot back toward its pre-press pose).
# Test/source only; not registered or adopted by the game. v01-v05 are kept unchanged.
#
# v05 header follows.
# NORTH (back-view) run/stop v05 = v04 a3743d03 mechanics unchanged + one authored-detail cleanup (art only).
# Every line from `var layers` through `snapshot()` (state, timing, gait, stop, re-press) is byte-identical
# to v04; knee_rows() and all geometry are unchanged. Only how two leg details are drawn changed:
#  1. Swing sole underside (rows between the rigid heel rows and the heel cap, only when reveal > 0, so
#     never under a grounded foot): v04's 5-row (x+j)%3 checker tread is replaced by an authored sole in
#     existing static colours: heel face, lit heel underside, a 1 px inset arch, ball row, then the
#     unchanged static heel cap. No new colours, no wider silhouette.
#  2. Strongly foreshortened shins (fewer rows than detail rows: tucked swing, touchdown): rows are kept
#     by a fixed priority (cuff top, hem/cuff overlap, shaft strap, fold, ...) instead of v04's
#     remove-from-middle, so a 1-2 row shin shows the boot cuff above the heel instead of the bare trouser
#     hem (v04 seam). Leg 0 also keeps its foot-top outline row 99 in compressed boots.
# Test/source only; not registered or adopted by the game. v01-v04 are kept unchanged.
#
# v04 header follows.
# NORTH (back-view) run/stop prototype v04: compact-stance gait construction. Test/source only; not
# registered or adopted by the game. v01 5ac05f65, v02 9c5435aa and v03 a93d429d are kept unchanged.
# Identity, palette, role layers and the final endpoint are the produced (unapproved) NORTH idle static
# pilot 9af15df7, read from its repo-local .pxo. No EAST/WEST/SOUTH image is flipped, mirrored or reused.
#
# Disclosed contract change (root-authorized): v02/v03 kept a 38-phase centred stance (+19..-18 rows),
# which forced an 18-row trailing extension. v04 shortens and forward-biases the ground stance to 20
# phases, depth +12 (ahead, partly under the coat hem) to -7 (behind), then an explicit bent-knee heel
# peel at phase 20 (heel cap 2 rows up, sole tread showing) and a tucked recovery swing.
# Unchanged: 140 logical px/s, 128-phase cycle (1 phase per rendered source row = 4.375 steps/s), cell
# 80x128, pivot (40,104), scale 0.5, the same static heel block / heel cap (rows sole-3..sole) as the
# contact feature, the stance law depth = MID - phase (1 source row per phase = world-locked).
#
# Leg construction (replaces the v02 resampled column and the v03 authored near leg): one articulated leg
# per side, hip row -> knee row -> heel cap, drawn from the static rows of the same leg. The thigh maps the
# static rows HIP_ROW..KNEE_ROW, the shin maps KNEE_ROW+1..sole-4 (trouser shin, cuff, boot shaft), the
# heel block is rigid. Detail rows (fold, strap, cuff, buckle) stay one row tall; plain rows repeat or
# drop. In stance the knee splits the hip-heel span in the static thigh:shin ratio (uniform projection of
# a near-straight leg); in swing a thigh factor sets the knee and the shin takes the rest, so a tucked
# heel shortens the boot on screen while the sole shows. At the home pose the map is the identity.
const SOURCE := "res://assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-editable_unapproved-v01_20261018-090713-99e861ce.pxo"
const SRC := Vector2i(80,112)
const CELL := Vector2i(80,128)
const PIVOT := Vector2i(40,104)
const CYCLE := 128.0
# Ground stance length in phases (phases 0..STANCE-1 are grounded) and depth at touchdown (= MID).
const STANCE := 20.0
const MID := 12.0
# Leg 0 = viewer left = character LEFT; leg 1 = viewer right = character RIGHT (knee strap, ponytail side).
const SOLE := [103,102]
const SPLIT_X := 41
const TROUSER_Y := 75
const BOOT_Y := 84
const CUFF_END := 88
const HEEL_ROWS := 4
const HIP_ROW := 62
const KNEE_ROW := 82
const OUTWARD := [-1,1]
# Rows that must stay one row tall when a segment is resampled (fold, knee strap, cuff, shaft strap).
const THIGH_RIGID := [[79,80],[77,78]]
const SHIN_RIGID := [[84,85,86,87,88,95,99],[84,85,86,87,88,93]]
# v05: when a shin has fewer rows than detail rows, keep them in this priority (then source order).
const SHIN_KEEP := [[85,84,95,87,99,86,88],[85,84,93,87,86,88]]
# Swing knots (foot phase, depth rows ahead(+)/behind(-), lift rows, sole reveal 0..1, medial px,
# bend 0..1, thigh factor). Depth/lift are screen source rows (heel cap row = sole - depth - lift).
# bend 0 = stance-like proportional knee; bend 1 = knee at HIP + thigh factor * static thigh.
# Phase 14 and 134 are phantoms on the stance line (shape the end tangents only).
# 19 = last grounded phase (-7). 20 = explicit peel: heel cap 2 rows up, 1 sole row, knee starts to bend.
# 24-52 = heel kicks up and back (sole shows, boot foreshortens). 64-74 = tucked leg passes under the body
# (other foot in mid stance). 90-104 = knee drives forward, shin unfolds under the coat hem.
# 116-127 = foot reaches slightly past and settles back onto the touchdown point (+12) from just above it.
const SWING := [[14.,-2.,0.,0.,0.,0.,1.],[19.,-7.,0.,0.,0.,0.,1.15],[20.,-7.2,2.,.25,0.,.3,1.12],[24.,-7.4,5.5,.5,0.,.7,1.08],[30.,-7.2,10.,.8,.3,1.,1.04],[40.,-6.,14.,1.,.7,1.,1.],[52.,-4.,16.,1.,1.,1.,.9],[64.,-1.,16.,.9,1.,1.,.72],[74.,2.,14.,.6,1.,1.,.58],[90.,7.,10.,.15,.6,1.,.46],[104.,12.6,6.,0.,.2,1.,.5],[116.,13.4,2.6,0.,0.,.6,.6],[124.,12.6,1.1,0.,0.,.2,.64],[127.,12.2,.6,0.,0.,.05,.66],[128.,12.,0.,0.,0.,0.,.66],[134.,6.,0.,0.,0.,0.,.8]]
# Torso height over one step (phase within 64; + = down): lowest in mid stance, highest in flight.
const BOB := [[0.,2.],[6.,3.],[13.,3.],[19.,1.],[26.,0.],[34.,-1.],[46.,-1.],[56.,0.],[61.,1.],[64.,2.]]
const COLORS := {"A":Color8(0x0a,0x0a,0x0e),"H":Color8(0x41,0x30,0x2b),"J":Color8(0x71,0x47,0x30),"Q":Color8(0x20,0x1c,0x20),"F":Color8(0x30,0x25,0x26)}
# Static trouser palette: a outline/shadow, c mid, b lit.
const P := {"a":Color8(0x22,0x28,0x39),"b":Color8(0x4a,0x62,0x5c),"c":Color8(0x32,0x45,0x42)}
# v06 stop/re-press timing (seconds). Landing slots [begin, length]: first, second foot.
const STOP_SLOTS := [[0.,.06],[.02,.058]]
const BODY_SETTLE := .12
const LIVE_SETTLE := .24
const RESTART_BLEND := .07
# Late-swing restart phase of a re-entering airborne foot: touchdown (phase 128) after 20 rows.
const RESTART_SWING := 108.
# Heel peel (one sole row) shown by a foot stepping home from behind until it lands.
const STEP_PEEL := .25
var layers := {}
var original: Image
var physical_y := 0.0
var render_y := 0.0
var origin_y := 0.0
var q0 := MID
var q := MID
var mode := "idle"
var age := 0.0
var stop_age := 0.0
var feet := []
var start_feet := []
var stop_feet := []
var last_body := Vector2.ZERO
var start_body := Vector2.ZERO
var stop_body := Vector2.ZERO
var live := 0.0
var start_live := 0.0
var stop_live := 0.0
var land_order := [0,1]
# v06 restart state: lead foot that may hold its contact through the first run frame, run frame count,
# per-foot blend clock start (age) and whether an anchored foot has followed its gait stance.
var hold_lead := -1
var run_frames := 0
var blend_t0 := [0.,0.]
var following := [false,false]
# fcx-v03 exact render optimization (UNAPPROVED, opt-in pilot only): immutable per-layer RGBA8 lookups built once
# in _init(). render_pose() paints raw RGBA8 buffers instead of per-texel get_pixel/set_pixel, visiting only opaque
# source texels in the same order; every row map, offset and colour test is unchanged, so its RGBA equals the frozen
# v02 copy (oracle-checked). State, timing and the advance() cadence are unchanged; the v02 helpers are kept as written.
class Fast:
	var px := {}     # layer -> PackedInt32Array (80x128, one little-endian RGBA8 texel per int)
	var rows := {}   # layer -> Array of PackedInt32Array: opaque x per row, ascending
	var side := {}   # layer -> [leg 0 rows, leg 1 rows]: opaque x per row inside that leg's columns
	var top := {}    # layer -> first row with an opaque texel (as _row_has scanning down from 0)
	var ink := {}    # COLORS key -> texel int exactly as set_pixel writes it
	var pa := 0
	var pb := 0
	var pc := 0
var _fast: Fast

func _init() -> void:
	var zip := ZIPReader.new()
	assert(zip.open(ProjectSettings.globalize_path(SOURCE))==OK)
	var data: Dictionary=JSON.parse_string(zip.read_file("data.json").get_string_from_utf8())
	for i in data.layers.size():
		var name: String=data.layers[i].name
		if name=="guides":continue
		var src:=Image.create_from_data(SRC.x,SRC.y,false,Image.FORMAT_RGBA8,zip.read_file("image_data/frames/1/layer_"+str(i+1)))
		var padded:=_blank()
		padded.blit_rect(src,Rect2i(Vector2i.ZERO,SRC),Vector2i.ZERO)
		layers[name]=padded
	zip.close()
	original=_blank()
	for image: Image in layers.values():original.blend_rect(image,Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
	feet=[_home(),_home()]
	_build_fast()
func _texel(c: Color) -> int:
	var one:=Image.create(1,1,false,Image.FORMAT_RGBA8)
	one.set_pixel(0,0,c)
	return one.get_data().to_int32_array()[0]
func _build_fast() -> void:
	_fast=Fast.new()
	for name: String in layers:
		var data: PackedInt32Array=(layers[name] as Image).get_data().to_int32_array()
		var rows:=[]
		var left:=[]
		var right:=[]
		for y in CELL.y:
			var xs:=PackedInt32Array()
			var l:=PackedInt32Array()
			var r:=PackedInt32Array()
			for x in CELL.x:
				if (data[y*CELL.x+x]>>24)&255:
					xs.append(x)
					if _leg_cols(0,x):l.append(x)
					if _leg_cols(1,x):r.append(x)
			rows.append(xs);left.append(l);right.append(r)
		_fast.px[name]=data
		_fast.rows[name]=rows
		_fast.side[name]=[left,right]
		var top:=0
		while top<SRC.y and (rows[top] as PackedInt32Array).is_empty():top+=1
		_fast.top[name]=top
	for key in COLORS:_fast.ink[key]=_texel(COLORS[key])
	_fast.pa=_texel(P.a);_fast.pb=_texel(P.b);_fast.pc=_texel(P.c)
func _blank_px() -> PackedInt32Array:
	var px:=PackedInt32Array()
	px.resize(CELL.x*CELL.y)
	px.fill(0)
	return px
func _image(px: PackedInt32Array) -> Image:return Image.create_from_data(CELL.x,CELL.y,false,Image.FORMAT_RGBA8,px.to_byte_array())
func _home() -> Dictionary:
	return {"lift":0.,"reveal":0.,"depth":0.,"medial":0.,"bend":0.,"thigh":1.,"ground":true,"phase":-1.}
func _ease(t: float) -> float:return smoothstep(0.,1.,clampf(t,0.,1.))
# Cubic Hermite through knots [[x, v1, v2, ...]] with tangents (v[k+1]-v[k-1])/(x[k+1]-x[k-1]) in units of
# x (non-uniform spacing handled); the first and last knots are phantoms that only shape the end tangents.
func _curve(knots: Array,x: float,column: int) -> float:
	var n := knots.size()-1
	var k := 1
	while k<n-2 and x>knots[k+1][0]:k+=1
	var x1: float=knots[k][0]
	var x2: float=knots[k+1][0]
	var w: float=x2-x1
	var t: float=clampf((x-x1)/w,0.,1.)
	var p1: float=knots[k][column]
	var p2: float=knots[k+1][column]
	var m1: float=(p2-float(knots[k-1][column]))/(x2-float(knots[k-1][0]))*w
	var m2: float=(float(knots[k+2][column])-p1)/(float(knots[k+2][0])-x1)*w
	var t2 := t*t
	var t3 := t2*t
	return (2.*t3-3.*t2+1.)*p1+(t3-2.*t2+t)*m1+(-2.*t3+3.*t2)*p2+(t3-t2)*m2
func _periodic(knots: Array,x: float) -> float:
	var period: float=knots[-1][0]-knots[0][0]
	x=fposmod(x-knots[0][0],period)+knots[0][0]
	var k := 0
	while k<knots.size()-2 and x>knots[k+1][0]:k+=1
	var t: float=(x-knots[k][0])/(knots[k+1][0]-knots[k][0])
	return lerpf(knots[k][1],knots[k+1][1],smoothstep(0.,1.,t))
func gait_foot(phase: float) -> Dictionary:
	phase=fposmod(phase,CYCLE)
	if phase<STANCE:
		# World-ground stance: flat boot, depth falls 1 source row per phase (= rendered travel).
		return {"lift":0.,"reveal":0.,"depth":MID-phase,"medial":0.,"bend":0.,"thigh":1.,"ground":true,"phase":phase}
	var x := phase
	return {"lift":maxf(0.,_curve(SWING,x,2)),"reveal":clampf(_curve(SWING,x,3),0.,1.),"depth":_curve(SWING,x,1),"medial":clampf(_curve(SWING,x,4),0.,1.),"bend":clampf(_curve(SWING,x,5),0.,1.),"thigh":_curve(SWING,x,6),"ground":false,"phase":phase}
func steady_body(phase_q: float) -> Vector2:
	# Weight shifts toward the stance foot (leg 0 mid stance q10, leg 1 mid stance q74).
	return Vector2(-cos((phase_q-10.)*TAU/CYCLE),_periodic(BOB,fposmod(phase_q,64.)))
func _copy_feet(value: Array) -> Array:return [value[0].duplicate(true),value[1].duplicate(true)]
func _mix(a: Dictionary,b: Dictionary,t: float) -> Dictionary:
	if t>=1.:return b.duplicate(true)
	var out := b.duplicate(true)
	for key in ["lift","reveal","depth","medial","bend","thigh"]:out[key]=lerpf(a[key],b[key],t)
	out.ground=false
	return out
# v06: a grounded foot at depth d is at stance phase MID-d; true if it is still in stance after `rows`.
func _stance_survives(i: int,rows: float) -> bool:return MID-roundf(feet[i].depth)+rows<=STANCE-1.
func _begin_run(previous_render_y: float) -> void:
	# (Re)start from idle or stop. The first frame's travel in rows is already known (render_y is updated).
	var rows1 := roundf((previous_render_y-render_y)*2.)
	hold_lead=-1
	# Grounded feet keep their world contact; the lead is the one farther ahead (most stance left), as v05.
	var lead := -1
	var grounded := 0
	for i in 2:
		if feet[i].ground:
			grounded+=1
			if lead<0 or feet[i].depth>feet[lead].depth:lead=i
	if lead>=0 and (grounded==2 or _stance_survives(lead,rows1)):
		q0=fposmod(MID-roundf(feet[lead].depth)-lead*64.,CYCLE)
		# Both feet down and the lead's stance ends inside the first frame: it holds through that frame
		# (push-off) rather than both feet lifting together.
		if not _stance_survives(lead,rows1):hold_lead=lead
	else:
		# One or no foot down and no surviving stance: the airborne foot (the lower one if both) re-enters at
		# late swing and lands after 20 rows; a grounded foot leaves into its swing from its contact.
		var air: int=(1-lead) if lead>=0 else (1 if feet[1].lift<feet[0].lift else 0)
		q0=fposmod(RESTART_SWING-air*64.,CYCLE)
	origin_y=previous_render_y
	start_feet=_copy_feet(feet)
	start_body=last_body
	start_live=live
	blend_t0=[0.,0.]
	following=[false,false]
	run_frames=0
	mode="run"
	age=0.
# v06 stop step home over its slot (t 0..1), in screen rows above the home row (h = depth + lift).
func _step_home(sf: Dictionary,t: float) -> Dictionary:
	var e := _ease(t)
	var out := _mix(sf,_home(),e)
	var d := roundi(float(out.depth))
	var h0 := roundi(float(sf.depth))+roundi(float(sf.lift))
	if h0>=1:
		# Starts above the home row: stays at least one row above it until it lands (a planted foot ahead
		# lifts clear with the v05 recovery arc).
		var arc := (2.+.25*absf(sf.depth))*sqrt(sin(PI*e)) if sf.ground else 0.
		out.lift=float(maxi(maxi(1,roundi(lerpf(float(h0),0.,e)+arc))-d,1))
	else:
		# Starts at or below the home row (behind): rises to it without passing it, heel peeled until it lands.
		out.lift=float(maxi(mini(0,roundi(lerpf(float(h0),0.,e)))-d,0))
		out.reveal=maxf(float(out.reveal),STEP_PEEL)
	return out
func advance(delta: float,world_y: float,intent: float) -> Dictionary:
	var previous_body_pixel := roundi(last_body.y)
	var previous_render_y := render_y
	var moved_north := world_y<physical_y-0.000001
	physical_y=world_y
	render_y=roundf(world_y*2.)*.5
	if intent>0. and moved_north:
		if mode!="run":_begin_run(previous_render_y)
		age+=delta
		run_frames+=1
		var travelled := (origin_y-render_y)*2.
		q=fposmod(q0+roundf(travelled),CYCLE)
		for i in 2:
			var g:=gait_foot(q+i*64.)
			# A foot that was planted when the run began stays planted on its world point (no blend).
			if start_feet[i].ground and start_feet[i].phase!=-2.:
				if g.ground:
					feet[i]=g
					following[i]=true
					continue
				if i==hold_lead and run_frames==1:
					# Push-off hold: the stance law continued through this first frame (world-locked).
					var ph := fposmod(q+i*64.,CYCLE)
					feet[i]={"lift":0.,"reveal":0.,"depth":MID-ph,"medial":0.,"bend":0.,"thigh":1.,"ground":true,"phase":ph}
					continue
				# It leaves its contact: after following its stance it continues in the gait exactly (as the
				# steady run); after a held contact it blends from that contact; otherwise from its start pose.
				start_feet[i].phase=-2.
				if following[i]:
					blend_t0[i]=-1.
				elif i==hold_lead:
					start_feet[i]=feet[i].duplicate(true)
					start_feet[i].phase=-2.
					blend_t0[i]=age-delta
			var t := _ease((age-float(blend_t0[i]))/RESTART_BLEND)
			feet[i]=_mix(start_feet[i],g,t)
			# A foot still blending toward its gait state is airborne: at least 1 row off the ground.
			if t<1.:feet[i].lift=maxf(feet[i].lift,1.)
		last_body=start_body.lerp(steady_body(q),_ease(age/.10))
		live=lerpf(start_live,1.,_ease(age/.08))
		# Rendered torso guard (EAST v03 concept): at most 1 source px per 60 Hz frame.
		var budget := maxi(0,ceili(48.0*maxf(delta,0.0)-0.000000001))
		last_body.y=float(clampi(roundi(last_body.y),previous_body_pixel-budget,previous_body_pixel+budget))
		last_body.x=float(roundi(last_body.x))
	else:
		if mode=="run":
			mode="stop"
			stop_age=0.
			stop_feet=_copy_feet(feet)
			stop_body=last_body
			stop_live=live
			# Airborne feet land first (lower one first); a planted foot holds its world point until it
			# steps home after them.
			land_order=[0,1]
			var key0: float=(100. if stop_feet[0].ground else 0.)+stop_feet[0].lift
			var key1: float=(100. if stop_feet[1].ground else 0.)+stop_feet[1].lift
			if key1<key0:land_order=[1,0]
		if mode=="stop":
			stop_age+=delta
			for slot in 2:
				var i: int=land_order[slot]
				# v06: both feet are home by 0.078 s (slots 0-0.060 and 0.020-0.078 s); the torso settles by
				# 0.12 s; only arms/hair/scarf continue to 0.24 s, so the last moving frames carry no leg change.
				var begin: float=STOP_SLOTS[slot][0]
				var sf: Dictionary=stop_feet[i]
				var t := clampf((stop_age-begin)/float(STOP_SLOTS[slot][1]),0.,1.)
				if sf.ground and absf(sf.depth)<.5:
					feet[i]=_home()
				elif sf.ground and stop_age<=begin:
					feet[i]=sf.duplicate(true)
				elif t>=1.:
					feet[i]=_home()
				else:
					feet[i]=_step_home(sf,t)
			var w := _ease(stop_age/BODY_SETTLE)
			last_body=Vector2(roundf(stop_body.x*(1.-w)),roundf(stop_body.y*(1.-w)))
			live=stop_live*(1.-_ease(stop_age/LIVE_SETTLE))
			if stop_age>=.26:
				mode="idle"
				feet=[_home(),_home()]
				last_body=Vector2.ZERO
				live=0.
	return snapshot()
func snapshot() -> Dictionary:
	return {"mode":mode,"q":q,"age":age,"stopAge":stop_age,"feet":_copy_feet(feet),"body":last_body,"live":live,"physicalY":physical_y,"renderY":render_y}
func _blank() -> Image:return Image.create(CELL.x,CELL.y,false,Image.FORMAT_RGBA8)
func _stamp(source: Image,dx: int,dy: int) -> Image:
	var image:=_blank()
	image.blit_rect(source,Rect2i(Vector2i.ZERO,CELL),Vector2i(dx,dy))
	return image
func _leg_cols(i: int,x: int) -> bool:return x<SPLIT_X if i==0 else x>=SPLIT_X
func _row(r: int,d0: int,d1: int,s0: int,s1: int) -> int:
	if d1<=d0:return s0
	return s0+clampi(floori((float(r-d0)+.5)*float(s1-s0+1)/float(d1-d0+1)),0,s1-s0)
func _put(image: Image,x: int,y: int,c: Color) -> void:
	if x>=0 and x<CELL.x and y>=0 and y<CELL.y and c.a8>0:image.set_pixel(x,y,c)
# Destination->source rows for s0..s1 drawn over n rows: detail rows stay one row tall; plain rows are
# repeated (or dropped) evenly. With fewer rows than detail rows, rows are removed from the middle.
func _detail_map(s0: int,s1: int,n: int,rigid: Array,keep: Array=[]) -> Array:
	# v05: fewer rows than detail rows -> the first n rows of the keep priority, in source order.
	if keep.size()>0 and n<rigid.size():
		var kept: Array=keep.slice(0,maxi(1,n))
		kept.sort()
		return kept
	var plain := []
	var counts := {}
	for s in range(s0,s1+1):
		counts[s]=1
		if not rigid.has(s):plain.append(s)
	var extra := n-(s1-s0+1)
	if plain.size()>0 and extra!=0:
		for k in absi(extra):
			var s: int=plain[mini(plain.size()-1,floori((float(k)+.5)*float(plain.size())/float(absi(extra))))]
			counts[s]=maxi(0,counts[s]+(1 if extra>0 else -1))
	var out := []
	for s in range(s0,s1+1):
		for c in range(int(counts[s])):out.append(s)
	while out.size()>n:out.remove_at(out.size()>>1)
	while out.size()<n:out.append(s1)
	return out
# Knee row for a leg state: stance-like proportional split blended with the swing thigh factor.
func knee_rows(i: int,foot: Dictionary,body_y: int) -> Dictionary:
	var sole: int=SOLE[i]
	var patch := roundi(5.*float(foot.reveal))
	var bottom: int=sole-roundi(foot.depth)-roundi(foot.lift)
	var hip := HIP_ROW+body_y
	var t0 := KNEE_ROW-HIP_ROW
	var s0 := sole-KNEE_ROW
	var span := bottom-hip
	var prop := float(span)/float(t0+s0)
	var f := lerpf(prop,float(foot.thigh),float(foot.bend))
	var heel_top := bottom-1-patch-2
	var thigh := clampi(roundi(float(t0)*f),3,maxi(3,heel_top-hip-2))
	var knee := hip+thigh
	return {"bottom":bottom,"patch":patch,"hip":hip,"knee":knee,"heelTop":heel_top,"thighRows":thigh,"shinRows":bottom-knee,"thighRatio":float(thigh)/float(t0),"shinRatio":float(bottom-knee)/float(s0),"spanRatio":float(span)/float(t0+s0)}
# One articulated leg (see header). Bottom-up: the static heel cap (sole-1, sole) always closes the boot
# (the named contact feature); above it the revealed sole rows; the static heel rows (sole-3, sole-2);
# the shin (static rows KNEE_ROW+1..sole-4); the thigh (static rows HIP_ROW..KNEE_ROW, visible part from
# TROUSER_Y). Trousers and boots use the same row map, so the cuff stays on the trouser hem.
func _leg(i: int,foot: Dictionary,body: Vector2i,vent: Image) -> Dictionary:
	var trousers: Image=layers["legs"]
	var boots: Image=layers["boots"]
	var sole: int=SOLE[i]
	var kr := knee_rows(i,foot,body.y)
	var bottom: int=kr.bottom
	var patch: int=kr.patch
	var patch_top := bottom-1-patch
	var heel_top: int=kr.heelTop
	var hip: int=kr.hip
	var knee: int=kr.knee
	var bx: int = -roundi(foot.medial)*OUTWARD[i]
	var hem := 74+body.y
	var tmap := _detail_map(HIP_ROW,KNEE_ROW,knee-hip+1,THIGH_RIGID[i])
	var smap := _detail_map(KNEE_ROW+1,sole-HEEL_ROWS,maxi(1,heel_top-knee-1),SHIN_RIGID[i],SHIN_KEEP[i])
	var identity := true
	var boot:=_blank()
	var leg:=_blank()
	# Fill under the coat hem with the first trouser row so a lifting hem never shows a gap (as v02).
	var first_visible := -1
	for y in range(hip,heel_top):
		var s: int=tmap[y-hip] if y<=knee else smap[mini(y-knee-1,smap.size()-1)]
		if s!=y-body.y:identity=false
		if s>=TROUSER_Y and first_visible<0:first_visible=y
		var dx := bx
		if y<=knee:dx=roundi(lerpf(float(body.x),float(bx),float(y-hip)/maxf(1.,float(knee-hip))))
		for x in CELL.x:
			if not _leg_cols(i,x):continue
			if s>=TROUSER_Y:_put(leg,x+dx,y,trousers.get_pixel(x,s))
			if y<=hem and x+dx>=0 and x+dx<CELL.x and vent.get_pixel(x+dx,y).a8>0:continue
			_put(boot,x+dx,y,boots.get_pixel(x,s))
	if first_visible<0:first_visible=heel_top
	for y in range(maxi(0,TROUSER_Y-3+body.y),first_visible):
		for x in CELL.x:
			if _leg_cols(i,x):_put(leg,x+body.x,y,trousers.get_pixel(x,TROUSER_Y))
	# Knee crease when the knee is visibly bent below the hem: the trouser row at the knee darkens
	# (lit -> mid, mid -> shadow), static palette only.
	var flexed: bool=float(foot.bend)>.5 and kr.shinRatio<.85 and knee>hem+1
	if flexed:
		identity=false
		for x in CELL.x:
			var c := leg.get_pixel(x,knee)
			if c.a8==0:continue
			if c==P.b:leg.set_pixel(x,knee,P.c)
			elif c==P.c:leg.set_pixel(x,knee,P.a)
	# Rigid heel rows (sole-3, sole-2) and heel cap (sole-1, sole): the static contact block.
	for n in 2:
		for x in CELL.x:
			if not _leg_cols(i,x):continue
			_put(boot,x+bx,heel_top+n,boots.get_pixel(x,sole-3+n))
			_put(boot,x+bx,bottom-1+n,boots.get_pixel(x,sole-1+n))
	if heel_top!=sole-3 or bottom!=sole or bx!=0:identity=false
	# Revealed sole between heel and the heel cap (v05, authored; static palette, outline A). Row 0 is the
	# heel face (as v04). Below it the rubber sole seen from behind: lit heel underside (H then F on the
	# lit viewer-left side, Q in shadow), arch rows inset 1 px each side (one F glint), and a ball row before
	# the unchanged heel cap. No per-texel tread pattern.
	var span := Vector2i(CELL.x,-1)
	for x in CELL.x:
		if _leg_cols(i,x) and boots.get_pixel(x,sole-2).a8>0:span=Vector2i(mini(span.x,x),maxi(span.y,x))
	for j in patch:
		var y := patch_top+j
		var r := j-1
		var arch: bool=j>0 and r>0 and (r<patch-2 or patch==3)
		var x0 := span.x+(1 if arch else 0)
		var x1 := span.y-(1 if arch else 0)
		for x in range(x0,x1+1):
			var key := "A"
			if x>x0 and x<x1:
				if j==0:key="J" if x<=span.x+2 else "H"
				elif arch:key="F" if x==x0+1 else "Q"
				elif r==0:key="H" if x<=span.x+2 else ("F" if x<=span.x+4 else "Q")
				else:key="F" if x<=span.x+2 else "Q"
			_put(boot,x+bx,y,COLORS[key])
	var info: Dictionary=kr.duplicate()
	info["soleRow"]=bottom
	info["kneeCrease"]=flexed
	info["identityMap"]=identity
	# Articulation amount of the foot state (0 only at the exact home pose): used by the stop checks.
	info["near"]=0. if (absf(foot.depth)<.001 and absf(foot.lift)<.001 and absf(foot.reveal)<.001 and absf(foot.medial)<.001 and absf(foot.bend)<.001) else 1.
	return {"trousers":leg,"boot":boot,"info":info}
# Coat skirt: the hem over a raised knee rises up to 2 px on that side.
func _coat(body: Vector2i,hem: Array) -> Image:
	var source: Image=layers["coat"]
	var image:=_blank()
	for y in SRC.y:
		for x in CELL.x:
			var h: int=hem[0] if x<SPLIT_X else hem[1]
			var s := y
			if y>=62 and h>0:
				if y>74-h:continue
				s=_row(y,62,74-h,62,74)
			_put(image,x+body.x,y+body.y,source.get_pixel(x,s))
	return image
# Free-end follow-through: rows below `root` shift progressively toward the tip (inverse nearest map).
func _follow(source: Image,body: Vector2i,root: int,tip: int,tip_shift: Vector2) -> Image:
	var image:=_blank()
	for y in CELL.y:
		for x in CELL.x:
			var f := clampf(float(y-body.y-root)/float(tip-root),0.,1.)
			var s := Vector2i(x-body.x-roundi(tip_shift.x*f),y-body.y-roundi(tip_shift.y*f))
			if s.x<0 or s.x>=CELL.x or s.y<0 or s.y>=CELL.y:continue
			var c := source.get_pixelv(s)
			if c.a8>0:image.set_pixel(x,y,c)
	return image
# Arm (unchanged from v01): run carriage raises the elbow and shortens the forearm; swung back the elbow
# goes out and the glove shows at the hip; swung forward the hand passes in front of the body.
func _arm(name: String,side: int,body: Vector2i,carry: float,swing: float) -> Image:
	var source: Image=layers[name]
	var image:=_blank()
	var top := 0
	while top<SRC.y and not _row_has(source,top):top+=1
	var back := maxf(0.,swing)
	var fwd := maxf(0.,-swing)
	var raise := roundi(carry*(1.+back+.5*fwd))
	var hidden := roundi(9.*carry*fwd)
	var fore_src := 11-hidden
	var fore_dst := maxi(1,roundi(float(fore_src)*(1.-.3*carry)))
	var elbow_dx: int = roundi(carry*swing)*OUTWARD[side]
	var d_cuff := 51-raise
	for y in range(top,d_cuff):
		var s := _row(y,top,d_cuff-1,top,50)
		var dx := roundi(float(elbow_dx)*float(y-top)/maxf(1.,float(d_cuff-1-top)))
		for x in CELL.x:_put(image,x+dx+body.x,y+body.y,source.get_pixel(x,s))
	for y in range(d_cuff,d_cuff+4):
		for x in CELL.x:_put(image,x+elbow_dx+body.x,y+body.y,source.get_pixel(x,51+y-d_cuff))
	var f0 := d_cuff+4
	for y in range(f0,f0+fore_dst):
		var s := _row(y,f0,f0+fore_dst-1,55,55+fore_src-1)
		for x in CELL.x:_put(image,x+elbow_dx+body.x,y+body.y,source.get_pixel(x,s))
	if hidden>0:
		var y := f0+fore_dst+body.y
		if y>0 and y<CELL.y:
			for x in CELL.x:
				if image.get_pixel(x,y-1).a8>0:image.set_pixel(x,y,COLORS.A)
	return image
func _row_has(image: Image,y: int) -> bool:
	for x in CELL.x:
		if image.get_pixel(x,y).a8>0:return true
	return false
# fcx-v03 raw-buffer forms of _leg/_coat/_follow/_arm (same rows, offsets, tests and write order as v02).
func _leg_fast(i: int,foot: Dictionary,body: Vector2i,vent: PackedInt32Array) -> Dictionary:
	var tr_px: PackedInt32Array=_fast.px["legs"]
	var bo_px: PackedInt32Array=_fast.px["boots"]
	var tr_rows: Array=_fast.side["legs"][i]
	var bo_rows: Array=_fast.side["boots"][i]
	var sole: int=SOLE[i]
	var kr := knee_rows(i,foot,body.y)
	var bottom: int=kr.bottom
	var patch: int=kr.patch
	var patch_top := bottom-1-patch
	var heel_top: int=kr.heelTop
	var hip: int=kr.hip
	var knee: int=kr.knee
	var bx: int = -roundi(foot.medial)*OUTWARD[i]
	var hem := 74+body.y
	var tmap := _detail_map(HIP_ROW,KNEE_ROW,knee-hip+1,THIGH_RIGID[i])
	var smap := _detail_map(KNEE_ROW+1,sole-HEEL_ROWS,maxi(1,heel_top-knee-1),SHIN_RIGID[i],SHIN_KEEP[i])
	var identity := true
	var boot:=_blank_px()
	var leg:=_blank_px()
	var W:=CELL.x
	var first_visible := -1
	for y in range(hip,heel_top):
		var s: int=tmap[y-hip] if y<=knee else smap[mini(y-knee-1,smap.size()-1)]
		if s!=y-body.y:identity=false
		if s>=TROUSER_Y and first_visible<0:first_visible=y
		var dx := bx
		if y<=knee:dx=roundi(lerpf(float(body.x),float(bx),float(y-hip)/maxf(1.,float(knee-hip))))
		if y<0 or y>=CELL.y:continue
		if s>=TROUSER_Y:
			for x in tr_rows[s]:
				var qx: int=x+dx
				if qx>=0 and qx<W:leg[y*W+qx]=tr_px[s*W+x]
		var vent_rows := y<=hem
		for x in bo_rows[s]:
			var qx: int=x+dx
			if qx<0 or qx>=W:continue
			if vent_rows and (vent[y*W+qx]>>24)&255:continue
			boot[y*W+qx]=bo_px[s*W+x]
	if first_visible<0:first_visible=heel_top
	for y in range(maxi(0,TROUSER_Y-3+body.y),first_visible):
		if y>=CELL.y:break
		for x in tr_rows[TROUSER_Y]:
			var qx: int=x+body.x
			if qx>=0 and qx<W:leg[y*W+qx]=tr_px[TROUSER_Y*W+x]
	var flexed: bool=float(foot.bend)>.5 and kr.shinRatio<.85 and knee>hem+1
	if flexed:
		identity=false
		if knee>=0 and knee<CELL.y:
			for x in W:
				var c:=leg[knee*W+x]
				if not ((c>>24)&255):continue
				if c==_fast.pb:leg[knee*W+x]=_fast.pc
				elif c==_fast.pc:leg[knee*W+x]=_fast.pa
	for n in 2:
		var hy:=heel_top+n
		if hy>=0 and hy<CELL.y:
			for x in bo_rows[sole-3+n]:
				var qx: int=x+bx
				if qx>=0 and qx<W:boot[hy*W+qx]=bo_px[(sole-3+n)*W+x]
		var cy:=bottom-1+n
		if cy>=0 and cy<CELL.y:
			for x in bo_rows[sole-1+n]:
				var qx: int=x+bx
				if qx>=0 and qx<W:boot[cy*W+qx]=bo_px[(sole-1+n)*W+x]
	if heel_top!=sole-3 or bottom!=sole or bx!=0:identity=false
	var span := Vector2i(CELL.x,-1)
	var heel_row: PackedInt32Array=bo_rows[sole-2]
	if not heel_row.is_empty():span=Vector2i(heel_row[0],heel_row[heel_row.size()-1])
	var ink: Dictionary=_fast.ink
	for j in patch:
		var y := patch_top+j
		var r := j-1
		var arch: bool=j>0 and r>0 and (r<patch-2 or patch==3)
		var x0 := span.x+(1 if arch else 0)
		var x1 := span.y-(1 if arch else 0)
		if y<0 or y>=CELL.y:continue
		for x in range(x0,x1+1):
			var key := "A"
			if x>x0 and x<x1:
				if j==0:key="J" if x<=span.x+2 else "H"
				elif arch:key="F" if x==x0+1 else "Q"
				elif r==0:key="H" if x<=span.x+2 else ("F" if x<=span.x+4 else "Q")
				else:key="F" if x<=span.x+2 else "Q"
			var qx: int=x+bx
			if qx>=0 and qx<W:boot[y*W+qx]=ink[key]
	var info: Dictionary=kr.duplicate()
	info["soleRow"]=bottom
	info["kneeCrease"]=flexed
	info["identityMap"]=identity
	info["near"]=0. if (absf(foot.depth)<.001 and absf(foot.lift)<.001 and absf(foot.reveal)<.001 and absf(foot.medial)<.001 and absf(foot.bend)<.001) else 1.
	return {"trousers":_image(leg),"boot":_image(boot),"info":info}
func _coat_fast(body: Vector2i,hem: Array) -> Image:
	var src: PackedInt32Array=_fast.px["coat"]
	var rows: Array=_fast.rows["coat"]
	var out:=_blank_px()
	var W:=CELL.x
	for y in SRC.y:
		var py:=y+body.y
		if py<0 or py>=CELL.y:continue
		var s0:=y
		var s1:=y
		var skip0:=false
		var skip1:=false
		var h0: int=hem[0]
		var h1: int=hem[1]
		if y>=62 and h0>0:
			if y>74-h0:skip0=true
			else:s0=_row(y,62,74-h0,62,74)
		if y>=62 and h1>0:
			if y>74-h1:skip1=true
			else:s1=_row(y,62,74-h1,62,74)
		if not skip0:
			for x in rows[s0]:
				if x>=SPLIT_X:break
				var qx: int=x+body.x
				if qx>=0 and qx<W:out[py*W+qx]=src[s0*W+x]
		if not skip1:
			for x in rows[s1]:
				if x<SPLIT_X:continue
				var qx: int=x+body.x
				if qx>=0 and qx<W:out[py*W+qx]=src[s1*W+x]
	return _image(out)
func _follow_fast(name: String,body: Vector2i,root: int,tip: int,tip_shift: Vector2) -> Image:
	var src: PackedInt32Array=_fast.px[name]
	var rows: Array=_fast.rows[name]
	var out:=_blank_px()
	var W:=CELL.x
	for y in CELL.y:
		var f := clampf(float(y-body.y-root)/float(tip-root),0.,1.)
		var sy: int=y-body.y-roundi(tip_shift.y*f)
		if sy<0 or sy>=CELL.y:continue
		var shift: int=body.x+roundi(tip_shift.x*f)
		for x in rows[sy]:
			var qx: int=x+shift
			if qx>=0 and qx<W:out[y*W+qx]=src[sy*W+x]
	return _image(out)
func _arm_fast(name: String,side: int,body: Vector2i,carry: float,swing: float) -> Image:
	var src: PackedInt32Array=_fast.px[name]
	var rows: Array=_fast.rows[name]
	var out:=_blank_px()
	var W:=CELL.x
	var top: int=_fast.top[name]
	var back := maxf(0.,swing)
	var fwd := maxf(0.,-swing)
	var raise := roundi(carry*(1.+back+.5*fwd))
	var hidden := roundi(9.*carry*fwd)
	var fore_src := 11-hidden
	var fore_dst := maxi(1,roundi(float(fore_src)*(1.-.3*carry)))
	var elbow_dx: int = roundi(carry*swing)*OUTWARD[side]
	var d_cuff := 51-raise
	for y in range(top,d_cuff):
		var s := _row(y,top,d_cuff-1,top,50)
		var dx := roundi(float(elbow_dx)*float(y-top)/maxf(1.,float(d_cuff-1-top)))
		_arm_row(out,src,rows[s],s,dx+body.x,y+body.y)
	for y in range(d_cuff,d_cuff+4):
		var s:=51+y-d_cuff
		_arm_row(out,src,rows[s],s,elbow_dx+body.x,y+body.y)
	var f0 := d_cuff+4
	for y in range(f0,f0+fore_dst):
		var s := _row(y,f0,f0+fore_dst-1,55,55+fore_src-1)
		_arm_row(out,src,rows[s],s,elbow_dx+body.x,y+body.y)
	if hidden>0:
		var y := f0+fore_dst+body.y
		if y>0 and y<CELL.y:
			var ink: int=_fast.ink["A"]
			for x in W:
				if (out[(y-1)*W+x]>>24)&255:out[y*W+x]=ink
	return _image(out)
func _arm_row(out: PackedInt32Array,src: PackedInt32Array,xs: PackedInt32Array,s: int,shift: int,py: int) -> void:
	if py<0 or py>=CELL.y:return
	for x in xs:
		var qx: int=x+shift
		if qx>=0 and qx<CELL.x:out[py*CELL.x+qx]=src[s*CELL.x+x]
func render_pose(state: Dictionary) -> Dictionary:
	if state.mode=="idle":
		return {"full":original.duplicate(),"roles":layers.duplicate(),"soleRows":SOLE.duplicate()}
	var b: Vector2=state.body
	var body := Vector2i(roundi(b.x),roundi(b.y))
	var amount: float=state.live
	var roles: Dictionary={}
	var trousers:=_blank()
	var boots:=_blank()
	var soles:=[]
	var legs_info:=[]
	var leg_images:=[]
	var vent:=_stamp(_vent(),body.x,body.y)
	var vent_px: PackedInt32Array=vent.get_data().to_int32_array()
	var hem:=[0,0]
	for i in 2:
		var data:=_leg_fast(i,state.feet[i],body,vent_px)
		trousers.blend_rect(data.trousers,Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
		boots.blend_rect(data.boot,Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
		soles.append(data.info.soleRow)
		legs_info.append(data.info)
		leg_images.append({"trousers":data.trousers,"boot":data.boot})
		# The hem rises over a knee lifted well above its standing row.
		hem[i]=clampi(roundi(float(KNEE_ROW+body.y-int(data.info.knee)-3)/4.),0,2)
	trousers.blend_rect(vent,Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
	roles["legs"]=trousers
	roles["boots"]=boots
	roles["coat"]=_coat_fast(body,hem)
	var qq: float=state.q
	var bob_now := _periodic(BOB,fposmod(qq,64.))
	var pony := Vector2(2.*cos((qq-40.)*TAU/CYCLE),_periodic(BOB,fposmod(qq-12.,64.))-bob_now)*amount
	var scarf := Vector2(1.5*cos((qq-44.)*TAU/CYCLE),-1.-maxf(0.,-bob_now))*amount
	roles["scarf-tail"]=_follow_fast("scarf-tail",body,60,78,scarf)
	var swing := cos(qq*TAU/CYCLE)*amount
	roles["arm-left"]=_arm_fast("arm-left",0,body,amount,swing)
	roles["arm-right"]=_arm_fast("arm-right",1,body,amount,-swing)
	for name in ["pack","canister","straps","bedroll","collar","hair"]:roles[name]=_stamp(layers[name],body.x,body.y)
	roles["ponytail"]=_follow_fast("ponytail",body,13,32,pony)
	var full:=_blank()
	for name: String in layers:full.blend_rect(roles[name],Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
	return {"full":full,"roles":roles,"soleRows":soles,"legs":legs_info,"legImages":leg_images}
# Legs-layer texels above the trousers (inner thighs seen through the coat vent) move with the torso.
func _vent() -> Image:
	var image:=_blank()
	image.blit_rect(layers["legs"],Rect2i(0,0,CELL.x,TROUSER_Y),Vector2i.ZERO)
	return image
