extends RefCounted
# NORTH (back-view) run/stop prototype v02: contact-trajectory correction of v01 5ac05f65 (kept unchanged as
# the failed contact baseline). Test/source only; not registered or adopted by the game.
# Identity, palette, role layers and the final endpoint are the produced (unapproved) NORTH idle static
# pilot 9af15df7, read from its repo-local .pxo. No EAST/WEST/SOUTH image is flipped, mirrored or reused.
# v02 contact contract: a planted foot is world-ground contact. The game moves the hero 1 world px per
# 2 source rows, and the gait clock advances 1 phase per source row of rendered travel, so a stance foot
# whose depth falls by exactly 1 source row per phase (depth = 19 - phase, 38 phases) keeps its heel cap
# (static boot rows sole-1..sole) at one world position for the whole stance at any frame rate.
# The ground stride is therefore drawn as projection: ahead = higher on screen (the far boot goes up under
# the coat hem), behind = lower (the near boot extends below the standing line). The cell grows from
# 80x112 to 80x128 with transparent rows at the bottom only; the pivot stays (40,104) and the scale 0.5,
# so every static texel keeps its world position. Heel peel happens explicitly at swing start (phases
# 38-46): the heel cap rises along the lift curve and the static-palette sole tread is revealed above it.
# The toe pivot is hidden behind the boot in a back view and is not drawn.
const SOURCE := "res://assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-editable_unapproved-v01_20261018-090713-99e861ce.pxo"
const SRC := Vector2i(80,112)
const CELL := Vector2i(80,128)
const PIVOT := Vector2i(40,104)
const CYCLE := 128.0
const STANCE := 38.0
# Stance depth (source rows ahead of the pivot) at phase p is MID - p: +19 at touchdown, -18 at the last
# stance phase. MID is also the fresh-start phase, where the stance depth is 0 (static pose).
const MID := 19.0
# Leg 0 = viewer left = character LEFT; leg 1 = viewer right = character RIGHT (knee strap, ponytail side).
const SOLE := [103,102]
const SPLIT_X := 41
const TROUSER_Y := 75
const TROUSER_END := 85
const BOOT_Y := 84
const CUFF_END := 88
const HEEL_ROWS := 4
# Hidden hip row (under the coat). Leg span hip->heel scales the stretchable rows (trousers, boot shaft);
# cuff (5 rows) and heel block (4 rows) stay rigid.
const HIP_ROW := 62
const RIGID_ROWS := 9
const OUTWARD := [-1,1]
# Swing knots (foot phase, lift px, sole reveal 0..1, depth px ahead(+)/behind(-), medial px). The first
# and last knots are phantoms continuing the stance line (depth slope -1), so the foot leaves and meets the
# ground with stance velocity. 38-44 = explicit heel peel; 44-64 = sharp kick back toward the camera
# (heel up, sole showing) so the near boot leaves the extended late-stance line quickly; 78-94 = passing
# under the body; 108-128 = reach ahead and land at depth +19.
# Iteration note: the first v02 curve ([46,5,.6,-23],[56,12,1,-22],[66,15,1,-15],[80,12,.5,-3]) kept the
# lifted boot below the standing line until ~phase 56, which read as a stilt leg in the 60 Hz capture.
const SWING := [[32.,0.,0.,-13.,0.],[38.,0.,0.,-19.,0.],[44.,7.,.7,-21.,0.],[52.,16.,1.,-19.,0.],[64.,18.,1.,-13.,1.],[78.,13.,.5,-2.,1.],[94.,8.,.15,9.,0.],[108.,4.,0.,18.,0.],[118.,1.5,0.,21.,0.],[128.,0.,0.,19.,0.],[134.,0.,0.,13.,0.]]
# Torso height over one step (phase within 64): low after contact, high in flight.
const BOB := [[0.,1.],[12.,2.],[26.,1.],[38.,0.],[50.,-2.],[58.,-1.],[64.,1.]]
const COLORS := {"A":Color8(0x0a,0x0a,0x0e),"H":Color8(0x41,0x30,0x2b),"J":Color8(0x71,0x47,0x30),"Q":Color8(0x20,0x1c,0x20),"F":Color8(0x30,0x25,0x26)}
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
func _home() -> Dictionary:
	return {"lift":0.,"reveal":0.,"depth":0.,"medial":0.,"ground":true,"phase":-1.}
func _ease(t: float) -> float:return smoothstep(0.,1.,clampf(t,0.,1.))
# Catmull-Rom through knots [[x, v1, v2, ...]]; periodic when `periodic`, otherwise the first and last
# knots are phantoms that only shape the end tangents.
func _curve(knots: Array,x: float,column: int,periodic: bool) -> float:
	var n := knots.size()-1
	var k := 0
	var p0: float
	var p3: float
	if periodic:
		var period: float=knots[n][0]-knots[0][0]
		x=fposmod(x-knots[0][0],period)+knots[0][0]
		while k<n-1 and x>knots[k+1][0]:k+=1
		p0=knots[(k-1+n)%n][column]
		p3=knots[(k+2)%n][column]
	else:
		k=1
		while k<n-2 and x>knots[k+1][0]:k+=1
		p0=knots[k-1][column]
		p3=knots[k+2][column]
	var t: float=clampf((x-knots[k][0])/(knots[k+1][0]-knots[k][0]),0.,1.)
	var p1: float=knots[k][column]
	var p2: float=knots[k+1][column]
	return .5*((2.*p1)+(-p0+p2)*t+(2.*p0-5.*p1+4.*p2-p3)*t*t+(-p0+3.*p1-3.*p2+p3)*t*t*t)
func gait_foot(phase: float) -> Dictionary:
	phase=fposmod(phase,CYCLE)
	if phase<STANCE:
		# World-ground stance: flat boot, depth falls 1 source row per phase (= rendered travel).
		return {"lift":0.,"reveal":0.,"depth":MID-phase,"medial":0.,"ground":true,"phase":phase}
	return {"lift":maxf(0.,_curve(SWING,phase,1,false)),"reveal":clampf(_curve(SWING,phase,2,false),0.,1.),"depth":_curve(SWING,phase,3,false),"medial":clampf(_curve(SWING,phase,4,false),0.,1.),"ground":false,"phase":phase}
func steady_body(phase_q: float) -> Vector2:
	# Weight shifts toward the stance foot (leg 0 midstance q19, leg 1 midstance q83).
	return Vector2(-cos((phase_q-MID)*TAU/CYCLE),_curve(BOB,fposmod(phase_q,64.),1,true))
func _copy_feet(value: Array) -> Array:return [value[0].duplicate(true),value[1].duplicate(true)]
func _mix(a: Dictionary,b: Dictionary,t: float) -> Dictionary:
	if t>=1.:return b.duplicate(true)
	var out := b.duplicate(true)
	for key in ["lift","reveal","depth","medial"]:out[key]=lerpf(a[key],b[key],t)
	out.ground=out.lift<=.01 and b.ground and t>=1.
	return out
func _begin_run(previous_render_y: float) -> void:
	if mode=="stop":
		# Re-press: a grounded foot keeps its world contact (stance phase chosen from its depth; the one
		# farther ahead has more stance left). With no grounded foot the lower one is placed in late swing,
		# far enough from touchdown that the start blend ends before it lands.
		var lead := -1
		for i in 2:
			if feet[i].ground and (lead<0 or feet[i].depth>feet[lead].depth):lead=i
		if lead>=0:
			q0=fposmod(MID-roundf(feet[lead].depth)-lead*64.,CYCLE)
		else:
			lead=1 if feet[1].lift<feet[0].lift else 0
			q0=fposmod(100.-lead*64.,CYCLE)
	else:
		q0=MID
	origin_y=previous_render_y
	start_feet=_copy_feet(feet)
	start_body=last_body
	start_live=live
	mode="run"
	age=0.
func advance(delta: float,world_y: float,intent: float) -> Dictionary:
	var previous_body_pixel := roundi(last_body.y)
	var previous_render_y := render_y
	var moved_north := world_y<physical_y-0.000001
	physical_y=world_y
	render_y=roundf(world_y*2.)*.5
	if intent>0. and moved_north:
		if mode!="run":_begin_run(previous_render_y)
		age+=delta
		var travelled := (origin_y-render_y)*2.
		q=fposmod(q0+roundf(travelled),CYCLE)
		for i in 2:
			var g:=gait_foot(q+i*64.)
			# A foot that was planted when the run began stays planted on its world point (no blend).
			if g.ground and start_feet[i].ground and start_feet[i].phase!=-2.:
				feet[i]=g
			else:
				feet[i]=_mix(start_feet[i],g,_ease(age/.08))
				# Once it has left the ground its start state no longer pins it.
				if not g.ground:start_feet[i].phase=-2.
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
				var begin := .0 if slot==0 else .06
				var sf: Dictionary=stop_feet[i]
				if sf.ground:
					if absf(sf.depth)<.5:
						feet[i]=_home()
					else:
						var t := _ease((stop_age-begin)/.10)
						if t<=0.:
							feet[i]=sf.duplicate(true)
						else:
							# Recovery step home: lifts clear of the ground, lands at the static sole.
							feet[i]=_mix(sf,_home(),t)
							if t<1.:feet[i].lift=(2.+.25*absf(sf.depth))*sin(PI*t)
				else:
					feet[i]=_mix(sf,_home(),_ease((stop_age-begin)/.09))
			var w := _ease(stop_age/.20)
			last_body=stop_body*(1.-w)
			live=stop_live*(1.-w)
			if stop_age>=.22:
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
# Nearest source row for destination row r in [d0,d1] mapped onto [s0,s1].
func _row(r: int,d0: int,d1: int,s0: int,s1: int) -> int:
	if d1<=d0:return s0
	return s0+clampi(floori((float(r-d0)+.5)*float(s1-s0+1)/float(d1-d0+1)),0,s1-s0)
func _put(image: Image,x: int,y: int,c: Color) -> void:
	if x>=0 and x<CELL.x and y>=0 and y<CELL.y and c.a8>0:image.set_pixel(x,y,c)
# Projected leg span factor: hip->heel screen span over the static span, for the stretchable rows only.
func span_factor(i: int,bottom: int,body_y: int) -> float:
	var span: float=float(bottom-(HIP_ROW+body_y))
	var rest: float=float(SOLE[i]-HIP_ROW)
	return clampf((span-RIGID_ROWS)/(rest-RIGID_ROWS),.5,1.6)
# One leg. Bottom-up: the static heel cap (sole-1, sole) always closes the boot (the named contact
# feature); above it the revealed sole rows; the static heel rows (sole-3, sole-2); the projected shaft;
# the rigid cuff. Trousers fill from under the coat to the cuff.
func _leg(i: int,foot: Dictionary,body: Vector2i,vent: Image) -> Dictionary:
	var trousers: Image=layers["legs"]
	var boots: Image=layers["boots"]
	var sole: int=SOLE[i]
	var reveal: float=foot.reveal
	var patch := roundi(5.*reveal)
	var bottom: int=sole-roundi(foot.depth)-roundi(foot.lift)
	var patch_top := bottom-1-patch
	var heel_top := patch_top-2
	var shaft_src := sole-HEEL_ROWS-CUFF_END
	var k := span_factor(i,bottom,body.y)
	var shaft := maxi(2,roundi(float(shaft_src)*k*(1.-.6*reveal)))
	var shaft_top := heel_top-shaft
	var cuff_top := shaft_top-(CUFF_END-BOOT_Y+1)
	var bx: int = -roundi(foot.medial)*OUTWARD[i]
	# The coat vent (inner thighs, torso-attached) stays in front of a boot that rises under the hem.
	var hem := 74+body.y
	var boot:=_blank()
	for y in range(maxi(0,cuff_top),mini(CELL.y,bottom+1)):
		if y>=patch_top and y<bottom-1:continue
		var s: int
		if y<shaft_top:s=BOOT_Y+(y-cuff_top)
		elif y<heel_top:s=_row(y,shaft_top,heel_top-1,CUFF_END+1,sole-HEEL_ROWS)
		elif y<patch_top:s=sole-3+(y-heel_top)
		else:s=sole-1+(y-(bottom-1))
		for x in CELL.x:
			if not _leg_cols(i,x):continue
			if y<=hem and x+bx>=0 and x+bx<CELL.x and vent.get_pixel(x+bx,y).a8>0:continue
			_put(boot,x+bx,y,boots.get_pixel(x,s))
	# Revealed sole between heel and the heel cap: heel face, then tread (static palette, outline A).
	var span := Vector2i(CELL.x,-1)
	for x in CELL.x:
		if _leg_cols(i,x) and boots.get_pixel(x,sole-2).a8>0:span=Vector2i(mini(span.x,x),maxi(span.y,x))
	for j in patch:
		var y := patch_top+j
		for x in range(span.x,span.y+1):
			var key := "A"
			if x>span.x and x<span.y:
				if j==0:key="J" if x<=span.x+2 else "H"
				else:key="F" if (x+j)%3==0 else "Q"
			_put(boot,x+bx,y,COLORS[key])
	# Trousers: source rows TROUSER_Y..TROUSER_END from just under the coat into the cuff, sliding laterally
	# from the torso offset at the hip to the boot offset at the cuff. Rows above TROUSER_Y repeat the first
	# trouser row under the coat so a lifting hem never shows a gap; the rest pose maps every row to itself.
	var leg:=_blank()
	var top := TROUSER_Y-3+body.y
	var hip := TROUSER_Y+body.y
	var end := cuff_top+TROUSER_END-BOOT_Y+1
	for y in range(maxi(0,top),mini(CELL.y,end)):
		var s := TROUSER_Y if y<hip else _row(y,hip,end-1,TROUSER_Y,TROUSER_END)
		var f := clampf(float(y-top)/maxf(1.,float(end-1-top)),0.,1.)
		var dx := roundi(lerpf(float(body.x),float(bx),f))
		for x in CELL.x:
			if not _leg_cols(i,x):continue
			_put(leg,x+dx,y,trousers.get_pixel(x,s))
	return {"trousers":leg,"boot":boot,"soleRow":bottom,"cuffTop":cuff_top,"spanFactor":k,"shaftRows":shaft}
# Coat skirt: the hem over a lifting knee rises up to 2 px on that side.
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
	var vent:=_stamp(_vent(),body.x,body.y)
	for i in 2:
		var data:=_leg(i,state.feet[i],body,vent)
		trousers.blend_rect(data.trousers,Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
		boots.blend_rect(data.boot,Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
		soles.append(data.soleRow)
		legs_info.append({"soleRow":data.soleRow,"cuffTop":data.cuffTop,"spanFactor":data.spanFactor,"shaftRows":data.shaftRows})
	trousers.blend_rect(vent,Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
	roles["legs"]=trousers
	roles["boots"]=boots
	var hem:=[clampi(roundi(state.feet[0].lift/4.),0,2),clampi(roundi(state.feet[1].lift/4.),0,2)]
	roles["coat"]=_coat(body,hem)
	var qq: float=state.q
	var pony := Vector2(2.*cos((qq-40.)*TAU/CYCLE),_curve(BOB,fposmod(qq-12.,64.),1,true)-_curve(BOB,fposmod(qq,64.),1,true))*amount
	var scarf := Vector2(1.5*cos((qq-44.)*TAU/CYCLE),-1.-maxf(0.,-_curve(BOB,fposmod(qq,64.),1,true)))*amount
	roles["scarf-tail"]=_follow(layers["scarf-tail"],body,60,78,scarf)
	var swing := cos(qq*TAU/CYCLE)*amount
	roles["arm-left"]=_arm("arm-left",0,body,amount,swing)
	roles["arm-right"]=_arm("arm-right",1,body,amount,-swing)
	for name in ["pack","canister","straps","bedroll","collar","hair"]:roles[name]=_stamp(layers[name],body.x,body.y)
	roles["ponytail"]=_follow(layers["ponytail"],body,13,32,pony)
	var full:=_blank()
	for name: String in layers:full.blend_rect(roles[name],Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
	return {"full":full,"roles":roles,"soleRows":soles,"legs":legs_info}
# Legs-layer texels above the trousers (inner thighs seen through the coat vent) move with the torso.
func _vent() -> Image:
	var image:=_blank()
	image.blit_rect(layers["legs"],Rect2i(0,0,CELL.x,TROUSER_Y),Vector2i.ZERO)
	return image
