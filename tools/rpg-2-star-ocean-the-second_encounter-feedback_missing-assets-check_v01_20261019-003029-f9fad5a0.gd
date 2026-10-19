extends SceneTree
var checks=[]
func ck(k: String,v: bool) -> void:checks.append({"key":k,"pass":v})
func _initialize() -> void:call_deferred("run")
func textures(m: RefCounted) -> int:
 var count=0
 for a in m._frames_by_kind.values():count+=a.size()
 return count
func run() -> void:
 var args=OS.get_cmdline_user_args()
 var cls=load(args[0])
 var base="user://encounter-feedback-missing-fixtures"
 var cases={"malformed":"{not-json","array":"[]","wrong-events":JSON.stringify({"events":[]}),"short-frames":JSON.stringify({"events":{"encounter":{"frames":["missing.png"]}}}),"missing-eight":JSON.stringify({"events":{"encounter":{"frames":["missing.png","missing.png","missing.png","missing.png","missing.png","missing.png","missing.png","missing.png"]}}}),"invalid-frame-types":JSON.stringify({"events":{"encounter":{"frames":[7,7,7,7,7,7,7,7]}}})}
 for key in cases:
  var folder=base.path_join(key)
  DirAccess.make_dir_recursive_absolute(folder)
  var file=FileAccess.open(folder.path_join(cls.MANIFEST_NAME),FileAccess.WRITE)
  file.store_string(cases[key]);file.close()
  var model=cls.new(folder)
  ck(key+"-no-partial-frames",textures(model)==0)
  ck(key+"-presentation-api-remains-safe",model.emit("encounter",Vector2.ZERO))
  model.advance(1.)
  ck(key+"-expires",model.events.is_empty())
 var absent=cls.new(base.path_join("absent"))
 ck("absent-manifest",textures(absent)==0)
 var valid=cls.new(args[1])
 ck("valid-assets-all32-textures",textures(valid)==32)
 var failed=checks.filter(func(c):return not c.pass)
 var result={"passed":checks.size()-failed.size(),"failed":failed.size(),"checks":checks,"sourceSha256":FileAccess.get_sha256(args[0]),"scope":"Missing paths/malformed manifest fields, not arbitrary corrupt-PNG decoding"}
 var f=FileAccess.open(args[2],FileAccess.WRITE);f.store_string(JSON.stringify(result," ")+"\n");f.close()
 print(JSON.stringify({"passed":result.passed,"failed":result.failed,"failures":failed}))
 print("ENCOUNTER_MISSING_ASSETS_DONE")
 quit(1 if failed.size()>0 else 0)
