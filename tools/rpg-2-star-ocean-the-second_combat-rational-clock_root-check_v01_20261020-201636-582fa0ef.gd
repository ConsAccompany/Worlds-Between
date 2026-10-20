extends SceneTree
const Loader = preload("res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd")
const FIXTURE = "res://tests/fixtures/csp-half-scale-v01_7d4bddce/rpg-2-star-ocean-the-second_combat-half-scale_fixture_not-art-v01_20261020-154048-7d4bddce.json"
var checks := 0
var serial := 0
func ck(ok: bool, why: String) -> void:
 checks += 1
 assert(ok, why)
func _initialize() -> void:
 call_deferred("run")
func manifest() -> Dictionary:
 var m: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(FIXTURE))
 m["sheet"] = FIXTURE.get_base_dir().path_join(String(m["sheet"])) if not String(m["sheet"]).contains("://") else m["sheet"]
 for action in m["actions"]:
  m["actions"][action] = {"loop": action in ["idle","move","guard"], "tick_rate":30,"frames":[{"cell":0,"ticks":2},{"cell":1,"ticks":2},{"cell":0,"ticks":1},{"cell":1,"ticks":2}]}
 return m
func loadm(m: Dictionary) -> Dictionary:
 serial += 1
 var path := "user://rpg-2-star-ocean-the-second_rational-clock_fixture-v01_20261020-201636-582fa0ef-%03d.json" % serial
 var f := FileAccess.open(path,FileAccess.WRITE)
 f.store_string(JSON.stringify(m)); f.close()
 Loader.clear_cache()
 return Loader.load_set(path,"hero:female")
func run() -> void:
 var m := manifest()
 var loaded := loadm(m)
 ck(loaded["status"] == "loaded", "rational set loads")
 var attack: Dictionary = loaded["actions"]["attack"]
 ck(absf(attack["duration"] - 7.0/30.0) < 1e-12, "ticks duration is rational, not rounded ms")
 for sample in [[0.0,0],[2.0/30.0-0.00001,0],[2.0/30.0,1],[4.0/30.0,2],[5.0/30.0-0.00001,2],[5.0/30.0,3],[7.0/30.0,3],[5.0,3]]:
  ck(Loader.frame_at(attack,sample[0]) == sample[1], "exact boundary " + str(sample))
 for fps in [30,60]:
  var t := 0.0
  for step in range(fps*2):
   var expected := 0 if t < 2.0/30.0-0.000001 else (1 if t < 4.0/30.0-0.000001 else (2 if t < 5.0/30.0-0.000001 else 3))
   ck(Loader.frame_at(attack,t)==expected,"shared-time " + str(fps) + " " + str(step))
   t += 1.0/fps
 m = manifest(); m["actions"]["guard"]={"loop":true,"tick_rate":30,"loop_start":1,"frames":[{"cell":0,"ticks":2},{"cell":1,"ticks":6},{"cell":0,"ticks":6}]}
 var guard: Dictionary = loadm(m)["actions"]["guard"]
 for sample in [[0.,0],[2./30.,1],[8./30.,2],[14./30.,1],[20./30.,2],[26./30.,1],[122./30.,1]]:
  ck(Loader.frame_at(guard,sample[0])==sample[1],"guard intro once " + str(sample))
 for rate in [0,-1,1001,30.5,true,"30",null]:
  m=manifest();m["actions"]["attack"]["tick_rate"]=rate
  ck(loadm(m)["status"]!="loaded","bad rate " + str(rate))
 for value in [0,-1,1.5,true,"2",null]:
  m=manifest();m["actions"]["attack"]["frames"][0]["ticks"]=value
  ck(loadm(m)["status"]!="loaded","bad tick " + str(value))
 m=manifest();m["actions"]["attack"]["frames"][0]["ms"]=67
 ck(loadm(m)["status"]!="loaded","both time units rejected")
 m=manifest();m["actions"]["attack"]["frames"][0].erase("ticks");m["actions"]["attack"]["frames"][0]["ms"]=67
 ck(loadm(m)["status"]!="loaded","mixed time units rejected")
 m=manifest();m["actions"]["attack"].erase("tick_rate")
 ck(loadm(m)["status"]!="loaded","ticks without rate rejected")
 for value in [-1,4,1.5,true,"1",null]:
  m=manifest();m["actions"]["guard"]["loop_start"]=value
  ck(loadm(m)["status"]!="loaded","bad loop start " + str(value))
 m=manifest();m["actions"]["attack"]["loop_start"]=0
 ck(loadm(m)["status"]!="loaded","nonloop intro rejected")
 print("ROOT_RATIONAL_CLOCK_PASS checks=", checks)
 quit(0)
