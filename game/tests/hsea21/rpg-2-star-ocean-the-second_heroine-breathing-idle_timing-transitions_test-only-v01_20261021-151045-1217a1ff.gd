extends SceneTree
const PLAYBACK = preload("res://scripts/hsea21/rpg-2-star-ocean-the-second_heroine-breathing-idle_playback-runtime_v01_20261021-151045-1217a1ff.gd")
var failed := 0
var checked := 0
func ck(ok: bool, label: String) -> void:
	checked += 1
	if not ok:
		failed += 1
		print("BREATH21 FAIL ", label)
func make_clock(direction: String = "south"):
	var clock = PLAYBACK.new()
	for face in ["south", "north", "east", "west"]:
		clock.clips[face] = {"cycle_us":2400000,"ends_us":[400000,620000,800000,1120000,1380000,1600000,1900000,2400000]}
	clock.reset(direction)
	return clock
func _initialize() -> void:
	for face in ["south", "north", "east", "west"]:
		for fps in [30,60]:
			var clock = make_clock(face)
			for tick in range(1,fps*6+1):
				var index: int = clock.step(1.0/float(fps),"idle",face)
				if tick == int(fps*0.4): ck(index==1,"400ms boundary fps"+str(fps)+face)
				if tick == fps: ck(index==3,"1s expected inhale sample fps"+str(fps)+face)
				if tick == int(fps*2.4): ck(index==0,"2400ms exact wrap fps"+str(fps)+face)
			ck(clock.step(0.0,"walk",face)==0 and clock.elapsed_us==0.0,"movement interrupts immediately "+face)
			ck(clock.step(0.08,"settle",face)==0,"settle does not breathe "+face)
			ck(clock.step(0.04,"idle",face)==0 and clock.elapsed_us==0.0,"settle completes at neutral "+face)
			ck(clock.step(0.4,"idle",face)==1,"fresh breath begins after rest "+face)
			ck(clock.step(0.0,"walk",face)==0,"zero-time repress cannot hold raised idle "+face)
	var mixed = make_clock()
	for delta in [0.07,0.03,0.16,0.14]:mixed.step(delta,"idle","south")
	ck(mixed.sample_index==1,"mixed-delta 400ms boundary")
	mixed.step(0.22,"idle","south")
	ck(mixed.sample_index==2,"620ms exclusive boundary")
	mixed.step(0.18,"idle","south")
	ck(mixed.sample_index==3,"800ms exclusive boundary")
	mixed.step(1.6,"idle","south")
	ck(mixed.sample_index==0 and is_zero_approx(mixed.elapsed_us),"mixed-delta exact full wrap")
	mixed.step(1.0,"idle","south")
	var before: float = mixed.elapsed_us
	for bad in [NAN,INF,-0.1]:ck(mixed.step(bad,"idle","south")==-1 and mixed.elapsed_us==before,"invalid delta preserves state")
	ck(mixed.step(0.1,"unknown","south")==-1 and mixed.elapsed_us==before,"unknown action preserves state")
	ck(mixed.step(0.1,"idle","up")==-1 and mixed.elapsed_us==before,"unknown direction preserves state")
	ck(mixed.step(0.1,"idle","north")==0 and mixed.elapsed_us==0.0,"facing change restarts neutral")
	mixed.step(1.0,"idle","north")
	ck(mixed.step(0.1,"idle","north",true)==0 and mixed.elapsed_us==0.0,"teleport/completion reset neutral")
	ck(mixed.step(1e308,"idle","north")>=0 and is_finite(mixed.elapsed_us),"finite huge delta bounded")
	var other=make_clock()
	ck(other.elapsed_us==0.0 and other.sample_index==0,"per-actor clock isolation")
	print("BREATH21_TIMING_PASS " if failed==0 else "BREATH21_TIMING_FAILED ",checked," checks; failures ",failed)
	quit(0 if failed==0 else 1)
