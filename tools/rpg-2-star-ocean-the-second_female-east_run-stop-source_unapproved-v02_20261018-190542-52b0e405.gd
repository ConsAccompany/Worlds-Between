extends RefCounted
# One authored EAST lateral gait. Test/source only; not registered or adopted by the game.
# Kinematic timing reflects the produced WEST contract; every layer, anchor and
# asymmetry is read from the produced EAST static source (no WEST/SOUTH image flip).
# v02 (bounded correction of v01 8aa2a7e3): trousers are the static trouser texels
# re-sampled through a pelvis/thigh/shin/boot joint chain (inverse-mapped, nearest),
# so outline, fill and crease stay the authored material and the rest chain is the
# identity map; a re-press bridge cannot lift the body before the landing foot lands.
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
# Rest knees: midpoint of the straight static hip-ankle line (static knee widening rows 80-83).
const KNEE := [Vector2(44.5,81),Vector2(37,80.5)]
# Static leg layers: trouser texels are rows < HEM; rows >= HEM belong to the boot.
const HEM := 88
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
var bridge_landed := false
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
	bridge_landed=false
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
		# The bridge resumes in late flight (q114) only so the airborne foot can land;
		# until it has landed the body may not rise above where it was (or standing height).
		if bridge_air>=0 and not bridge_landed:
			if feet[bridge_air].ground:bridge_landed=true
			else:last_body.y=maxf(last_body.y,minf(start_body.y,0.))
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
# Two-bone knee with the static thigh/shin lengths, bending forward (+x). A straight
# rest leg returns the rest knee, so the rest chain maps every trouser texel to itself.
func knee_for(i: int,hip: Vector2,ankle: Vector2) -> Vector2:
	var l1: float=HIP[i].distance_to(KNEE[i])
	var l2: float=KNEE[i].distance_to(ANKLE[i])
	var d:=ankle-hip
	var dist:=d.length()
	if dist>=l1+l2-.0001:return hip+d*(l1/(l1+l2))
	var dir:=d/dist
	var along:=(l1*l1-l2*l2+dist*dist)/(2.*dist)
	return hip+dir*along+dir.orthogonal()*sqrt(maxf(0.,l1*l1-along*along))
# Posed bone a0->a1 back to rest bone b0->b1: length is scaled, cloth width is kept.
func _bone(p: Vector2,a0: Vector2,a1: Vector2,b0: Vector2,b1: Vector2) -> Vector2:
	var e:=a1-a0
	var f:=b1-b0
	return b0+f*((p-a0).dot(e)/e.length_squared())+f.normalized().orthogonal()*(p-a0).dot(e.normalized().orthogonal())
func _band(p: Vector2,joint: Vector2,u: Vector2,v: Vector2,half: float) -> float:
	return smoothstep(-half,half,(p-joint).dot((u+v).normalized()))
# Static trouser texels re-sampled through pelvis -> thigh -> shin -> boot. Each
# destination texel takes exactly one source texel (binary alpha, static palette).
func _trousers(i: int,foot: Dictionary,boot: Dictionary,body: Vector2i) -> Image:
	var image:=_blank()
	var source: Image=layers["near-leg-boot" if i==0 else "far-leg-boot"]
	var hip: Vector2=HIP[i]+Vector2(body)
	var ankle: Vector2=boot.ankle
	var knee:=knee_for(i,hip,ankle)
	var toe: Vector2=TOE[i]
	var target: Vector2=boot.contact
	var angle: float=foot.angle
	var down:=Vector2(0,1)
	var thigh:=(knee-hip).normalized()
	var shin:=(ankle-knee).normalized()
	var boot_down:=down.rotated(angle)
	var hem_joint:=(Vector2(ANKLE[i].x,HEM-.5)-toe).rotated(angle)+target
	var lo:=hip.min(knee).min(ankle)-Vector2(14,14)
	var hi:=hip.max(knee).max(ankle)+Vector2(14,6)
	var taken:={}
	for y in range(maxi(0,floori(lo.y)),mini(112,ceili(hi.y)+1)):
		for x in range(maxi(0,floori(lo.x)),mini(80,ceili(hi.x)+1)):
			var p:=Vector2(x,y)
			var s:=p-Vector2(body)
			s=s.lerp(_bone(p,hip,knee,HIP[i],KNEE[i]),_band(p,hip,down,thigh,2.))
			s=s.lerp(_bone(p,knee,ankle,KNEE[i],ANKLE[i]),_band(p,knee,thigh,shin,2.5))
			s=s.lerp((p-target).rotated(-angle)+toe,_band(p,hem_joint,shin,boot_down,1.5))
			var t:=Vector2i(s.round())
			if t.x<0 or t.x>=80 or t.y<0 or t.y>=HEM:continue
			var c:=source.get_pixelv(t)
			if c.a8>0:image.set_pixel(x,y,c);taken[Vector2i(x,y)]=t
	# Rotation spurs: drop a texel only if the warp left it with at most one 4-neighbour
	# and fewer than its source texel had. The rest chain removes nothing.
	var spurs:=[]
	for d: Vector2i in taken:
		var have:=_neighbours(image,d,112)
		if have<=1 and have<_neighbours(source,taken[d],HEM):spurs.append(d)
	for d: Vector2i in spurs:image.set_pixelv(d,Color(0,0,0,0))
	return image
func _neighbours(image: Image,p: Vector2i,max_y: int) -> int:
	var n:=0
	for o in [Vector2i(1,0),Vector2i(-1,0),Vector2i(0,1),Vector2i(0,-1)]:
		var q: Vector2i=p+o
		if q.x>=0 and q.x<80 and q.y>=0 and q.y<mini(112,max_y) and image.get_pixelv(q).a8>0:n+=1
	return n
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
		var leg:=_trousers(i,state.feet[i],boot,Vector2i(roundi(body.x),roundi(body.y)))
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
