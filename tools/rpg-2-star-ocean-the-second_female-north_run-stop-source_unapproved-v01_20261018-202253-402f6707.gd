extends RefCounted
# One authored NORTH (back-view) run/stop prototype. Test/source only; not registered or adopted by the game.
# Identity, palette, role layers and the final endpoint are the produced (unapproved) NORTH idle static
# pilot 9af15df7, read from its repo-local .pxo. No EAST/WEST/SOUTH image is flipped, mirrored or reused;
# only timing/state concepts follow the produced EAST v03 contract (distance-driven 128-phase clock, start
# blend, release-time settle, rendered torso step guard).
# Perspective contract: a back view has no screen-Y foot lock. Contact is pose state: a stance foot keeps
# its lateral columns and stays on the floor band (sole row = static sole -2..+2, ahead..behind in depth);
# the swing foot kicks back toward the camera (heel up, sole revealed, shaft foreshortened), passes under
# the body and reaches ahead. Every leg, boot, arm, coat, scarf and ponytail texel is a static source texel
# moved by an integer row/column remap (nearest, binary alpha); only the revealed sole rows under a lifted
# heel are drawn here, from the static palette.
const SOURCE := "res://assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-editable_unapproved-v01_20261018-090713-99e861ce.pxo"
const CELL := Vector2i(80,112)
const CYCLE := 128.0
const STANCE := 38.0
# Leg 0 = viewer left = character LEFT; leg 1 = viewer right = character RIGHT (knee strap, ponytail side).
const SOLE := [103,102]
const SPLIT_X := 41
const TROUSER_Y := 75
# Last trouser row: rows BOOT_Y..TROUSER_END hold trouser texels beside the boot cuff.
const TROUSER_END := 85
const BOOT_Y := 84
const CUFF_END := 88
const HEEL_ROWS := 4
const OUTWARD := [-1,1]
# Swing knots (foot phase, lift px, sole reveal 0..1, depth px ahead(+)/behind(-), medial px).
const SWING := [[38.,0.,.3,-2.,0.],[48.,6.,.75,-3.,0.],[62.,13.,1.,-3.,1.],[78.,10.,.6,-1.,1.],[94.,5.,.15,1.,0.],[112.,1.5,0.,2.5,0.],[128.,0.,0.,2.,0.]]
# Torso height over one step (phase within 64): low after contact, high in flight.
const BOB := [[0.,1.],[12.,2.],[26.,1.],[38.,0.],[50.,-2.],[58.,-1.],[64.,1.]]
const COLORS := {"A":Color8(0x0a,0x0a,0x0e),"H":Color8(0x41,0x30,0x2b),"J":Color8(0x71,0x47,0x30),"Q":Color8(0x20,0x1c,0x20),"F":Color8(0x30,0x25,0x26)}
var layers := {}
var original: Image
var physical_y := 0.0
var render_y := 0.0
var origin_y := 0.0
var q0 := 20.0
var q := 20.0
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
		layers[name]=Image.create_from_data(80,112,false,Image.FORMAT_RGBA8,zip.read_file("image_data/frames/1/layer_"+str(i+1)))
	zip.close()
	original=Image.create(80,112,false,Image.FORMAT_RGBA8)
	for image: Image in layers.values():original.blend_rect(image,Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
	feet=[_home(),_home()]
func _home() -> Dictionary:
	return {"lift":0.,"reveal":0.,"depth":0.,"medial":0.,"ground":true,"phase":-1.}
func _ease(t: float) -> float:return smoothstep(0.,1.,clampf(t,0.,1.))
# Periodic Catmull-Rom through knots [[phase, v1, v2, ...]] spanning one period.
func _curve(knots: Array,phase: float,column: int) -> float:
	var n := knots.size()-1
	var period: float=knots[n][0]-knots[0][0]
	phase=fposmod(phase-knots[0][0],period)+knots[0][0]
	var k := 0
	while k<n-1 and phase>knots[k+1][0]:k+=1
	var t: float=(phase-knots[k][0])/(knots[k+1][0]-knots[k][0])
	var p0: float=knots[(k-1+n)%n][column]
	var p1: float=knots[k][column]
	var p2: float=knots[k+1][column]
	var p3: float=knots[(k+2)%n][column]
	return .5*((2.*p1)+(-p0+p2)*t+(2.*p0-5.*p1+4.*p2-p3)*t*t+(-p0+3.*p1-3.*p2+p3)*t*t*t)
func gait_foot(phase: float) -> Dictionary:
	phase=fposmod(phase,CYCLE)
	if phase<STANCE:
		# Stance: lateral columns locked, depth drifts ahead->behind, heel peels off in late stance.
		var heel := _ease((phase-26.)/12.)
		return {"lift":0.,"reveal":.3*heel,"depth":lerpf(2.,-2.,phase/STANCE),"medial":0.,"ground":true,"phase":phase}
	return {"lift":maxf(0.,_curve(SWING,phase,1)),"reveal":clampf(_curve(SWING,phase,2),0.,1.),"depth":_curve(SWING,phase,3),"medial":clampf(_curve(SWING,phase,4),0.,1.),"ground":false,"phase":phase}
func steady_body(phase_q: float) -> Vector2:
	# Weight shifts toward the stance foot (leg 0 midstance q19, leg 1 midstance q83).
	return Vector2(-cos((phase_q-19.)*TAU/CYCLE),_curve(BOB,fposmod(phase_q,64.),1))
func _copy_feet(value: Array) -> Array:return [value[0].duplicate(true),value[1].duplicate(true)]
func _mix(a: Dictionary,b: Dictionary,t: float) -> Dictionary:
	var out := b.duplicate(true)
	for key in ["lift","reveal","depth","medial"]:out[key]=lerpf(a[key],b[key],t)
	out.ground=out.lift<=.01 and b.ground
	return out
func _begin_run(previous_render_y: float) -> void:
	if mode=="stop":
		# Re-press: the grounded foot that is farther ahead keeps an early stance; an airborne foot keeps swinging.
		var lead := 0
		if feet[1].ground and (not feet[0].ground or feet[1].depth>feet[0].depth):lead=1
		elif not feet[0].ground and not feet[1].ground and feet[1].lift<feet[0].lift:lead=1
		q0=6.+lead*64.
	else:
		q0=20.
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
			feet[i]=_mix(start_feet[i],gait_foot(q+i*64.),_ease(age/.08))
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
			# The lower airborne foot lands first; a grounded foot steps home after it.
			land_order=[0,1]
			if (not stop_feet[1].ground and stop_feet[0].ground) or (not stop_feet[0].ground and not stop_feet[1].ground and stop_feet[1].lift<stop_feet[0].lift):land_order=[1,0]
		if mode=="stop":
			stop_age+=delta
			for slot in 2:
				var i: int=land_order[slot]
				var begin := .0 if slot==0 else .06
				var t := _ease((stop_age-begin)/.09)
				var home := _home()
				feet[i]=_mix(stop_feet[i],home,t)
				if stop_feet[i].ground and absf(stop_feet[i].depth)>=1. and t>0. and t<1.:
					feet[i].lift=1.5*sin(PI*t)
					feet[i].ground=false
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
func _blank() -> Image:return Image.create(80,112,false,Image.FORMAT_RGBA8)
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
	if x>=0 and x<80 and y>=0 and y<112 and c.a8>0:image.set_pixel(x,y,c)
# One leg: trousers stretch between the coat (moves with the torso) and the boot cuff; the boot keeps its
# cuff and heel rows, foreshortens its shaft as the heel comes toward the camera, and shows its sole.
func _leg(i: int,foot: Dictionary,body: Vector2i) -> Dictionary:
	var trousers: Image=layers["legs"]
	var boots: Image=layers["boots"]
	var sole: int=SOLE[i]
	var reveal: float=foot.reveal
	var patch := roundi(5.*reveal)
	# Rows bottom-up: the static rounded heel underside (sole-1, sole) always closes the boot; above it the
	# revealed sole rows; then the static heel rows (sole-3, sole-2); the foreshortened shaft; the cuff.
	var bottom: int=sole-roundi(foot.depth)-roundi(foot.lift)
	var patch_top := bottom-1-patch
	var heel_top := patch_top-2
	var shaft_src := sole-HEEL_ROWS-CUFF_END
	var shaft := maxi(2,roundi(float(shaft_src)*(1.-.7*reveal)))
	var shaft_top := heel_top-shaft
	var cuff_top := shaft_top-(CUFF_END-BOOT_Y+1)
	var bx: int = -roundi(foot.medial)*OUTWARD[i]
	var boot:=_blank()
	for y in range(maxi(0,cuff_top),mini(112,bottom+1)):
		if y>=patch_top and y<bottom-1:continue
		var s: int
		if y<shaft_top:s=BOOT_Y+(y-cuff_top)
		elif y<heel_top:s=_row(y,shaft_top,heel_top-1,CUFF_END+1,sole-HEEL_ROWS)
		elif y<patch_top:s=sole-3+(y-heel_top)
		else:s=sole-1+(y-(bottom-1))
		for x in 80:
			if not _leg_cols(i,x):continue
			_put(boot,x+bx,y,boots.get_pixel(x,s))
	# Revealed sole between heel and the rounded underside: heel face, then tread (static palette, outline A).
	var span := Vector2i(80,-1)
	for x in 80:
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
	# from the torso offset at the hip to the boot offset at the cuff.
	# Rows above TROUSER_Y repeat the first trouser row under the coat so a lifting hem never shows a gap;
	# the rest pose maps every trouser row to itself.
	var leg:=_blank()
	var top := TROUSER_Y-3+body.y
	var hip := TROUSER_Y+body.y
	var end := cuff_top+TROUSER_END-BOOT_Y+1
	for y in range(maxi(0,top),mini(112,end)):
		var s := TROUSER_Y if y<hip else _row(y,hip,end-1,TROUSER_Y,TROUSER_END)
		var f := clampf(float(y-top)/maxf(1.,float(end-1-top)),0.,1.)
		var dx := roundi(lerpf(float(body.x),float(bx),f))
		for x in 80:
			if not _leg_cols(i,x):continue
			_put(leg,x+dx,y,trousers.get_pixel(x,s))
	return {"trousers":leg,"boot":boot,"soleRow":bottom,"cuffTop":cuff_top}
# Coat skirt: the hem over a lifting knee rises up to 2 px on that side.
func _coat(body: Vector2i,hem: Array) -> Image:
	var source: Image=layers["coat"]
	var image:=_blank()
	for y in 112:
		for x in 80:
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
	for y in 112:
		for x in 80:
			var f := clampf(float(y-body.y-root)/float(tip-root),0.,1.)
			var s := Vector2i(x-body.x-roundi(tip_shift.x*f),y-body.y-roundi(tip_shift.y*f))
			if s.x<0 or s.x>=80 or s.y<0 or s.y>=112:continue
			var c := source.get_pixelv(s)
			if c.a8>0:image.set_pixel(x,y,c)
	return image
# Arm: run carriage raises the elbow (cuff) and shortens the forearm; swung back (toward the camera) the
# elbow goes out and the gloved hand shows at the hip; swung forward the hand passes in front of the body.
func _arm(name: String,side: int,body: Vector2i,carry: float,swing: float) -> Image:
	var source: Image=layers[name]
	var image:=_blank()
	var top := 0
	while top<112 and not _row_has(source,top):top+=1
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
		for x in 80:_put(image,x+dx+body.x,y+body.y,source.get_pixel(x,s))
	for y in range(d_cuff,d_cuff+4):
		for x in 80:_put(image,x+elbow_dx+body.x,y+body.y,source.get_pixel(x,51+y-d_cuff))
	var f0 := d_cuff+4
	for y in range(f0,f0+fore_dst):
		var s := _row(y,f0,f0+fore_dst-1,55,55+fore_src-1)
		for x in 80:_put(image,x+elbow_dx+body.x,y+body.y,source.get_pixel(x,s))
	if hidden>0:
		# Close the cut forearm with the static 1-texel outline colour.
		var y := f0+fore_dst+body.y
		if y>0 and y<112:
			for x in 80:
				if image.get_pixel(x,y-1).a8>0:image.set_pixel(x,y,COLORS.A)
	return image
func _row_has(image: Image,y: int) -> bool:
	for x in 80:
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
	for i in 2:
		var data:=_leg(i,state.feet[i],body)
		trousers.blend_rect(data.trousers,Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
		boots.blend_rect(data.boot,Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
		soles.append(data.soleRow)
	trousers.blend_rect(_stamp(_vent(),body.x,body.y),Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
	roles["legs"]=trousers
	roles["boots"]=boots
	var hem:=[clampi(roundi(state.feet[0].lift/4.),0,2),clampi(roundi(state.feet[1].lift/4.),0,2)]
	roles["coat"]=_coat(body,hem)
	var qq: float=state.q
	var pony := Vector2(2.*cos((qq-40.)*TAU/CYCLE),_curve(BOB,fposmod(qq-12.,64.),1)-_curve(BOB,fposmod(qq,64.),1))*amount
	var scarf := Vector2(1.5*cos((qq-44.)*TAU/CYCLE),-1.-maxf(0.,-_curve(BOB,fposmod(qq,64.),1)))*amount
	roles["scarf-tail"]=_follow(layers["scarf-tail"],body,60,78,scarf)
	var swing := cos(qq*TAU/CYCLE)*amount
	roles["arm-left"]=_arm("arm-left",0,body,amount,swing)
	roles["arm-right"]=_arm("arm-right",1,body,amount,-swing)
	for name in ["pack","canister","straps","bedroll","collar","hair"]:roles[name]=_stamp(layers[name],body.x,body.y)
	roles["ponytail"]=_follow(layers["ponytail"],body,13,32,pony)
	var full:=_blank()
	for name: String in layers:full.blend_rect(roles[name],Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
	return {"full":full,"roles":roles,"soleRows":soles}
# Legs-layer texels above the trousers (inner thighs seen through the coat vent) move with the torso.
func _vent() -> Image:
	var image:=_blank()
	image.blit_rect(layers["legs"],Rect2i(0,0,80,TROUSER_Y),Vector2i.ZERO)
	return image
