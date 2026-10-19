extends SceneTree
var checks:Array=[]
func ck(k:String,v:bool)->void:checks.append({"key":k,"pass":v})
func _initialize()->void:call_deferred("run")
func run()->void:
 var args=OS.get_cmdline_user_args()
 var loader=load(args[0])
 var source=args[1]
 var out=args[2]
 var name:String=loader.MANIFEST_NAME
 var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(source.path_join(name)))
 DirAccess.make_dir_recursive_absolute(out)
 var fixtures=out.path_join("fixtures")
 DirAccess.make_dir_recursive_absolute(fixtures)
 for kind in base.events:
  for png in base.events[kind].frames:
   DirAccess.copy_absolute(source.path_join(png),fixtures.path_join(png))
 var tiny=Image.create(8,8,false,Image.FORMAT_RGBA8)
 tiny.fill(Color.RED)
 tiny.save_png(fixtures.path_join("rpg-2-star-ocean-the-second_common-vfx_wrong-size-fixture_v01_20261019-164412-1f3bff80.png"))
 var cases=["fps-dictionary","fps-string","fps-fractional","cell-string","pivot-invalid","events-array","framecount-dictionary","framecount-string","framecount-fractional","frame-list-type","frame-list-short","frame-type-invalid","missing-png","path-traversal","wrong-image-size","duration-type","native-duration-type","native-duration-total","kind-dictionary","valid"]
 if args.has("--one"):cases=["fps-dictionary"]
 for label in cases:
  var data=base.duplicate(true)
  var top=false
  match label:
   "fps-dictionary":data.fps={};top=true
   "fps-string":data.fps="12";top=true
   "fps-fractional":data.fps=12.5;top=true
   "cell-string":data.cell="64x64";top=true
   "pivot-invalid":data.pivot=[false,32];top=true
   "events-array":data.events=[];top=true
   "framecount-dictionary":data.events.attack.frameCount={}
   "framecount-string":data.events.attack.frameCount="8"
   "framecount-fractional":data.events.attack.frameCount=8.5
   "frame-list-type":data.events.attack.frames={}
   "frame-list-short":data.events.attack.frames.pop_back()
   "frame-type-invalid":data.events.attack.frames[7]=5
   "missing-png":data.events.attack.frames[7]="missing.png"
   "path-traversal":data.events.attack.frames[7]="../"+data.events.attack.frames[0]
   "wrong-image-size":data.events.attack.frames[7]="rpg-2-star-ocean-the-second_common-vfx_wrong-size-fixture_v01_20261019-164412-1f3bff80.png"
   "duration-type":data.events.attack.durationSeconds=[]
   "native-duration-type":data.events.attack.nativeFrameDurations[0]={}
   "native-duration-total":data.events.attack.nativeFrameDurations[0]=10.
   "kind-dictionary":data.events.attack=[]
  var file=FileAccess.open(fixtures.path_join(name),FileAccess.WRITE)
  file.store_string(JSON.stringify(data))
  file.close()
  var layer=loader.new(fixtures)
  for kind in base.events:
   var expected=8 if label=="valid" or (not top and kind!="attack") else 0
   ck(label+"-"+kind,layer._frames_by_kind[kind].size()==expected)
  ck(label+"-fallback-still-emits",layer.emit("attack",Vector2.ZERO))
 var missing=loader.new(out.path_join("absent"))
 ck("missing-all-fallback",missing._frames_by_kind.attack.is_empty() and missing.emit("attack",Vector2.ZERO))
 var bad=FileAccess.open(fixtures.path_join(name),FileAccess.WRITE)
 bad.store_string("{bad-json")
 bad.close()
 var malformed=loader.new(fixtures)
 ck("invalid-json-fallback",malformed._frames_by_kind.attack.is_empty() and malformed.emit("attack",Vector2.ZERO))
 var failed=checks.filter(func(c):return not c.pass)
 var report={"passed":checks.size()-failed.size(),"failed":failed.size(),"failures":failed,"checks":checks,"loaderSha256":FileAccess.get_sha256(args[0])}
 var file=FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_common-vfx_root-loader-report_v01_20261019-164412-1f3bff80.json"),FileAccess.WRITE)
 file.store_string(JSON.stringify(report," ")+"\n")
 file.close()
 print(JSON.stringify({"passed":report.passed,"failed":report.failed,"failures":failed}))
 print("COMMON_VFX_LOADER_ROOT_DONE")
 quit(1 if failed.size()>0 else 0)
