extends "rpg-2-star-ocean-the-second_heroine-sea_motion-capture-root_test-only-v02_20261020-193528-841e9bf3.gd"
# Staged visual state reel; inherits the tested same-arena drawing/setup controls.
# This never sends normal attack input, changes HP or claims gameplay synchronization.
func _run() -> void:
 var a := OS.get_cmdline_user_args()
 assert(a.size()==5,"config,out,lang,fps,plate")
 assert(FileAccess.get_sha256("res://scripts/battle_arena.gd")==ARENA_SHA)
 var cfg := _json(a[0])
 var out: String=a[1]
 var language: String=a[2]
 var fps: int=int(a[3])
 assert(fps in [30,60] and language in ["en","zh"])
 root.size=Vector2i(1280,720)
 await process_frame
 await process_frame
 assert(root.get_visible_rect().size==Vector2(640,360))
 var arena: Node2D=await _setup(language,a[4]=="outskirts")
 var textures: Dictionary={}
 for key in cfg["poses"]:
  textures[key]=_load_texture(cfg["root"],cfg["root"],cfg["poses"][key])
 var baseline: Image=await _capture(arena,"",Vector2i(1280,720))
 var ui:=_controls(arena)
 var x:=roundf(float(arena.fighters[0]["x"]))
 var original: Texture2D=arena._female_combat_texture(arena.fighters[0],0)
 var original_rect:=Rect2i(Vector2i(int(x),272)-Vector2i(arena.HERO_COMBAT_ANCHOR),Vector2i(original.get_size()))
 var bounds:=original_rect.merge(Rect2i(Vector2i(int(x)-32,204),Vector2i(68,72)))
 var phys:=Rect2i(bounds.position*2,bounds.size*2)
 var critical: Array=[]
 var hashes: Array[String]=[]
 var report_frames: Array=[]
 var fdir:=out.path_join("frames-"+language)
 DirAccess.make_dir_recursive_absolute(fdir)
 var frame_index:=0
 var actual_poses: Array[String]=[]
 for segment in cfg["timeline"]:
  actual_poses.append(String(segment["pose"]))
  arena.inject=true
  arena.candidate=textures[String(segment["pose"])]
  for sample in (fps/30):
   var path:=fdir.path_join("frame_%05d.png"%frame_index)
   var im: Image=await _capture(arena,path,Vector2i(1280,720))
   hashes.append(FileAccess.get_sha256(path))
   if bool(segment.get("critical",false)) and sample==0:
    var label: String=segment["label"]
    var cp:=out.path_join("rpg-2-star-ocean-the-second_heroine-sea-all8_%s-%s_staged-v01_%s.png"%[language,label,cfg["tag"]])
    assert(im.save_png(cp)==OK)
    var aa:=baseline.get_data()
    var bb:=im.get_data()
    var outside:=0
    for py in 720:
     for px in 1280:
      var idx: int=(py*1280+px)*4
      if (aa[idx]!=bb[idx] or aa[idx+1]!=bb[idx+1] or aa[idx+2]!=bb[idx+2] or aa[idx+3]!=bb[idx+3]) and not phys.has_point(Vector2i(px,py)):
       outside+=1
    assert(outside==0,"Only heroine bounds may change")
    assert(_controls(arena)==ui)
    critical.append({"action":segment["action"],"pose":segment["pose"],"label":label,"file":cp.get_file(),"sha256":FileAccess.get_sha256(cp),"outsideHero":outside,"frame":frame_index})
   frame_index+=1
 arena.inject=false
 var restored: Image=await _capture(arena,"",Vector2i(1280,720))
 assert(restored.get_data()==baseline.get_data())
 assert(_controls(arena)==ui)
 assert(actual_poses.size()==cfg["timeline"].size())
 var report: Dictionary={"staged":true,"all8VisualStatesOnly":true,"normalInputGameplay":false,"motionApproved":false,"fps":fps,"language":language,"plate":a[4],"arenaSha256":ARENA_SHA,"configSha256":FileAccess.get_sha256(a[0]),"harnessSha256":FileAccess.get_sha256(get_script().resource_path),"width":1280,"height":720,"logical":[640,360],"frames":frame_index,"seconds":float(frame_index)/fps,"posesByTick":actual_poses,"framesHash":_sha_text("\n".join(hashes)),"critical":critical,"restoredExact":true,"controlsExact":true,"cameraPartyDefaultUnchanged":true,"knownAttackDamageContactMismatchMs":166.667,"skillSemantics":"hero personal skill grants next_attack_bonus atpress, not direct damage; staged skill apex is not damage synchronization"}
 var f:=FileAccess.open(out.path_join("rpg-2-star-ocean-the-second_heroine-sea-all8_%s-report_staged-v01_%s.json"%[language,cfg["tag"]]),FileAccess.WRITE)
 f.store_string(JSON.stringify(report,"  ")+"\n")
 f.close()
 print("HSEA_ALL8_STAGED_OK lang=",language," frames=",frame_index," outside=0 restore=true")
 current_scene=null
 arena.queue_free()
 await process_frame
 call_deferred("quit",0)
