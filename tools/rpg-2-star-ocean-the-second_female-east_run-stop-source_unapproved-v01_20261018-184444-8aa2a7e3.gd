extends RefCounted
# One authored EAST lateral gait. Test/source only; not registered or adopted by the game.
# Kinematic timing reflects the produced WEST contract; every layer, anchor and
# asymmetry is read from the produced EAST static source (no WEST/SOUTH image flip).
const SOURCE := "res://../outputs/female-east-static-v01/rpg-2-star-ocean-the-second_protagonist-female_east-layered-source_unapproved-v01_20261018-175114-d55a2ba6.pxo"
const CELL := Vector2i(80,112)
const FLOOR := 104.0
const CONTACT := 38.0
const STRIDE := 128.0
const LEAN := 2.0
# EAST rest anchors (source pixels). Near = character right (i0), far = character left (i1).
const TOE := [Vector2(55,103),Vector2(47,103)]
const ANKLE := [Vector2(45,91),Vector2(37,91)]
const HIP := [Vector2(44,71),Vector2(37,70)]
const SHOULDER := Vector2(45,43)
const ELBOW := Vector2(46,56)
# Rest trouser contours in the dynamic vertex order:
# top-right, top-left, left-knee, left-ankle, right-ankle, right-knee.
const REST_OUTER := [
	[Vector2(48,70),Vector2(40,71),Vector2(38,82),Vector2(41,92),Vector2(49,91),Vector2(51,83)],
	[Vector2(41,69),Vector2(33,69),Vector2(32,85),Vector2(34,93),Vector2(41,91),Vector2(43,81)]]
const REST_INNER := [
	[Vector2(47,72),Vector2(42,74),Vector2(41,82),Vector2(42,90),Vector2(46,89),Vector2(48,82)],
	[Vector2(39,73),Vector2(35,73),Vector2(35,82),Vector2(35,90),Vector2(38,90),Vector2(40,82)]]
var layers := {}
var original: Image
var physical_x := 0.0
var render_x := 0.0
var origin_x := 0.0
var q0 := 13.0
var q := 13.0
var mode := "idle"
var age := 0.0
var stop_age := 0.0
var body_y := 0.0
var feet := []
var start_feet := []
var stop_feet := []
var last_body := Vector2.ZERO
var stop_body := Vector2.ZERO
var return_weight := 0.0
var bridge_air := -1
var start_body := Vector2.ZERO

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
	feet=[_home(0),_home(1)]
func _home(i: int) -> Dictionary:
	return {"x":ANKLE[i].x-40.,"sole":FLOOR,"angle":0.0,"ground":true,"phase":0.0}
func _ease(t: float) -> float:return smoothstep(0.,1.,clampf(t,0.,1.))
# Foot x is the ankle offset from pivot40; east stance carries the planted foot
# backward (-x) at exactly the body speed so its toe texels stay world-locked.
func gait_foot(phase: float) -> Dictionary:
	phase=fposmod(phase,128.)
	if phase<CONTACT:
		return {"x":18.-phase,"sole":FLOOR,"angle":0.28*_ease((phase-30.)/8.),"ground":true,"phase":phase}
	var p := Vector2.ZERO
	# Reflected WEST swing knots: toe-off behind, compact tuck, forward reach, contact.
	var keys := [[38.,Vector2(-20,103)],[52.,Vector2(-17,94)],[72.,Vector2(-6,85)],[94.,Vector2(7,88)],[112.,Vector2(15,98)],[128.,Vector2(18,104)]]
	for i in range(keys.size()-1):
		if phase<=keys[i+1][0]:
			p=keys[i][1].lerp(keys[i+1][1],_ease((phase-keys[i][0])/(keys[i+1][0]-keys[i][0])))
			break
	var angle := 0.65*sin(PI*(phase-CONTACT)/(128.-CONTACT))
	return {"x":p.x,"sole":minf(103.,p.y),"angle":angle,"ground":false,"phase":phase}
func steady_body(phase_q: float) -> Vector2:
	var step_phase := fposmod(phase_q,64.)
	var y := 2.*sin(PI*clampf(step_phase/CONTACT,0.,1.)) if step_phase<CONTACT else -2.*sin(PI*(step_phase-CONTACT)/(64.-CONTACT))
	return Vector2(LEAN,y)
func _copy_feet(value: Array) -> Array:return [value[0].duplicate(true),value[1].duplicate(true)]
func _begin_run(previous_render_x: float) -> void:
	# Raster contact chooses the handoff, not the analytical sole.
	for i in 2:
		var boot_image: Image=_boot(i,feet[i]).image
		feet[i].ground=false
		for x in 80:
			if boot_image.get_pixel(x,103).a8>0:feet[i].ground=true;break
	# Frontmost grounded foot (largest x when facing east) keeps the most stance.
	var support := 0
	if feet[1].ground and (not feet[0].ground or feet[1].x>feet[0].x):support=1
	bridge_air=-1
	if mode=="stop" and (not feet[0].ground or not feet[1].ground):
		bridge_air=0 if not feet[0].ground else 1
		if not feet[0].ground and not feet[1].ground and feet[1].sole>feet[0].sole:bridge_air=1
		q0=fposmod(114.-bridge_air*64.,128.)
	else:
		q0=fposmod(18.-float(feet[support].x)-support*64.,128.)
	origin_x=previous_render_x
	start_feet=_copy_feet(feet)
	start_body=last_body
	mode="run"
	age=0.
	return_weight=0.
func advance(delta: float,world_x: float,intent: float) -> Dictionary:
	var previous_render_x := render_x
	var moved_east := world_x>physical_x+0.000001
	physical_x=world_x
	render_x=roundf(world_x*2.)*.5
	if intent<0.:
		# WEST input shows the produced WEST static placeholder; no WEST motion is claimed here.
		mode="reverse-placeholder"
		feet=[_home(0),_home(1)]
		body_y=0.
		last_body=Vector2.ZERO
		return snapshot()
	if intent>0. and moved_east:
		if mode!="run":_begin_run(previous_render_x)
		age+=delta
		var travelled := (render_x-origin_x)*2.
		q=fposmod(q0+roundf(travelled),128.)
		for i in 2:
			var target := gait_foot(q+i*64.)
			if bridge_air>=0 and age<.12:
				var landing := .05 if i==bridge_air else .07
				if i==bridge_air:
					target.sole=lerpf(start_feet[i].sole,FLOOR,_ease(age/landing))
					target.x=lerpf(start_feet[i].x,target.x,_ease(age/landing))
					target.angle=lerpf(start_feet[i].angle,target.angle,_ease(age/landing))
					if age<landing:target.sole=minf(103.,target.sole)
				else:
					# Supporting foot stays pinned to the world while the airborne foot lands.
					var pin_x: float=start_feet[i].x-roundf(travelled)
					var release_t := _ease((age-landing)/.05)
					target.x=lerpf(pin_x,target.x,release_t)
					if age<=landing:
						target.sole=lerpf(start_feet[i].sole,FLOOR,_ease(age/landing))
						target.angle=lerpf(start_feet[i].angle,0.,_ease(age/landing))
						if not start_feet[i].ground and age<landing:target.sole=minf(103.,target.sole)
					else:
						target.sole=minf(103.,lerpf(FLOOR,target.sole,release_t))
						target.angle=lerpf(0.,target.angle,release_t)
				target.ground=target.sole>=FLOOR-.01
			elif bridge_air<0 and age<.07:
				target.sole=lerpf(FLOOR,target.sole,_ease(age/.07))
				if not target.ground:target.sole=minf(103.,target.sole)
				target.ground=target.sole>=FLOOR-.01
			feet[i]=target
		var steady := steady_body(q)
		body_y=steady.y
		last_body=start_body.lerp(steady,_ease(age/.10))
	else:
		if mode=="run":
			mode="stop"
			stop_age=0.
			stop_feet=_copy_feet(feet)
			stop_body=last_body
		if mode=="stop":
			stop_age+=delta
			for i in 2:
				var land_time := .03 if i==0 else .07
				var home_time := .065+i*.065
				var t := _ease((stop_age-home_time)/.065)
				feet[i]=stop_feet[i].duplicate(true)
				feet[i].sole=lerpf(stop_feet[i].sole,FLOOR,_ease(stop_age/land_time))
				feet[i].angle=lerpf(stop_feet[i].angle,0.,_ease(stop_age/land_time))
				feet[i].x=lerpf(stop_feet[i].x,_home(i).x,t)
				if t>0. and t<1.:feet[i].sole-=2.*sin(PI*t)
				feet[i].ground=feet[i].sole>=FLOOR-.01
			return_weight=_ease(stop_age/.22)
			last_body=stop_body*(1.-return_weight)
			if stop_age>=.22:
				mode="idle"
				feet=[_home(0),_home(1)]
				last_body=Vector2.ZERO
	return snapshot()
func snapshot() -> Dictionary:
	return {"mode":mode,"q":q,"age":age,"stopAge":stop_age,"feet":_copy_feet(feet),"body":last_body,"returnWeight":return_weight,"physicalX":physical_x,"renderX":render_x,"bridgeAir":bridge_air}
func _blank() -> Image:return Image.create(80,112,false,Image.FORMAT_RGBA8)
func _poly(image: Image,points: PackedVector2Array,color: Color) -> void:
	var lo:=Vector2(80,112)
	var hi:=Vector2.ZERO
	for p in points:lo=lo.min(p);hi=hi.max(p)
	for y in range(maxi(0,floori(lo.y)),mini(112,ceili(hi.y)+1)):
		for x in range(maxi(0,floori(lo.x)),mini(80,ceili(hi.x)+1)):
			if Geometry2D.is_point_in_polygon(Vector2(x+.5,y+.5),points):image.set_pixel(x,y,color)
func _segment(image: Image,a: Vector2,b: Vector2,width: float,color: Color) -> void:
	var n := (b-a).orthogonal().normalized()*width*.5
	_poly(image,PackedVector2Array([a+n,b+n,b-n,a-n]),color)
func _color(hex: String) -> Color:return Color.html(hex)
func _stamp(source: Image,dx: int,dy: int) -> Image:
	var image:=_blank()
	image.blit_rect(source,Rect2i(Vector2i.ZERO,CELL),Vector2i(dx,dy))
	return image
# Inverse-mapped nearest rotation: every destination texel samples one source
# texel, so rotated boots/forearms keep solid clusters instead of forward-map holes.
func _rotate_pixels(source: Image,center: Vector2,angle: float,target: Vector2,min_y: int,max_y: int) -> Image:
	var image:=_blank()
	var lo:=Vector2(80,112)
	var hi:=Vector2(-1,-1)
	for corner in [Vector2(0,min_y),Vector2(79,min_y),Vector2(0,max_y-1),Vector2(79,max_y-1)]:
		var p: Vector2=(corner-center).rotated(angle)+target
		lo=lo.min(p);hi=hi.max(p)
	for y in range(maxi(0,floori(lo.y)-1),mini(112,ceili(hi.y)+2)):
		for x in range(maxi(0,floori(lo.x)-1),mini(80,ceili(hi.x)+2)):
			var s: Vector2i=Vector2i(((Vector2(x,y)-target).rotated(-angle)+center).round())
			if s.x<0 or s.x>=80 or s.y<min_y or s.y>=max_y:continue
			var c:=source.get_pixelv(s)
			if c.a8>0:image.set_pixel(x,y,c)
	return image
func _boot(i: int,foot: Dictionary) -> Dictionary:
	var source: Image=layers["near-leg-boot" if i==0 else "far-leg-boot"]
	var toe: Vector2=TOE[i]
	var ankle: Vector2=ANKLE[i]
	var target:=Vector2(40.+foot.x-(ankle.x-toe.x),foot.sole-1.)
	var image:=_rotate_pixels(source,toe,foot.angle,target,88,104)
	return {"image":image,"ankle":(ankle-toe).rotated(foot.angle)+target,"contact":target}
func _pants(i: int,ankle: Vector2,body: Vector2,rest_weight: float) -> Image:
	var image:=_blank()
	var hip: Vector2=HIP[i]+body
	# Knee bends forward (+x) and slightly down from the hip-ankle line: compact, not an IK bow.
	var knee: Vector2=hip.lerp(ankle,.5)+Vector2(3.,2.)
	var n1: Vector2=(knee-hip).orthogonal().normalized()
	var n2: Vector2=(ankle-knee).orthogonal().normalized()
	var outer:=PackedVector2Array([hip+n1*4,hip-n1*4,knee-n2*4,ankle-n2*4,ankle+n2*4,knee+n1*4])
	var inside:=PackedVector2Array([hip+n1*2,hip-n1*2,knee-n2*2,ankle-n2*2,ankle+n2*2,knee+n1*2])
	for j in 6:
		outer[j]=outer[j].lerp(REST_OUTER[i][j],rest_weight)
		inside[j]=inside[j].lerp(REST_INNER[i][j],rest_weight)
	_poly(image,outer,_color("222839"))
	_poly(image,inside,_color("324542"))
	# Front crease light on the forward (+x) side of the thigh.
	_segment(image,hip.lerp(knee,.45)+n1*1.5,knee+n1*1.5,1.,_color("4a625c"))
	return image
func _trail(source: Image,body: Vector2,amount: float,from_y: int,to_y: int) -> Image:
	# Free ends trail behind (-x) progressively down the lock/tail; the root stays attached.
	var image:=_blank()
	for y in 112:
		var frac:=clampf(float(y-from_y)/float(to_y-from_y),0.,1.)
		var shift:=roundi(amount*frac)
		for x in 80:
			var c:=source.get_pixel(x,y)
			if c.a8==0:continue
			var point:=Vector2i(x+roundi(body.x)+shift,y+roundi(body.y))
			if point.x>=0 and point.x<80 and point.y>=0 and point.y<112 and image.get_pixelv(point).a8==0:image.set_pixelv(point,c)
	return image
func render_pose(state: Dictionary) -> Dictionary:
	if state.mode=="idle" or state.mode=="reverse-placeholder":
		return {"full":original.duplicate(),"roles":layers.duplicate(),"contacts":[TOE[0],TOE[1]]}
	var body: Vector2=state.body
	var weight: float=state.returnWeight if state.mode=="stop" else 0.
	var live:=1.-weight
	var roles: Dictionary={}
	var contacts:=[]
	for i in [1,0]:
		var boot:=_boot(i,state.feet[i])
		var leg:=_pants(i,boot.ankle,body,weight)
		leg.blend_rect(boot.image,Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
		roles["far-leg-boot" if i==1 else "near-leg-boot"]=leg
		contacts.push_front(boot.contact)
	for name: String in layers:
		if name.ends_with("leg-boot"):continue
		roles[name]=_stamp(layers[name],roundi(body.x),roundi(body.y))
	# Torso cadence drives a delayed follow-through of scarf tail and ponytail tips.
	var follow:=(-1.-sin((state.q-12.)*TAU/64.))*live
	roles["scarf-tail"]=_trail(layers["scarf-tail"],body,follow,50,72)
	roles["ponytail"]=_trail(layers["ponytail"],body,follow*.8,16,35)
	# Near (right) arm counter-swings the near leg: back at near contact (q0), forward at q64.
	var swing:=.42*cos(state.q*TAU/128.)*live
	var bend:=-.6*live
	var near: Image=layers["near-arm"]
	var shoulder: Vector2=SHOULDER+body
	var upper:=_rotate_pixels(near,SHOULDER,swing,shoulder,43,56)
	var elbow: Vector2=(ELBOW-SHOULDER).rotated(swing)+shoulder
	var fore:=_rotate_pixels(near,ELBOW,swing+bend,elbow,56,71)
	var arm:=_blank()
	arm.blit_rect(near,Rect2i(0,0,80,43),Vector2i(roundi(body.x),roundi(body.y)))
	arm.blend_rect(upper,Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
	arm.blend_rect(fore,Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
	roles["near-arm"]=arm
	var full:=_blank()
	for name: String in layers:full.blend_rect(roles[name],Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
	return {"full":full,"roles":roles,"contacts":contacts}
