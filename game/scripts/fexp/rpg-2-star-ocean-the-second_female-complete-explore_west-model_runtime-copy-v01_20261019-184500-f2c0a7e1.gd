extends RefCounted
# One authored lateral gait. Test/source only; not registered or adopted by the game.
const SOURCE := "res://assets/fexp/rpg-2-star-ocean-the-second_protagonist-female_west-layered-source_unapproved-v01_20261018-174421-618816ac.pxo"
const CELL := Vector2i(80,112)
const FLOOR := 104.0
const CONTACT := 38.0
const STRIDE := 128.0
const COLORS := {"ink":"222839","cloth":"324542","light":"4a625c","edge":"0a0a0e"}
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
var observed := {}
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
	return {"x":-5.0 if i==0 else 2.0,"sole":FLOOR,"angle":0.0,"ground":true,"phase":0.0}
func _ease(t: float) -> float:return smoothstep(0.,1.,clampf(t,0.,1.))
func gait_foot(phase: float) -> Dictionary:
	phase=fposmod(phase,128.)
	if phase<CONTACT:
		return {"x":phase-18.,"sole":FLOOR,"angle":-0.28*_ease((phase-30.)/8.),"ground":true,"phase":phase}
	var p := Vector2.ZERO
	# Named authored knots, interpolated jointly rather than stretching a straight reach.
	var keys := [[38.,Vector2(20,103)],[52.,Vector2(17,94)],[72.,Vector2(6,85)],[94.,Vector2(-7,88)],[112.,Vector2(-15,98)],[128.,Vector2(-18,104)]]
	for i in range(keys.size()-1):
		if phase<=keys[i+1][0]:
			p=keys[i][1].lerp(keys[i+1][1],_ease((phase-keys[i][0])/(keys[i+1][0]-keys[i][0])))
			break
	var angle := -0.65*sin(PI*(phase-CONTACT)/(128.-CONTACT))
	return {"x":p.x,"sole":minf(103.,p.y),"angle":angle,"ground":false,"phase":phase}
func _copy_feet(value: Array) -> Array:return [value[0].duplicate(true),value[1].duplicate(true)]
func _begin_run(previous_render_x: float) -> void:
	# Raster contact determines the handoff: a subpixel shuffle can still
	# visibly touch the floor even when its analytical sole is just above it.
	for i in 2:
		var boot_image: Image=_boot(i,feet[i]).image
		feet[i].ground=false
		for x in 80:
			if boot_image.get_pixel(x,103).a8>0:feet[i].ground=true;break
	var support := 0
	if feet[1].ground and (not feet[0].ground or feet[1].x<feet[0].x):support=1
	bridge_air=-1
	if mode=="stop" and (not feet[0].ground or not feet[1].ground):
		# Resume through a short landing, rather than dropping a boot and
		# immediately lifting both again on an unrelated phase.
		bridge_air=0 if not feet[0].ground else 1
		if not feet[0].ground and not feet[1].ground and feet[1].sole>feet[0].sole:bridge_air=1
		q0=fposmod(114.-bridge_air*64.,128.)
	else:
		q0=fposmod(float(feet[support].x)+18.-support*64.,128.)
	origin_x=previous_render_x
	start_feet=_copy_feet(feet)
	start_body=last_body
	mode="run"
	age=0.
	return_weight=0.
func advance(delta: float,world_x: float,intent: float) -> Dictionary:
	var previous_render_x := render_x
	var moved_west := world_x<physical_x-0.000001
	physical_x=world_x
	render_x=roundf(world_x*2.)*.5
	if intent>0.:
		mode="reverse-placeholder"
		feet=[_home(0),_home(1)]
		body_y=0.
		last_body=Vector2.ZERO
		return snapshot()
	if intent<0. and moved_west:
		if mode!="run":_begin_run(previous_render_x)
		age+=delta
		q=fposmod(q0+roundf((origin_x-render_x)*2.),128.)
		for i in 2:
			var target := gait_foot(q+i*64.)
			if bridge_air>=0 and age<.12:
				var landing := .05 if i==bridge_air else .07
				if i==bridge_air:
					# Chosen boot joins its natural contact at q128, not mid-flight.
					target.sole=lerpf(start_feet[i].sole,FLOOR,_ease(age/landing))
					target.x=lerpf(start_feet[i].x,target.x,_ease(age/landing))
					target.angle=lerpf(start_feet[i].angle,target.angle,_ease(age/landing))
					if age<landing:target.sole=minf(103.,target.sole)
				else:
					var pin_x: float=start_feet[i].x+(origin_x-render_x)*2.
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
		var step_phase := fposmod(q,64.)
		var desired := 2.*sin(PI*clampf(step_phase/CONTACT,0.,1.)) if step_phase<CONTACT else -2.*sin(PI*(step_phase-CONTACT)/(64.-CONTACT))
		body_y=desired
		last_body=start_body.lerp(Vector2(-2.,body_y),_ease(age/.10))
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
func _rotate_pixels(source: Image,center: Vector2,angle: float,target: Vector2,min_y: int,max_y: int) -> Image:
	var image:=_blank()
	for y in range(min_y,max_y):
		for x in 80:
			var c:=source.get_pixel(x,y)
			if c.a8==0:continue
			var p: Vector2i=Vector2i(((Vector2(x,y)-center).rotated(angle)+target).round())
			if p.x>=0 and p.x<80 and p.y>=0 and p.y<112:image.set_pixelv(p,c)
	return image
func _boot(i: int,foot: Dictionary) -> Dictionary:
	var source: Image=layers["near-leg-boot" if i==0 else "far-leg-boot"]
	var toe:=Vector2(25,103) if i==0 else Vector2(33,103)
	var ankle:=Vector2(35,91) if i==0 else Vector2(42,91)
	var target:=Vector2(40.+foot.x-(ankle.x-toe.x),foot.sole-1.)
	var image:=_rotate_pixels(source,toe,foot.angle,target,88,104)
	return {"image":image,"ankle":(ankle-toe).rotated(foot.angle)+target,"contact":target}
func _pants(i: int,ankle: Vector2,body: Vector2,rest_weight: float) -> Image:
	var image:=_blank()
	var hip:=Vector2(36,70) if i==0 else Vector2(42,70)
	hip+=body
	# Authored lateral knee contour, rather than a symmetric IK bow that made the
	# contact thigh nearly horizontal. The shallow forward/down offset retains
	# a descending thigh and shin while the ankle follows its real contact pin.
	var knee: Vector2=hip.lerp(ankle,.5)+Vector2(-3.,2.)
	var n1: Vector2=(knee-hip).orthogonal().normalized()
	var n2: Vector2=(ankle-knee).orthogonal().normalized()
	var outer:=PackedVector2Array([hip+n1*4,hip-n1*4,knee-n2*4,ankle-n2*4,ankle+n2*4,knee+n1*4])
	var inside:=PackedVector2Array([hip+n1*2,hip-n1*2,knee-n2*2,ankle-n2*2,ankle+n2*2,knee+n1*2])
	var rest_outer:=PackedVector2Array([Vector2(32,70),Vector2(41,72),Vector2(42,80),Vector2(39,91),Vector2(31,92),Vector2(29,84)]) if i==0 else PackedVector2Array([Vector2(39,68),Vector2(47,70),Vector2(47,89),Vector2(45,94),Vector2(38,93),Vector2(36,81)])
	var rest_inner:=PackedVector2Array([Vector2(33,72),Vector2(39,74),Vector2(39,80),Vector2(36,89),Vector2(32,90),Vector2(31,84)]) if i==0 else PackedVector2Array([Vector2(41,73),Vector2(45,73),Vector2(45,88),Vector2(42,92),Vector2(39,90),Vector2(39,80)])
	for j in 6:outer[j]=outer[j].lerp(rest_outer[j],rest_weight);inside[j]=inside[j].lerp(rest_inner[j],rest_weight)
	_poly(image,outer,_color("222839"))
	_poly(image,inside,_color("324542"))
	_segment(image,hip.lerp(knee,.5),knee,1.,_color("4a625c"))
	return image
func render_pose(state: Dictionary) -> Dictionary:
	if state.mode=="idle":return {"full":original.duplicate(),"roles":layers.duplicate(),"contacts":[Vector2(25,103),Vector2(33,103)]}
	var body: Vector2=state.body
	var weight: float=state.returnWeight if state.mode=="stop" else 0.
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
	# The scarf/coat/pony free ends lag the torso with a restrained source-pixel delay.
	var lag:=roundi(sin((state.q-12.)*TAU/128.)*(1.-weight))
	for name in ["scarf-tail","ponytail"]:
		var source: Image=layers[name]
		var image:=_blank()
		for y in 112:
			for x in 80:
				var c:=source.get_pixel(x,y)
				if c.a8==0:continue
				var shift:=lag if (y>25 if name=="ponytail" else y>60) else 0
				var point:=Vector2i(x+roundi(body.x)+shift,y+roundi(body.y))
				if point.x>=0 and point.x<80 and point.y>=0 and point.y<112:image.set_pixelv(point,c)
		roles[name]=image
	var near: Image=layers["near-arm"]
	var upper:=_rotate_pixels(near,Vector2(34,43),-.45*cos(state.q*TAU/128.)*(1.-weight),Vector2(34,43)+body,43,58)
	var elbow: Vector2=(Vector2(32,57)-Vector2(34,43)).rotated(-.45*cos(state.q*TAU/128.)*(1.-weight))+Vector2(34,43)+body
	var fore:=_rotate_pixels(near,Vector2(32,57),(-.55-.45*cos(state.q*TAU/128.))*(1.-weight),elbow,58,71)
	var neck:=_blank()
	neck.blit_rect(near,Rect2i(0,0,80,43),Vector2i(roundi(body.x),roundi(body.y)))
	neck.blend_rect(upper,Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
	neck.blend_rect(fore,Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
	roles["near-arm"]=neck
	var full:=_blank()
	for name: String in layers:full.blend_rect(roles[name],Rect2i(Vector2i.ZERO,CELL),Vector2i.ZERO)
	return {"full":full,"roles":roles,"contacts":contacts}
